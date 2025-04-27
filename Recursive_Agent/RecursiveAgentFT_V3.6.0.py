"""
recursive_agent_ft.py  (v3.6.0)
------------------------------------------------------------
Flow‑layer agent with depth‑breathing, expanded synergy scoring,
adaptive promotion thresholds, FieldAnchor recovery, musical harmony
boosting and Prometheus observability.
Compatible with NoorFastTimeCore ≥ v7.2 and LogicalAgentAT ≥ v2.7.
"""

from __future__ import annotations

__version__ = "3.6.0"

import time
import math
import hashlib
from copy import deepcopy
from collections import defaultdict
from typing import List, Optional, Dict, Any

import numpy as np

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import LogicalAgentAT

# ──────────────────────────────────────────────────────────────
# Prometheus metrics (guarded)
# ──────────────────────────────────────────────────────────────
try:
    from prometheus_client import Histogram, Gauge, Counter  # type: ignore

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds",
        "entangled_step latency",
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor recoveries")
except Exception:  # pragma: no cover
    class _Stub:  # pylint: disable=too-few-public-methods
        def __getattr__(self, _):
            return lambda *a, **k: None

    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = _Stub()

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _short_hash(s: str, length: int = 4) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:length]


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        a, b = a.flatten(), b.flatten()
    n = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / n)


_HARMONIC_TARGETS = [0.5, 0.866]  # major/minor third (≈60°) & perfect fifth (≈30°)


def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    if len(vecs) < 3:
        return False
    # normalise
    vecs = [v / (np.linalg.norm(v) + 1e-12) for v in vecs]
    scores = [abs(_cosine(vecs[i], vecs[j])) for i in range(3) for j in range(i + 1, 3)]
    return all(any(abs(s - t) < 0.05 for t in _HARMONIC_TARGETS) for s in scores)

# ──────────────────────────────────────────────────────────────
# Main class
# ──────────────────────────────────────────────────────────────


