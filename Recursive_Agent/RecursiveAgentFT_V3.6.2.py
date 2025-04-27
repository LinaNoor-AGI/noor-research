"""
recursive_agent_ft.py  (v3.6.2)
------------------------------------------------------------
Flow‑layer agent with depth‑breathing chaos, harmonic synergy, adaptive
thresholds, FieldAnchor poetry, dynamic path capping and full Prometheus
observability.
Compatible with NoorFastTimeCore ≥ 7.2 • LogicalAgentAT ≥ 2.7.
"""

from __future__ import annotations

__version__ = "3.6.2"

import math, time, hashlib, random
from copy import deepcopy
from collections import defaultdict
from typing import List, Optional, Dict, Any

import numpy as np

# Prometheus ---------------------------------------------------------------
try:
    from prometheus_client import Histogram, Gauge, Counter  # type: ignore

    STEP_LATENCY_HIST = Histogram(
        "recursive_agent_step_latency_seconds", "entangled_step latency",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
    )
    DEPTH_GAUGE = Gauge("recursive_agent_recursion_depth", "Current max_depth")
    DRIFT_COUNTER = Counter("recursive_agent_drift_total", "FieldAnchor / fallback recoveries")
except Exception:  # pragma: no cover
    class _Stub:  # pylint:disable=too-few-public-methods
        def __getattr__(self, _):
            return lambda *a, **k: None

    STEP_LATENCY_HIST = DEPTH_GAUGE = DRIFT_COUNTER = _Stub()

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import LogicalAgentAT

# ------------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------------

def _short_hash(s: str, length: int = 6) -> str:
    return hashlib.sha1(s.encode("utf-8", "replace")).hexdigest()[:length]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.flatten(), b.flatten()
    dot = float(np.dot(a, b))
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / denom

_MAJOR_THIRD = 0.5  # cos 60°
_MINOR_THIRD = 0.70710678  # cos 45°
_PERF_FIFTH = 0.8660254  # cos 30°
_HARM_TOL = 0.04


def _is_harmonic_triad(vecs: List[np.ndarray]) -> bool:
    # take first three distinct non‑zero vectors
    vs = [v for v in vecs if np.linalg.norm(v) > 1e-9][:3]
    if len(vs) < 3:
        return False
    sims = [_cos(vs[i], vs[j]) for i in range(3) for j in range(i + 1, 3)]
    for s in sims:
        if any(abs(s - t) < _HARM_TOL for t in (_MAJOR_THIRD, _MINOR_THIRD, _PERF_FIFTH)):
            return True
    return False

# ------------------------------------------------------------------------
# class
# ------------------------------------------------------------------------


