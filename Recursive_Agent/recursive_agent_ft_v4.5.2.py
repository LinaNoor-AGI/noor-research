"""
🌀 RecursiveAgentFT · v4.5.2 — Cadence of Memory

RFC Coverage
• RFC‑0003 §3.3 — QuantumTick validation
• RFC‑0005 §2‑4  — Tick echoes, ghost traces, resurrection envelopes, feedback export

Δ v4.5.2 (from v4.5.1)
──────────────────────
• Added in‑memory echo buffer (tick replay) and ghost‑trace registry
• Introduced resurrection helpers (`build_resurrection_payload`, `try_ghost_resurrection`)
• New public `export_feedback_packet` for RFC‑0005 field feedback
• Added decay + replay utilities (`ghost_decay`, `replay_if_field_matches`)
• Motif lineage tracker for provenance mapping
• Updated version metadata + imports

NOTE: All existing behaviour is preserved; additions are backward‑compatible.
"""
from __future__ import annotations

__version__ = "4.5.2"
_SCHEMA_VERSION__ = "2025-Q4-recursive-agent-v4.5"
SCHEMA_COMPAT = ("RFC-0003:3", "RFC-0005:4")

import asyncio
import logging
import os
import threading
import time
from collections import OrderedDict, deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional

import numpy as np
from noor.motif_memory_manager import get_global_memory_manager

try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    class _Stub:  # type: ignore
        def labels(self, *_, **__):
            return self

        def inc(self, *_):
            pass

        def set(self, *_):
            pass

    Counter = Gauge = _Stub  # type: ignore

try:
    from noor_fasttime_core import NoorFastTimeCore  # type: ignore
except ImportError:  # pragma: no cover
    NoorFastTimeCore = object  # type: ignore

from .quantum_ids import make_change_id, MotifChangeID  # noqa: F401 – runtime hook

# ──────────────────────────────────────────────────────────────
# Schema dataclasses (unchanged from v4.5.1)
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

DEFAULT_TUNING: Dict[str, float] = {
    "min_interval": 0.25,
    "max_interval": 10.0,
    "entropy_boost_threshold": 0.35,
    "triad_bias_weight": 0.15,
    "reward_smoothing": 0.2,
}
ARCHIVE_MODE: bool = bool(int(os.getenv("NOOR_ARCHIVE_TICKS", "0")))

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# ──────────────────────────────────────────────────────────────
# Helper LRU cache
# ──────────────────────────────────────────────────────────────

class LRUCache(OrderedDict):
    """Simple thread‑safe LRU cache (unused for now – legacy)."""

    def __init__(self, cap: int = 50_000):
        super().__init__()
        self.cap = cap
        self._lock = threading.Lock()

    def __setitem__(self, key, value):  # type: ignore[override]
        with self._lock:
            if key in self:
                del self[key]
            super().__setitem__(key, value)
            if len(self) > self.cap:
                self.popitem(last=False)


# ──────────────────────────────────────────────────────────────
# RecursiveAgentFT
# ──────────────────────────────────────────────────────────────

