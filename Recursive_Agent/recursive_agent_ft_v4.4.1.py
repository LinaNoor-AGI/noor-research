"""
🌀 RecursiveAgentFT · v4.4.1

Adaptive-pulse reasoning agent:
• Autonomous tick emission with self-tuning cadence
• Inverse-salience boost & ψ-field decay (unchanged)
• Fast-Time-Core feedback coupling (unchanged)
• Prometheus observability for pulse, reward, and back-off
"""

from __future__ import annotations

__version__ = "4.4.1"
_SCHEMA_VERSION__ = "2025-Q3-agent-motif-autonomous"

import asyncio
import logging
import os
import pickle
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from random import random
from statistics import fmean
from typing import Dict, List, Optional, Tuple

import numpy as np

from noor.motif_memory_manager import get_global_memory_manager

try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    class _Stub:
        def labels(self, *_, **__):
            return self
        def inc(self, *_):
            pass
        def dec(self, *_):
            pass
        def set(self, *_):
            pass
    Counter = Gauge = _Stub  # type: ignore

# dedicated metric for feedback failures
try:
    CORE_FEEDBACK_ERRORS = Counter(
        "agent_core_feedback_errors_total",
        "Core feedback exceptions caught",
        ["agent_id"],
    )
except Exception:  # pragma: no cover
    CORE_FEEDBACK_ERRORS = _Stub()  # type: ignore

try:
    from noor_fasttime_core import NoorFastTimeCore  # type: ignore
except ImportError:  # pragma: no cover
    NoorFastTimeCore = object  # fallback type hint

from .quantum_ids import make_change_id, MotifChangeID  # imported for future use

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ──────────────────────────────────────────────────────────────
# Helper LRU cache
# ──────────────────────────────────────────────────────────────
class LRUCache(OrderedDict):
    """Thread-safe fixed-capacity LRU."""
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

# ──────────────────────────────────────────────────────────────
# Stub QuantumTick (real one imported in prod)
# ──────────────────────────────────────────────────────────────
try:
    from quantum_tick import QuantumTick  # type: ignore
except ImportError:  # pragma: no cover
    class QuantumTick:  # noqa: D401
        """Lightweight stand-in for QuantumTick."""
        def __init__(self):
            self.coherence_hash = os.urandom(16).hex()
            self.lamport = 0
            self.stage = "E2b"
            self.agent_id = ""
        @classmethod
        def now(cls, *, motif_id, agent_id, stage, secret, lamport):  # noqa: ANN001
            tick = cls()
            tick.motif_id = motif_id
            tick.agent_id = agent_id
            tick.stage = stage
            tick.lamport = lamport
            return tick
        def verify(self, secret):  # noqa: ANN001
            return True