class RecursiveAgentFT:
    """Symbolic flow agent with chaos‑aware depth, harmony sensing and recovery."""

    # ----------------------------- init ---------------------------------
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        *,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.6.2",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5,
        verbose: bool = True,
        enable_gremlin_mode: bool = False,
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
        self.enable_gremlin_mode = enable_gremlin_mode

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.time_step: int = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._dyad_path_tracker: Dict[str, int] = defaultdict(int)

        self._enforce_agent_boundary()

    # ------------------------------------------------------------------
    # depth breathing helpers
    # ------------------------------------------------------------------
    def adjust_max_depth(self, richness: float, watcher_var: float) -> None:
        old = self.max_depth
        if richness > 0.7:
            self.max_depth = min(5, self.max_depth + 1)
        elif richness < 0.3:
            self.max_depth = max(2, self.max_depth - 1)
        if watcher_var > 0.25:
            self.max_depth = min(5, self.max_depth + 1)
        # chaotic jitter
        jitter_p = 0.2 if self.enable_gremlin_mode else 0.1
        if 0.4 < richness < 0.6 and np.random.rand() < jitter_p:
            self.max_depth = max(2, min(5, self.max_depth + np.random.choice([-1, 1])))
        if self.max_depth != old and self.verbose and self.traversal_memory:
            self.traversal_memory[-1]["note"] = f"🌀 Depth shifts to {self.max_depth} in rich winds"
        DEPTH_GAUGE.set(self.max_depth)

    # ------------------------------------------------------------------
    def adjust_promotion_thresholds(self, ctx: float) -> None:
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

        # gather context -------------------------------------------------
        fields = self._gather_watcher_fields()
        watcher_ctx = {
            w: w.get_dyad_context_ratio() for w in self.watchers if hasattr(w, "get_dyad_context_ratio")
        }
        ctx_ratio = max(0.1, np.mean(list(watcher_ctx.values())) if watcher_ctx else 1.0)

        if self.time_step % 25 == 0:
            self.adjust_promotion_thresholds(ctx_ratio)

        richness_sigma = np.std(list(self.synergy_memory.values()) or [0.0])
        self.adjust_max_depth(0.7 * ctx_ratio + 0.3 * richness_sigma, np.std(list(watcher_ctx.values()) or [0.0]))

        self.core.update_context_ratio(ctx_ratio)

        # choose next state ---------------------------------------------
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = self.generate_field_paths(fields, self.max_depth)
            best_synergy, best_path, best_state = -np.inf, [], self._fallback_step()
            for p in all_paths:
                cand = self._build_state_from_path(p)
                score = self._score_candidate(cand, p, watcher_ctx, ctx_ratio)
                if score > best_synergy:
                    best_synergy, best_path, best_state = score, p, cand
            self.core.futures = [self._build_state_from_path(p) for p in all_paths]
            synergy, chosen_path, chosen_next_state = best_synergy, best_path, best_state

        # dyad penalty & cap -------------------------------------------
        dyad_penalty = self._compute_dyad_penalty(chosen_path, watcher_ctx, ctx_ratio)
        if self.core.gate_overlay == 0:
            dyad_penalty = (dyad_penalty + self.gate0_dyad_penalty) / 2.0
        synergy *= dyad_penalty
        synergy = min(synergy, 10.0)

        alert = "⚠️ dyad_dominance_detected" if dyad_penalty < 0.8 else None
        event = self._maybe_promote_meta_field(chosen_path)

        # core step ------------------------------------------------------
        self.core.step(chosen_next_state)
        self.time_step += 1
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        sig = self.path_signature(chosen_path)
        self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + math.tanh(synergy)

        step_rec: Dict[str, Any] = {
            "time_step": self.time_step,
            "chosen_path": [f.get("index", -1) for f in chosen_path],
            "synergy": synergy,
            "dyad_penalty": dyad_penalty,
            "alert": alert,
            "event": event,
            "next_state": chosen_next_state,
        }

        # FieldAnchor recovery -----------------------------------------
        if not self.core.is_active:
            restored = False
            if callable(getattr(self.core, "restore_from_anchor", None)):
                self.core.restore_from_anchor(); restored = True
            else:
                self.core.step(self._fallback_step())
            DRIFT_COUNTER.inc()
            step_rec["event"] = (step_rec.get("event") or "") + (
                "|FieldAnchor" if restored else "|anchor_fallback"
            )
            step_rec["verse"] = "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"
            self.core.update_context_ratio(min(1.0, ctx_ratio + 0.05))
            # recovery ghost
            gid = f"recovery_{_short_hash(str(self.time_step))}"
            for w in self.watchers:
                w.register_ghost_motif(gid, origin="recovery", strength=0.05)

        # latency check -----------------------------------------------
        latency = time.perf_counter() - start_t
        STEP_LATENCY_HIST.observe(latency)
        if latency > 0.1:
            step_rec["alert"] = (step_rec.get("alert") or "") + "|⚠️ latency_spike"
            self.max_depth = max(2, self.max_depth - 1)
            DEPTH_GAUGE.set(self.max_depth)
            step_rec["note"] = (step_rec.get("note") or "") + "|📉 Depth eased for speed"

        self.traversal_memory.append(step_rec)

    # ------------------------------------------------------------------
    # scoring helpers
    # ------------------------------------------------------------------
    def _score_candidate(self, cand: np.ndarray, path, watcher_ctx, default_ctx) -> float:
        synergy = self._ghost_core_feasibility(cand) + 1.0
        sig = self
