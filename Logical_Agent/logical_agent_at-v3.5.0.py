"""
🔭 LogicalAgentAT · v3.5.0

RFC coverage  
• RFC-0003 §3-4  (tick validation & annotations)  
• RFC-0004       (tool / observer handshake)  
• RFC-0005 §2-4  (resurrection-feedback stubs)

Δ v3.5.0
────────
• TickAnnotations dataclass — all RFC fields present  
• Field-feedback ingestion via `field_feedback.make_field_feedback`  
• Observer-mode toggle + Prom MODE_GAUGE  
• Async façade `a_evaluate_tick`  
• π-groupoid & feature-flag scaffolds  
• `tool_hello()` for ψ-hello@Ξ handshake (RFC-0004)
"""
from __future__ import annotations

import hashlib
import logging
import os
import random
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from tick_schema import (
    validate_tick,
    QuantumTick,
    CrystallizedMotifBundle,
)
from field_feedback import make_field_feedback, FieldFeedback

# ─── Logger ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ─── Optional motif-memory layer (lazy import) ──────────────────────────
try:
    from noor.motif_memory_manager import get_global_memory_manager
except ImportError:  # pragma: no cover
    get_global_memory_manager = None  # type: ignore

try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    class _Stub:                       # noqa: D401
        def labels(self, *_, **__):     # noqa: ANN001
            return self
        def inc(self, *_):              # noqa: D401
            pass
    Counter = Gauge = _Stub            # type: ignore

from .quantum_ids import MotifChangeID, make_change_id

__version__      = "3.5.0"
_SCHEMA_VERSION__ = "2025-Q4-logical-agent-v1.0"
SCHEMA_COMPAT     = ("RFC-0003:4", "RFC-0004", "RFC-0005:4")
__all__ = (
    "LogicalAgentAT",
    "TickAnnotations",
    "FieldFeedback",
)

# ──────────────────────────────────────────────────────────────
# Triad-related tunables
# ──────────────────────────────────────────────────────────────
TRIAD_STABLE_THRESH = float(os.getenv("NOOR_TRIAD_STABLE_THRESH", "0.70"))
DYAD_JOURNAL_LEN    = int(os.getenv("NOOR_DYAD_JOURNAL_LEN",  "64"))
ANNOTS_CAP          = int(os.getenv("NOOR_ANNOTATION_CAP",    "256"))

# ──────────────────────────────────────────────────────────────
# Prometheus metrics
# ──────────────────────────────────────────────────────────────
TICKS_TOTAL = Counter(
    "logical_agent_ticks_total",
    "Quantum ticks registered",
    ["stage", "agent_id"],
)
TICK_HMAC_FAILURES = Counter(
    "logical_agent_tick_hmac_failures_total",
    "Tick HMAC verification failures",
    ["agent_id"],
)
FEATURE_TOGGLE_COUNTER = Counter(
    "logical_agent_feature_toggles_total",
    "Dynamic feature-flag toggles",
    ["flag", "agent_id"],
)
MEMORY_BOOSTS_TOTAL = Counter(
    "logical_agent_memory_boosts_total",
    "STMM boosts applied by LogicalAgentAT",
    ["agent_id"],
)
# Dyad → triad completions
DYAD_COMPLETIONS = Counter(
    "logical_agent_dyad_completions_total",
    "Dyad completions detected",
    ["agent_id"],
)

# New observer-mode gauge
MODE_GAUGE = Gauge(
    "logical_agent_observer_mode",
    "1 if observer/passive else 0",
    ["agent_id"],
)

# ──────────────────────────────────────────────────────────────
# RFC-0003 §4 — tick-annotation container
# ──────────────────────────────────────────────────────────────
@dataclass(slots=True)
class TickAnnotations:
    triad_complete: bool = False
    memory_promotion: bool = False
    reward_delta: float = 0.0
    ctx_ratio: float = 0.5
    trust: float = 0.5
    resurrection_hint: Optional[str] = None
    extensions: Dict[str, Any] = field(default_factory=dict)

# ──────────────────────────────────────────────────────────────
# Quantum-Tick 2.0 dataclass
# ──────────────────────────────────────────────────────────────
@dataclass
class QuantumTick:
    motif_id: str
    lamport_clock: int
    hlc_ts: str            # ISO-8601 + logical
    coherence_hash: str    # 12-hex
    agent_id: str
    stage: str
    tick_hmac: Optional[str] = None

    @classmethod
    def now(
        cls,
        motif_id: str,
        agent_id: str,
        *,
        secret: bytes | None = None,
        lamport_clock: int = 0,
        stage: str = "E2b",
    ) -> "QuantumTick":
        coherence_hash = f"{random.getrandbits(48):012x}"
        hlc_ts = f"{time.strftime('%Y-%m-%dT%H:%M:%S')}.{lamport_clock:04d}Z"
        tick_hmac = None
        if secret:
            m = hashlib.sha256(secret)
            m.update(coherence_hash.encode())
            m.update(str(lamport_clock).encode())
            tick_hmac = m.hexdigest()
        return cls(
            motif_id,
            lamport_clock,
            hlc_ts,
            coherence_hash,
            agent_id,
            stage,
            tick_hmac,
        )

