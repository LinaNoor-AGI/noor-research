"""
recursive_agent_ft.py  (v3.5.2)
------------------------------------------------------------
Flow-layer agent with dyad-aware scoring, vector dampening,
MetaField auto-promotion, harmonic gate coupling,
structured ghost ascent, and poetic gate-0 logging.
Compatible with logical_agent_at v2.6 and noor_fasttime_core v7.1.
"""

from __future__ import annotations

__version__ = "3.5.2"

import numpy as np
import hashlib
from copy import deepcopy
from collections import defaultdict
from typing import List, Optional, Dict, Any

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import LogicalAgentAT

def _short_hash(s: str, length: int = 4) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:length]

class RecursiveAgentFT:
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.5.2",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
        gate0_dyad_penalty: float = 0.95,
        meta_promote_threshold: int = 3,
        ghost_promote_threshold: int = 5
    ):
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

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.time_step = 0
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []
        self._dyad_path_tracker = defaultdict(int)

        self._enforce_agent_boundary()

    def entangled_step(self) -> None:
        fields = self._gather_watcher_fields()
        watcher_ctx = {w: w.get_dyad_context_ratio() for w in self.watchers}
        ctx_ratio = np.mean(list(watcher_ctx.values())) if watcher_ctx else 1.0
        ctx_ratio = max(0.1, ctx_ratio)
        self.core.update_context_ratio(ctx_ratio)

        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = self.generate_field_paths(fields, self.max_depth)
            best_synergy = -np.inf
            best_path, best_state = [], self._fallback_step()

            for path_fields in all_paths:
                candidate = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate, path_fields, watcher_ctx, ctx_ratio)
                if score > best_synergy:
                    best_synergy, best_path, best_state = score, path_fields, candidate

            self.core.futures = [self._build_state_from_path(p) for p in all_paths]
            synergy = best_synergy
            chosen_next_state = best_state
            chosen_path = best_path

        dyad_penalty = self._compute_dyad_penalty(chosen_path, watcher_ctx, ctx_ratio)
        if self.core.gate_overlay == 0:
            dyad_penalty = (dyad_penalty + self.gate0_dyad_penalty) / 2
        synergy *= dyad_penalty
        alert = "⚠️ dyad_dominance_detected" if dyad_penalty < 0.8 else None
        event = self._maybe_promote_meta_field(chosen_path)

        self.core.step(chosen_next_state)
        self.time_step += 1

        for w in self.watchers:
            w.observe_state(chosen_next_state)

        sig = self.path_signature(chosen_path)
        self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        step_record = {
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in chosen_path],
            "synergy": synergy,
            "dyad_penalty": dyad_penalty,
            "alert": alert,
            "event": event,
            "next_state": chosen_next_state
        }
        if self.core.gate_overlay == 0 and dyad_penalty < 1.0:
            step_record["gate0_verse"] = {
                "text": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا",
                "t": self.time_step
            }

        self.traversal_memory.append(step_record)

    def _maybe_promote_meta_field(self, chosen_path):
        dyads = [f for f in chosen_path if f.get("dyad_flag")]
        thirds = {m for f in chosen_path for m in f["motifs"] if f not in dyads}
        for d in dyads:
            key = f"{tuple(sorted(d['motifs']))}|{','.join(sorted(thirds))}"
            self._dyad_path_tracker[key] += 1
            count = self._dyad_path_tracker[key]

            if count == self.meta_promote_threshold:
                ids = [f["index"] for f in chosen_path]
                for w in self.watchers:
                    try:
                        w.register_meta_field(ids, meta_strength=0.9)
                    except Exception:
                        pass
                return "MetaField upgrade triggered"

            if count == self.ghost_promote_threshold:
                ghost_id = f"dyad_ghost_{_short_hash(key)}"
                for w in self.watchers:
                    try:
                        if ghost_id not in w.get_ghost_motifs():
                            w.register_ghost_motif(ghost_id, origin="dyad_auto_resonance")
                        w.promote_ghost_to_field(ghost_id)
                    except Exception:
                        pass
                return "Ghost motif auto-promoted"

        if len(self._dyad_path_tracker) > 1000:
            self._dyad_path_tracker = {
                k: v for k, v in sorted(
                    self._dyad_path_tracker.items(),
                    key=lambda x: -x[1]
                )[:100]
            }
        return None

    def get_dyad_resonance(self, min_count: int = 2) -> Dict[str, float]:
        return {
            k: np.log1p(v) for k, v in self._dyad_path_tracker.items()
            if v >= min_count
        }

    def get_promotion_config(self) -> Dict[str, int]:
        return {
            "meta_threshold": self.meta_promote_threshold,
            "ghost_threshold": self.ghost_promote_threshold
        }

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
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

            state += env * 0.05 + vec * weight
        return state

    def _score_candidate(self, candidate: np.ndarray, path_fields: List[Dict[str, Any]], watcher_ctx, default_ctx) -> float:
        synergy = self._ghost_core_feasibility(candidate) + 1.0
        sig = self.path_signature(path_fields)
        mem_val = self.synergy_memory.get(sig, 0.0)
        synergy += np.tanh(mem_val) if self.enable_synergy_normalization else mem_val * 0.01

        if self.enable_internal_time_decay:
            decay = sum(f.get("internal_time", 0.0) for f in path_fields)
            synergy *= np.exp(-decay)

        dyad_penalty = self._compute_dyad_penalty(path_fields, watcher_ctx, default_ctx)
        synergy *= dyad_penalty
        priority_avg = np.mean([self._clamp_priority(f.get("priority_weight", 1.0)) for f in path_fields])
        synergy *= priority_avg

        return synergy

    def _compute_dyad_penalty(self, path_fields, watcher_ctx, default_ctx) -> float:
        penalty = 1.0
        for f in path_fields:
            if f.get("dyad_flag") and not f.get("dyad_exempt"):
                ctx = watcher_ctx.get(f["watcher"], default_ctx)
                penalty *= 1.0 - 0.2 / (1 + np.exp(5 * (ctx - 0.5)))
        return penalty

    def _fallback_step(self) -> np.ndarray:
        return self.core.current_state + np.random.normal(0, 0.05, self.state_dim)

    def _clamp_priority(self, value: float) -> float:
        return max(0.0, min(value, 5.0))

    # Placeholder stubs
    def _gather_watcher_fields(self):
        return []

    def generate_field_paths(self, fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
        all_paths = []
        frontier = [[f] for f in fields]
        for _ in range(max_depth - 1):
            new_frontier = []
            for path in frontier:
                for f in fields:
                    new_frontier.append(path + [f])
            frontier = new_frontier
        all_paths.extend(frontier)
        return all_paths

    def path_signature(self, path_fields: List[Dict[str, Any]]) -> str:
        return "-".join(str(f["index"]) for f in path_fields)

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_alive() else 0.0

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field["watcher"]
        vecs = [w.motif_embeddings[m] for m in field["motifs"] if m in w.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(self.state_dim)

    def _enforce_agent_boundary(self):
        for forbidden in ["propagate_signal", "register_motif_entanglement"]:
            if hasattr(self, forbidden):
                raise QuantumNoorException(f"Agent boundary violation: {forbidden}")
