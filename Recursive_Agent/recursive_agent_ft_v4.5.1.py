"""
🌀 RecursiveAgentFT · v4.5.1 — Cadence of Memory

• Emits RFC-0003–compliant QuantumTicks carrying multi-motif bundles.
• Self-tunes cadence via reward EMA, field-entropy drift, triadic alignment.
• Provides public observe_feedback() for Logic / Core evaluators.
• Exports CrystallizedMotifBundle frames for ψ-teleport@Ξ archival (RFC-0005).
"""
from __future__ import annotations

__version__ = "4.5.1"
_SCHEMA_VERSION__ = "2025-Q4-agent-motif-autonomous"

import asyncio
import logging
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import numpy as np
from noor.motif_memory_manager import get_global_memory_manager

try:
    from prometheus_client import Counter, Gauge
except ImportError:
    class _Stub:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def set(self, *_): pass
    Counter = Gauge = _Stub  # type: ignore

try:
    from noor_fasttime_core import NoorFastTimeCore  # type: ignore
except ImportError:
    NoorFastTimeCore = object  # type: ignore

from .quantum_ids import make_change_id, MotifChangeID

# ──────────────────────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────────────────────
@dataclass(slots=True)
class QuantumTickV2:
    tick_id: str
    motif_id: str
    coherence_hash: str
    lamport: int
    agent_id: str
    stage: str
    motifs: List[str]
    reward_ema: float
    timestamp_ms: int
    field_signature: str
    tick_hmac: Optional[str] = None

@dataclass(slots=True)
class TickEntropy:
    decay_slope: float
    coherence: float
    triad_complete: bool
    age: float

@dataclass(slots=True)
class CrystallizedMotifBundle:
    motif_bundle: List[str]
    field_signature: str
    tick_entropy: TickEntropy

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
DEFAULT_TUNING = dict(
    min_interval = 0.25,
    max_interval = 10.0,
    entropy_boost_threshold = 0.35,
    triad_bias_weight = 0.15,
    reward_smoothing = 0.2,
)
ARCHIVE_MODE = bool(int(os.getenv("NOOR_ARCHIVE_TICKS", "0")))

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
    def __setitem__(self, key, value):
        with self._lock:
            if key in self: del self[key]
            super().__setitem__(key, value)
            if len(self) > self.cap: self.popitem(last=False)

