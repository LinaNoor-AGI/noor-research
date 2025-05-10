"""
🔭 LogicalAgentAT · v3.1.1

Topological watcher & algebraic ecology with Quantum‑Tick 2.0, dynamic
feature flags, hardened schema guards, and Prometheus metrics.

Changes vs 3.1.0
────────────────
* Added `enable_gremlin_mode` default + handling in `__init__`
* Prometheus `.labels()` calls now use explicit keyword labels
* Thread‑safe π‑groupoid helpers
* Import fixes (`time.perf_counter`)
* Laplacian smoothing gracefully degrades if `scipy` is missing
* Guard to prevent double‑patching of dynamic‑flag mix‑ins
"""
from __future__ import annotations

__version__ = "3.1.1"
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
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    # Stub for metrics in minimal environments
    class _Stub:                                 # noqa: D401
        def __init__(self, *_, **__):
            self._v = 0
            self._lock = threading.Lock()

        def inc(self, amt: float = 1.0):
            with self._lock:
                self._v += amt

        def labels(self, *_, **__):
            return self

        def set(self, v):                         # noqa: ANN001
            with self._lock:
                self._v = v

    Counter = Gauge = _Stub                      # type: ignore


# ──────────────────────────────────────────────────────────────
# 0. Prometheus metrics
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
MOTIF_COLLAPSES = Counter(
    "logical_agent_motif_collapses_total",
    "Motif collapse events",
    ["watcher", "agent_id"],
)
# feature‑flag metric injected later


# ──────────────────────────────────────────────────────────────
# 1. Quantum‑Tick 2.0 dataclass
# ──────────────────────────────────────────────────────────────
@dataclass
class QuantumTick:
    motif_id: str
    lamport_clock: int
    hlc_ts: str            # ISO‑8601 + logical
    coherence_hash: str    # 12‑hex
    agent_id: str
    tick_hmac: Optional[str] = None

    @classmethod
    def now(
        cls,
        motif_id: str,
        agent_id: str,
        *,
        secret: bytes | None = None,
        lamport_clock: int = 0,
    ) -> "QuantumTick":
        """Factory that fills lamport, HLC and HMAC."""
        coherence_hash = f"{random.getrandbits(48):012x}"
        hlc_ts = f"{time.strftime('%Y-%m-%dT%H:%M:%S')}.{lamport_clock:04d}Z"
        tick_hmac = None
        if secret:
            m = hashlib.sha256()
            m.update(secret)
            m.update(coherence_hash.encode())
            m.update(str(lamport_clock).encode())
            tick_hmac = m.hexdigest()
        return cls(
            motif_id=motif_id,
            lamport_clock=lamport_clock,
            hlc_ts=hlc_ts,
            coherence_hash=coherence_hash,
            agent_id=agent_id,
            tick_hmac=tick_hmac,
        )


