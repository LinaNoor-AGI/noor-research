"""
🔭 LogicalAgentAT · v3.2.0

Watcher with Quantum‑Tick 2.0, dynamic feature flags, π‑groupoid union‑find
and **motif‑change registry** (new).

Δ v3.2.0
────────
• Motif‑change ring (16 entries) per motif using MotifChangeID from quantum_ids.py
• `register_tick()` now generates change‑ID when the incoming tick differs
  from the last stored in that motif’s buffer.
• New helper `get_latest_change(motif_id)` returns the most recent change‑ID.
• ctor accepts explicit `hmac_secret=None` and `async_mode=False`; env‑var
  fallback only when arg is None.
• Prometheus stubs, dynamic‑flag mix‑in, and π‑groupoid from v3.1.1 retained.
"""
from __future__ import annotations

__version__ = "3.2.0"
_SCHEMA_VERSION__ = "2025-Q2-quantum-tick"

import hashlib
import os
import random
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from time import perf_counter

try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    class _Stub:                           # noqa: D401
        def labels(self, *_, **__):        # noqa: ANN001
            return self
        def inc(self, *_):                 # noqa: D401
            pass
    Counter = _Stub                        # type: ignore

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
    "Dynamic feature‑flag toggles",
    ["flag", "agent_id"],
)

# ──────────────────────────────────────────────────────────────
# Quantum‑Tick 2.0 dataclass
# ──────────────────────────────────────────────────────────────
@dataclass
class QuantumTick:
    motif_id: str
    lamport_clock: int
    hlc_ts: str            # ISO‑8601 + logical
    coherence_hash: str    # 12‑hex
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
    Watcher that stores QuantumTicks per motif, tracks motif‑level change
    events, exposes dynamic feature flags, and maintains π‑groupoid unions.
    """

    def __init__(
        self,
        *,
        agent_id: str = "watcher@default",
        enable_quantum_ticks: bool = True,
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
        self.tick_buffer_size = tick_buffer_size
        self.pi_max_classes = pi_max_classes
        self.hmac_shared_secret = hmac_secret
        self.verbose = verbose

        # locks
        if async_mode:
            try:
                from anyio import Lock as _ALock  # type: ignore
                self._lock = _ALock()
            except ImportError:   # pragma: no cover
                self._lock = threading.RLock()
        else:
            self._lock = threading.RLock()
        self._pi_lock = threading.RLock()

        # buffers
        self._buffers: Dict[str, deque[QuantumTick]] = {}
        self._changes: Dict[str, deque[MotifChangeID]] = {}
        self._epoch_histogram: Dict[str, int] = {}
        self.history: List[str] = []

        # π‑groupoid DSU
        self._pi_classes: Dict[str, str] = {}

        # dynamic flags will be injected later
        if not hasattr(self, "_init_dynamic_flags"):
            self._init_dynamic_flags = lambda: None  # type: ignore

    # ────────────────────────────────
    # Quantum‑tick API
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
            # motif‑change detection
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
    # π‑Groupoid helpers (thread‑safe)
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
# dynamic‑flag mix‑in (unchanged from v3.1.1 but patched once)
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

    _orig_init = LogicalAgentAT.__init__
    def _patched_init(self, *a, **kw):             # noqa: D401
        _orig_init(self, *a, **kw)                 # type: ignore[arg-type]
        self._init_dynamic_flags()
    LogicalAgentAT.__init__ = _patched_init        # type: ignore[assignment]

    LogicalAgentAT._dyn_flag_patch_applied = True  # type: ignore[attr-defined]

# END_OF_FILE
