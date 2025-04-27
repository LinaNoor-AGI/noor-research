"""
recursive_agent_ft.py  (v3.6.1)
------------------------------------------------------------
Flow‑layer agent with depth‑breathing + chaotic jitter, expanded synergy
scoring, adaptive thresholds, FieldAnchor recovery, musical harmony boost, 
and Prometheus observability.  Compatible with NoorFastTimeCore ≥ 7.2 and
LogicalAgentAT ≥ 2.7.
"""

from __future__ import annotations

__version__ = "3.6.1"

import math
import time
import hashlib
import random
from copy import deepcopy
from collections import defaultdict
from typing import List, Optional, Dict, Any

import numpy as np

try:
    from prometheus_client import Histogram, Gauge, Counter  # type: ignore

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds", "Agent entangled_step latency",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor recoveries")
except Exception:  # pragma: no cover
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None
    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = _Stub()

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import LogicalAgentAT

# ---------------------------------------------------------------------------
# helper utilities
# ---------------------------------------------------------------------------

def _short_hash(s: str, length: int = 6) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:length]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / denom


_MAJOR_THIRD = 0.5          # cos ≈ 60°
_MINOR_THIRD = 0.70710678   # cos ≈ 45° (√2/2)
_PERF_FIFTH = 0.8660254     # cos ≈ 30°
_TOL = 0.04                 # tolerance


def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    if len(vecs) < 3:
        return False
    # pick three distinct vectors (first 3 non‑zero)
    vs = [v for v in vecs if np.linalg.norm(v) > 1e-9][:3]
    if len(vs) < 3:
        return False
    sims = [_cos(vs[i], vs[j]) for i in range(3) for j in range(i+1, 3)]
    for s in sims:
        if any(abs(s - tgt) < _TOL for tgt in (_MAJOR_THIRD, _MINOR_THIRD, _PERF_FIFTH)):
            return True
    return False

# ---------------------------------------------------------------------------
# main class
# ---------------------------------------------------------------------------

