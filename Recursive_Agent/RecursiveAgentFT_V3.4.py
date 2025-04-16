# recursive_agent_ft.py (v3.4)
# By Lina Noor & Uncle (2025)
#
# This version builds on v3.3 by:
#   - Projecting futures to NoorFastTimeCore before stepping
#   - Ensuring OR_condition(futures) activates correctly
#   - No structural changes to BFS or synergy memory

import numpy as np
from copy import deepcopy
from typing import List, Optional, Dict, Any

from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException
from logical_agent import LogicalAgentAT

__version__ = "3.4.0"

# --- BFS Helper Functions ---

def generate_field_paths(fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
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

def path_signature(path_fields: List[Dict[str, Any]]) -> str:
    return "-".join(str(f["index"]) for f in path_fields)

# --- RecursiveAgentFT ---

class RecursiveAgentFT:
    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.4",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True
    ):
        self.version = __version__
        self.name = name
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay

        if not (1 <= max_depth <= 5):
            raise ValueError("max_depth must be between 1 and 5")

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.time_step = 0
        self._last_future = initial_state.copy()
        self.synergy_memory: Dict[str, float] = {}
        self.traversal_memory: List[Dict[str, Any]] = []

        self._enforce_agent_boundary()

    def entangled_step(self) -> None:
        fields = self._gather_watcher_fields()
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = generate_field_paths(fields, self.max_depth)
            best_synergy = -999999.0
            best_path = None
            best_state = self._fallback_step()
            for path_fields in all_paths:
                candidate = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate, path_fields)
                if score > best_synergy:
                    best_synergy = score
                    best_path = path_fields
                    best_state = candidate

            # 🔁 Inserted in v3.4: send all futures to core
            futures = [self._build_state_from_path(path) for path in all_paths]
            self.core.futures = futures

            synergy = best_synergy
            chosen_path = best_path if best_path else []
            chosen_next_state = best_state

        self.core.step(chosen_next_state)
        self._last_future = chosen_next_state
        self.time_step += 1

        for w in self.watchers:
            w.observe_state(chosen_next_state)

        if chosen_path:
            sig = path_signature(chosen_path)
            self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        self.traversal_memory.append({
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in chosen_path],
            "synergy": synergy,
            "next_state": chosen_next_state
        })

    def run_for(self, steps: int) -> None:
        for _ in range(steps):
            self.entangled_step()
            if not self.core.is_alive():
                print(f"[{self.name}] Core failed feasibility at t={self.time_step}")
                break

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.watchers:
            for i, f in enumerate(w.entanglement_fields):
                fcopy = dict(f)
                fcopy["index"] = i
                fcopy["watcher"] = w
                results.append(fcopy)
        return results

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for field in path_fields:
            env = self._get_environment_influence()
            curvature = field.get("curvature", 1.0)
            weight = field["strength"] * (1 + curvature)
            vec = self._field_vector(field)
            state += env * 0.05 + vec * weight

            for _, subs in field.get("substructures", {}).items():
                subv = self._substructure_vector(subs, field["watcher"])
                state += 0.5 * weight * subv
        return state

    def _score_candidate(self, candidate: np.ndarray, path_fields: List[Dict[str, Any]]) -> float:
        synergy = self._ghost_core_feasibility(candidate)
        synergy += 1.0  # watcher resonance
        sig = path_signature(path_fields)
        val = self.synergy_memory.get(sig, 0.0)
        synergy += np.tanh(val) if self.enable_synergy_normalization else val * 0.01
        if self.enable_internal_time_decay:
            decay = sum(f.get("internal_time", 0.0) for f in path_fields)
            synergy *= np.exp(-decay)
        return synergy

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

    def _substructure_vector(self, motifs: List[str], watcher: LogicalAgentAT) -> np.ndarray:
        vecs = [watcher.motif_embeddings[m] for m in motifs if m in watcher.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(self.state_dim)

    def _fallback_step(self) -> np.ndarray:
        return self.core.current_state + np.random.normal(0, 0.05, self.state_dim)

    def _enforce_agent_boundary(self):
        for forbidden in ["propagate_signal", "register_motif_entanglement"]:
            if hasattr(self, forbidden):
                raise QuantumNoorException(f"Agent boundary violation: {forbidden}")

    def is_alive(self) -> bool:
        return self.core.is_alive()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "time_step": self.time_step,
            "synergy_memory": dict(self.synergy_memory),
            "core_state": self.core.current_state.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecursiveAgentFT":
        agent = cls(initial_state=np.array(data.get("core_state", [0, 0])))
        agent.version = data.get("version", "3.4.0")
        agent.time_step = data.get("time_step", 0)
        agent.synergy_memory = data.get("synergy_memory", {})
        return agent

    def __repr__(self):
        return (f"<RecursiveAgentFT v{self.version} name={self.name}, "
                f"time_step={self.time_step}, alive={self.is_alive()}, "
                f"synergy_memory={len(self.synergy_memory)}>" )
