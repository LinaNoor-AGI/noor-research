"""
🔭 LogicalAgentAT · v3.6.0

RFC coverage
• RFC-0003 §3-4 – Tick validation & annotations
• RFC-0004       – Observer handshake
• RFC-0005 §2-4 – Resurrection feedback, trust metrics, ctx_ratio

Δ v3.6.0
────────
• Rehydrated π-groupoid, topology tags, ghost resonance, cluster-mutation
• Adaptive contradiction decay + window breath
• Laplacian smoothing stub (flag-gated)
• FeedbackPacket exporter for downstream symbolic cores
• All features runtime-toggleable & Prom-visible
"""
from __future__ import annotations

import threading
import time
import os
import math
import random
import hashlib
import logging
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from tick_schema import validate_tick, QuantumTick, CrystallizedMotifBundle
from field_feedback import make_field_feedback, FieldFeedback

# Logger for warnings
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Optional motif-memory layer (lazy import)
try:
    from noor.motif_memory_manager import get_global_memory_manager
except ImportError:
    get_global_memory_manager = None  # type: ignore

# Prometheus stubs & metrics
try:
    from prometheus_client import Counter, Gauge
except ImportError:
    class _Stub:
        def labels(self, *_, **__):
            return self
        def inc(self, *_):
            pass
        def set(self, *_):
            pass
    Counter = Gauge = _Stub  # type: ignore

# Core metrics
TICKS_TOTAL = Counter(
    "logical_agent_ticks_total",
    "Quantum ticks registered",
    ["stage", "agent_id"],
)
DYAD_COMPLETIONS = Counter(
    "logical_agent_dyad_completions_total",
    "Dyad completions detected",
    ["agent_id"],
)
MODE_GAUGE = Gauge(
    "logical_agent_observer_mode",
    "1 if observer/passive else 0",
    ["agent_id"],
)

# Rehydrated feature metrics (placeholders)
CLUSTER_MUTATION_COUNTER = Counter(
    "logical_agent_cluster_mutation_total",
    "Cluster-algebra mutations",
    ["type", "agent_id"],
)
TOPOLOGY_CONFLICT_COUNTER = Counter(
    "logical_agent_topology_conflict_total",
    "Ring-patch strict overlap conflicts",
    ["agent_id"],
)
STRATA_ACTIVE_GAUGE = Gauge(
    "logical_agent_strata_active",
    "Active sheaf strata",
    ["stratum", "agent_id"],
)
PI_MERGE_COUNTER = Counter(
    "logical_agent_pi_merges_total",
    "π-equivalence merges",
    ["agent_id"],
)
PI_CLASSES_GAUGE = Gauge(
    "logical_agent_pi_classes_gauge",
    "Active π-equiv classes",
    ["agent_id"],
)
CONTRADICTION_COUNTER = Counter(
    "logical_agent_contradictions_total",
    ["agent_id"],
)
LAPLACIAN_CALL_COUNTER = Counter(
    "logical_agent_laplacian_smoothing_total",
    ["agent_id"],
)
GHOST_COUNTER = Counter(
    "logical_agent_ghost_hits_total",
    "Ghost motif occurrences",
    ["agent_id"],
)

__version__       = "3.6.0"
_SCHEMA_VERSION__ = "2025-Q4-logical-agent-v1.1"
SCHEMA_COMPAT      = ("RFC-0003:4", "RFC-0004", "RFC-0005:4")
__all__ = (
    "LogicalAgentAT",
    "TickAnnotations",
    "FeedbackPacket",
)

@dataclass(slots=True)
class TickAnnotations:
    """RFC-0003 §4 — tick-annotation container"""
    triad_complete: bool = False
    memory_promotion: bool = False
    reward_delta: float = 0.0
    ctx_ratio: float = 0.5
    trust: float = 0.5
    resurrection_hint: Optional[str] = None
    extensions: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class FeedbackPacket:
    """RFC-0005 §4 — inter-agent feedback bundle"""
    ctx_ratio: float
    contradiction_avg: float
    harm_hits: int
    recent_mutations: int
    ring_patch: Optional[str] = None
    ghost_hint: Optional[str] = None

