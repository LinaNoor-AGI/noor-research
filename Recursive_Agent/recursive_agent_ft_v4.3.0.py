﻿"""
🌀 RecursiveAgentFT · v4.3.0

Motif-aware reasoning agent with
• Dynamic boost            • Latency-coupled decay
• Presence-field modulation • Live RL feedback to NoorFastTimeCore
"""
from __future__ import annotations

import asyncio
import logging
import os
import pickle
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from random import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from motif_memory_manager_v1.0.1 import get_global_memory_manager

try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    class _Stub:                               # noqa: D401
        def labels(self, *_, **__):             # noqa: ANN001
            return self
        def inc(self, *_):                      # noqa: D401
            pass
        def dec(self, *_):                      # noqa: D401
            pass
        def set(self, *_):                      # noqa: D401
            pass
    Counter = Gauge = _Stub                    # type: ignore

try:
    from noor_fasttime_core import NoorFastTimeCore  # type: ignore
except ImportError:  # pragma: no cover
    NoorFastTimeCore = object  # fallback type hint

from .quantum_ids import make_change_id, MotifChangeID  # not used yet but imported for future use

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ──────────────────────────────────────────────────────────────
# Helper LRU cache
# ──────────────────────────────────────────────────────────────
class LRUCache(OrderedDict):
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
__version__ = "4.3.0"
_SCHEMA_VERSION__ = "2025-Q3-agent-motif-adaptive"

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

    # ─── Symbolic-Metabolism Constants (tweakable at runtime) ──────────
    BOOST_JITTER: float = 0.05    # ±5 % noise on boost
    DECAY_JITTER: float = 0.05    # ±5 % noise on decay
    FIELD_DECAY_MAP: dict[str, float] = {
        "ψ-null@Ξ":      0.7,
        "ψ-resonance@Ξ": 1.0,
        "ψ-spar@Ξ":      1.3,
        "ψ-mock@Ξ":      1.4,
    }

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
    ):
        env_secret = os.getenv("NOOR_SHARED_HMAC")
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
        self.seen_hashes = LRUCache()

        # RL weights
        self.rl_weights = {
            "delta_entropy": 0.4,
            "join_latency_ok": 0.3,
            "harmonic_hit": 0.2,
            "duplicate_tick": -1.0,
        }
        self._reward_ema = 0.0

        # Concurrency limiter
        if async_mode:
            import anyio  # type: ignore
            self._spawn_sem = anyio.CapacityLimiter(max_parallel)
        else:
            self._spawn_sem = asyncio.BoundedSemaphore(max_parallel)

    # ──────────────────────────────
    # Presence-field heuristic
    # ──────────────────────────────
    def _resolve_field(self, motif: str) -> str:  # noqa: D401
        """Best-effort field resolver. Falls back gracefully if unavailable."""
        try:
            from symbolic_task_engine import SymbolicTaskEngine  # type: ignore
            eng = SymbolicTaskEngine.INSTANCE
            if eng and hasattr(eng, "resolve_presence_field"):
                return eng.resolve_presence_field([motif])
        except Exception:  # pragma: no cover
            pass
        # simple heuristic fallback
        if motif in {"silence", "grief"}:
            return "ψ-bind@Ξ"
        return "ψ-resonance@Ξ"

    # ──────────────────────────────
    # Utilities
    # ──────────────────────────────
    def increment_lamport(self) -> int:
        self._lamport += 1
        return self._lamport

    def get_parallel_running(self) -> int:
        if isinstance(self._spawn_sem, asyncio.Semaphore):
            return self._spawn_sem._value  # type: ignore[attr-defined]
        else:  # anyio limiter
            return self._spawn_sem.borrowed_tokens  # type: ignore[attr-defined]

    # ──────────────────────────────
    # Tick emission
    # ──────────────────────────────
    def _emit_tick(self, motif: str, stage: str = "E2b") -> QuantumTick:
        lamport = self.increment_lamport()
        tick = QuantumTick.now(
            motif_id=motif,
            agent_id=self.agent_id,
            stage=stage,
            secret=None if self.low_latency_mode else self.hmac_secret,
            lamport=lamport,
        )
        return tick

    # ──────────────────────────────
    # Public async spawn
    # ──────────────────────────────
    async def spawn(self, motif: str, *, stage: str = "E2b"):
        # ── Adaptive boost before semaphore acquisition ────────────────
        memory = get_global_memory_manager()
        stmm, _ = memory.export_state()
        weight = stmm.get(motif, 0.0)
        base_boost = max(0.05, 1.0 - max(0.0, weight))
        boost = base_boost * (1.0 + (random() - 0.5) * self.BOOST_JITTER)
        memory.access(motif, boost=boost)

        if getattr(memory, "_trace", False):
            memory._log("tick_spawned", motif, boost)

        # acquire
        if isinstance(self._spawn_sem, asyncio.Semaphore):
            await self._spawn_sem.acquire()
        else:
            await self._spawn_sem.acquire_on_behalf_of(asyncio.current_task())  # type: ignore[attr-defined]

        start = time.perf_counter()
        try:
            tick = self._emit_tick(motif, stage)
            entropy_signal = np.random.rand()

            # distribute tick to watchers
            for w in self.watchers:
                w.register_tick(motif, tick)

            latency = time.perf_counter() - start
            bias_score, next_budget = self._feedback_to_core(
                entropy_signal, latency, tick
            )
            # adjust internal latency budget and reward weight
            self.latency_budget = next_budget
            self.rl_weights["join_latency_ok"] = 0.3 * (
                self.latency_budget / float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
            )

            # reward update
            reward = 1.0 + bias_score
            self._reward_ema = 0.9 * self._reward_ema + 0.1 * reward
            self.REWARD_MEAN.labels(agent_id=self.agent_id).set(self._reward_ema)
            self.TICKS_EMITTED.labels(stage=stage, agent_id=self.agent_id).inc()
            return tick
        finally:
            # ── Adaptive decay after feedback ───────────────────────────
            decay_alpha = min(1.0, self.latency_budget * 20)
            field = self._resolve_field(motif)
            decay_alpha *= self.FIELD_DECAY_MAP.get(field, 1.0)
            decay_alpha *= 1.0 + (random() - 0.5) * self.DECAY_JITTER

            try:
                memory.update_cycle(decay_factor=decay_alpha)
            except TypeError:
                memory.update_cycle()  # backward-compat

            # release
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
        bias, next_budget = self.core.receive_feedback(
            ctx_ratio=1.0,
            ghost_entropy=entropy,
            harm_hits=0,
            step_latency=latency,
            latest_tick=tick,
            parallel_running=parallel_running,
        )
        return bias, next_budget

# End of File