# ──────────────────────────────────────────────────────────────
# 2. LogicalAgentAT core
# ──────────────────────────────────────────────────────────────
class LogicalAgentAT:
    """
    Watcher that stores QuantumTicks per motif (ring buffer), enforces schema
    guards, and exposes dynamic feature flags for adaptive behaviour.
    """

    # default constructor knobs
    def __init__(
        self,
        *,
        agent_id: str = "watcher@default",
        enable_quantum_ticks: bool = True,
        tick_buffer_size: int = 128,
        pi_max_classes: int = 20_000,
        hmac_shared_secret: Optional[bytes] = os.getenv("NOOR_TICK_HMAC", "").encode()
        or None,
        # new flag
        enable_gremlin_mode: bool = False,
        verbose: bool = False,
    ):
        self.agent_id = agent_id
        self.enable_quantum_ticks = enable_quantum_ticks
        self.tick_buffer_size = tick_buffer_size
        self.pi_max_classes = pi_max_classes
        self.hmac_shared_secret = hmac_shared_secret
        self.enable_gremlin_mode = enable_gremlin_mode
        self.verbose = verbose

        # internal
        self._lock = threading.RLock()
        self._buffers: Dict[str, deque[QuantumTick]] = {}
        self._epoch_histogram: Dict[str, int] = {}
        self.history: List[str] = []

        # π‑groupoid (concurrent safe)
        self._pi_classes: Dict[str, str] = {}
        self._pi_lock = threading.RLock()

    # ────────────────────────────────
    # Quantum‑tick API
    # ────────────────────────────────
    def register_tick(self, motif_id: str, tick: QuantumTick) -> None:
        if not self.enable_quantum_ticks:
            return

        if not self._verify_tick_schema(tick):
            raise ValueError("Tick schema mismatch")

        if self.hmac_shared_secret and not self.verify_hmac(tick):
            TICK_HMAC_FAILURES.labels(agent_id=self.agent_id).inc()
            return

        with self._lock:
            buf = self._buffers.setdefault(
                motif_id, deque(maxlen=self.tick_buffer_size)
            )
            buf.append(tick)
            self._epoch_histogram[motif_id] = (
                self._epoch_histogram.get(motif_id, 0) + 1
            )
        TICKS_TOTAL.labels(stage=tick.stage, agent_id=self.agent_id).inc()

    def get_latest_tick(self, motif_id: str) -> Optional[QuantumTick]:
        buf = self._buffers.get(motif_id)
        return buf[-1] if buf else None

    def export_tick_histogram(self) -> Dict[str, Any]:
        """Return a motif → count histogram (copy)."""
        with self._lock:
            return dict(self._epoch_histogram)

    # ────────────────────────────────
    # Dynamic feature flag helpers
    #   (runtime mix‑ins injected later)
    # ────────────────────────────────
    def set_feature(self, name: str, value: bool, *, reason: str = "") -> None:
        raise NotImplementedError("dynamic flags injected later")

    def get_feature(self, name: str) -> bool:                # noqa: D401
        raise NotImplementedError

    def list_dynamic_flags(self) -> Dict[str, bool]:
        raise NotImplementedError

    # ────────────────────────────────
    # HMAC helpers
    # ────────────────────────────────
    def verify_hmac(self, tick: QuantumTick) -> bool:        # noqa: D401
        if not tick.tick_hmac or not self.hmac_shared_secret:
            return False
        m = hashlib.sha256()
        m.update(self.hmac_shared_secret)
        m.update(tick.coherence_hash.encode())
        m.update(str(tick.lamport_clock).encode())
        return m.hexdigest() == tick.tick_hmac

    # ────────────────────────────────
    # Schema guard & migrations
    # ────────────────────────────────
    @staticmethod
    def _verify_tick_schema(tick: QuantumTick) -> bool:
        """Basic field presence & size checks (expand as needed)."""
        return (
            isinstance(tick.coherence_hash, str)
            and len(tick.coherence_hash) == 12
            and isinstance(tick.lamport_clock, int)
        )

    # ────────────────────────────────
    # Optional Laplacian smoothing util
    # ────────────────────────────────
    def _maybe_smooth_graph(self, G):                        # noqa: D401, ANN001
        if not getattr(self, "enable_laplacian", False):
            return
        try:
            from scipy.sparse.linalg import eigsh            # type: ignore
            # _apply_laplacian_smoothing inlined for brevity
            eigsh(G)                                         # placeholder
        except ImportError:
            if self.verbose:
                self.history.append("⚠️ scipy missing – Laplacian skipped")
        except Exception:                                    # pragma: no cover
            pass

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

    # internal π helpers
    def _find_root(self, x: str) -> str:
        path = []
        while x in self._pi_classes:
            path.append(x)
            x = self._pi_classes[x]
        # path compression
        for p in path:
            self._pi_classes[p] = x
        return x


# ──────────────────────────────────────────────────────────────
# inject methods only if not already present
# ──────────────────────────────────────────────────────────────
# Dynamic‑Feature‑Flag mix‑in (v3.1.1)
# ──────────────────────────────────────────────────────────────

