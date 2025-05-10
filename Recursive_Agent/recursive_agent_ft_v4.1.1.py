"""
🌀 RecursiveAgentFT · v4.1.1

Recursive Agent of Flow, Collapse, and Traceable Witnessing.

* Adaptive RL reward tuning with meta‑adjustment
* Concurrency control (asyncio / trio) with blocking time‑out & metrics
* Replayable, HMAC‑signed QuantumTicks with Lamport + HLC clocks
* SQLite ring‑buffer for tick history
* Prometheus instrumentation with graceful degradation
* Extensive logging & warning hooks so production mis‑configs surface quickly

Everything is **enabled by default**; `low_latency_mode` disables heavy features
for micro‑benchmarks.
"""
from __future__ import annotations

__version__ = "4.1.1"
_SCHEMA_VERSION__ = "2025‑Q3‑agent‑lamport‑rl"

import asyncio
import logging
import os
import pickle
import sqlite3
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ---------------------------------------------------------------------------
# Metrics (Prometheus) with stub fallback – emits a warning once.
# ---------------------------------------------------------------------------
try:
    from prometheus_client import Counter, Gauge  # type: ignore
except ImportError:  # pragma: no cover
    logger.warning(
        "Prometheus client not available; metrics will be collected with a stub."
    )

    class _Stub:  # noqa: D401
        """Minimal stub matching Counter/Gauge API."""

        def __init__(self, *_, **__):
            self._value = 0
            self._lock = threading.Lock()

        def inc(self, amt: float = 1.0):
            with self._lock:
                self._value += amt

        def dec(self, amt: float = 1.0):
            with self._lock:
                self._value -= amt

        def set(self, val):  # noqa: ANN001
            with self._lock:
                self._value = val

        def labels(self, *_, **__):
            return self

    Counter = Gauge = _Stub  # type: ignore

# ---------------------------------------------------------------------------
# Dependency placeholders (only active in unit‑test / standalone runs)
# ---------------------------------------------------------------------------
try:
    from logical_agent_at import LogicalAgentAT  # type: ignore
except ImportError:  # pragma: no cover
    logger.warning("Using stub LogicalAgentAT — install real module in production.")

    class LogicalAgentAT:  # type: ignore
        """Very light watcher stub."""

        def __init__(self, hmac_shared_secret: Optional[bytes] | None = None):
            self.hmac_shared_secret = hmac_shared_secret

        def register_tick(self, motif: str, tick):  # noqa: ANN001
            logger.debug("Stub watcher got tick %s (motif %s)", tick, motif)

        def verify_hmac(self, tick) -> bool:  # noqa: ANN001
            if self.hmac_shared_secret is None:
                return True
            return tick.verify(self.hmac_shared_secret)


try:
    from quantum_tick import QuantumTick  # type: ignore
except ImportError:  # pragma: no cover
    logger.warning("Using stub QuantumTick — install real module in production.")

    class QuantumTick:  # type: ignore
        """Stand‑in implementation with minimal fields."""

        def __init__(self):
            self.coherence_hash = os.urandom(16).hex()
            self.hlc_ts = time.time()
            self.tick_hmac = b""
            self.replayable = False
            self.previous_hash: Optional[str] = None
            self.lamport = 0
            self.stage = ""
            self.agent_id = ""
            self.motif_id = ""

        # ----------------------------- factory -----------------------------
        @classmethod
        def now(
            cls,
            *,
            motif_id: str,
            agent_id: str,
            stage: str,
            secret: Optional[bytes],
            lamport: int,
        ):
            import hashlib, hmac

            tick = cls()
            tick.motif_id = motif_id
            tick.agent_id = agent_id
            tick.stage = stage
            tick.lamport = lamport
            if secret:
                tick.tick_hmac = hmac.new(
                    secret,
                    f"{tick.coherence_hash}{lamport}".encode(),
                    hashlib.sha256,
                ).digest()
            return tick

        def verify(self, secret: bytes) -> bool:
            import hashlib, hmac

            if not secret:
                return True
            expected = hmac.new(
                secret,
                f"{self.coherence_hash}{self.lamport}".encode(),
                hashlib.sha256,
            ).digest()
            return hmac.compare_digest(self.tick_hmac, expected)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _get_semaphore(max_parallel: int):
    """Return an asyncio or trio capacity‑limiter depending on runtime."""
    try:
        import trio  # type: ignore

        return trio.CapacityLimiter(max_parallel)  # type: ignore[return-value]
    except ImportError:  # pragma: no cover
        return asyncio.BoundedSemaphore(max_parallel)