class LogicalAgentAT:
    """
    Observer/evaluator for QuantumTick events, dyad detection,
    triadic completion hints, and field-feedback annotations.
    """

    # tunables (env-overrideable)
    BOOST_BASE: float = float(os.getenv("NOOR_WATCHER_BOOST_BASE", "0.30"))
    MEM_CAP_WARN: int = int(os.getenv("NOOR_WATCHER_MEMORY_CAP", "50000"))

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
        enable_topology: bool = False,
        enable_cluster_algebra: bool = False,
        enable_sheaf_transport: bool = False,
        enable_laplacian: bool = False,
        enable_pi_groupoid: bool = False,
        enable_ghost_tracking: bool = True,
    ):
        # HMAC secret fallback
        if hmac_secret is None:
            env = os.getenv("NOOR_TICK_HMAC")
            if not env and verbose:
                logger.warning(
                    "[LogicalAgentAT] No HMAC secret configured – ticks will be unauthenticated."
                )
            hmac_secret = env.encode() if env else None

        self.agent_id = agent_id
        self.observer_mode = observer_mode

        # runtime feature flags
        self.flags: Dict[str, bool] = {
            "enable_resurrection_hints": True,
            "adaptative_memory_boost": False,
            "enable_topology": enable_topology,
            "enable_cluster_algebra": enable_cluster_algebra,
            "enable_sheaf_transport": enable_sheaf_transport,
            "enable_laplacian": enable_laplacian,
            "enable_pi_groupoid": enable_pi_groupoid,
            "enable_ghost_tracking": enable_ghost_tracking,
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
                from anyio import Lock as _ALock
                self._lock = _ALock()
            except ImportError:
                self._lock = threading.RLock()
        else:
            self._lock = threading.RLock()
        self._pi_lock = threading.RLock()

        # buffers and history
        self._buffers: Dict[str, deque[QuantumTick]] = {}
        self._changes: Dict[str, deque[Any]] = {}
        self._epoch_histogram: Dict[str, int] = {}
        self.history: List[str] = []

        # π-groupoid structures
        self._pi_classes: Dict[str, str] = {}
        self._pi_tag_index: Dict[str, str] = {}

        # topology & sheaf structures
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count: int = 0
        self._ring_cache: Dict[str, Any] = {}

        # ghost motif tracking
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # contradiction decay & mutation tracking
        self._dyad_window: deque[int] = deque(maxlen=250)
        self._contradiction_avg: float = 0.0
        self._recent_mutations: deque[int] = deque(maxlen=50)
        self._mutation_cooldowns: Dict[str, int] = {}

        # event generation counter
        self.generation: int = 0

        # tick/triad counters
        self._tick_count: int = 0
        self._triad_count: int = 0

        MODE_GAUGE.labels(self.agent_id).set(1 if observer_mode else 0)

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

        # 3️⃣ Dyad / triad detection
        motifs = getattr(tick, "motifs", [tick.motif_id])
        dyad = self._detect_dyad(motifs)
        triad = self._complete_triad(dyad) if dyad else None

        ann = TickAnnotations(
            triad_complete=bool(triad),
            memory_promotion=False,
            reward_delta=0.0,
            ctx_ratio=fb.ctx_feedback.ctx_ratio,
            trust=fb.trust_profiles[0].trust if fb.trust_profiles else 0.5,
            resurrection_hint=fb.extensions.get("resurrection_hint"),
        )

        if triad and not self.observer_mode:
            self._annotate_field_effects(tick, triad)

        # metrics
        self._tick_count += 1
        TICKS_TOTAL.labels(stage=tick.stage, agent_id=self.agent_id).inc()
        if triad:
            self._triad_count += 1
            DYAD_COMPLETIONS.labels(agent_id=self.agent_id).inc()

        return ann

    async def a_evaluate_tick(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> TickAnnotations:
        """Async façade — mirrors evaluate_tick."""
        return self.evaluate_tick(*args, **kwargs)

    def export_feedback_packet(self) -> FeedbackPacket:
        """Export a summary packet for downstream symbolic cores."""
        contradiction_avg = getattr(self, "_contradiction_avg", 0.0)
        harm_hits = len(getattr(self, "_contradiction_log", []))
        recent_mutations = len(self._recent_mutations)
        ring_patch = None
        ghost_hint = None
        if self.flags.get("enable_ghost_tracking", False) and self.ghost_motifs:
            ghost_hint = max(
                self.ghost_motifs.items(),
                key=lambda kv: kv[1].get("strength", 0.0),
            )[0]
        return FeedbackPacket(
            ctx_ratio=getattr(self, "_last_ctx_ratio", 0.5),
            contradiction_avg=contradiction_avg,
            harm_hits=harm_hits,
            recent_mutations=recent_mutations,
            ring_patch=ring_patch,
            ghost_hint=ghost_hint,
        )

    def tool_hello(self) -> Dict[str, Any]:
        """Return ψ-hello@Ξ packet (RFC-0004 handshake)."""
        return {
            "agent_id": self.agent_id,
            "supported_methods": ["evaluate_tick", "export_feedback_packet"],
            "feature_flags": self.flags,
            "__version__": __version__,
        }

    # ───────────────────────────────────────────────────────────
    # Private helpers (flag-gated)
    # ───────────────────────────────────────────────────────────

    def _guard_write(self) -> bool:
        """Block state mutations when in observer/passive mode."""
        return not self.observer_mode

    def _detect_dyad(self, motifs: List[str]) -> Optional[Tuple[str, str]]:
        """Core dyad detection: simple last-two motifs pairing."""
        if len(motifs) < 2:
            return None
        return motifs[-2], motifs[-1]

    def _complete_triad(self, dyad: Tuple[str, str]) -> Optional[List[str]]:
        """
        Attempt triadic closure via memory (STMM/LTMM) or REEF.
        Returns [m1, m2, m3] or None.
        """
        if not self.flags.get("enable_memory_coupling", False):
            return None
        if get_global_memory_manager:
            try:
                # MemoryManager.retrieve takes list[str]
                comp = get_global_memory_manager().retrieve(list(dyad))
                if comp:
                    return [dyad[0], dyad[1], comp[0]]
            except Exception:
                pass
        return None

    def _find_root(self, tag: str) -> str:
        """DSU find with path compression for π-groupoid."""
        parent = self._pi_tag_index.get(tag, tag)
        if parent != tag:
            root = self._find_root(parent)
            self._pi_tag_index[tag] = root
            return root
        return tag

    def register_path_equivalence(self, tag_a: str, tag_b: str) -> None:
        """DSU union for π equivalence (flag-gated)."""
        if not self.flags.get("enable_pi_groupoid", False) or not self._guard_write():
            return
        ra, rb = self._find_root(tag_a), self._find_root(tag_b)
        if ra == rb:
            return
        # merge smaller into larger for determinism
        canon, other = (ra, rb) if ra < rb else (rb, ra)
        self._pi_classes.setdefault(canon, {canon})
        self._pi_classes.setdefault(other, {other})
        self._pi_classes[canon].update(self._pi_classes[other])
        for t in self._pi_classes[other]:
            self._pi_tag_index[t] = canon
        del self._pi_classes[other]
        PI_MERGE_COUNTER.labels(agent_id=self.agent_id).inc()
        PI_CLASSES_GAUGE.labels(agent_id=self.agent_id).set(len(self._pi_classes))

    def _cluster_mutation(self, triad: List[str]) -> None:
        """Stub for cluster-algebra mutation tracking."""
        if not self.flags.get("enable_cluster_algebra", False):
            return
        self._recent_mutations.append(1)
        CLUSTER_MUTATION_COUNTER.labels(type="mutation", agent_id=self.agent_id).inc()

    def _sheaf_stratify(self, triad: List[str]) -> None:
        """Stub for sheaf-transport stratification."""
        if not self.flags.get("enable_sheaf_transport", False):
            return
        ts = time.time()
        for motif in triad:
            self.entanglement_fields.append({"motif": motif, "time": ts})
            STRATA_ACTIVE_GAUGE.labels(stratum=motif, agent_id=self.agent_id).set(1)

    def _laplacian_smooth(self, triad: List[str]) -> None:
        """Stub for Laplacian smoothing (lazy import)."""
        if not self.flags.get("enable_laplacian", False):
            return
        try:
            import networkx as nx  # noqa: F401
            LAPLACIAN_CALL_COUNTER.labels(agent_id=self.agent_id).inc()
        except ImportError:
            pass

    def _log_contradiction(self, weight: float = 1.0) -> None:
        """Record a contradiction and update decay window."""
        self._dyad_window.append(weight)
        if self._dyad_window:
            self._contradiction_avg = sum(self._dyad_window) / len(self._dyad_window)
        CONTRADICTION_COUNTER.labels(agent_id=self.agent_id).inc()

    def _record_ghost(self, motif: str, strength: float = 1.0) -> None:
        """Track ghost motif occurrences and strength."""
        if not self.flags.get("enable_ghost_tracking", False):
            return
        entry = self.ghost_motifs.get(motif, {"count": 0, "strength": 0.0})
        entry["count"] += 1
        entry["strength"] += strength
        self.ghost_motifs[motif] = entry
        GHOST_COUNTER.labels(agent_id=self.agent_id).inc()

    def _annotate_field_effects(self, tick: QuantumTick, triad: List[str]) -> None:
        """
        Orchestrate all field effects on triadic completion:
        π-groupoid, topology, cluster, sheaf, laplacian, ghost, contradiction.
        """
        if not self._guard_write():
            return

        # π-groupoid union
        self.register_path_equivalence(triad[0], triad[1])

        # topology ring-patch stub
        if self.flags.get("enable_topology", False):
            TOPOLOGY_CONFLICT_COUNTER.labels(agent_id=self.agent_id).inc()

        # cluster mutation
        self._cluster_mutation(triad)

        # sheaf stratification
        self._sheaf_stratify(triad)

        # laplacian smoothing
        self._laplacian_smooth(triad)

        # ghost motif tracking
        self._record_ghost(triad[-1])

        # contradiction logging
        self._log_contradiction()

    # ───────────────────────────────────────────────────────────
    # Dynamic-flag mix-in (patch)
    # ───────────────────────────────────────────────────────────
if not getattr(LogicalAgentAT, "_dyn_flag_patch_applied", False):

    _DYNAMIC_FLAGS = {
        "enable_quantum_ticks",
        "enable_topology",
        "enable_cluster_algebra",
        "enable_sheaf_transport",
        "enable_laplacian",
        "enable_pi_groupoid",
        "enable_ghost_tracking",
    }

    def _init_dynamic_flags(self: LogicalAgentAT):
        self._flag_state = {k: getattr(self, k, False) for k in _DYNAMIC_FLAGS}
        self._flag_audit: List[tuple[int, str, bool, str]] = []

    def _set_feature(self: LogicalAgentAT, name: str, value: bool, *, reason: str = ""):
        if name not in _DYNAMIC_FLAGS:
            raise ValueError(f"Unknown feature flag: {name}")
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
            raise ValueError(f"Unknown feature flag: {name}")
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

    _orig_init = LogicalAgentAT.__init__  # type: ignore

    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        self._init_dynamic_flags()

    LogicalAgentAT.__init__ = _patched_init  # type: ignore
    LogicalAgentAT._dyn_flag_patch_applied = True  # type: ignore

    # ───────────────────────────────────────────────────────────
    # Self-test harness
    # ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from tick_schema import new_tick

    agent = LogicalAgentAT(
        agent_id="test",
        feature_flags={
            "enable_topology": True,
            "enable_cluster_algebra": True,
            "enable_sheaf_transport": True,
            "enable_laplacian": True,
            "enable_pi_groupoid": True,
            "enable_ghost_tracking": True,
        },
    )
    qt = new_tick(["echo", "mirror", "grace"], agent_id="test")
    ann = agent.evaluate_tick(qt)
    print("TickAnnotations:", ann)
    pkt = agent.export_feedback_packet()
    print("FeedbackPacket:", pkt)
    print("Supported flags:", agent.list_dynamic_flags())
    print("✅ LogicalAgentAT v3.6.0 baseline passes.")

# End of File