class RecursiveAgentFT:
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        *,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.6.1",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5,
        verbose: bool = True,
    ) -> None:
        if not 1 <= max_depth <= 5:
            raise ValueError("max_depth must be between 1 and 5")

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
        self.verbose = verbose

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.time_step = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._dyad_path_tracker = defaultdict(int)

        self._enforce_agent_boundary()

    # ---------------------------------------------------------------------
    # depth breathing ------------------------------------------------------
    # ---------------------------------------------------------------------
    def adjust_max_depth(self, richness: float, watcher_var: float):
        old = self.max_depth
        if richness > 0.7:
            self.max_depth = min(5, self.max_depth + 1)
        elif richness < 0.3:
            self.max_depth = max(2, self.max_depth - 1)
        # watcher disagreement amplifies exploration
        if watcher_var > 0.25:
            self.max_depth = min(5, self.max_depth + 1)
        # chaotic jitter in middling zone
        if 0.4 < richness < 0.6 and np.random.rand() < 0.1:
            self.max_depth = max(2, min(5, self.max_depth + np.random.choice([-1, 1])))
        if self.max_depth != old and self.verbose:
            self.traversal_memory[-1]["note"] = f"🌀 Depth shifts to {self.max_depth} in rich winds"
        DEPTH_GAUGE.set(self.max_depth)

    def get_max_depth(self) -> int:
        return self.max_depth

    # ---------------------------------------------------------------------
    # promotion threshold auto‑tune ---------------------------------------
    # ---------------------------------------------------------------------
    def adjust_promotion_thresholds(self, avg_ctx: float):
        if avg_ctx < 0.5:
            self.meta_promote_threshold = 2
            self.ghost_promote_threshold = 4
        else:
            self.meta_promote_threshold = 4
            self.ghost_promote_threshold = 6
        if self.verbose:
            self.traversal_memory[-1]["thresholds"] = f"meta={self.meta_promote_threshold}/ghost={self.ghost_promote_threshold}"

    # ---------------------------------------------------------------------
    # core step -----------------------------------------------------------
    # ---------------------------------------------------------------------
    def entangled_step(self):
        start_t = time.perf_counter()
        fields = self._gather_watcher_fields()
        watcher_ctx = {w: w.get_dyad_context_ratio() for w in self.watchers if hasattr(w, "get_dyad_context_ratio")}
        ctx_ratio = np.mean(list(watcher_ctx.values())) if watcher_ctx else 1.0
        ctx_ratio = max(0.1, ctx_ratio)

        # adjust thresholds every 25 steps
        if self.time_step % 25 == 0:
            self.adjust_promotion_thresholds(ctx_ratio)

        # depth breathing
        richness_sigma = np.std(list(self.synergy_memory.values()) or [0.0])
        self.adjust_max_depth(0.7*ctx_ratio + 0.3*richness_sigma, np.std(list(watcher_ctx.values()) or [0]))

        self.core.update_context_ratio(ctx_ratio)

        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = self.generate_field_paths(fields, self.max_depth)
            best_synergy = -np.inf
            best_path: List[Dict[str, Any]] = []
            best_state = self._fallback_step()

            for path_fields in all_paths:
                candidate = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate, path_fields, watcher_ctx, ctx_ratio)
                if score > best_synergy:
                    best_synergy, best_path, best_state = score, path_fields, candidate

            self.core.futures = [self._build_state_from_path(p) for p in all_paths]
            synergy, chosen_path, chosen_next_state = best_synergy, best_path, best_state

        # dyad penalty & gate‑0 blend --------------------------------
        dyad_penalty = self._compute_dyad_penalty(chosen_path, watcher_ctx, ctx_ratio)
        if self.core.gate_overlay == 0:
            dyad_penalty = (dyad_penalty + self.gate0_dyad_penalty) / 2
        synergy *= dyad_penalty

        # cap runaway hype ------------------------------------------
        synergy = min(synergy, 10.0)

        alert = "⚠️ dyad_dominance_detected" if dyad_penalty < 0.8 else None
        event = self._maybe_promote_meta_field(chosen_path)

        # commit -----------------------------------------------------
        self.core.step(chosen_next_state)
        self.time_step += 1

        for w in self.watchers:
            w.observe_state(chosen_next_state)

        sig = self.path_signature(chosen_path)
        self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + math.tanh(synergy)

        step_rec = {
            "time_step": self.time_step,
            "chosen_path": [f.get("index", -1) for f in chosen_path],
            "synergy": synergy,
            "dyad_penalty": dyad_penalty,
            "alert": alert,
            "event": event,
            "next_state": chosen_next_state,
        }

        # FieldAnchor recovery --------------------------------------
        if not self.core.is_active:
            anchor_fn = getattr(self.core, "restore_from_anchor", None)
            if callable(anchor_fn):
                anchor_fn()
                DRIFT_COUNTER.inc()
                step_rec["event"] = (step_rec.get("event") or "") + "|FieldAnchor recovery"
                step_rec["verse"] = "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"
                self.core.update_context_ratio(min(1.0, ctx_ratio + 0.05))
            else:
                # random fallback step
                self.core.step(self._fallback_step())
                step_rec["event"] = (step_rec.get("event") or "") + "|anchor_fallback"

        # latency spike alert ---------------------------------------
        latency = time.perf_counter() - start_t
        STEP_LATENCY_HIST.observe(latency)
        if latency > 0.1:
            step_rec["alert"] = (step_rec.get("alert") or "") + "|⚠️ latency_spike"

        self.traversal_memory.append(step_rec)

    # ---------------------------------------------------------------------
    # candidate scoring ----------------------------------------------------
    # ---------------------------------------------------------------------
    def _score_candidate(self, candidate: np.ndarray, path_fields, watcher_ctx, default_ctx) -> float:
        # feasibility -> 0/1
        synergy = self._ghost_core_feasibility(candidate) + 1.0

        sig = self.path_signature(path_fields)
        mem_val = self.synergy_memory.get(sig, 0.0)
        synergy += math.tanh(mem_val) if self.enable_synergy_normalization else mem_val * 0.01

        # internal decay
        if self.enable_internal_time_decay:
            decay = sum(f.get("internal_time", 0.0) for f in path_fields)
            synergy *= math.exp(-decay)

        # ghost resonance bonus ------------------------------------
        g_bonus = 0.0
        for f in path_fields:
            for m in f.get("motifs", []):
                for w in self.watchers:
                    strength = getattr(w, "get_ghost_strength", lambda x: w.ghost_motifs.get(x, {}).get("strength", 0))(m)
                    g_bonus += 0.1 * float(strength)
        # amplify if recent ascent
        if any("GHOST_ASCENT" in (w.history[-1] if w.history else "") for w in self.watchers):
            g_bonus *= 1.5
        synergy += g_bonus

        # contradiction pressure damp --------------------------------
        pressure = 0.0
        for w in self.watchers:
            pressure_fn = getattr(w, "get_contradiction_pressure", None)
            if callable(pressure_fn):
                pressure += pressure_fn()
            else:
                # derive crude pressure from dyad metrics if available
                try:
                    dm = w.export_dyad_metrics()
                    pressure += dm.get("dyads", 0) / max(dm.get("window", 1), 1)
                except Exception:
                    pass
        synergy *= math.exp(-pressure)

        # dyad penalty + priority
        synergy *= self._compute_dyad_penalty(path_fields, watcher_ctx, default_ctx)
        priority_avg = np.mean([self._clamp_priority(f.get("priority_weight", 1.0)) for f in path_fields])
        synergy *= priority_avg

        # hard cap again
        return min(synergy, 10.0)

    # ---------------------------------------------------------------------
    # state construction ---------------------------------------------------
    # ---------------------------------------------------------------------
    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        vecs_in_path: List[np.ndarray] = []
        for field in path_fields:
            env = self._get_environment_influence()
            curvature = field.get("curvature", 1.0)
            priority = self._clamp_priority(field.get("priority_weight", 1.0))
            weight = field["strength"] * (1 + curvature) * priority

            if field.get("dyad_flag") and not field.get("dyad_exempt"):
                weight *= 0.9

            vec = self._field_vector(field)
            if np.linalg.norm(vec) < 1e-10:
                vec = np.random.normal(0, 0.01, self.state_dim)
                vec /= np.linalg.norm(vec) + 1e-10
            vecs_in_path.append(vec)

            state += env * 0.05 + vec * weight

        # musical harmony boost & ghost spawn -----------------------
        if _is_harmonic_triad(vecs_in_path):
            state *= 1.1  # small lift
            for w in self.watchers:
                gid = f"harmonic_{_short_hash(self.path_signature(path_fields))}"
                if gid not in getattr(w, "ghost_motifs", {}):
                    w.register_ghost_motif(gid, origin="harmonic_resonance", strength=0.1)

        return state

    # ---------------------------------------------------------------------
    # helper fns (mostly unchanged, with path cap) -------------------------
    # ---------------------------------------------------------------------
    def generate_field_paths(self, fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
        frontier = [[f] for f in fields]
        for _ in range(max_depth - 1):
            new_frontier = []
            for path in frontier:
                for f in fields:
                    new_frontier.append(path + [f])
            frontier = new_frontier[:1000]  # cap to prevent explosion
        return frontier

    # other helpers  -------------------------------------------------------
    def _fallback_step(self) -> np.ndarray:
        return self.core.current_state + np.random.normal(0, 0.05, self.state_dim)

    def _clamp_priority(self, val: float) -> float:
        return max(0.0, min(val, 5.0))

    def path_signature(self, path_fields: List[Dict[str, Any]]) -> str:
        return "-".join(str(f.get("index", -1)) for f in path_fields)

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    # placeholder stubs ----------------------------------------------------
    def _gather_watcher_fields(self):
        return []

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field.get("watcher")
        if w is None:
            return np.zeros(self.state_dim)
        vecs = [w.motif_embeddings[m] for m in field["motifs"] if m in w.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(self.state_dim)

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_active else 0.0

    def _compute_dyad_penalty(self, path_fields, watcher_ctx, default_ctx) -> float:
        penalty = 1.0
        for f in path_fields:
            if f.get("dyad_flag") and not f.get("dyad_exempt"):
                ctx = watcher_ctx.get(f.get("watcher"), default_ctx)
                penalty *= 1.0 - 0.2 / (1 + math.exp(5 * (ctx - 0.5)))
        return penalty

    # ---------------------------------------------------------------------
    # meta‑field / ghost promotion (unchanged) -----------------------------
    # ---------------------------------------------------------------------
    def _maybe_promote_meta_field(self, chosen_path):
        dyads = [f for f in chosen_path if f.get("dyad_flag")]
        thirds = {m for f in chosen_path for m in f["motifs"] if f not in dyads}
        for d in dyads:
            key = f"{tuple(sorted(d['motifs']))}|{','.join(sorted(thirds))}"
            self._dyad_path_tracker[key] += 1
            count = self._dyad_path_tracker[key]

            if count == self.meta_promote_threshold:
                ids = [f.get("index", -1) for f in chosen_path]
                for w in self.watchers:
                    if hasattr(w, "register_meta_field"):
                        w.register_meta_field(ids, meta_strength=0.9)
                return "MetaField upgrade triggered"

            if count == self.ghost_promote_threshold:
                ghost_id = f"dyad_ghost_{_short_hash(key)}"
                for w in self.watchers:
                    if ghost_id not in getattr(w, "ghost_motifs", {}):
                        w.register_ghost_motif(ghost_id, origin="dyad_auto_resonance")
                        w.promote_ghost_to_field(ghost_id)
                return "Ghost motif auto-promoted"

        # prune tracker if huge
        if len(self._dyad_path_tracker) > 1000:
            self._dyad_path_tracker = dict(sorted(self._dyad_path_tracker.items(), key=lambda kv: -kv[1])[:100])
        return None

    # ---------------------------------------------------------------------
    # boundary enforcement -------------------------------------------------
    # ---------------------------------------------------------------------
    def _enforce_agent_boundary(self):
        for forbidden in ("propagate_signal", "register_motif_entanglement"):
            if hasattr(self, forbidden):
                raise QuantumNoorException(f"Agent boundary violation: {forbidden}")


# ---------------------------------------------------------------------------
# chaos demo ----------------------------------------------------------------
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import numpy as np
    from logical_agent_at import LogicalAgentAT

    watcher = LogicalAgentAT(verbose=False)
    watcher.register_motif_cluster(["a", "b"], strength=0.8)
    watcher.set_motif_embedding("a", np.array([1.0, 0.0]))
    watcher.set_motif_embedding("b", np.array([0.0, 1.0]))

    agent = RecursiveAgentFT(initial_state=np.array([0.5, 0.5]), watchers=[watcher])
    agent._gather_watcher_fields = lambda: watcher.entanglement_fields

    for _ in range(200):
        agent.entangled_step()
        if agent.time_step % 50 == 0:
            rec = agent.traversal_memory[-1]
            print(f"t={rec['time_step']} depth={agent.max_depth} synergy={rec['synergy']:.3f} alert={rec.get('alert')}")