class LRUCache(OrderedDict):
    """Tiny size‑bounded LRU cache with thread‑safety."""

    def __init__(self, cap: int = 50_000):
        super().__init__()
        self.cap = cap
        self._lock = threading.Lock()

    def __setitem__(self, key, value):  # noqa: ANN001
        with self._lock:
            if key in self:
                del self[key]
            super().__setitem__(key, value)
            if len(self) > self.cap:
                self.popitem(last=False)

    def get(self, key, default=None):  # noqa: ANN001
        with self._lock:
            return super().get(key, default)


# ---------------------------------------------------------------------------
# CommentaryRecord dataclass
# ---------------------------------------------------------------------------


@dataclass
class CommentaryRecord:
    schema_version: str
    type: str
    value: str
    entropy: float
    tick_ref: Optional[QuantumTick]
    previous_hash: Optional[str]
    spawn_id: Optional[str]
    join_id: Optional[str]
    stage: Optional[str]
    origin: Optional[str]
    replayable: bool = False


# ---------------------------------------------------------------------------
# RecursiveAgentFT
# ---------------------------------------------------------------------------


class RecursiveAgentFT:
    """Recursive agent that generates, signs, and evaluates QuantumTicks."""

    # ---- Prometheus metrics -------------------------------------------------
    _M_SPAWN_RUNNING = Counter(
        "agent_spawn_running_total", "Current concurrent spawns", ["agent_id"]
    )
    _M_SPAWN_BLOCKED = Counter(
        "agent_spawn_blocked_total", "Spawn attempts blocked", ["agent_id", "reason"]
    )
    _M_TICKS_EMITTED = Counter(
        "agent_ticks_emitted_total", "Ticks emitted", ["agent_id", "stage"]
    )
    _M_HMAC_FAILURE = Counter(
        "agent_tick_hmac_failures_total", "HMAC verification failures", ["agent_id"]
    )
    _M_DUP_TICK = Counter(
        "agent_tick_duplicate_total", "Duplicate ticks", ["agent_id"]
    )
    _M_REPLAYABLE = Counter(
        "agent_replayable_ticks_total", "Replayable ticks stored", ["agent_id"]
    )
    _M_REWARD_MEAN = Gauge("agent_reward_mean", "EMA of reward", ["agent_id"])

    LATENCY_BUDGET = float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))

    # --------------------------------------------------------------------- #
    # constructor                                                           #
    # --------------------------------------------------------------------- #
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: List[LogicalAgentAT],
        *,
        agent_id: str = "agent@default",
        max_parallel: int = 8,
        hmac_secret: Optional[bytes] = None,
        rl_spawn_reward: Optional[Callable[[QuantumTick], float]] = None,
        commentary_mode: str = "auto",
        allow_replayable_ticks: bool = True,
        seen_hash_cap: int = 50_000,
        low_latency_mode: bool = False,
        spawn_timeout: float | None = 5.0,
    ) -> None:
        self.agent_id = agent_id
        self.core_state = initial_state.astype(float, copy=True)
        self.watchers = watchers
        self.hmac_secret = (
            hmac_secret or os.getenv("NOOR_SHARED_HMAC", "").encode() or None
        )
        self.commentary_mode = commentary_mode
        self.allow_replayable_ticks = allow_replayable_ticks and not low_latency_mode
        self.low_latency_mode = low_latency_mode
        self.spawn_timeout = spawn_timeout
        self.rl_spawn_reward = rl_spawn_reward or self._default_spawn_reward
        self._spawn_sem = _get_semaphore(max_parallel)
        self._lamport = 0
        self._last_tick_hash: Dict[str, str] = {}
        self.seen_hashes = LRUCache(cap=seen_hash_cap)

        # RL weights – documented rationale
        self.rl_weights: Dict[str, float] = {
            "delta_entropy": +0.4,   # reward higher collapse entropy
            "join_latency_ok": +0.3,  # reward staying within latency budget
            "harmonic_hit": +0.2,     # reward motif‑specific harmonic criteria
            "duplicate_tick": -1.0,   # penalise duplicates harshly
        }
        self._entropy_history: List[float] = []
        self._latency_mean: float = 0.0
        self._reward_ema: float = 0.0

        # Replay DB if enabled
        self._db: Optional[sqlite3.Connection]
        if self.allow_replayable_ticks:
            self._db = sqlite3.connect("replay_ticks.db", check_same_thread=False)
            self._setup_db()
        else:
            self._db = None

        # metric label cache
        self._labels = {"agent_id": self.agent_id}

    # ------------------------------------------------------------------ #
    # DB helpers                                                          #
    # ------------------------------------------------------------------ #
    def _setup_db(self):
        assert self._db is not None
        with self._db:
            self._db.execute(
                """
                CREATE TABLE IF NOT EXISTS ticks (
                    coherence_hash TEXT PRIMARY KEY,
                    blob            BLOB,
                    ts              REAL
                )
                """
            )

    def _db_put_tick(self, tick: QuantumTick):
        if not self._db:
            return
        try:
            with self._db:
                self._db.execute(
                    "INSERT OR REPLACE INTO ticks VALUES (?,?,?)",
                    (tick.coherence_hash, pickle.dumps(tick), time.time()),
                )
                self._db.execute(
                    """
                    DELETE FROM ticks
                    WHERE coherence_hash NOT IN (
                        SELECT coherence_hash
                        FROM ticks
                        ORDER BY ts DESC
                        LIMIT 10000
                    )
                    """
                )
        except sqlite3.DatabaseError as exc:  # pragma: no cover
            logger.exception("SQLite error persisting tick: %s", exc)

    def _db_get_tick(self, coherence_hash: str) -> Optional[QuantumTick]:
        if not self._db:
            return None
        try:
            cur = self._db.execute(
                "SELECT blob FROM ticks WHERE coherence_hash=?",
                (coherence_hash,),
            )
            row = cur.fetchone()
            if row:
                return pickle.loads(row[0])  # noqa: S301 (trusted env)
        except sqlite3.DatabaseError as exc:  # pragma: no cover
            logger.exception("SQLite error loading tick: %s", exc)
        return None

    # ------------------------------------------------------------------ #
    # RL helpers                                                          #
    # ------------------------------------------------------------------ #
    def set_reward_weight(self, key: str, value: float):
        self.rl_weights[key] = float(value)

    def update_rewards(self, **weights: float):
        for k, v in weights.items():
            self.rl_weights[k] = float(v)

    def ingest_feedback(self, ctx_ratio: float, entropy: float, latency: float):
        self._entropy_history.append(entropy)
        self._latency_mean = 0.9 * self._latency_mean + 0.1 * latency
        self._auto_adjust_weights()

    def _auto_adjust_weights(self):
        if len(self._entropy_history) < 2:
            return
        # simple gradient sign ascent on entropy
        g = np.gradient(np.array(self._entropy_history))[-1]
        self.rl_weights["delta_entropy"] += 0.05 * np.sign(g)
        # punish latency overshoot
        if self._latency_mean > self.LATENCY_BUDGET:
            self.rl_weights["join_latency_ok"] *= 0.8

    @staticmethod
    def _default_spawn_reward(_: QuantumTick) -> float:  # noqa: D401
        return 1.0

    # ------------------------------------------------------------------ #
    # Lamport clock                                                       #
    # ------------------------------------------------------------------ #
    def increment_lamport(self) -> int:
        self._lamport += 1
        return self._lamport

    # ------------------------------------------------------------------ #
    # Tick emission                                                       #
    # ------------------------------------------------------------------ #
    def emit_tick(
        self, motif: str, *, stage: str = "E2b", replayable: bool = False
    ) -> QuantumTick:
        lamport = self.increment_lamport()
        tick = QuantumTick.now(
            motif_id=motif,
            agent_id=self.agent_id,
            stage=stage,
            secret=None if self.low_latency_mode else self.hmac_secret,
            lamport=lamport,
        )
        tick.previous_hash = self._last_tick_hash.get(motif)
        if replayable and self.allow_replayable_ticks:
            tick.replayable = True

        # duplicate suppression
        if tick.coherence_hash in self.seen_hashes:
            self._M_DUP_TICK.labels(**self._labels).inc()
            return tick
        self.seen_hashes[tick.coherence_hash] = True

        # persist if replayable
        if tick.replayable:
            self._M_REPLAYABLE.labels(**self._labels).inc()
            self._db_put_tick(tick)

        # send to watchers
        for watcher in self.watchers:
            if (
                not self.low_latency_mode
                and watcher.hmac_shared_secret is not None
                and not watcher.verify_hmac(tick)
            ):
                self._M_HMAC_FAILURE.labels(**self._labels).inc()
                logger.warning(
                    "Watcher rejected tick due to HMAC mismatch (agent %s)", self.agent_id
                )
                continue
            watcher.register_tick(motif, tick)

        self._M_TICKS_EMITTED.labels(stage=stage, **self._labels).inc()
        self._last_tick_hash[motif] = tick.coherence_hash

        # reward tracking
        reward = self.rl_spawn_reward(tick)
        self._reward_ema = 0.9 * self._reward_ema + 0.1 * reward
        self._M_REWARD_MEAN.labels(**self._labels).set(self._reward_ema)
        return tick

    # ------------------------------------------------------------------ #
    # Replay                                                              #
    # ------------------------------------------------------------------ #
    def replay_from(self, coherence_hash: str):
        if not self.allow_replayable_ticks:
            raise RuntimeError("Replay disabled (low‑latency mode or flag).")
        tick = self._db_get_tick(coherence_hash)
        if tick is None:
            raise KeyError(f"No stored tick with hash {coherence_hash}")
        for watcher in self.watchers:
            watcher.register_tick(tick.motif_id, tick)

    # ------------------------------------------------------------------ #
    # Spawn (async)                                                       #
    # ------------------------------------------------------------------ #
    async def spawn(self, motif: str, *, stage: str = "E2b") -> QuantumTick:
        """Spawn a reasoning branch, respecting the max‑parallel cap."""
        # Acquire semaphore with optional timeout
        try:
            if isinstance(self._spawn_sem, asyncio.Semaphore):
                if self.spawn_timeout is None:
                    await self._spawn_sem.acquire()
                else:
                    await asyncio.wait_for(
                        self._spawn_sem.acquire(), timeout=self.spawn_timeout
                    )
            else:  # trio limiter — no built‑in timeout
                await self._spawn_sem.acquire_on_behalf_of(asyncio.current_task())  # type: ignore[attr-defined]
        except (asyncio.TimeoutError, ValueError):
            self._M_SPAWN_BLOCKED.labels(reason="blocked", **self._labels).inc()
            raise

        self._M_SPAWN_RUNNING.labels(**self._labels).inc()
        start = time.perf_counter()
        try:
            tick = self.emit_tick(
                motif, stage=stage, replayable=self.allow_replayable_ticks
            )
            latency = time.perf_counter() - start
            # entropy placeholder – replace with real collapse entropy if available
            entropy_signal = np.random.rand()
            self.ingest_feedback(1.0, entropy_signal, latency)
            return tick
        finally:
            # release semaphore
            if isinstance(self._spawn_sem, asyncio.Semaphore):
                self._spawn_sem.release()
            else:
                self._spawn_sem.release_on_behalf_of(asyncio.current_task())  # type: ignore[attr-defined]
            self._M_SPAWN_RUNNING.labels(**self._labels).dec()

# END_OF_FILE
