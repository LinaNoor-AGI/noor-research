# recursive_agent-ft.py (v3.1)
# By Lina Noor & Uncle (2025)
#
# RecursiveAgentFT v3.1:
#  - Incorporates watchers' contradiction + verse weighting
#  - Uses a ghost core for ephemeral checks
#  - Maintains synergy memory for repeated path preference
#  - Optional alignment drift logic via watchers
#

import numpy as np
from copy import deepcopy
from typing import List, Optional, Dict, Any

from noor_fasttime_core_v6_1 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v2_2 import LogicalAgentAT

########################################################
# Utility: path signature for synergy memory
########################################################

def path_signature(path: List[int]) -> str:
    """
    A simple textual signature for a chosen path (list of field indices).
    Could be expanded to incorporate watchers' substruct or motif details.
    """
    return "-".join(str(i) for i in path)

class RecursiveAgentFT:
    """
    RecursiveAgentFT v3.1:
      - Enhances v3.0 by:
        1) using ghost copies of the core for ephemeral synergy checks
        2) referencing watchers for contradiction logs + verse seeds
        3) storing synergy memory for repeated path preference
        4) (optional) alignment drift detection from watchers

      The core logic remains partial BFS / path expansions over watchers' fields.
      synergy = ghost_core_feasibility + watchers resonance - contradiction penalty + verse bonus + memory feedback.
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.1",
        max_depth: int = 2,
        enable_contradiction_penalty: bool = True,
        enable_verse_bonus: bool = True,
        enable_drift_correction: bool = False
    ):
        """
        :param initial_state: starting array
        :param watchers: watchers array
        :param environment: optional environment data
        :param state_dim: dimension of the state
        :param name: agent name
        :param max_depth: how deep BFS paths can go
        :param enable_contradiction_penalty: subtract synergy if fields are known to conflict
        :param enable_verse_bonus: add synergy if fields are seeded with verse
        :param enable_drift_correction: optionally read watchers' alignment drift
        """
        self.version = "3.1"
        self.name = name
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.watchers = watchers if watchers else []

        # toggles
        self.enable_contradiction_penalty = enable_contradiction_penalty
        self.enable_verse_bonus = enable_verse_bonus
        self.enable_drift_correction = enable_drift_correction

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.time_step = 0
        self._last_future = initial_state.copy()
        self.traversal_memory: List[Dict[str, Any]] = []

        # synergy memory to track repeated path success
        self.synergy_memory: Dict[str, float] = {}

    ##################################################
    # Public run methods
    ##################################################

    def entangled_step(self):
        """
        1) gather watchers' fields + data (contradictions, verse info, synergy memory)
        2) partial BFS or path expansions
        3) ephemeral synergy check with ghost core
        4) pick best path => next state
        5) step real core
        6) watchers observe
        7) store logs, synergy memory
        """
        fields = self._gather_watcher_fields()
        # fallback if no fields
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = self._generate_field_paths(fields, self.max_depth)
            best_synergy = -999999.0
            best_path = None
            best_state = self._fallback_step()

            # watchers might have contradiction logs, verse info, alignment drift
            watchers_data = self._collect_watchers_data()

            for path_fields in all_paths:
                candidate = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate, path_fields, watchers_data)
                if score > best_synergy:
                    best_synergy = score
                    best_path = path_fields
                    best_state = candidate

            chosen_next_state = best_state
            synergy = best_synergy
            path_indices = [f["index"] for f in best_path] if best_path else []

        # step real core
        self.core.step(chosen_next_state)
        self._last_future = chosen_next_state
        self.time_step += 1

        # watchers observe
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        # synergy memory update
        if best_path is not None:
            sig = path_signature([f["index"] for f in best_path])
            self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        # store in traversal_memory
        record = {
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in best_path] if best_path else [],
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

    ##################################################
    # 1) Build + Score + Choose
    ##################################################

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.watchers:
            if hasattr(w, "entanglement_fields"):
                for i, field in enumerate(w.entanglement_fields):
                    # store index for usage
                    fcopy = dict(field)
                    fcopy["index"] = i
                    fcopy["watcher"] = w
                    results.append(fcopy)
        return results

    def _generate_field_paths(self, fields: List[Dict[str, Any]], depth: int) -> List[List[Dict[str, Any]]]:
        # BFS or partial expansions
        # For simplicity, we do a small BFS that picks up to depth layers
        # Real logic might be domain-specific.

        if depth <= 1:
            return [[f] for f in fields]

        frontier = [[f] for f in fields]
        for _ in range(depth - 1):
            new_frontier = []
            for path in frontier:
                for f in fields:
                    new_frontier.append(path + [f])
            frontier = new_frontier
        return frontier

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for field in path_fields:
            # environment influence each field
            env_vec = self._get_environment_influence()
            state += env_vec * 0.05

            # add field vector
            field_vec = self._field_vector(field)
            curvature = field.get("curvature", 1.0)
            # if not provided, compute from watcher
            if curvature == 1.0 and hasattr(field["watcher"], "compute_entanglement_curvature"):
                curvature = field["watcher"].compute_entanglement_curvature(field["index"])

            weight = field["strength"] * (1.0 + curvature)
            state += weight * field_vec

            # substructures
            for key, submotifs in field.get("substructures", {}).items():
                sub_vec = self._substructure_vector(submotifs, field["watcher"])
                state += 0.5 * weight * sub_vec
        return state

    def _score_candidate(
        self,
        candidate: np.ndarray,
        path_fields: List[Dict[str, Any]],
        watchers_data: Dict[str, Any]
    ) -> float:
        synergy = 0.0

        # 1) ephemeral check with ghost core
        synergy += self._ghost_core_feasibility(candidate)

        # 2) watchers resonance (naive approach: multiply factor)
        resonance_factor = 1.0
        # optional drift correction
        if self.enable_drift_correction:
            if watchers_data.get("alignment_drift", False):
                # say we do a small synergy boost
                resonance_factor *= 1.1
        synergy += resonance_factor

        # 3) contradiction penalty
        if self.enable_contradiction_penalty:
            # for each pair in path, see if watchers have contradiction recurrence
            penalty = 0.0
            contradiction_map = watchers_data.get("contradiction_map", {})
            # naive approach: sum penalty for each pair in path
            # we can do pairwise or simply add penalty if any field is in repeated contradiction
            path_idxs = [f["index"] for f in path_fields]
            # for each pair i < j, check map
            for i in range(len(path_idxs) - 1):
                for j in range(i+1, len(path_idxs)):
                    pair = tuple(sorted((path_idxs[i], path_idxs[j])))
                    penalty += contradiction_map.get(pair, 0) * 0.1  # each recurrence = 0.1 penalty
            synergy -= penalty

        # 4) verse bonus
        if self.enable_verse_bonus:
            verse_bonus_total = 0.0
            # watchers might store verse seeds in field
            for f in path_fields:
                # if watchers store e.g. f['verse_seed'] or something
                # we can do: verse_bonus_total += f.get('verse_seed', 0.0)
                pass
            synergy += verse_bonus_total

        # 5) synergy memory
        sig = path_signature([f["index"] for f in path_fields])
        synergy += self.synergy_memory.get(sig, 0.0) * 0.01  # small factor

        return synergy

    ##################################################
    # 2) Ghost Core for ephemeral feasibility
    ##################################################

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_alive() else 0.0

    ##################################################
    # 3) Gather watchers data: contradiction recurrences, alignment drift
    ##################################################

    def _collect_watchers_data(self) -> Dict[str, Any]:
        """
        Aggregates watchers' contradiction logs, verse seeds, alignment drift flags, etc.
        """
        data = {}
        # build a combined contradiction_map if multiple watchers
        combined_map = {}
        alignment_drift_flag = False
        for w in self.watchers:
            # check if w has analyze_contradiction_recurrence
            if hasattr(w, 'analyze_contradiction_recurrence'):
                c_map = w.analyze_contradiction_recurrence()
                for k, v in c_map.items():
                    combined_map[k] = combined_map.get(k, 0) + v

            # check alignment drift if watchers track it
            if self.enable_drift_correction and hasattr(w, 'detect_alignment_drift'):
                # hypothetical method
                if w.detect_alignment_drift():
                    alignment_drift_flag = True

        data["contradiction_map"] = combined_map
        data["alignment_drift"] = alignment_drift_flag
        return data

    ##################################################
    # 4) Helpers
    ##################################################

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

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
        return np.mean(sub_vecs, axis=0) if sub_vecs else np.zeros(self.state_dim)

    def _fallback_step(self) -> np.ndarray:
        noise = np.random.normal(0, 0.05, self.state_dim)
        return self.core.current_state + noise

    ##################################################
    # 5) API
    ##################################################

    def is_alive(self) -> bool:
        return self.core.is_alive()

    def __repr__(self) -> str:
        return (f"<RecursiveAgentFT v3.1 name={self.name}, "
                f"time_step={self.time_step}, "
                f"alive={self.is_alive()}, "
                f"synergy_memory={len(self.synergy_memory)}>")
