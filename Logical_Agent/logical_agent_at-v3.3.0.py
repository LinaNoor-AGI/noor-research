```python
"""
🔭 LogicalAgentAT · v3.3.0

Watcher with Quantum-Tick 2.0, dynamic feature flags, π-groupoid union-find,
**motif-change registry**, and now **adaptive motif-memory coupling**.

Δ v3.3.0
────────
• Light STMM boost on every tick (adaptive, inverse-salience + epoch-aware).  
• Optional “off” switch (`enable_memory_coupling=False`) in ctor.  
• Prometheus counter `logical_agent_memory_boosts_total`.  
• `export_memory_state(top_k, weight_cutoff)` for dashboards / API.  
• Import of motif memory layer is lazy-safe (watcher still runs if missing).
"""
from __future__ import annotations

__version__ = "3.3.0"
_SCHEMA_VERSION__ = "2025-Q3-motif-watch-memory"

import hashlib
import os
import random
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ─── Optional motif-memory layer (won’t hard-fail if absent) ────────────
try:
    from motif_memory_manager_v1.0.1 import get_global_memory_manager
except ImportError:  # pragma: no cover
    get_global_memory_manager = None  # type: ignore

try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    class _Stub:
        def labels(self, *_, **__):  # noqa: ANN001
            return self
        def inc(self, *_):           # noqa: D401
            pass
    Counter = _Stub  # type: ignore

from .quantum_ids import MotifChangeID, make_change_id

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
    Watcher that stores QuantumTicks per motif, tracks motif-level change
    events, exposes dynamic feature flags, maintains π-groupoid unions,
    and reinforces active motifs in short-term memory.
    """

    # ────────────────────────────────
    # Construction
    # ────────────────────────────────
    def __init__(
        self,
        *,
        agent_id: str = "watcher@default",
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
            hmac_secret = env.encode() if env else None

        self.agent_id = agent_id
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
            except ImportError:  # pragma: no cover
                self._lock = threading.RLock()
        else:
            self._lock = threading.RLock()
        self._pi_lock = threading.RLock()

        # buffers
        self._buffers: Dict[str, deque[QuantumTick]] = {}
        self._changes: Dict[str, deque[MotifChangeID]] = {}
        self._epoch_histogram: Dict[str, int] = {}
        self.history: List[str] = []

        # π-groupoid DSU
        self._pi_classes: Dict[str, str] = {}

        # dynamic flags will be injected later (mixin below)
        if not hasattr(self, "_init_dynamic_flags"):
            self._init_dynamic_flags = lambda: None  # type: ignore

    # ────────────────────────────────
    # Adaptive boost helper
    # ────────────────────────────────
    def _adaptive_boost(self, motif_id: str, *, hist_value: int) -> float:
        """
        Compute a dynamic boost (≈0.05 → 0.30) based on:
        • inverse salience (lighter motifs get stronger boost)
        • how many ticks we've already seen for this motif in the current epoch
        """
        if not get_global_memory_manager:
            return 0.1  # static fallback when memory layer absent
        memory = get_global_memory_manager()
        stmm, _ = memory.export_state()
        weight = stmm.get(motif_id, 0.0)
        epoch_penalty = 1.0 if hist_value < 5 else 0.7
        base = max(0.05, 0.30 * (1.0 - weight) * epoch_penalty)
        return round(base, 3)

    # ────────────────────────────────
    # Quantum-tick API
    # ────────────────────────────────
    def register_tick(self, motif_id: str, tick: QuantumTick) -> None:
        if not self.enable_quantum_ticks:
            return

        if self.hmac_shared_secret and not self.verify_hmac(tick):
            TICK_HMAC_FAILURES.labels(agent_id=self.agent_id).inc()
            return

        with self._lock:
            buf = self._buffers.setdefault(
                motif_id, deque(maxlen=self.tick_buffer_size)
            )
            # motif-change detection
            last_hash = buf[-1].coherence_hash if buf else None
            buf.append(tick)
            self._epoch_histogram[motif_id] = (
                self._epoch_histogram.get(motif_id, 0) + 1
            )

            if tick.coherence_hash != last_hash:
                change_ring = self._changes.setdefault(
                    motif_id, deque(maxlen=16)
                )
                change_ring.append(make_change_id(tick, motif_id))

            # ─── Motif-memory coupling ──────────────────────────────
            if (
                self.enable_memory_coupling
                and get_global_memory_manager
            ):
                boost = self._adaptive_boost(
                    motif_id,
                    hist_value=self._epoch_histogram.get(motif_id, 0),
                )
                memory = get_global_memory_manager()
                memory.access(motif_id, boost=boost)
                if getattr(memory, "_trace", None):
                    memory._log(
                        "watcher_memory_boost",
                        motif_id,
                        boost,
                        agent=self.agent_id,
                    )
                MEMORY_BOOSTS_TOTAL.labels(agent_id=self.agent_id).inc()

        TICKS_TOTAL.labels(stage=tick.stage, agent_id=self.agent_id).inc()

    def get_latest_tick(self, motif_id: str) -> Optional[QuantumTick]:
        buf = self._buffers.get(motif_id)
        return buf[-1] if buf else None

    def get_latest_change(self, motif_id: str) -> Optional[MotifChangeID]:
        ring = self._changes.get(motif_id)
        return ring[-1] if ring else None

    def export_tick_histogram(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._epoch_histogram)

    # ────────────────────────────────
    # Memory snapshot helper
    # ────────────────────────────────
    def export_memory_state(
        self,
        *,
        top_k: int | None = None,
        weight_cutoff: float = 0.0,
    ) -> Dict[str, Dict[str, float]]:
        """
        Return trimmed STMM/LTMM copies.
        • top_k – keep only the N heaviest motifs (None = no limit)
        • weight_cutoff – drop motifs below this weight
        """
        if not get_global_memory_manager:
            return {"stmm": {}, "ltmm": {}}
        stmm, ltmm = get_global_memory_manager().export_state()

        def _trim(store: Dict[str, float]) -> Dict[str, float]:
            items = [(k, v) for k, v in store.items() if v >= weight_cutoff]
            items.sort(key=lambda t: -t[1])
            return dict(items[:top_k]) if top_k else dict(items)

        return {"stmm": _trim(stmm), "ltmm": _trim(ltmm)}

    # ────────────────────────────────
    # HMAC helpers
    # ────────────────────────────────
    def verify_hmac(self, tick: QuantumTick) -> bool:
        if not tick.tick_hmac or not self.hmac_shared_secret:
            return False
        m = hashlib.sha256(self.hmac_shared_secret)
        m.update(tick.coherence_hash.encode())
        m.update(str(tick.lamport_clock).encode())
        return m.hexdigest() == tick.tick_hmac

    # ────────────────────────────────
    # π-Groupoid helpers (thread-safe)
    # ────────────────────────────────
    def register_path_equivalence(self, a: str, b: str) -> None:
        if len(self._pi_classes) >= self.pi_max_classes:
            return
        with self._pi_lock:
            ra, rb = self._find_root(a), self._find_root(b)
            if ra != rb:
                self._pi_classes[rb] = ra

    def are_paths_equivalent(self, a: str, b: str) -> bool:
        with self._pi_lock:
            return self._find_root(a) == self._find_root(b)

    def get_equivalence_class(self, x: str) -> str:
        with self._pi_lock:
            return self._find_root(x)

    def _find_root(self, x: str) -> str:
        path = []
        while x in self._pi_classes:
            path.append(x)
            x = self._pi_classes[x]
        for p in path:  # path compression
            self._pi_classes[p] = x
        return x

# ──────────────────────────────────────────────────────────────
# dynamic-flag mix-in (unchanged from v3.1.1 but patched once)
# ──────────────────────────────────────────────────────────────
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

    LogicalAgentAT.__init__ = _patched_init        # type: ignore[assignment]
    LogicalAgentAT._dyn_flag_patch_applied = True  # type: ignore[attr-defined]

# End of File
```