class RecursiveAgentFT:
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        *,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.6.0",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5,
    ) -> None:
        # cfg
        self.version = __version__
        self.name = name
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay
        self.gate0_dyad_penalty = gate0_dyad_penalty
        self.meta_promote_threshold = meta_promote_threshold
        self.ghost_promote_threshold = ghost_promote_threshold

        if not (1 <= max_depth <= 5):
            raise ValueError("max_depth must be between 1 and 5")

        # triad links
        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []

        # internal stores
        self.time_step = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._dyad_path_tracker = defaultdict(int)

        # prometheus
        DEPTH_GAUGE.set(self.max_depth)

        self._enforce_agent_boundary()

    # ---------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------

    def get_max_depth(self) -> int:
        return self.max_depth

    def set_promotion_thresholds(self, meta: int, ghost: int):
        self.meta_promote_threshold = int(meta)
        self.ghost_promote_threshold = int(ghost)

    # ---------------------------------------------------------
    # Depth & threshold adjusters
    # ---------------------------------------------------------

    def adjust_max_depth(self):
        r = self.core.dyad_context_ratio  # 0 bad, 1 good
        σ = np.std(list(self.synergy_memory.values()) or [0.0])
        richness = 0.7 * r + 0.3 * float(σ)

        # watcher disagreement amplifies search
        ratios = [w.get_dyad_context_ratio() for w in self.watchers] or [r]
        if np.std(ratios) > 0.25:
            richness = min(1.0, richness + 0.2)

        if richness > 0.7:
            self.max_depth = min(5, self.max_depth + 1)
        elif richness < 0.3:
            self.max_depth = max(2, self.max_depth - 1)
        DEPTH_GAUGE.set(self.max_depth)

    def adjust_promotion_thresholds(self):
        ratios = [w.get_dyad_context_ratio() for w in self.watchers] or [1.0]
        avg_ctx = float(np.mean(ratios))
        if avg_ctx < 0.5:
            self.meta_promote_threshold = max(2, self.meta_promote_threshold - 1)
            self.ghost_promote_threshold = max(4, self.ghost_promote_threshold - 1)
        else:
            self.meta_promote_threshold = min(5, self.meta_promote_threshold + 1)
            self.ghost_promote_threshold = min(8, self.ghost_promote_threshold + 1)

    # ---------------------------------------------------------
    # Core cycle
    # ---------------------------------------------------------

    def entangled_step(self) -> None:
        start_t = time.perf_counter()

        # depth & threshold breathing
        self.adjust_max_depth()
        if self.time_step % 25 == 0 and self.time_step > 0:
            self.adjust_promotion_thresholds()

        # watcher context
        fields = self._gather_watcher_fields()
        watcher_ctx = {w: w.get_dyad_context_ratio() for w in self.watchers}
        ctx_ratio = max(0.1, float(np.mean(list(watcher_ctx.values()) or [1.0])))
        self.core.update_context_ratio(ctx_ratio)

        # candidate selection
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = self.generate_field_paths(fields, self.max_depth)
            best_synergy, best_state, best_path = -math.inf, None, None
            for path_fields in all_paths:
                cand = self._build_state_from_path(path_fields)
                score = self._score_candidate(cand, path_fields, watcher_ctx, ctx_ratio)
                if score > best_synergy:
                    best_synergy, best_state, best_path = score, cand, path_fields
            self.core.futures = [self._build_state_from_path(p) for p in all_paths]
            chosen_next_state, synergy, chosen_path = best_state, best_synergy, best_path

        # dyad penalty & gate‑0 adjustment
        dyad_penalty = self._compute_dyad_penalty(chosen_path, watcher_ctx, ctx_ratio)
        if self.core.gate_overlay == 0:
            dyad_penalty = (dyad_penalty + self.gate0_dyad_penalty) / 2
        synergy *= dyad_penalty

        alert = "⚠️ dyad_dominance_detected" if dyad_penalty < 0.8 else None
        event = self._maybe_promote_meta_field(chosen_path)

        # core step & collapse recovery
        self.core.step(chosen_next_state)
        if not self.core.is_active:
            anchor_fn = getattr(self.core, "restore_from_anchor", None)
            if callable(anchor_fn):
                anchor_fn()
                DRIFT_COUNTER.inc()
                event = (event or "") + "|FieldAnchor recovery"

        # notify watchers
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        # bookkeeping
        self.time_step += 1
        sig = self.path_signature(chosen_path)
        self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        step_rec = {
            "t": self.time_step,
            "path": [f.get("index") for f in chosen_path],
            "synergy": synergy,
            "dyad_penalty": dyad_penalty,
            "alert": alert,
            "event": event,
        }
        self.traversal_memory.append(step_rec)

        # prometheus latency
        STEP_LATENCY_HIST.observe(time.perf_counter() - start_t)

    # ---------------------------------------------------------
    # Candidate construction & scoring
    # ---------------------------------------------------------

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for field in path_fields:
            env = self._get_environment_influence()
            curvature = field.get("curvature", 1.0)
            priority = self._clamp_priority(field.get("priority_weight", 1.0))
            weight = field["strength"] * (1 + curvature) * priority

            # harmonic triad boost
            vecs = [self._field_vector(field)]
            if _is_harmonic_triad(vecs):
                weight *= 1.1
            weight = min(weight, field["strength"] * 1.25)  # cap global

            if field.get("dyad_flag") and not field.get("dyad_exempt"):
                weight *= 0.9

            vec = vecs[0]
            if np.linalg.norm(vec) < 1e-10:
                vec = np.random.normal(0, 0.01, self.state_dim)
                vec /= np.linalg.norm(vec) + 1e-10
            state += env * 0.05 + vec * weight
        return state

    def _score_candidate(
        self,
        candidate: np.ndarray,
        path_fields: List[Dict[str, Any]],
        watcher_ctx: Dict[LogicalAgentAT, float],
        default_ctx: float,
    ) -> float:
        synergy = 1.0 + self._ghost_core_feasibility(candidate)
        sig = self.path_signature(path_fields)
        mem_val = self.synergy_memory.get(sig, 0.0)
        synergy += np.tanh(mem_val) if self.enable_synergy_normalization else mem_val * 0.01

        if self.enable_internal_time_decay:
            decay = sum(f.get("internal_time", 0.0) for f in path_fields)
            synergy *= math.exp(-decay)

        # ghost resonance bonus
        g_bonus = 0.0
        for f in path_fields:
            w = f["watcher"]
            ghost_strength = 0.0
            if hasattr(w, "get_ghost_strength"):
                for m in f["motifs"]:
                    ghost_strength += w.get_ghost_strength(m) or 0.0
            g_bonus += ghost_strength * 0.1
        synergy += g_bonus

        # contradiction pressure damp
        pressures = [getattr(w, "get_contradiction_pressure")() for w in self.watchers if hasattr(w, "get_contradiction_pressure")]
        if pressures:
            synergy *= math.exp(-float(np.mean(pressures)))

        # dyad penalty & priority blend
        synergy *= self._compute_dyad_penalty(path_fields, watcher_ctx, default_ctx)
        synergy *= float(np.mean([self._clamp_priority(f.get("priority_weight", 1.0)) for f in path_fields]))
        return synergy

    # ---------------------------------------------------------
    # Utilities (mostly unchanged)
    # ---------------------------------------------------------

    def _compute_dyad_penalty(self, path_fields, watcher_ctx, default_ctx) -> float:
        penalty = 1.0
        for f in path_fields:
            if f.get("dyad_flag") and not f.get("dyad_exempt"):
                ctx = watcher_ctx.get(f["watcher"], default_ctx)
                penalty *= 1.0 - 0.2 / (1 + math.exp(5 * (ctx - 0.5)))
        return penalty

    def _fallback_step(self) -> np.ndarray:
        return self.core.current_state + np.random.normal(0, 0.05, self.state_dim)

    def _clamp_priority(self, value: float) -> float:
        return max(0.0, min(value, 5.0))

    # placeholder — expected to be overridden or wired externally
    def _gather_watcher_fields(self):
        return []

    def generate_field_paths(self, fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
        frontier = [[f] for f in fields]
        for _ in range(max_depth - 1):
            frontier = [p + [f] for p in frontier for f in fields]
        return frontier

    def path_signature(self, path_fields: List[Dict[str, Any]]) -> str:
        return "-".join(str(f.get("index")) for f in path_fields)

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_active else 0.0

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field["watcher"]
        vecs = [w.motif_embeddings[m] for m in field["motifs"] if m in w.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(self.state_dim)

    # ---------------------------------------------------------
    # Promotion / resonance util (unchanged logic)
    # ---------------------------------------------------------

    def _maybe_promote_meta_field(self, chosen_path):
        dyads = [f for f in chosen_path if f.get("dyad_flag")]
        thirds = {m for f in chosen_path for m in f["motifs"] if f not in dyads}
        for d in dyads:
            key = f"{tuple(sorted(d['motifs']))}|{','.join(sorted(thirds))}"
            self._dyad_path_tracker[key] += 1
            count = self._dyad_path_tracker[key]

            if count == self.meta_promote_threshold:
                ids = [f.get("index") for f in chosen_path]
                for w in self.watchers:
                    if hasattr(w, "register_meta_field"):
                        w.register_meta_field(ids, meta_strength=0.9)
                return "MetaField upgrade triggered"

            if count == self.ghost_promote_threshold:
                ghost_id = f"dyad_ghost_{_short_hash(key)}"
                for w in self.watchers:
                    if hasattr(w, "get_ghost_motifs") and ghost_id not in w.get_ghost_motifs():
                        w.register_ghost_motif(ghost_id, origin="dyad_auto_resonance")
                        w.promote_ghost_to_field(ghost_id)
                return "Ghost motif auto‑promoted"

        # prune tracker size
        if len(self._dyad_path_tracker) > 1000:
            self._dyad_path_tracker = dict(sorted(self._dyad_path_tracker.items(), key=lambda x: -x[1])[:100])
        return None

    # ---------------------------------------------------------
    # Boundary enforcement
    # ---------------------------------------------------------

    def _enforce_agent_boundary(self):
        for forbidden in ["propagate_signal", "register_motif_entanglement"]:
            if hasattr(self, forbidden):
                raise QuantumNoorException(f"Agent boundary violation: {forbidden}")