# ──────────────────────────────────────────────────────────────
# RecursiveAgentFT
# ──────────────────────────────────────────────────────────────
class RecursiveAgentFT:
    # Metrics
    TICKS_EMITTED = Counter(
        "agent_ticks_emitted_total", "Ticks emitted", ["agent_id", "stage"]
    )
    DUP_TICK = Counter(
        "agent_tick_duplicate_total", "Duplicate ticks", ["agent_id"]
    )
    REWARD_MEAN = Gauge(
        "agent_reward_mean", "EMA of reward", ["agent_id"]
    )
    AGENT_EMISSION_INTERVAL = Gauge(
        "agent_emission_interval_seconds", "Current autonomous emission interval", ["agent_id"]
    )
    AGENT_PULSE_TOTAL = Counter(
        "agent_autonomous_loops_total", "Autonomous emission loops executed", ["agent_id"]
    )
    PULSE_BACKOFF_TOTAL = Counter(
        "agent_pulse_backoff_total", "Times emission loop back-off applied", ["agent_id"]
    )
    AGENT_ARCHIVAL_FRAMES = Counter(
        "agent_archival_frames_total", "Crystallization events emitted", ["agent_id"]
    )
    AGENT_TRIADS_COMPLETED = Counter(
        "agent_triads_completed_total", "Triads completed via feedback", ["agent_id"]
    )

    def __init__(
        self,
        initial_state,
        watchers: List,
        *,
        agent_id: str = "agent@default",
        max_parallel: int = 8,
        hmac_secret: bytes | None = None,
        core: Optional[NoorFastTimeCore] = None,
        async_mode: bool = False,
    ):
        env = os.getenv("NOOR_SHARED_HMAC", "")
        self.hmac_secret = hmac_secret or (env.encode() if env else None)
        self.agent_id = agent_id
        self.core = core
        self.watchers = watchers
        self._lamport = 0
        self._last_tick_hash: str = ""
        self._reward_ema = 1.0
        self._last_latency = 0.0
        self._silence_streak = 0
        # tunables
        self.min_interval = DEFAULT_TUNING["min_interval"]
        self.max_interval = DEFAULT_TUNING["max_interval"]
        self.entropy_boost_threshold = DEFAULT_TUNING["entropy_boost_threshold"]
        self.triad_bias_weight = DEFAULT_TUNING["triad_bias_weight"]
        self.reward_smoothing = DEFAULT_TUNING["reward_smoothing"]
        self.base_interval = (self.min_interval + self.max_interval) / 2
        # concurrency
        if async_mode:
            import anyio
            self._spawn_sem = anyio.CapacityLimiter(max_parallel)
        else:
            self._spawn_sem = asyncio.BoundedSemaphore(max_parallel)
        self._emission_task: Optional[asyncio.Task] = None
        # memory
        self.mem = get_global_memory_manager()
        # Archival hook (overrideable)
        self.on_archival = getattr(self, "on_archival", lambda bundle: None)
        # Track last interval and triadic hit
        self._last_interval = self.base_interval
        self._last_triad_hit = False

    # ──────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────
    def spawn(self, initial_motifs: Optional[List[str]] = None) -> None:
        """
        Starts autonomous emission loop. Seeds first emission if provided.
        """
        if initial_motifs:
            self._initial_motifs = initial_motifs.copy()
        self.start_pulse()

    def observe_feedback(self, tick_id: str, reward: float, annotations: Dict[str, Any]) -> None:
        """
        Entry for logic/core evaluators. Updates EMA, triad counter, silence streak.
        """
        # update EMA
        self._reward_ema = (
            (1 - self.reward_smoothing) * self._reward_ema
            + self.reward_smoothing * reward
        )
        self.REWARD_MEAN.labels(agent_id=self.agent_id).set(self._reward_ema)

        # triadic feedback
        triad_hit = bool(annotations.get("triad_complete"))
        if triad_hit:
            self.AGENT_TRIADS_COMPLETED.labels(agent_id=self.agent_id).inc()
            self._silence_streak = 0
        else:
            self._silence_streak += 1

        # record for interval tuning
        self._last_triad_hit = triad_hit

    def export_state(self) -> Dict[str, Any]:
        """
        Returns snapshot of cadence metrics, reward EMA, last tick hash.
        """
        return {
            "interval": self._last_interval,
            "reward_ema": self._reward_ema,
            "last_tick_hash": self._last_tick_hash,
        }

    def set_entropy_profile(self, profile: Dict[str, float]) -> None:
        """
        Hot-swap decay & boost tunables.
        """
        for k in ["entropy_boost_threshold", "triad_bias_weight", "reward_smoothing"]:
            if k in profile:
                setattr(self, k, profile[k])

    # ──────────────────────────────────────────────────────────
    # Internal Chooser
    # ──────────────────────────────────────────────────────────
    def _choose_motifs(self) -> List[str]:
        # start with last motifs
        motifs = getattr(self, '_last_motifs', []).copy()
        if motifs:
            extra = self.mem.retrieve(motifs[-1], top_k=2)
            motifs.extend(extra)
        # cap length
        cap = 3
        return motifs[-cap:]

    # ──────────────────────────────────────────────────────────
    # Emit single tick (+ validation)
    # ──────────────────────────────────────────────────────────
    def _emit_tick(self, motifs: List[str], stage: str = "E2b") -> QuantumTickV2:
        lam = self._lamport + 1
        self._lamport = lam
        coh = os.urandom(16).hex()
        # HMAC
        hmac_sig: Optional[str] = None
        if self.hmac_secret:
            import hashlib
            m = hashlib.sha256(self.hmac_secret)
            m.update(coh.encode())
            m.update(str(lam).encode())
            hmac_sig = m.hexdigest()

        ts_ms = int(time.time() * 1000)
        field_sig = self._resolve_field(motifs[-1] if motifs else "silence")
        tick_id = f"tick:{coh[:6]}"

        qt = QuantumTickV2(
            tick_id=tick_id,
            motif_id=motifs[-1] if motifs else "silence",
            coherence_hash=coh,
            lamport=lam,
            agent_id=self.agent_id,
            stage=stage,
            motifs=motifs,
            reward_ema=self._reward_ema,
            timestamp_ms=ts_ms,
            field_signature=field_sig,
            tick_hmac=hmac_sig,
        )

        # validate against RFC-0003 §3.3
        self.validate_tick(qt)

        self._last_tick_hash = coh
        return qt

    def validate_tick(self, tick: QuantumTickV2) -> None:
        """
        Ensure the tick meets RFC-0003 §3.3 requirements.
        Raises ValueError on any violation.
        """
        import re

        if not isinstance(tick.tick_id, str) or not re.match(r"^tick:[0-9a-f]{6}$", tick.tick_id):
            raise ValueError(f"Invalid tick_id: {tick.tick_id!r}")

        if not isinstance(tick.motifs, list) or not tick.motifs or not all(isinstance(m, str) for m in tick.motifs):
            raise ValueError(f"Invalid motifs list: {tick.motifs!r}")

        if not isinstance(tick.reward_ema, float) or not (0.0 <= tick.reward_ema <= 1.0):
            raise ValueError(f"Invalid reward_ema: {tick.reward_ema!r}")

        if not isinstance(tick.timestamp_ms, int) or tick.timestamp_ms < 0:
            raise ValueError(f"Invalid timestamp_ms: {tick.timestamp_ms!r}")

        if not isinstance(tick.field_signature, str) or not tick.field_signature:
            raise ValueError(f"Invalid field_signature: {tick.field_signature!r}")

        if not isinstance(tick.coherence_hash, str) or not tick.coherence_hash:
            raise ValueError("Missing coherence_hash")

        if not isinstance(tick.lamport, int) or tick.lamport < 0:
            raise ValueError(f"Invalid lamport: {tick.lamport!r}")

    # ──────────────────────────────────────────────────────────
    def _crystallize_tick(self, tick: QuantumTickV2) -> CrystallizedMotifBundle:
        # build entropy frame
        te = TickEntropy(
            decay_slope=self._last_latency,
            coherence=1.0,
            triad_complete=False,
            age=0.0,
        )
        return CrystallizedMotifBundle(
            motif_bundle=tick.motifs,
            field_signature=tick.field_signature,
            tick_entropy=te,
        )

    def _update_interval(self, entropy: float, triad_hit: bool = False) -> float:
        # blend reward and entropy
        adj = 1.0 - (self._reward_ema - 1.0)
        if entropy < self.entropy_boost_threshold:
            adj *= 0.5
        # apply triadic bias acceleration
        if triad_hit:
            adj *= (1.0 - self.triad_bias_weight)
        interval = self.base_interval * adj
        interval = max(self.min_interval, min(self.max_interval, interval))
        self._last_interval = interval
        self.AGENT_EMISSION_INTERVAL.labels(self.agent_id).set(interval)
        return interval

    def _inject_entropy_boost(self):
        if self._silence_streak >= 3:
            # revive pulse
            motif = "ψ-revive@Ξ"
            for w in self.watchers or []:
                if hasattr(w, 'register_tick'):
                    w.register_tick(motif, None)

    # ──────────────────────────────────────────────────────────
    # Autonomous emission loop
    # ──────────────────────────────────────────────────────────
    async def start_continuous_emission(self):
        """
        Loop: choose motifs, emit tick, optional archive, feedback, sleep.
        """
        try:
            while True:
                # seed or choose
                if hasattr(self, '_initial_motifs') and self._initial_motifs:
                    motifs = self._initial_motifs
                    del self._initial_motifs
                else:
                    motifs = self._choose_motifs() or ["silence"]
                # emit
                tick = self._emit_tick(motifs)
                self.TICKS_EMITTED.labels(stage=tick.stage, agent_id=self.agent_id).inc()
                # watchers
                for m in tick.motifs:
                    for w in self.watchers or []:
                        if hasattr(w, 'register_tick'):
                            w.register_tick(m, tick)
                # archive
                if ARCHIVE_MODE:
                    bundle = self._crystallize_tick(tick)
                    self.AGENT_ARCHIVAL_FRAMES.labels(agent_id=self.agent_id).inc()
                    self.on_archival(bundle)
                # core feedback
                start = time.perf_counter()
                entropy = np.random.rand()
                latency = time.perf_counter() - start
                self._last_latency = latency
                if self.core:
                    try:
                        self.core.receive_feedback(
                            ctx_ratio=1.0,
                            ghost_entropy=entropy,
                            harm_hits=0,
                            step_latency=latency,
                            latest_tick=tick,
                            parallel_running=0,
                        )
                    except Exception:
                        pass
                # interval
                interval = self._update_interval(entropy, self._last_triad_hit)
                self.AGENT_PULSE_TOTAL.labels(agent_id=self.agent_id).inc()
                # sleep
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("[%s] emission loop cancelled", self.agent_id)
        except Exception as exc:
            logger.warning("[%s] emission loop error: %s", self.agent_id, exc)

    def start_pulse(self) -> None:
        if not self._emission_task or self._emission_task.done():
            self._emission_task = asyncio.create_task(self.start_continuous_emission())

    def stop_pulse(self) -> None:
        if self._emission_task and not self._emission_task.done():
            self._emission_task.cancel()

    # ──────────────────────────────────────────────────────────
    # Field resolution fallback
    # ──────────────────────────────────────────────────────────
    def _resolve_field(self, motif: str) -> str:
        try:
            from symbolic_task_engine import SymbolicTaskEngine
            eng = SymbolicTaskEngine.INSTANCE
            if eng and hasattr(eng, 'resolve_presence_field'):
                return eng.resolve_presence_field([motif])
        except Exception:
            pass
        if motif in {"silence", "grief"}:
            return "ψ-bind@Ξ"
        return "ψ-resonance@Ξ"

# End of File
