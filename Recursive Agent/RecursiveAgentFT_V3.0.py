# recursive_agent-ft.py (v3.0)
# Comprehensive Upgraded Implementation
# By Lina Noor & Uncle (2025)
#
# This version integrates ephemeral synergy checks, environment weighting,
# partial BFS logic over watchers' entanglement fields, nested substructures,
# and advanced triadic feasibility alignment with NoorFastTimeCore v5.3.
# It's no longer a reference scaffold—it’s a domain-aligned entangled walker.

import numpy as np
import itertools
from typing import List, Dict, Optional, Any

# Adjust imports to your local filenames/paths
from noor_fasttime_core_v5_3 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v2_0 import LogicalAgentAT

###############################################################
# Helper BFS / Partial Permutation logic for fields
###############################################################
def generate_field_paths(
    fields: List[Dict[str, Any]],
    max_depth: int = 2
) -> List[List[Dict[str, Any]]]:
    """
    A partial BFS that builds small paths from the available fields.
    Each path is a list of field dicts in a chosen sequence.
    :param fields: list of field dicts (each has curvature, strength, etc.)
    :param max_depth: how many fields to chain in a path.
    """
    # We do a BFS up to depth = max_depth
    # You can adapt for more advanced constraints.

    all_paths = []
    frontier = [[f] for f in fields]  # start each path with 1 field

    for _ in range(max_depth - 1):
        new_frontier = []
        for path in frontier:
            # For simplicity, we allow reusing the same fields multiple times,
            # but you might want to exclude already-used fields.
            for f in fields:
                new_frontier.append(path + [f])
        frontier = new_frontier

    # Combine single-field and multi-field paths
    # If you also want single-step paths only, that’s already in frontier.
    all_paths.extend(frontier)

    return all_paths


class RecursiveAgentFT:
    """
    RecursiveAgentFT v3 (Final Form)
    - Implements ephemeral synergy checks with the core.
    - Integrates environment weighting.
    - Uses BFS-based partial path expansions over watchers' entanglement fields.
    - Accumulates substructure vectors.
    - Picks the best path via synergy scoring.
    - Steps the core with the resulting final state.
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3_final",
        max_depth: int = 2
    ):
        """
        :param initial_state: starting array
        :param watchers: watchers array
        :param environment: optional environment data
        :param state_dim: dimension of the state
        :param name: agent name
        :param max_depth: how deep BFS paths can go
        """
        self.version = "3.0-final"
        self.name = name
        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []

        self.time_step = 0
        self._last_future = initial_state.copy()

        # For logging expansions
        self.traversal_memory: List[Dict[str, Any]] = []

        self._enforce_agent_boundary()

    ############################################
    # Public: The main method to step
    ############################################

    def entangled_step(self):
        """
        1) gather fields from watchers
        2) build BFS partial permutations (paths)
        3) ephemeral synergy check each path
        4) pick best path => final state => step core
        """
        fields = self._gather_watcher_fields()

        # fallback if no fields
        if not fields:
            next_state = self._fallback_step()
            synergy = 0.0
            chosen_path = []
        else:
            # build BFS expansions up to max_depth
            all_paths = generate_field_paths(fields, max_depth=self.max_depth)
            # ephemeral check synergy for each path
            best_synergy = -999999.0
            best_path = None
            best_state = self._fallback_step()

            for path in all_paths:
                candidate_state = self._build_state_from_path(path)
                score = self._ephemeral_synergy_check(candidate_state)
                if score > best_synergy:
                    best_synergy = score
                    best_path = path
                    best_state = candidate_state

            synergy = best_synergy
            chosen_path = best_path if best_path else []
            next_state = best_state

        # Step the core with best state
        self.core.step(next_state)
        self.time_step += 1
        self._last_future = next_state

        # watchers observe
        for w in self.watchers:
            if hasattr(w, "observe_state"):
                w.observe_state(next_state)

        # log it
        self.traversal_memory.append({
            "time_step": self.time_step,
            "chosen_path": [p["motifs"] for p in chosen_path],
            "synergy": synergy,
            "next_state": next_state
        })

    def step(self):
        """
        Backward-compat alias to entangled_step
        """
        self.entangled_step()

    def run_for(self, steps: int):
        for _ in range(steps):
            self.entangled_step()
            if not self.core.is_alive():
                print(f"[{self.name}] Core feasibility lost at t={self.time_step}.")
                break

    ############################################
    # 1) BFS Field Gathering & State Building
    ############################################

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.watchers:
            if hasattr(w, "entanglement_fields"):
                for i, field in enumerate(w.entanglement_fields):
                    c = w.compute_entanglement_curvature(i)
                    results.append({
                        "watcher": w,
                        "index": i,
                        "motifs": field["motifs"],
                        "substructures": field.get("substructures", {}),
                        "strength": field["strength"],
                        "curvature": c
                    })
        return results

    def _build_state_from_path(self, path: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for f in path:
            # add environment influence each field?
            env_vec = self._get_environment_influence()
            state += env_vec * 0.05  # small infusion

            # incorporate field vector
            field_vec = self._field_vector(f)
            weight = f["strength"] * (1.0 + f["curvature"])
            state += weight * field_vec

            # handle substructures
            for sub_name, submotifs in f.get("substructures", {}).items():
                sub_vec = self._substructure_vector(submotifs, f["watcher"])
                state += 0.5 * weight * sub_vec
        return state

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field["watcher"]
        motif_vecs = []
        for m in field["motifs"]:
            if m in w.motif_embeddings:
                motif_vecs.append(w.motif_embeddings[m])
        if motif_vecs:
            return np.mean(motif_vecs, axis=0)
        else:
            return np.zeros(self.state_dim)

    def _substructure_vector(self, submotifs: List[str], watcher: LogicalAgentAT) -> np.ndarray:
        sub_vecs = []
        for sm in submotifs:
            if sm in watcher.motif_embeddings:
                sub_vecs.append(watcher.motif_embeddings[sm])
        return np.mean(sub_vecs, axis=0) if sub_vecs else np.zeros(self.state_dim)

    ############################################
    # 2) EPHEMERAL SYNERGY CHECK
    ############################################

    def _ephemeral_synergy_check(self, candidate: np.ndarray) -> float:
        """
        Temporarily step the core with 'candidate', see if it's alive.
        Then revert. Also incorporate watchers' resonance or random logic.
        """
        old_active = self.core.is_alive()
        old_len = len(self.core.all_states)

        self.core.step(candidate)
        feasible = self.core.is_alive()

        # watchers resonance factor
        watchers_resonance = 1.0
        for w in self.watchers:
            # naive approach: entanglement_echo on a random motif or something.
            # Or we can just multiply a bit.
            watchers_resonance *= 1.0 + 0.01 * np.random.rand()

        synergy = (1.0 if feasible else 0.0) + watchers_resonance

        # revert ephemeral step
        if len(self.core.all_states) > old_len:
            self.core.state_history.pop()
        self.core._update_logical_feasibility()
        self.core.is_active = old_active

        return synergy

    ############################################
    # 3) Utility & Boundaries
    ############################################

    def _fallback_step(self) -> np.ndarray:
        """
        If no watchers' fields exist, do a random step.
        """
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

    def __repr__(self):
        return (
            f"<RecursiveAgentFT v3.0-final name={self.name}, time={self.time_step}, "
            f"alive={self.is_alive()}>"
        )