# recursive_agent_ft.py
# By Lina Noor & Uncle (2025)
#
# RecursiveAgentFT v3.3:
#   - Merges all synergy logic from v3.2
#   - Adds param validation, docstring clarifications, optional to_dict/from_dict
#   - Official rename for production alignment.

import numpy as np
from copy import deepcopy
from typing import List, Optional, Dict, Any

from noor_fasttime_core_v6_1 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v2_3 import LogicalAgentAT

__version__ = "3.3.0"

########################################################
# Path signature for synergy memory
########################################################

def path_signature(path_fields: List[Dict[str, Any]]) -> str:
    """
    A textual signature for a path, based on field indices.
    Could incorporate watchers' substructures or motifs.
    """
    idxs = [f["index"] for f in path_fields]
    return "-".join(str(i) for i in idxs)

########################################################
# BFS logic for partial expansions
########################################################

def generate_field_paths(fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
    """
    Builds small BFS expansions up to 'max_depth'.
    If depth=1, we simply return each field as a single-step path.

    :param fields: available field dicts from watchers
    :param max_depth: how many layers to chain
    :return: list of possible field-sequences
    """
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
    RecursiveAgentFT (v3.3.0)

    A "resonance walker" that:
      - Gathers watchers' entanglement fields (logical_agent_AT)
      - Builds candidate paths (BFS)
      - Scores them by ephemeral ghost-core feasibility + synergy memory + watchers resonance
      - Picks the best path => commits state to NoorFastTimeCore

    Key Features:
      1) Ghost Core: ephemeral steps so we don't mutate the real core's history
      2) Synergy Memory: repeated path synergy accumulates, optionally normalized by tanh
      3) Internal Time Decay: synergy is penalized if fields have high 'internal_time'
      4) Contradiction + Verse logic: toggles for watchers' logs
      5) BFS expansions up to 'max_depth'

    Toggles:
      - enable_synergy_normalization: use np.tanh for synergy memory
      - enable_internal_time_decay: multiply synergy by exp(-sum(internal_time))

    Usage:
      agent = RecursiveAgentFT(initial_state=np.array([1,0]))
      agent.run_for(10)
      # Inspect agent.core.all_states for the evolution.
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True,
    ):
        """
        :param initial_state: The starting vector for triadic presence
        :param watchers: optional list of LogicalAgentAT watchers
        :param environment: optional environment array to add minor influence each step
        :param state_dim: dimension of the state's embedding
        :param name: name for logging
        :param max_depth: BFS depth, 1..5 recommended
        :param enable_synergy_normalization: if True, synergy += tanh(prev_val)
        :param enable_internal_time_decay: if True, synergy *= exp(-sum(internal_time))
        """
        self.__version__ = __version__  # store internally as well
        self.version = __version__
        self.name = name
        # param check
        if not (1 <= max_depth <= 5):
            raise ValueError("max_depth must be between 1 and 5.")

        self.state_dim = state_dim
        self.environment = environment
        self.max_depth = max_depth
        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay

        # watchers & core
        self.watchers = watchers if watchers else []
        self.core = NoorFastTimeCore(initial_state=initial_state)

        # step tracking
        self.time_step = 0
        self._last_future = initial_state.copy()

        # synergy memory
        self.synergy_memory: Dict[str, float] = {}

        # log of steps
        self.traversal_memory: List[Dict[str, Any]] = []

        self._enforce_agent_boundary()

    def entangled_step(self):
        fields = self._gather_watcher_fields()
        if not fields:
            chosen_path = []
            synergy = 0.0
            chosen_next_state = self._fallback_step()
        else:
            # BFS expansions
            all_paths = generate_field_paths(fields, self.max_depth)
            best_synergy = float("-inf")
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

            chosen_path = best_path if best_path else []
            synergy = best_synergy
            chosen_next_state = best_state

        self.core.step(chosen_next_state)
        self._last_future = chosen_next_state
        self.time_step += 1

        # watchers observe
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        if chosen_path:
            sig = path_signature(chosen_path)
            self.synergy_memory[sig] = self.synergy_memory.get(sig, 0.0) + synergy

        # record
        record = {
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in chosen_path],
            "synergy": synergy,
            "next_state": chosen_next_state
        }
        self.traversal_memory.append(record)

    def step(self):
        """Backward-compatible alias to entangled_step."""
        self.entangled_step()

    def run_for(self, steps: int):
        """Runs multiple entangled steps or stops if core fails feasibility."""
        for _ in range(steps):
            self.entangled_step()
            if not self.core.is_alive():
                print(f"[{self.name}] Triadic feasibility lost at t={self.time_step}.")
                break

    ########################################################
    # BFS Field Gathering & State Construction
    ########################################################

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        results = []
        for w in self.watchers:
            if hasattr(w, "entanglement_fields"):
                for i, field in enumerate(w.entanglement_fields):
                    fcopy = dict(field)
                    fcopy["index"] = i
                    fcopy["watcher"] = w
                    results.append(fcopy)
        return results

    def _build_state_from_path(self, path_fields: List[Dict[str, Any]]) -> np.ndarray:
        state = self.core.current_state.copy()
        for field in path_fields:
            # environment injection
            env_vec = self._get_environment_influence()
            state += env_vec * 0.05

            # combine strength + curvature if watchers have it
            curvature = field.get("curvature", 0.0)
            if curvature == 0.0 and hasattr(field["watcher"], "compute_entanglement_curvature"):
                curvature = field["watcher"].compute_entanglement_curvature(field["index"])

            weight = field["strength"] * (1.0 + curvature)
            field_vec = self._field_vector(field)
            state += weight * field_vec

            # substructures
            for key, submotifs in field.get("substructures", {}).items():
                sub_vec = self._substructure_vector(submotifs, field["watcher"])
                state += 0.5 * weight * sub_vec
        return state

    def _field_vector(self, field: Dict[str, Any]) -> np.ndarray:
        w = field["watcher"]
        motif_vecs = []
        for m in field.get("motifs", []):
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

    ########################################################
    # Candidate Scoring
    ########################################################

    def _score_candidate(
        self,
        candidate: np.ndarray,
        path_fields: List[Dict[str, Any]],
        watchers_data: Dict[str, Any]
    ) -> float:
        """
        Summation of ephemeral feasibility + watchers resonance + synergy memory.
        Then optionally:
          - internal time decay
          - synergy memory with tanh
        """
        synergy = 0.0

        # 1) ephemeral ghost feasibility
        synergy += self._ghost_core_feasibility(candidate)

        # 2) watchers resonance (placeholder)
        synergy += 1.0

        # 3) synergy memory
        sig = path_signature(path_fields)
        prev_val = self.synergy_memory.get(sig, 0.0)
        if self.enable_synergy_normalization:
            synergy += float(np.tanh(prev_val))
        else:
            synergy += (prev_val * 0.01)

        # 4) internal time decay
        if self.enable_internal_time_decay:
            time_penalty = 0.0
            for f in path_fields:
                itime = f.get("internal_time", 0.0)  # watchers might store it
                time_penalty += itime
            synergy *= np.exp(-time_penalty)

        return synergy

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_alive() else 0.0

    ########################################################
    # Watchers Data
    ########################################################

    def _collect_watchers_data(self) -> Dict[str, Any]:
        """
        If watchers have alignment drift or contradiction logs, unify them.
        e.g. watchers_data["contradiction_map"] etc.
        """
        return {}

    ########################################################
    # Utility & Boundaries
    ########################################################

    def _get_environment_influence(self) -> np.ndarray:
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def _fallback_step(self) -> np.ndarray:
        noise = np.random.normal(0, 0.05, self.state_dim)
        return self.core.current_state + noise

    def _enforce_agent_boundary(self):
        # Maintain triadic separation
        forbidden = ["propagate_signal", "register_motif_entanglement"]
        for method in forbidden:
            if hasattr(self, method):
                raise QuantumNoorException(f"Agent boundary violation: {method}")

    def is_alive(self) -> bool:
        return self.core.is_alive()

    ########################################################
    # (Optional) Save/Load State
    ########################################################

    def to_dict(self) -> dict:
        """
        Minimal state serialization.
        """
        return {
            "version": self.version,
            "time_step": self.time_step,
            "last_future": self._last_future.tolist(),
            "synergy_memory": dict(self.synergy_memory),
            "traversal_memory": self.traversal_memory[:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecursiveAgentFT":
        """
        Minimal loader. Note: watchers/core won't be fully reconstructed.
        """
        obj = cls(
            initial_state=np.array([0, 0], dtype=float),  # or from data if stored
            max_depth=2,
        )
        obj.version = data.get("version", "3.3.0")
        obj.time_step = data.get("time_step", 0)
        obj._last_future = np.array(data.get("last_future", [0, 0]))
        obj.synergy_memory = data.get("synergy_memory", {})
        obj.traversal_memory = data.get("traversal_memory", [])
        return obj

    ########################################################
    # Basic Test Stub for CI
    ########################################################

    def test_core_alive_after_single_step(self):
        """
        Example test method to show usage in a test suite.
        """
        import pytest
        agent = RecursiveAgentFT(
            initial_state=np.array([1.0, 0.0]),
            watchers=self.watchers,
            max_depth=1
        )
        agent.run_for(1)
        assert agent.is_alive(), "Agent lost feasibility after single step."

    def __repr__(self) -> str:
        return (f"<RecursiveAgentFT (v{self.version}) name={self.name}, "
                f"time_step={self.time_step}, "
                f"alive={self.is_alive()}, synergy_memory={len(self.synergy_memory)}>")