# ──────────────────────────────────────────────────────────────
# LogicalAgentAT core
# ──────────────────────────────────────────────────────────────
class LogicalAgentAT:
    """
    Observer/evaluator for QuantumTick events, dyad detection,
    triadic completion hints, and field-feedback annotations.
    """

    # tunables (env-overrideable)
    BOOST_BASE: float = float(os.getenv("NOOR_WATCHER_BOOST_BASE", "0.30"))
    MEM_CAP_WARN: int = int(os.getenv("NOOR_WATCHER_MEMORY_CAP", "50000"))

    # ────────────────────────────────
    # Construction
    # ────────────────────────────────
    def __init__(
        self,
        *,
        agent_id: str = "logical@default",
        observer_mode: bool = False,
        feature_flags: Optional[Dict[str, bool]] = None,
        enable_quantum_ticks: bool = True,
        enable_memory_coupling: bool = True,
        tick_buffer_size: int = 128,
        pi_max_classes: int = 20_000,
        hmac_secret: Optional[bytes] = None,
        async_mode: bool = False,
        verbose: bool = False,
    ):
        if hmac_secret is None:
            env = os.getenv("NOOR_TICK_HMAC")
            if not env and verbose:
                logger.warning(
                    "[LogicalAgentAT] No HMAC secret configured – "
                    "ticks will be accepted unauthenticated."
                )
            hmac_secret = env.encode() if env else None

        self.agent_id = agent_id
        self.observer_mode = observer_mode
        self.flags: Dict[str, bool] = {
            "enable_resurrection_hints": True,
            "adaptative_memory_boost": False,
            **(feature_flags or {}),
        }
        self.enable_quantum_ticks = enable_quantum_ticks
        self.enable_memory_coupling = enable_memory_coupling
        self.tick_buffer_size = tick_buffer_size
        self.pi_max_classes = pi_max_classes
        self.hmac_shared_secret = hmac_secret
        self.verbose = verbose

        # locks
        if async_mode:
            try:
                from anyio import Lock as _ALock  # type: ignore
                self._lock = _ALock()
            except ImportError:
                self._lock = threading.RLock()
        else:
            self._lock = threading.RLock()
        self._pi_lock = threading.RLock()

        # buffers
        self._buffers: Dict[str, deque[QuantumTick]] = {}
        self._changes: Dict[str, deque[MotifChangeID]] = {}
        self._epoch_histogram: Dict[str, int] = {}
        self.history: List[str] = []

        # π-groupoid placeholder
        self._pi_classes: Dict[str, str] = {}

        # dyad / triad extras
        self._dyad_journal: deque[tuple[str, str, Optional[str]]] = deque(
            maxlen=DYAD_JOURNAL_LEN
        )
        self._tick_annotations: Dict[str, Dict[str, Any]] = {}
        self._last_motif: Optional[str] = None

        # counters
        self._tick_count = 0
        self._triad_count = 0

        MODE_GAUGE.labels(self.agent_id).set(1 if observer_mode else 0)

    # ────────────────────────────────
    # Public evaluator (RFC compliant)
    # ────────────────────────────────
    def evaluate_tick(
        self,
        tick: QuantumTick,
        *,
        raw_feedback: Optional[Dict[str, Any]] = None,
        archival_bundle: Optional[CrystallizedMotifBundle] = None,
    ) -> TickAnnotations:
        """Validate + annotate a QuantumTick, returning TickAnnotations."""
        # 1️⃣ RFC schema guard
        validate_tick(tick)

        # 2️⃣ Field-feedback (ctx_ratio, trust, entropy…)
        fb: FieldFeedback = make_field_feedback(
            tick, raw_feedback, archival_bundle
        )

        # 3️⃣ Dyad / triad detection (stub)
        dyad = self._detect_dyad(tick.motifs)
        triad = self._complete_triad(dyad) if dyad else None

        ann = TickAnnotations(
            triad_complete=bool(triad),
            ctx_ratio=fb.ctx_feedback.ctx_ratio,
            trust=fb.trust_profiles[0].trust if fb.trust_profiles else 0.5,
            resurrection_hint=fb.extensions.get("resurrection_hint"),
        )

        if triad and self._guard_write():
            self._annotate_field_effects(tick, triad)

        # metrics
        self._tick_count += 1
        TICKS_TOTAL.labels(stage=tick.stage, agent_id=self.agent_id).inc()
        if triad:
            self._triad_count += 1
            DYAD_COMPLETIONS.labels(agent_id=self.agent_id).inc()

        return ann

    async def a_evaluate_tick(self, *a, **kw) -> TickAnnotations:  # noqa: D401
        """Async façade — mirrors evaluate_tick."""
        return self.evaluate_tick(*a, **kw)

    # ────────────────────────────────
    # Observer / tool handshake
    # ────────────────────────────────
    def tool_hello(self) -> Dict[str, Any]:
        """Return ψ-hello@Ξ packet (RFC-0004)."""
        return {
            "motif": "ψ-hello@Ξ",
            "module_id": f"logical_agent/{self.agent_id}",
            "declares": ["tick_evaluation"],
            "intent": (
                "field_observer" if self.observer_mode
                else "reasoning_evaluator"
            ),
        }

    # ────────────────────────────────
    # Internal helpers (stubs now)
    # ────────────────────────────────
    def _detect_dyad(self, motifs: List[str]) -> Optional[Tuple[str, str]]:
        return None  # TODO: o3 pattern matcher

    def _complete_triad(self, dyad: Tuple[str, str]) -> Optional[str]:
        return None  # TODO: consult memory / REEF

    def _annotate_field_effects(
        self, tick: QuantumTick, triad: Optional[str]
    ) -> None:
        """Placeholder for memory boost / π-union tagging."""
        return

    def _guard_write(self) -> bool:
        """Block state-mutations when in observer/passive mode."""
        return not self.observer_mode

    # ────────────────────────────────
    # Snapshot helpers
    # ────────────────────────────────
    def export_metrics(self) -> Dict[str, Any]:
        return {
            "ticks": self._tick_count,
            "triads": self._triad_count,
            "observer": self.observer_mode,
            "flags": self.flags.copy(),
        }

    def set_mode(self, observer: bool = True) -> None:
        self.observer_mode = observer
        MODE_GAUGE.labels(self.agent_id).set(1 if observer else 0)

