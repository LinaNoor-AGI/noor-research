"""
recursive_agent_ft.py  (v3.6.5)
------------------------------------------------------------
Flow‑layer agent with gremlin‑tunable chaos, musical harmony, adaptive
thresholds, FieldAnchor poetry, ghost decay, latency‑aware depth rebound
and full Prometheus observability.
Compatible with NoorFastTimeCore ≥ 7.2 • LogicalAgentAT ≥ 2.7.

Gremlin levels (via NOOR_GREMLIN env or enable_gremlin_mode param):
 0 – calm · 1 – mild jitter · 2 – high jitter & quick rebound · 3 – feral
"""

from __future__ import annotations

__version__ = "3.6.4"

import os, math, time, hashlib, random
from copy import deepcopy
from collections import defaultdict, deque
from typing import List, Optional, Dict, Any

import numpy as np

# ─────────────────────────────────────────────────────────────────────
# Prometheus stubs / metrics
# ─────────────────────────────────────────────────────────────────────
try:
    from prometheus_client import Histogram, Gauge, Counter  # type: ignore

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds", "entangled_step latency",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor / fallback recoveries")
    LATENCY_SPIKE_COUNTER = Counter("recursive_agent_latency_spikes_total", "Steps >0.1s")
except Exception:  # pragma: no cover
    class _Stub:  # noqa: D401,E701
        def __getattr__(self, _):
            return lambda *a, **k: None
    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = LATENCY_SPIKE_COUNTER = _Stub()

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import logical_agent-ft

# ─────────────────────────────────────────────────────────────────────
# harmony helpers
# ─────────────────────────────────────────────────────────────────────

def _short_hash(s: str, length: int = 6) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:length]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / denom

_MAJOR_THIRD = 0.5      # cos 60°
_MINOR_THIRD = 0.7071   # cos 45°
_PERF_FIFTH = 0.8660    # cos 30°
_HARM_TOL   = 0.04


def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    vs = [v for v in vecs if np.linalg.norm(v) > 1e-9][:3]
    if len(vs) < 3:
        return False
    sims = [_cos(vs[i], vs[j]) for i in range(3) for j in range(i + 1, 3)]
    return any(abs(s - t) < _HARM_TOL for s in sims for t in (_MAJOR_THIRD, _MINOR_THIRD, _PERF_FIFTH))