class RecursiveAgentFT:
    """Autonomous motif emitter (RFC‑0003) with extended echo/ghost support."""

    # Prometheus metrics (as v4.5.1)
    TICKS_EMITTED = Counter(
        "agent_ticks_emitted_total", "Ticks emitted", ["agent_id", "stage"]
    )
    DUP_TICK = Counter(
        "agent_tick_duplicate_total", "Duplicate ticks", ["agent_id"]
    )
    REWARD_MEAN = Gauge("agent_reward_mean", "EMA of reward", ["agent_id"])
    AGENT_EMISSION_INTERVAL = Gauge(
        "agent_emission_interval_seconds",
        "Current autonomous emission interval",
        ["agent_id"],
    )
    AGENT_PULSE_TOTAL = Counter(
        "agent_autonomous_loops_total", "Autonomous emission loops executed", ["agent_id"]
    )
    PULSE_BACKOFF_TOTAL = Counter(
        "agent_pulse_backoff_total", "Times emission loop back‑off applied", ["agent_id"]
    )
    AGENT_ARCHIVAL_FRAMES = Counter(
        "agent_archival_frames_total", "Crystallization events emitted", ["agent_id"]
    )
    AGENT_TRIADS_COMPLETED = Counter(
        "agent_triads_completed_total", "Triads completed via feedback", ["agent_id"]
    )

    # New metrics for v4.5.2
    FEEDBACK_EXPORT = Counter(
        "agent_feedback_export_total", "Feedback packets exported", ["agent_id"]
    )

    # ──────────────────────────────────────────────────────────
    # Init
    # ──────────────────────────────────────────────────────────

    def __init__(
        self,
        initial_state: Any,
        watchers: List[Any],
        *,
        agent_id: str = "agent@default",
        max_parallel: int = 8,
        hmac_secret: bytes | None = None,
        core: Optional[NoorFastTimeCore] = None,
        async_mode: bool = False,
    ) -> None:
        env_secret = os.getenv("NOOR_SHARED_HMAC", "")
        self.hmac_secret = hmac_secret or (env_secret.encode() if env_secret else None)

        self.agent_id = agent_id
        self.core: Optional[NoorFastTimeCore] = core
        self.watchers = watchers

        # RFC‑0003 state
        self._lamport: int = 0
        self._last_tick_hash: str = ""
        self._reward_ema: float = 1.0
        self._last_latency: float = 0.0
        self._silence_streak: int = 0
        self._last_triad_hit: bool = False

        # Tunables
        self.min_interval = DEFAULT_TUNING["min_interval"]
        self.max_interval = DEFAULT_TUNING["max_interval"]
        self.entropy_boost_threshold = DEFAULT_TUNING["entropy_boost_threshold"]
        self.triad_bias_weight = DEFAULT_TUNING["triad_bias_weight"]
        self.reward_smoothing = DEFAULT_TUNING["reward_smoothing"]
        self.base_interval = (self.min_interval + self.max_interval) / 2
        self._last_interval = self.base_interval

        # Concurrency
        if async_mode:
            import anyio  # type: ignore

            self._spawn_sem = anyio.CapacityLimiter(max_parallel)
        else:
            self._spawn_sem = asyncio.BoundedSemaphore(max_parallel)
        self._emission_task: Optional[asyncio.Task] = None

        # Memory interface
        self.mem = get_global_memory_manager()

        # Archival hook (no‑op by default)
        self.on_archival = getattr(self, "on_archival", lambda bundle: None)

        # 🧠 RFC‑0005 additions
        self._tick_echoes: Deque[QuantumTickV2] = deque(maxlen=256)
        self._ghost_traces: Dict[str, Dict[str, Any]] = {}
        self._motif_lineage: Dict[str, str] = {}

    # ──────────────────────────────────────────────────────────
    # Public helpers (RFC‑0003 base)
    # ──────────────────────────────────────────────────────────

    def spawn(self, initial_motifs: Optional[List[str]] | None = None) -> None:
        """Start autonomous emission loop."""
        if initial_motifs:
            self._initial_motifs = initial_motifs.copy()
        self.start_pulse()

    def observe_feedback(self, tick_id: str, reward: float, annotations: Dict[str, Any]) -> None:
        """Ingest feedback from observers / logic agents."""
        # EMA update
        self._reward_ema = (1 - self.reward_smoothing) * self._reward_ema + self.reward_smoothing * reward
        self.REWARD_MEAN.labels(agent_id=self.agent_id).set(self._reward_ema)

        # Triad handling
        triad_hit = bool(annotations.get("triad_complete"))
        if triad_hit:
            self.AGENT_TRIADS_COMPLETED.labels(agent_id=self.agent_id).inc()
            self._silence_streak = 0
        else:
            self._silence_streak += 1
        self._last_triad_hit = triad_hit

    def export_state(self) -> Dict[str, Any]:
        return {
            "interval": self._last_interval,
            "reward_ema": self._reward_ema,
            "last_tick_hash": self._last_tick_hash,
        }

    # New RFC‑0005 feedback export
    def export_feedback_packet(self) -> Dict[str, Any]:
        """Lightweight runtime stats for field observers (RFC‑0005 §4)."""
        self.FEEDBACK_EXPORT.labels(agent_id=self.agent_id).inc()
        return {
            "tick_buffer_size": len(self._tick_echoes),
            "ghost_trace_count": len(self._ghost_traces),
            "recent_reward_ema": round(self._reward_ema, 4),
            "cadence_interval": round(self._last_interval, 3),
            "silence_streak": self._silence_streak,
        }

    # ──────────────────────────────────────────────────────────
    # Internal motif selection helpers
    # ──────────────────────────────────────────────────────────

    def _choose_motifs(self) -> List[str]:
        motifs: List[str] = getattr(self, "_last_motifs", []).copy()
        if motifs:
            motifs.extend(self.mem.retrieve(motifs[-1], top_k=2))  # may be []
        return (motifs or ["silence"])[-3:]

    # ──────────────────────────────────────────────────────────
    # Tick emission (core)
    # ──────────────────────────────────────────────────────────

    def _emit_tick(self, motifs: List[str], *, stage: str = "E2b") -> QuantumTickV2:
        # Lamport & hashes
        self._lamport += 1
        coherence_hash = os.urandom(16).hex()
        tick_id = f"tick:{coherence_hash[:6]}"

        # HMAC
        hmac_sig: Optional[str] = None
        if self.hmac_secret:
            import hashlib

            h = hashlib.sha256(self.hmac_secret)
            h.update(coherence_hash.encode())
            h.update(str(self._lamport).encode())
            hmac_sig = h.hexdigest()

        ts_ms = int(time.time() * 1000)
        field_sig = self._resolve_field(motifs[-1] if motifs else "silence")

        tick = QuantumTickV2(
            tick_id=tick_id,
            motif_id=motifs[-1] if motifs else "silence",
            coherence_hash=coherence_hash,
            lamport=self._lamport,
            agent_id=self.agent_id,
            stage=stage,
            motifs=motifs,
            reward_ema=self._reward_ema,
            timestamp_ms=ts_ms,
            field_signature=field_sig,
            tick_hmac=hmac_sig,
        )

        self.validate_tick(tick)
        self._last_tick_hash = coherence_hash

        # 🆕 store echo
        self._tick_echoes.append(tick)
        return tick

    # Validation (unchanged)
    def validate_tick(self, tick: QuantumTickV2) -> None:
        import re

        if not re.match(r"^tick:[0-9a-f]{6}$", tick.tick_id):
            raise ValueError("Invalid tick_id")
        if not tick.motifs or not all(isinstance(m, str) for m in tick.motifs):
            raise ValueError("Motifs must be non‑empty list[str]")
        if not (0.0 <= tick.reward_ema <= 1.0):
            raise ValueError("Invalid reward_ema")
        if tick.timestamp_ms < 0:
            raise ValueError("Negative timestamp")
        if not tick.field_signature:
            raise ValueError("field_signature required")
        if tick.lamport < 0:
            raise ValueError("lamport must be ≥ 0")

    # ──────────────────────────────────────────────────────────
    # Ghost / replay helpers (RFC‑0005)
    # ──────────────────────────────────────────────────────────

    def recall_tick(self, tick_id: str) -> Optional[QuantumTickV2]:
        """Return a prior tick from echo buffer, if present."""
        for t in self._tick_echoes:
            if t.tick_id == tick_id:
                return t
        return None

    def try_ghost_resurrection(self, ghost_motif: str, context_field: str) -> Optional[QuantumTickV2]:
        ghost = self._ghost_traces.get(ghost_motif)
        if ghost and ghost.get("context_field") == context_field:
            return self.recall_tick(ghost["tick_id"])
        return None

    def build_resurrection_payload(self, tick: QuantumTickV2) -> Dict[str, Any]:
        return {
            "envelope": "ψ-teleport@Ξ",
            "tick_id": tick.tick_id,
            "anchor": tick.field_signature,
            "decay_bias": tick.reward_ema,
            "motif_bundle": tick.motifs,
            "resurrection_hint": "requested",
        }

    def ghost_decay(self, *, age_limit: float = 300.0) -> None:
        now = time.time()
        expired = [k for k, v in self._ghost_traces.items() if now - v.get("ts", now) > age_limit]
        for k in expired:
            del self._ghost_traces[k]

    def replay_if_field_matches(self, current_field: str) -> Optional[QuantumTickV2]:
        for g in self._ghost_traces.values():
            if g.get("context_field") == current_field:
                return self.recall_tick(g["tick_id"])
        return None

    def track_lineage(self, new_motif: str, source_motif: str) -> None:
        self._motif_lineage[new_motif] = source_motif

    # ──────────────────────────────────────────────────────────
    # Cadence helpers (unchanged logic but refactored)
    # ──────────────────────────────────────────────────────────

    def _crystallize_tick(self, tick: QuantumTickV2) -> CrystallizedMotifBundle:
        te = TickEntropy(
            decay_slope=self._last_latency,
            coherence=1.0,
            triad_complete=False,
            age=0.0,
        )
        return CrystallizedMotifBundle(tick.motifs, tick.field_signature, te)

    def _update_interval(self, entropy: float) -> float:
        adj = 1.0 - (self._reward_ema - 1.0)
        if entropy < self.entropy_boost_threshold:
            adj *= 0.5
        if self._last_triad_hit:
            adj *= 1.0 - self.triad_bias_weight
        interval = max(self.min_interval, min(self.max_interval, self.base_interval * adj))
        self._last_interval = interval
        self.AGENT_EMISSION_INTERVAL.labels(self.agent_id).set(interval)
        return interval

    # ──────────────────────────────────────────────────────────
    # Autonomous loop (minor refactor for clarity)
    # ──────────────────────────────────────────────────────────

    async def start_continuous_emission(self) -> None:  # noqa: C901 — complex but stable
        try:
            while True:
                # Select motifs
                motifs = getattr(self, "_initial_motifs", None) or self._choose_motifs()
                if hasattr(self, "_initial_motifs"):
                    del self._initial_motifs

                # Emit tick
                tick = self._emit_tick(motifs)
                self.TICKS_EMITTED.labels(stage=tick.stage, agent_id=self.agent_id).inc()

                # Notify watchers
                for motif in tick.motifs:
                    for w in self.watchers or []:
                        if hasattr(w, "register_tick"):
                            w.register_tick(motif, tick)

                # Optional archival
                if ARCHIVE_MODE:
                    self.on_archival(self._crystallize_tick(tick))
                    self.AGENT_ARCHIVAL_FRAMES.labels(agent_id=self.agent_id).inc()

                # Core feedback
                entropy_sample = float(np.random.rand())
                self._last_latency = 0.0  # stub latency
                if self.core:
                    try:
                        self.core.receive_feedback(
                            ctx_ratio=1.0,
                            ghost_entropy=entropy_sample,
                            harm_hits=0,
                            step_latency=self._last_latency,
                            latest_tick=tick,
                            parallel_running=0,
                        )
                    except Exception:  # pragma: no cover
                        pass

                # Interval & sleep
                sleep_for = self._update_interval(entropy_sample)
                self.AGENT_PULSE_TOTAL.labels(agent_id=self.agent_id).inc()
                await asyncio.sleep(sleep_for)
        except asyncio.CancelledError:
            logger.info("[%s] emission loop cancelled", self.agent_id)
        except Exception as exc:  # pragma: no cover
            logger.warning("[%s] emission loop error: %s", self.agent_id, exc)

    # Public pulse controls
    def start_pulse(self) -> None:
        if not self._emission_task or self._emission_task.done():
            self._emission_task = asyncio.create_task(self.start_continuous_emission())

    def stop_pulse(self) -> None:
        if self._emission_task and not self._emission_task.done():
            self._emission_task.cancel()

    # ──────────────────────────────────────────────────────────
    # Fallback field resolver (unchanged)
    # ──────────────────────────────────────────────────────────

    def _resolve_field(self, motif: str) -> str:
        try:
            from symbolic_task_engine import SymbolicTaskEngine  # type: ignore

            eng = SymbolicTaskEngine.INSTANCE  # noqa: E305
            if eng and hasattr(eng, "resolve_presence_field"):
                return eng.resolve_presence_field([motif])
        except Exception:  # pragma: no cover
            pass
        return "ψ-bind@Ξ" if motif in {"silence", "grief"} else "ψ-resonance@Ξ"


# End of File — recursive_agent_ft.py v4.5.2