# ────────────────────────────────
# dynamic-flag mix-in (unchanged from v3.1.1 but patched once)
# ────────────────────────────────
if not getattr(LogicalAgentAT, "_dyn_flag_patch_applied", False):

    _DYNAMIC_FLAGS = {
        "enable_quantum_ticks",
        "enable_topology",
        "enable_cluster_algebra",
        "enable_sheaf_transport",
        "enable_laplacian",
        "enable_pi_groupoid",
    }

    def _init_dynamic_flags(self: LogicalAgentAT):
        self._flag_state: Dict[str, bool] = {
            k: getattr(self, k, False) for k in _DYNAMIC_FLAGS
        }
        self._flag_audit: List[tuple[int, str, bool, str]] = []

    def _set_feature(self: LogicalAgentAT, name: str, value: bool, *, reason: str = ""):
        if name not in _DYNAMIC_FLAGS:
            raise ValueError(name)
        with self._lock:
            old = getattr(self, name, False)
            if old == value:
                return
            setattr(self, name, value)
            self._flag_state[name] = value
            ts = int(time.time_ns())
            self._flag_audit.append((ts, name, value, reason))
            FEATURE_TOGGLE_COUNTER.labels(flag=name, agent_id=self.agent_id).inc()

    def _get_feature(self: LogicalAgentAT, name: str) -> bool:
        if name not in _DYNAMIC_FLAGS:
            raise ValueError(name)
        return getattr(self, name, False)

    def _list_dynamic_flags(self: LogicalAgentAT) -> Dict[str, bool]:
        return {k: getattr(self, k, False) for k in _DYNAMIC_FLAGS}

    for _n, _f in {
        "_init_dynamic_flags": _init_dynamic_flags,
        "set_feature":        _set_feature,
        "get_feature":        _get_feature,
        "list_dynamic_flags": _list_dynamic_flags,
    }.items():
        if not hasattr(LogicalAgentAT, _n):
            setattr(LogicalAgentAT, _n, _f)

    _orig_init = LogicalAgentAT.__init__  # type: ignore[attr-defined]

    def _patched_init(self, *a, **kw):  # noqa: D401
        _orig_init(self, *a, **kw)      # type: ignore[arg-type]
        self._init_dynamic_flags()

    LogicalAgentAT.__init__ = _patched_init
    LogicalAgentAT._dyn_flag_patch_applied = True

# ────────────────────────────────
# Self-test harness
# ────────────────────────────────

if __name__ == "__main__":
    from tick_schema import new_tick

    qt  = new_tick(["mirror", "grace"], agent_id="demo")
    ag  = LogicalAgentAT()
    ann = ag.evaluate_tick(qt)
    print(ann)
    print("✅ LogicalAgentAT v3.5.0 baseline passes.")

# End of File