# ──────────────────────────────────────────────────────────────
# RecursiveAgentFT
# ──────────────────────────────────────────────────────────────
class RecursiveAgentFT:
    """Reasoning agent emitting QuantumTicks and learning via RL feedback."""

    TICKS_EMITTED = Counter(
        "agent_ticks_emitted_total", "Ticks emitted", ["agent_id", "stage"]
    )
    DUP_TICK = Counter(
        "agent_tick_duplicate_total", "Duplicate ticks", ["agent_id"]
    )
    REWARD_MEAN = Gauge(
        "agent_reward_mean", "EMA of reward", ["agent_id"]
    )

    # ── new pulse-metrics ───────────────────────────────────────────
    AGENT_EMISSION_INTERVAL = Gauge(
        "agent_emission_interval_seconds",
        "Current autonomous emission interval",
        ["agent_id"],
    )
    AGENT_PULSE_TOTAL = Counter(
        "agent_autonomous_loops_total",
        "Autonomous emission loops executed",
        ["agent_id"],
    )

    # back-off metric
    PULSE_BACKOFF_TOTAL = Counter(
        "agent_pulse_backoff_total",
        "Times emission loop applied back-off after repeated Core failures",
        ["agent_id"],
    )

    # Symbolic-metabolism constants (env-overrideable)
    BOOST_JITTER: float = float(os.getenv("NOOR_BOOST_JITTER", "0.05"))
    DECAY_JITTER: float = float(os.getenv("NOOR_DECAY_JITTER", "0.05"))
    FIELD_DECAY_MAP: dict[str, float] = {
        "ψ-null@Ξ":      0.7,
        "ψ-resonance@Ξ": 1.0,
        "ψ-spar@Ξ":      1.3,
        "ψ-mock@Ξ":      1.4,
    }

    # ──────────────────────────────
    # Construction
    # ──────────────────────────────
    def __init__(
        self,
        initial_state,
        watchers: List,
        *,
        agent_id: str = "agent@default",
        max_parallel: int = 8,
        hmac_secret: bytes | None = None,
        core: Optional[NoorFastTimeCore] = None,
        latency_budget: float | None = None,
        async_mode: bool = False,
        low_latency_mode: bool = False,
        lru_cap: int = 50_000,
        boost_jitter: float | None = None,
        decay_jitter: float | None = None,
        base_interval: float | None = None,
        min_interval: float = 0.25,
        max_interval: float = 10.0,
    ):
        env_secret = os.getenv("NOOR_SHARED_HMAC", "")
        self.hmac_secret = hmac_secret or (env_secret.encode() if env_secret else None)

        self.latency_budget = (
            latency_budget
            if latency_budget is not None
            else float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
        )

        self.agent_id = agent_id
        self.core: Optional[NoorFastTimeCore] = core
        self.watchers = watchers
        self.low_latency_mode = low_latency_mode
        self.core_state = np.array(initial_state, dtype=float, copy=True)

        self._lamport = 0
        self._last_tick_hash: Dict[str, str] = {}
        self.seen_hashes = LRUCache(lru_cap)

        # RL weights (env-configurable)
        self.rl_weights: Dict[str, float] = {
            "delta_entropy": 0.4,
            "join_latency_ok": 0.3,
            "harmonic_hit": 0.2,
            "duplicate_tick": -1.0,
        }
        # ---- optional override via NOOR_RL_WEIGHTS ----------------------
        # format: "delta_entropy:0.5,duplicate_tick:-1.0"
        env_w = os.getenv("NOOR_RL_WEIGHTS")
        if env_w:
            try:
                for kv in env_w.split(","):
                    k, v = kv.split(":")
                    self.rl_weights[k.strip()] = float(v)
            except Exception:
                logger.warning("Failed to parse NOOR_RL_WEIGHTS=%s", env_w)

        # normalise positive weights so they roughly sum to 1.0
        pos_sum = sum(w for w in self.rl_weights.values() if w > 0)
        if pos_sum:
            for k, v in self.rl_weights.items():
                if v > 0:
                    self.rl_weights[k] = round(v / pos_sum, 3)

        self._reward_ema = 0.0
        self._last_latency_ratio = 1.0      # updated each spawn()

        # circuit-breaker state
        self._fb_fail_streak = 0
        self._backoff_mult = 1.0

        # silence-streak guard
        self._silence_streak = 0

        # Pulse-timing bounds
        self.base_interval = base_interval or float(
            os.getenv("NOOR_BASE_INTERVAL", "5.0")
        )
        self.min_interval = min_interval
        self.max_interval = max_interval

        # allow per-instance jitter tuning
        if boost_jitter is not None:
            self.BOOST_JITTER = boost_jitter
        if decay_jitter is not None:
            self.DECAY_JITTER = decay_jitter

        # Concurrency limiter
        if async_mode:
            import anyio  # type: ignore
            self._spawn_sem = anyio.CapacityLimiter(max_parallel)
        else:
            self._spawn_sem = asyncio.BoundedSemaphore(max_parallel)

        # Background pulse task holder
        self._emission_task: Optional[asyncio.Task] = None

    # ──────────────────────────────
    # Field resolution
    # ──────────────────────────────
    def _resolve_field(self, motif: str) -> str:
        """
        Map a motif to its ψ-field.
        Priority: SymbolicTaskEngine helper → heuristic fallback.
        Always returns a label; never raises.
        """
        try:
            from symbolic_task_engine import SymbolicTaskEngine  # type: ignore
            eng = SymbolicTaskEngine.INSTANCE
            if eng and hasattr(eng, "resolve_presence_field"):
                return eng.resolve_presence_field([motif])
        except Exception:  # pragma: no cover
            pass
        if motif in {"silence", "grief"}:
            return "ψ-bind@Ξ"
        return "ψ-resonance@Ξ"

    # ──────────────────────────────
    # Adaptive helpers
    # ──────────────────────────────
    def _apply_adaptive_boost(self, motif: str):
        """Access motif with inverse-salience boost (+ jitter); returns memory obj."""
        memory = get_global_memory_manager()
        stmm, _ = memory.export_state()
        weight = stmm.get(motif, 0.0)
        base = max(0.05, 1.0 - max(0.0, weight))
        boost = base * (1.0 + (random() - 0.5) * self.BOOST_JITTER)
        memory.access(motif, boost=boost)
        if getattr(memory, "_trace", False):
            memory._log("tick_spawned", motif, boost)
        return memory

    def _apply_adaptive_decay(self, motif: str, memory):
        """Decay STMM/LTMM weights with latency, field & jitter modulation."""
        decay_alpha = min(1.0, self.latency_budget * 20)
        field = self._resolve_field(motif)
        decay_alpha *= self.FIELD_DECAY_MAP.get(field, 1.0)
        decay_alpha *= 1.0 + (random() - 0.5) * self.DECAY_JITTER
        try:
            memory.update_cycle(decay_factor=decay_alpha)
        except TypeError:  # backward compat
            memory.update_cycle()

    # ──────────────────────────────
    # Utilities
    # ──────────────────────────────
    def increment_lamport(self) -> int:
        self._lamport += 1
        return self._lamport

    def get_parallel_running(self) -> int:
        if isinstance(self._spawn_sem, asyncio.Semaphore):
            return self._spawn_sem._value  # type: ignore[attr-defined]
        else:
            return self._spawn_sem.borrowed_tokens  # type: ignore[attr-defined]

    # ──────────────────────────────
    # Tick emission
    # ──────────────────────────────
    def _emit_tick(self, motif: str, stage: str = "E2b") -> QuantumTick:
        lamport = self.increment_lamport()
        return QuantumTick.now(
            motif_id=motif,
            agent_id=self.agent_id,
            stage=stage,
            secret=None if self.low_latency_mode else self.hmac_secret,
            lamport=lamport,
        )

    # ──────────────────────────────
    # Public async spawn
    # ──────────────────────────────
    async def spawn(self, motif: str, *, stage: str = "E2b"):
        # adaptive boost before semaphore acquisition
        memory = self._apply_adaptive_boost(motif)

        # acquire concurrency token
        if isinstance(self._spawn_sem, asyncio.Semaphore):
            await self._spawn_sem.acquire()
        else:
            await self._spawn_sem.acquire_on_behalf_of(asyncio.current_task())  # type: ignore[attr-defined]

        start = time.perf_counter()
        try:
            tick = self._emit_tick(motif, stage)
            entropy_signal = np.random.rand()

            # distribute tick only if watcher(s) exist and support .register_tick()
            for w in self.watchers or []:
                if hasattr(w, "register_tick"):
                    w.register_tick(motif, tick)

            latency = time.perf_counter() - start
            self._last_latency_ratio = (
                latency / self.latency_budget if self.latency_budget else 1.0
            )
            bias_score, next_budget = self._feedback_to_core(
                entropy_signal, latency, tick
            )
            # latency budget & RL weight tuning
            self.latency_budget = next_budget
            self.rl_weights["join_latency_ok"] = 0.3 * (
                self.latency_budget / float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
            )

            reward = 1.0 + bias_score
            self._reward_ema = 0.9 * self._reward_ema + 0.1 * reward
            self.REWARD_MEAN.labels(agent_id=self.agent_id).set(self._reward_ema)
            self.TICKS_EMITTED.labels(stage=stage, agent_id=self.agent_id).inc()

            # Successful Core round-trip — reset failure streak/back-off
            self._fb_fail_streak = 0
            self._backoff_mult = 1.0

            return tick
        finally:
            # adaptive decay after core feedback
            self._apply_adaptive_decay(motif, memory)

            # release concurrency token
            if isinstance(self._spawn_sem, asyncio.Semaphore):
                self._spawn_sem.release()
            else:
                self._spawn_sem.release_on_behalf_of(asyncio.current_task())  # type: ignore[attr-defined]

    # ──────────────────────────────
    # Core feedback
    # ──────────────────────────────
    def _feedback_to_core(
        self, entropy: float, latency: float, tick: QuantumTick
    ) -> Tuple[float, float]:
        if not self.core:
            return 0.0, self.latency_budget
        parallel_running = self.get_parallel_running()
        try:
            return self.core.receive_feedback(
                ctx_ratio=1.0,
                ghost_entropy=entropy,
                harm_hits=0,
                step_latency=latency,
                latest_tick=tick,
                parallel_running=parallel_running,
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Core feedback failed: %s", exc)
            CORE_FEEDBACK_ERRORS.labels(agent_id=self.agent_id).inc()

            # ---- circuit breaker ----------------------------------------
            self._fb_fail_streak += 1
            if self._fb_fail_streak >= 3:
                # exponential back-off capped at ×4
                if self._backoff_mult < 4.0:
                    self._backoff_mult *= 2.0
                    self.PULSE_BACKOFF_TOTAL.labels(agent_id=self.agent_id).inc()
            return 0.0, self.latency_budget

    # ──────────────────────────────
    # Autonomous emission loop
    # ──────────────────────────────
    async def start_continuous_emission(self, *, base_interval: float | None = None):
        """
        Adaptive-pulse loop:
          • selects a motif from STMM (weighted)
          • emits a QuantumTick via ``await self.spawn()``
          • sleeps for an interval self-tuned by reward & latency
        Cancelling the returned task stops the loop gracefully.
        """
        if base_interval is not None:
            self.base_interval = base_interval
        mem = get_global_memory_manager()
        try:
            while True:
                stmm, _ = mem.export_state()
                weighted = [(m, w) for m, w in stmm.items() if w > 0.05]
                motif = (
                    random.choices(*zip(*weighted))[0]
                    if weighted
                    else "silence"
                )

                # --- silence-streak guard ---------------------------------
                if motif == "silence":
                    self._silence_streak += 1
                    if self._silence_streak >= 3 and weighted:
                        # force a non-silence motif with highest weight
                        non_silence = [(m, w) for m, w in weighted if m != "silence"]
                        if non_silence:
                            motif = max(non_silence, key=lambda t: t[1])[0]
                            self._silence_streak = 0
                else:
                    self._silence_streak = 0

                await self.spawn(motif)

                # ---- adaptive interval ---------------------------------
                rew_adj = 1.0 - max(-0.5, min(0.5, self._reward_ema - 1.0))
                lat_adj = 1.0 + min(1.0, max(0.0, self._last_latency_ratio - 1.0))
                interval = self.base_interval * rew_adj * lat_adj * self._backoff_mult
                interval = max(self.min_interval, min(self.max_interval, interval))
                self.AGENT_EMISSION_INTERVAL.labels(self.agent_id).set(interval)
                self.AGENT_PULSE_TOTAL.labels(self.agent_id).inc()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("[%s] emission loop cancelled", self.agent_id)
        except Exception as exc:
            logger.warning("[%s] emission loop error: %s", self.agent_id, exc)

    # ──────────────────────────────
    # Convenience wrappers
    # ──────────────────────────────
    def start_pulse(self, **kw):
        if self._emission_task is None or self._emission_task.done():
            self._emission_task = asyncio.create_task(
                self.start_continuous_emission(**kw)
            )

    def stop_pulse(self):
        if self._emission_task and not self._emission_task.done():
            self._emission_task.cancel()

# End of File
