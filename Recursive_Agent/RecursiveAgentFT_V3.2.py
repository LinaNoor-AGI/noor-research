# recursive_agent-ft.py (v3_2)
# By Lina Noor & Uncle (2025)
#
# RecursiveAgentFT v3.2:
#   - Switch synergy memory scaling to np.tanh
#   - Apply internal time decay factor for fields with 'internal_time'
#   - Keep all toggles optional so we don’t break existing usage.
#
import numpy as np
from copy import deepcopy
from typing import List, Optional, Dict, Any

from noor_fasttime_core_v6_1 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v2_3 import LogicalAgentAT

########################################################
# Path signature for synergy memory
########################################################

def path_signature(path_fields: List[Dict[str, Any]]) -> str:
    """
    A textual signature for a path, based on field indices.
    """
    idxs = [f["index"] for f in path_fields]
    return "-".join(str(i) for i in idxs)

########################################################
# BFS logic (unchanged from v3.1)
########################################################

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

class RecursiveAgentFT:
    """
    RecursiveAgentFT v3.2:
      - Inherits from v3.1, adding:
        1) synergy memory scaled by np.tanh
        2) optional internal time decay factor
      - Toggles: enable_synergy_normalization, enable_internal_time_decay
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.2",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True
    ):
        """
        :param initial_state: starting array
        :param watchers: watchers array
        :param environment: optional environment data
        :param state_dim: dimension of the state
        :param name: agent name
        :param max_depth: BFS depth
        :param enable_synergy_normalization: if True, use np.tanh for synergy memory
        :param enable_internal_time_decay: if True, apply exp(-internal_time_sum)
        """
        self.version = "3.2"
        self.name = name
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []

        self.time_step = 0
        self._last_future = initial_state.copy()

        self.traversal_memory: List[Dict[str, Any]] = []
        # synergy memory from v3.1
        self.synergy_memory: Dict[str, float] = {}

        self._enforce_agent_boundary()

    def entangled_step(self):
        fields = self._gather_watcher_fields()
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = generate_field_paths(fields, self.max_depth)
            best_synergy = -999999.0
            best_path = None
            best_state = self._fallback_step()

            watchers_data = self._collect_watchers_data()

            for path_fields in all_paths:
                candidate = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate, path_fields, watchers_data)
                if score > best_synergy:
                    best_synergy = score
                    best_path = path_fields
                    best_state = candidate

            synergy = best_synergy
            chosen_path = best_path if best_path else []
            chosen_next_state = best_state

        self.core.step(chosen_next_state)
        self._last_future = chosen_next_state
        self.time_step += 1

        for w in self.watchers:
            w.observe_state(chosen_next_state)

        if chosen_path is not None:
            sig = path_signature(chosen_path)
            # increment synergy memory
            self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        # store log
        record = {
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in chosen_path],
            "synergy": synergy,
            "next_state": chosen_next_state
        }
        self.traversal_memory.append(record)

    def step(self):
        self.entangled_step()

    def run_for(self, steps: int):
        for _ in range(steps):
            self.entangled_step()
            if not self.core.is_alive():
                print(f"[{self.name}] Core feasibility lost at t={self.time_step}.")
                break

    ######################################################
    # BFS Field Gathering & State Construction
    ######################################################

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.watchers:
            if hasattr(w, "entanglement_fields"):
                for i, field in enumerate(w.entanglement_fields):
                    # assume watchers can do compute_entanglement_curvature
                    c = w.compute_entanglement_curvature(i)
                    fcopy = dict(field)
                    fcopy["index"] = i
                    fcopy["curvature"] = c
                    fcopy["watcher"] = w
                    results.append(fcopy)
        return results

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for f in path_fields:
            env_vec = self._get_environment_influence()
            state += env_vec * 0.05

            # normal weighting by strength + curvature
            weight = f["strength"] * (1.0 + f["curvature"])
            state += weight * self._field_vector(f)

            # substructures
            for key, submotifs in f.get("substructures", {}).items():
                sub_vec = self._substructure_vector(submotifs, f["watcher"])
                state += 0.5 * weight * sub_vec
        return state

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field["watcher"]
        motif_vecs = []
        for m in field["motifs"]:
            if m in w.motif_embeddings:
                motif_vecs.append(w.motif_embeddings[m])
        if not motif_vecs:
            return np.zeros(self.state_dim)
        return np.mean(motif_vecs, axis=0)

    def _substructure_vector(self, submotifs: List[str], watcher: LogicalAgentAT) -> np.ndarray:
        sub_vecs = []
        for sm in submotifs:
            if sm in watcher.motif_embeddings:
                sub_vecs.append(watcher.motif_embeddings[sm])
        if sub_vecs:
            return np.mean(sub_vecs, axis=0)
        else:
            return np.zeros(self.state_dim)

    ######################################################
    # Candidate Scoring (Ephemeral synergy check etc.)
    ######################################################

    def _score_candidate(
        self,
        candidate: np.ndarray,
        path_fields: List[Dict[str, Any]],
        watchers_data: Dict[str, Any]
    ) -> float:
        synergy = self._ghost_core_feasibility(candidate)

        # watchers resonance factor (placeholder from v3.0)
        watchers_resonance = 1.0
        synergy += watchers_resonance

        # synergy memory scaling
        sig = path_signature(path_fields)
        prev_val = self.synergy_memory.get(sig, 0.0)
        if self.enable_synergy_normalization:
            synergy += float(np.tanh(prev_val))
        else:
            synergy += prev_val * 0.01

        # internal time decay
        if self.enable_internal_time_decay:
            time_penalty = 0.0
            for f in path_fields:
                # watchers may store 'internal_time' in the field or we fetch from get_field_expanded_data
                # if so, let's do a direct approach:
                itime = f.get("internal_time", 0.0)
                # or ask watchers: w.get_field_expanded_data(i)["internal_time"]
                time_penalty += itime
            synergy *= np.exp(-time_penalty)

        return synergy

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_alive() else 0.0

    ######################################################
    # Collect watchers data if needed
    ######################################################

    def _collect_watchers_data(self) -> Dict[str, Any]:
        # If watchers have further advanced data, we’d unify them here.
        return {}

    ######################################################
    # Utility & Boundaries
    ######################################################

    def _fallback_step(self) -> np.ndarray:
        noise = np.random.normal(0, 0.05, self.state_dim)
        return self.core.current_state + noise

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def _enforce_agent_boundary(self):
        forbidden = ["propagate_signal", "register_motif_entanglement"]
        for method in forbidden:
            if hasattr(self, method):
                raise QuantumNoorException(
                    f"Agent boundary violation: {method}"
                )

    def is_alive(self) -> bool:
        return self.core.is_alive()

    def __repr__(self) -> str:
        return (
            f"<RecursiveAgentFT v3.2 name={self.name}, time_step={self.time_step}, "
            f"alive={self.is_alive()}, synergy_memory={len(self.synergy_memory)}>")