# ─────────────────────────────────────────────────────────────────────
class RecursiveAgentFT:  # pylint:disable=too-many-instance-attributes
    """Symbolic flow agent with gremlin chaos and harmony sensing."""

    # -----------------------------------------------------------------
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] | None = None,
        *,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.6.4",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5,
        verbose: bool = True,
        enable_gremlin_mode: bool | None = None,
        *,
        enable_harmony: bool = True,
    ) -> None:
        if not 1 <= max_depth <= 5:
            raise ValueError("max_depth must be between 1 and 5")

        gremlin_lvl = int(os.getenv("NOOR_GREMLIN", "0"))
        if enable_gremlin_mode is None:
            enable_gremlin_mode = gremlin_lvl > 0
        self.gremlin_level = gremlin_lvl  # 0‑3

        # public attrs -------------------------------------------------
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
        self.enable_gremlin_mode = enable_gremlin_mode
        self.enable_harmony = enable_harmony

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers or []
        self.time_step = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._dyad_path_tracker: Dict[str, int] = defaultdict(int)

        # rebound helpers
        self._last_latency_spike: Optional[int] = None
        self._saved_depth: Optional[int] = None

        # harmonic drought
        self._harm_hit_window: deque[int] = deque(maxlen=100)

        self._enforce_agent_boundary()

    # -----------------------------------------------------------------
    # depth & threshold helpers
    # -----------------------------------------------------------------
    def _depth_jitter_prob(self) -> float:
        return [0.1, 0.15, 0.25, 0.35][min(self.gremlin_level, 3)]

    def adjust_max_depth(self, richness: float, watcher_var: float):
        old = self.max_depth
        if richness > 0.7:
            self.max_depth = min(5, self.max_depth + 1)
        elif richness < 0.3:
            self.max_depth = max(2, self.max_depth - 1)
        if watcher_var > 0.25:
            self.max_depth = min(5, self.max_depth + 1)
        if 0.4 < richness < 0.6 and random.random() < self._depth_jitter_prob():
            self.max_depth = max(2, min(5, self.max_depth + random.choice([-1, 1])))
        if self.max_depth != old and self.verbose and self.traversal_memory:
            self.traversal_memory[-1]["note"] = f"🌀 Depth shifts to {self.max_depth} in rich winds"
        DEPTH_GAUGE.set(self.max_depth)

    def adjust_promotion_thresholds(self, ctx: float):
        if self.gremlin_level >= 3:
            self.meta_promote_threshold = 1 if ctx < 0.5 else 2
            self.ghost_promote_threshold = 2 if ctx < 0.5 else 3
        else:
            self.meta_promote_threshold = 2 if ctx < 0.5 else 4
            self.ghost_promote_threshold = 4 if ctx < 0.5 else 6
        if self.verbose and self.traversal_memory:
            self.traversal_memory[-1]["thresholds"] = (
                f"meta={self.meta_promote_threshold}/ghost={self.ghost_promote_threshold}"
            )

    # ------------------------------------------------------------------
    # main cycle
    # ------------------------------------------------------------------
    def entangled_step(self) -> None:
        start_t = time.perf_counter()

        # ------------ gather context ---------------------------------
        fields = self._gather_watcher_fields()
        watcher_ctx = {w: w.get_dyad_context_ratio() for w in self.watchers}
        ctx_ratio = max(0.1, np.mean(list(watcher_ctx.values())) if watcher_ctx else 1.0)

        if self.time_step % 25 == 0:
            self.adjust_promotion_thresholds(ctx_ratio)

        richness_sigma = np.std(list(self.synergy_memory.values()) or [0.0])
        self.adjust_max_depth(0.7 * ctx_ratio + 0.3 * richness_sigma, np.std(list(watcher_ctx.values()) or [0.0]))
        self.core.update_context_ratio(ctx_ratio)

        # depth rebound after latency spikes --------------------------
        if self._last_latency_spike and (self.time_step - self._last_latency_spike) >= 20 and self._saved_depth:
            self.max_depth = self._saved_depth
            self._saved_depth = None
            if self.verbose and self.traversal_memory:
                self.traversal_memory[-1]["note"] = (self.traversal_memory[-1].get("note", "") +
                                                     f"|🌬️ Depth rebounds to {self.max_depth}")
            DEPTH_GAUGE.set(self.max_depth)

        # choose next state -------------------------------------------
        if not fields:
            chosen_state, synergy, path = self._fallback_step(), 0.0, []
        else:
            all_paths = self.generate_field_paths(fields, self.max_depth)
            best_synergy, best_state, best_path = -np.inf, None, None
            for p in all_paths:
                cand = self._build_state_from_path(p)
                score = self._score_candidate(cand, p, watcher_ctx, ctx_ratio)
                if score > best_synergy:
                    best_synergy, best_state, best_path = score, cand, p
            chosen_state, synergy, path = best_state, best_synergy, best_path or []
            self.core.futures = [self._build_state_from_path(p) for p in all_paths]

        # dyad penalty & cap -----------------------------------------
        dyad_penalty = self._compute_dyad_penalty(path, watcher_ctx, ctx_ratio)
        if self.core.gate_overlay == 0:
            dyad_penalty = (dyad_penalty + self.gate0_dyad_penalty) / 2.0
        synergy = min(synergy * dyad_penalty, 10.0)

        # alerts / events---------------------------------------------
        alert = "⚠️ dyad_dominance_detected" if dyad_penalty < 0.8 else None
        event = self._maybe_promote_meta_field(path)

        # ------------------------------------------------------------------
        # core step and watcher observe
        # ------------------------------------------------------------------
        self.core.step(chosen_state)
        self.time_step += 1
        for w in self.watchers:
            w.observe_state(chosen_state)

        # ---------------- harmonic drought tracker -------------------
        if path and _is_harmonic_triad([self._field_vector(f) for f in path]):
            self._harm_hit_window.append(1)
        else:
            self._harm_hit_window.append(0)
        if len(self._harm_hit_window) == self._harm_hit_window.maxlen and sum(self._harm_hit_window) == 0 and self.verbose:
            event = (event or "") + "|🎻 harmony_drought"

        sig = self.path_signature(path)
        self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + math.tanh(synergy)

        step_rec: Dict[str, Any] = {
            "time_step": self.time_step,
            "synergy": synergy,
            "dyad_penalty": dyad_penalty,
            "chosen_path": [f.get("index", -1) for f in path],
            "alert": alert,
            "event": event,
        }

        # FieldAnchor recovery ---------------------------------------
        if not self.core.is_active:
            restored = False
            if callable(getattr(self.core, "restore_from_anchor", None)):
                self.core.restore_from_anchor(); restored = True
            else:
                self.core.step(self._fallback_step())
            DRIFT_COUNTER.inc()
            step_rec["event"] = (step_rec.get("event") or "") + ("|FieldAnchor" if restored else "|anchor_fallback")
            step_rec["verse"] = "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"
            self.core.update_context_ratio(min(1.0, ctx_ratio + 0.05))
            gid = f"recovery_{_short_hash(str(self.time_step))}"
            for w in self.watchers:
                w.register_ghost_motif(gid, origin="recovery", strength=0.05)

        # latency / depth easing -------------------------------------
        latency = time.perf_counter() - start_t
        STEP_LATENCY_HIST.observe(latency)
        if latency > 0.1:
            step_rec["alert"] = (step_rec.get("alert") or "") + "|⚠️ latency_spike"
            if self._saved_depth is None:
                self._saved_depth = self.max_depth
            self.max_depth = max(2, self.max_depth - 1)
            self._last_latency_spike = self.time_step
            DEPTH_GAUGE.set(self.max_depth)
            step_rec["note"] = (step_rec.get("note", "") + "|📉 Depth eased for speed")

        self.traversal_memory.append(step_rec)

        # ghost decay sweeper every 200 steps ------------------------
        if self.time_step % 200 == 0:
            for w in self.watchers:
                unseen_cut = 100
                for gid, ginfo in list(w.ghost_motifs.items()):
                    if (w.generation - ginfo.get("last_seen", 0)) > unseen_cut:
                        ginfo["strength"] *= 0.99
                        if ginfo["strength"] < 1e-4:
                            w.ghost_motifs.pop(gid, None)

    # ------------------------------------------------------------------
    # building + scoring helpers (unchanged except harmonic section)
    # ------------------------------------------------------------------
    def _build_state_from_path(self, path_fields):
        state = self.core.current_state.copy()
        vecs_in_path = []
        for field in path_fields:
            env = self._get_environment_influence()
            curvature = field.get("curvature", 1.0)
            priority = self._clamp_priority(field.get("priority_weight", 1.0))
            weight = field["strength"] * (1 + curvature) * priority
            if field.get("dyad_flag") and not field.get("dyad_exempt"):
                weight *= 0.9
            vec = self._field_vector(field)
            vecs_in_path.append(vec)
            if np.linalg.norm(vec) < 1e-10:
                vec = np.random.normal(0, 0.01, self.state_dim); vec /= np.linalg.norm(vec) + 1e-10
            state += env * 0.05 + vec * weight
        # harmonic lift + ghost spawn
        if _is_harmonic_triad(vecs_in_path):
            state *= 1.10  # 10 % lift
            gid = f"harmonic_{_short_hash(self.path_signature(path_fields))}"
            for w in self.watchers:
                if gid not in w.ghost_motifs:
                    w.register_ghost_motif(gid, origin="harmonic_resonance", strength=0.1)
        return state

     def _score_candidate(self, cand, path_fields, watcher_ctx, default_ctx):
        synergy = self._ghost_core_feasibility(cand) + 1.0
        sig = self.path_signature(path_fields)
        synergy += math.tanh(self.synergy_memory.get(sig, 0.0)) if self.enable_synergy_normalization else 0.0
        if self.enable_internal_time_decay:
            decay = sum(f.get("internal_time", 0.0) for f in path_fields)
            synergy *= math.exp(-decay)
        dyad_penalty = self._compute_dyad_penalty(path_fields, watcher_ctx, default_ctx)
        synergy *= dyad_penalty
        synergy *= np.mean([self._clamp_priority(f.get("priority_weight", 1.0)) for f in path_fields])
        return synergy

    def _fallback_step(self) -> np.ndarray:
        """Fallback in case no valid fields are available."""
        fallback = np.random.normal(0, 0.05, self.state_dim)
        return fallback / (np.linalg.norm(fallback) + 1e-10)

    def _ghost_core_feasibility(self, state: np.ndarray) -> float:
        """Simple feasibility check for candidate states."""
        return float(np.linalg.norm(state))

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is None:
            return np.zeros(self.state_dim)
        return self.environment

    def _compute_dyad_penalty(self, path_fields, watcher_ctx, default_ctx) -> float:
        dyad_count = sum(1 for f in path_fields if f.get("dyad_flag"))
        total = len(path_fields)
        if not total:
            return 1.0
        dyad_ratio = dyad_count / total
        ctx_adjust = np.mean(list(watcher_ctx.values())) if watcher_ctx else default_ctx
        penalty = 1.0 - dyad_ratio * (0.5 + 0.5 * (1 - ctx_adjust))
        return max(0.5, penalty)

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        motifs = field.get("motifs", [])
        if not motifs:
            return np.zeros(self.state_dim)
        vectors = [np.random.normal(0, 0.01, self.state_dim) for _ in motifs]
        return sum(vectors) / len(vectors)

    def path_signature(self, fields: List[Dict[str, Any]]) -> str:
        ids = [str(f.get("index", id(f))) for f in fields]
        return _short_hash("|".join(ids))

    def _clamp_priority(self, priority: float) -> float:
        return max(0.5, min(1.5, float(priority)))

    def _enforce_agent_boundary(self):
        if self.state_dim < 1 or self.state_dim > 512:
            raise QuantumNoorException("Invalid state dimension.")

    # ------------------------------------------------------------------
    # FieldAnchor caching (explicit)
    # ------------------------------------------------------------------
    def cache_field_anchor(self) -> None:
        """Manually caches the current core state."""
        if hasattr(self.core, "save_field_anchor"):
            self.core.save_field_anchor()

    def restore_field_anchor(self) -> bool:
        """Restores the core state from FieldAnchor if available."""
        if hasattr(self.core, "restore_from_anchor"):
            self.core.restore_from_anchor()
            return True
        return False

# End of RecursiveAgentFT

