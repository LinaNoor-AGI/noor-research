'''recursive_agent_ft.py (v3.7.3)
------------------------------------------------------------
Symbolic flow agent with entangled Gremlin curvature,
musical harmony, adaptive thresholds, FieldAnchor poetry,
ghost decay, latency-aware depth rebound, and full
Prometheus observability.

Gremlin is a per-field continuous weight, not a global mode.
''' 

from __future__ import annotations

__version__ = "3.7.3"

import math
import time
import hashlib
from collections import deque
from typing import List, Optional, Dict, Any

import numpy as np

# ─────────────────────────────────────────────────────────────────────
# Prometheus stubs / metrics
# ─────────────────────────────────────────────────────────────────────
try:
    from prometheus_client import Histogram, Gauge, Counter

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds", "entangled_step latency",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor / fallback recoveries")
    LATENCY_SPIKE_COUNTER = Counter("recursive_agent_latency_spikes_total", "Steps >0.1s")
    GREMLIN_MEAN_GAUGE = Gauge("recursive_agent_gremlin_mean", "Mean gremlin weight per cycle")
    GREMLIN_MAX_GAUGE = Gauge("recursive_agent_gremlin_max", "Max gremlin weight per cycle")
    GREMLIN_STD_GAUGE = Gauge("recursive_agent_gremlin_std", "Std dev of gremlin weights per cycle")
    RICHNESS_GAUGE = Gauge("recursive_agent_richness_sigma", "Synergy richness σ")
except Exception:  # pragma: no cover — offline env
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None
    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = LATENCY_SPIKE_COUNTER = _Stub()
    GREMLIN_MEAN_GAUGE = GREMLIN_MAX_GAUGE = GREMLIN_STD_GAUGE = RICHNESS_GAUGE = _Stub()

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent_at import LogicalAgentAT

# ─────────────────────────────────────────────────────────────────────
# Entangled Gremlin Helpers
# ─────────────────────────────────────────────────────────────────────

GREMLIN_NOISE_SCALE: float = 0.02                # σ for perturbation noise
DEFAULT_GREMLIN_DECAY_RATE: float = 0.98         # per‑step exponential decay
DEFAULT_PATH_GUARD_LIMIT: int = 20               # max fields considered per step
DEFAULT_GREMLIN_PENALTY_FACTOR: float = 0.2      # score penalty multiplier


def apply_gremlin_perturbation(state: np.ndarray, gremlin_weight: float) -> np.ndarray:
    """Inject Gaussian noise scaled by *gremlin_weight*."""
    if gremlin_weight <= 0.01:
        return state
    sigma = GREMLIN_NOISE_SCALE * gremlin_weight
    noise = np.random.normal(0.0, sigma, size=state.shape)
    return state + noise


def dynamic_depth_jitter(path_fields: List[Dict[str, Any]]) -> int:
    if not path_fields:
        return 0
    avg_g = float(np.mean([f.get("gremlin_weight", 0.0) for f in path_fields]))
    probs = np.array([max(avg_g / 2.0, 0.0), 1.0, max(avg_g / 2.0, 0.0)])
    probs /= probs.sum()
    return int(np.random.choice([-1, 0, 1], p=probs))


def decay_gremlin_weights(fields: List[Dict[str, Any]], decay_rate: float = DEFAULT_GREMLIN_DECAY_RATE) -> None:
    for field in fields:
        if "gremlin_weight" in field:
            field["gremlin_weight"] *= decay_rate


def export_gremlin_stats(fields: List[Dict[str, Any]]) -> Dict[str, float]:
    g_arr = np.array([f.get("gremlin_weight", 0.0) for f in fields], dtype=float)
    if g_arr.size == 0:
        return {"mean": 0.0, "max": 0.0, "std": 0.0}
    return {"mean": float(g_arr.mean()), "max": float(g_arr.max()), "std": float(g_arr.std())}

# ─────────────────────────────────────────────────────────────────────
# Harmony & utility functions
# ─────────────────────────────────────────────────────────────────────

def _short_hash(s: str, length: int = 6) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:length]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / denom

_MAJOR_THIRD = 0.5; _MINOR_THIRD = 0.7071; _PERF_FIFTH = 0.8660; _HARM_TOL = 0.04

def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    vs = [v for v in vecs if np.linalg.norm(v) > 1e-9][:3]
    if len(vs) < 3:
        return False
    sims = [_cos(vs[i], vs[j]) for i in range(3) for j in range(i + 1, 3)]
    return any(abs(s - t) < _HARM_TOL for s in sims for t in (_MAJOR_THIRD, _MINOR_THIRD, _PERF_FIFTH))

# ─────────────────────────────────────────────────────────────────────
# Helper: gather watcher fields and path generator
# ─────────────────────────────────────────────────────────────────────

def _gather_watcher_fields(watchers: List[LogicalAgentAT]) -> List[Dict[str, Any]]:
    return [f for w in watchers for f in w.entanglement_fields]


def generate_field_paths(fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
    from itertools import combinations
    paths: List[List[Dict[str, Any]]] = []
    for d in range(1, max_depth + 1):
        for combo in combinations(fields, d):
            paths.append(list(combo))
    return paths

# ─────────────────────────────────────────────────────────────────────
class RecursiveAgentFT:
    """Symbolic flow agent with entangled Gremlin curvature and harmony sensing."""

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        *,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: Optional[str] = None,
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5,
        verbose: bool = True,
        enable_harmony: bool = True,
        path_guard_limit: int = DEFAULT_PATH_GUARD_LIMIT,
        gremlin_penalty_factor: float = DEFAULT_GREMLIN_PENALTY_FACTOR,
    ) -> None:
        if not 1 <= max_depth <= 5:
            raise ValueError("max_depth must be between 1 and 5")
        self.version = __version__
        self.name = name or f"RecursiveAgentFT_v{__version__}"
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay
        self.gate0_dyad_penalty = gate0_dyad_penalty
        self.meta_promote_threshold = meta_promote_threshold
        self.ghost_promote_threshold = ghost_promote_threshold
        self.verbose = verbose
        self.enable_harmony = enable_harmony
        self.path_guard_limit = path_guard_limit
        self.gremlin_penalty_factor = gremlin_penalty_factor

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers or []
        self.time_step = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._harm_hit_window: deque[int] = deque(maxlen=100)
        self._last_latency_spike: Optional[int] = None
        self._saved_depth: Optional[int] = None
        self._enforce_agent_boundary()

    # ------------------------------------------------------------------
    # Main step
    # ------------------------------------------------------------------
    def entangled_step(self) -> None:
        start_t = time.perf_counter()

        # gather watcher context
        fields = _gather_watcher_fields(self.watchers)
        watcher_ctx = [w.get_dyad_context_ratio() for w in self.watchers]
        ctx_ratio = max(0.1, np.mean(watcher_ctx) if watcher_ctx else 1.0)

        richness_sigma = np