if not getattr(LogicalAgentAT, "_dyn_flag_patch_applied", False):

    # ----------------------------------------------------------
    # Metric for live feature‑flag flips
    # ----------------------------------------------------------
    try:
        from prometheus_client import Counter as _ToggleCounter
        _FEATURE_TOGGLE_COUNTER = _ToggleCounter(
            "logical_agent_feature_toggles_total",
            "Dynamic feature‑flag toggles",
            ["flag", "agent_id"],
        )
    except Exception:                                            # pragma: no cover
        class _FeatureStub:                                      # noqa: D401
            def __getattr__(self, _):                            # noqa: ANN001
                return lambda *a, **k: None                      # noqa: E731

        _FEATURE_TOGGLE_COUNTER = _FeatureStub()                 # type: ignore

    # ----------------------------------------------------------
    # Whitelist of flags that may be flipped at runtime
    # ----------------------------------------------------------
    _DYNAMIC_FLAGS = {
        "enable_quantum_ticks",
        "enable_topology",
        "enable_cluster_algebra",
        "enable_sheaf_transport",
        "enable_laplacian",
        "enable_pi_groupoid",
        "enable_gremlin_mode",
    }

    # ----------------------------------------------------------
    # Helper functions to be added as methods
    # ----------------------------------------------------------
    def _init_dynamic_flags(self: "LogicalAgentAT"):
        """Initialise persistent flag‑state mirror & audit trail (thread‑safe)."""
        self._flag_state: Dict[str, bool] = {
            k: getattr(self, k, False) for k in _DYNAMIC_FLAGS
        }
        self._flag_audit: List[tuple[int, str, bool, str]] = []  # (ts, flag, val, reason)

    def _set_feature(self: "LogicalAgentAT", name: str, value: bool, *, reason: str = ""):
        """
        Atomically toggle a whitelisted feature flag.

        Parameters
        ----------
        name   : str   – flag name (must be in whitelist)
        value  : bool  – new value
        reason : str   – optional human note for audit trail

        Raises
        ------
        ValueError if `name` is not a recognised dynamic flag.
        """
        if name not in _DYNAMIC_FLAGS:
            raise ValueError(f"'{name}' is not a dynamic flag")
        with self._lock:
            old = getattr(self, name, False)
            if old == value:
                return
            setattr(self, name, value)
            self._flag_state[name] = value
            ts = int(time.time_ns())          # high‑res timestamp
            self._flag_audit.append((ts, name, value, reason))
            _FEATURE_TOGGLE_COUNTER.labels(flag=name, agent_id=self.agent_id).inc()
            if self.verbose:
                self.history.append(f"⚙️ feature '{name}' → {value}  ({reason})")

    def _get_feature(self: "LogicalAgentAT", name: str) -> bool:
        if name not in _DYNAMIC_FLAGS:
            raise ValueError(f"'{name}' is not a dynamic flag")
        return getattr(self, name, False)

    def _list_dynamic_flags(self: "LogicalAgentAT") -> Dict[str, bool]:
        return {k: getattr(self, k, False) for k in _DYNAMIC_FLAGS}

    # ----------------------------------------------------------
    # Inject methods only if missing
    # ----------------------------------------------------------
    for _fname, _impl in {
        "_init_dynamic_flags": _init_dynamic_flags,
        "set_feature":        _set_feature,
        "get_feature":        _get_feature,
        "list_dynamic_flags": _list_dynamic_flags,
    }.items():
        if not hasattr(LogicalAgentAT, _fname):
            setattr(LogicalAgentAT, _fname, _impl)

    # ----------------------------------------------------------
    # Wrap original __init__ once to ensure dynamic‑flag init
    # ----------------------------------------------------------
    _orig_init = LogicalAgentAT.__init__

    def _patched_init(self, *args, **kwargs):                    # noqa: D401
        _orig_init(self, *args, **kwargs)
        # Initialise flags after base init
        if not hasattr(self, "_flag_state"):                     # guard idempotence
            self._init_dynamic_flags()

    LogicalAgentAT.__init__ = _patched_init                      # type: ignore[assignment]

    # sentinel so we don’t patch twice in same interpreter
    LogicalAgentAT._dyn_flag_patch_applied = True                # type: ignore[attr-defined]

# END_OF_FILE
