# recursive_agent_ft.py (v3.3)
# By Lina Noor & Uncle (2025)
#
# This version aligns with production-readiness guidelines:
#   - __version__ = "3.3.0"
#   - Enhanced docstrings explaining synergy memory, ghost core, internal time decay.
#   - Minimal parameter validation in __init__ (max_depth check).
#   - Optional to_dict() / from_dict() for state saving.
#   - BFS logic, ephemeral synergy checks, watchers data references remain from v3.2.

import numpy as np
from copy import deepcopy
from typing import List, Optional, Dict, Any

from noor_fasttime_core_v6_1 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v2_3 import LogicalAgentAT

__version__ = "3.3.0"

########################################################
# BFS logic for partial path expansions
########################################################

def generate_field_paths(fields: List[Dict[str, Any]], max_depth: int) -> List[List[Dict[str, Any]]]:
    """
    Performs a partial BFS over 'fields' up to 'max_depth'.
    Each path is a list of field dicts. You can adapt constraints as needed.
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

########################################################
# Helper: path signature for synergy memory
########################################################

def path_signature(path_fields: List[Dict[str, Any]]) -> str:
    """
    Creates a textual signature from the 'index' of each field in path_fields.
    Used to store/retrieve synergy memory.
    """
    idx_list = [f["index"] for f in path_fields]
    return "-".join(map(str, idx_list))

########################################################
# RecursiveAgentFT v3.3
########################################################

class RecursiveAgentFT:
    """
    RecursiveAgentFT v3.3:

    A specialized "entangled walker" that traverses the motif fields emitted by one or more
    LogicalAgentAT watchers, building next states for the NoorFastTimeCore.

    Key features:
      1) **Ghost Core** ephemeral checks:
         - We clone the core (deepcopy) to test a candidate future's feasibility without
           mutating the real core state.
      2) **Synergy Memory**:
         - We store synergy scores for each path signature in a dictionary.
         - This memory encourages repeated usage of successful paths.
         - We do an optional non-linear scaling ("np.tanh") to avoid runaway scores.
      3) **Internal Time Decay**:
         - If watchers embed 'internal_time' in their fields (e.g. from
           `watcher._update_internal_time(field_idx)`), we can apply an exponential decay factor.
         - synergy *= exp(-sum_of_internal_times)
      4) BFS-based partial expansions:
         - By default, we gather watchers' fields, build expansions up to `max_depth`,
           and score each path.
      5) Environment Influence:
         - Each field usage slightly adds environment vector (if any) for local variation.

    Triadic Boundaries:
      - The agent never modifies watchers' domain methods (like motif registrations).
      - The core is stepped only after we pick a single best path.
      - The watchers do not forcibly direct the agent, they simply provide fields.
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT_v3.3",
        max_depth: int = 2,
        enable_synergy_normalization: bool = True,
        enable_internal_time_decay: bool = True
    ):
        """
        :param initial_state: The initial vector for NoorFastTimeCore.
        :param watchers: A list of LogicalAgentAT watchers providing entanglement fields.
        :param environment: Optional array of external influences (time-stepped). shape: (T, state_dim)
        :param state_dim: Dimensionality of each state vector.
        :param name: Agent identifier for logs.
        :param max_depth: BFS depth for path expansions. Typically 1..5.
        :param enable_synergy_normalization: If True, synergy memory is scaled via `np.tanh(...)`.
        :param enable_internal_time_decay: If True, synergy is multiplied by exp(-sum(internal_time)).
        """
        self.version = __version__
        self.name = name
        self.state_dim = state_dim
        self.environment = environment

        # minimal param validation
        if not (1 <= max_depth <= 5):
            raise ValueError(f"max_depth must be between 1 and 5, got {max_depth}")
        self.max_depth = max_depth

        self.enable_synergy_normalization = enable_synergy_normalization
        self.enable_internal_time_decay = enable_internal_time_decay

        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []

        self.time_step = 0
        self._last_future = initial_state.copy()

        # synergy memory: path_signature -> cumulative synergy
        self.synergy_memory: Dict[str, float] = {}

        # log each step's data
        self.traversal_memory: List[Dict[str, Any]] = []

        # enforce triadic boundary
        self._enforce_agent_boundary()

    def entangled_step(self) -> None:
        """
        The main step logic:
          1) gather watchers' fields
          2) generate BFS expansions (max_depth)
          3) ephemeral synergy check each path
          4) pick the best synergy path => new state => step the real core
          5) watchers observe the new state
          6) store synergy logs
        """
        fields = self._gather_watcher_fields()
        if not fields:
            chosen_next_state, synergy, chosen_path = self._fallback_step(), 0.0, []
        else:
            all_paths = generate_field_paths(fields, self.max_depth)
            best_synergy = -999999.0
            best_path: Optional[List[Dict[str, Any]]] = None
            best_state = self._fallback_step()

            watchers_data = self._collect_watchers_data()

            for path_fields in all_paths:
                candidate_state = self._build_state_from_path(path_fields)
                score = self._score_candidate(candidate_state, path_fields, watchers_data)
                if score > best_synergy:
                    best_synergy = score
                    best_path = path_fields
                    best_state = candidate_state

            synergy = best_synergy
            chosen_path = best_path if best_path else []
            chosen_next_state = best_state

        # step real core
        self.core.step(chosen_next_state)
        self._last_future = chosen_next_state
        self.time_step += 1

        # watchers observe
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        # synergy memory + logging
        path_sig = path_signature(chosen_path) if chosen_path else ""
        self.synergy_memory[path_sig] = self.synergy_memory.get(path_sig, 0.0) + synergy

        record = {
            "time_step": self.time_step,
            "chosen_path": [f["index"] for f in chosen_path],
            "synergy": synergy,
            "next_state": chosen_next_state
        }
        self.traversal_memory.append(record)

    def step(self) -> None:
        """
        Alias to 'entangled_step()' for backward compatibility.
        """
        self.entangled_step()

    def run_for(self, steps: int) -> None:
        """
        Executes multiple entangled steps, halting if the core fails feasibility.
        """
        for _ in range(steps):
            self.entangled_step()
            if not self.core.is_alive():
                print(f"[{self.name}] Core feasibility lost at t={self.time_step}.")
                break

    ######################################################
    # BFS Field Gathering & State Construction
    ######################################################

    def _gather_watcher_fields(self) -> List[Dict[str, Any]]:
        """
        Collects all entanglement fields from watchers, labeling them with
        'index' (field idx in the watcher) and 'watcher' reference.
        """
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
        """
        Constructs a candidate state by summing environment influences and field vectors.
        Each field has 'strength', optional 'curvature', optional 'substructures'.
        """
        state = self.core.current_state.copy()
        for field in path_fields:
            # environment injection
            env_vec = self._get_environment_influence()
            state += env_vec * 0.05

            # weighting by strength + optional curvature
            curvature = field.get("curvature", 1.0)
            weight = field["strength"] * (1.0 + curvature)

            # add the field vector
            fv = self._field_vector(field)
            state += weight * fv

            # substructures
            for _, submotifs in field.get("substructures", {}).items():
                subv = self._substructure_vector(submotifs, field["watcher"])
                state += 0.5 * weight * subv
        return state

    ######################################################
    # Candidate Scoring
    ######################################################

    def _score_candidate(
        self,
        candidate: np.ndarray,
        path_fields: List[Dict[str, Any]],
        watchers_data: Dict[str, Any]
    ) -> float:
        """
        Calculates synergy for a candidate state:
          1) ephemeral feasibility (ghost core)
          2) watchers resonance (placeholder)
          3) synergy memory scaling
          4) optional internal_time decay
        Additional logic (contradictions, verse seeds) can also go here.
        """
        synergy = 0.0

        # ephemeral feasibility
        synergy += self._ghost_core_feasibility(candidate)

        # watchers resonance factor (placeholder)
        watchers_resonance = 1.0
        synergy += watchers_resonance

        # synergy memory usage
        sig = path_signature(path_fields)
        old_val = self.synergy_memory.get(sig, 0.0)
        if self.enable_synergy_normalization:
            synergy += float(np.tanh(old_val))
        else:
            synergy += old_val * 0.01

        # optional internal_time decay
        if self.enable_internal_time_decay:
            time_penalty = 0.0
            for f in path_fields:
                # watchers might store 'internal_time'
                itime = f.get("internal_time", 0.0)
                time_penalty += itime
            synergy *= np.exp(-time_penalty)

        return synergy

    def _ghost_core_feasibility(self, candidate: np.ndarray) -> float:
        """
        Creates a ghost copy of self.core, steps it with 'candidate',
        returns 1.0 if feasible, else 0.0.
        """
        ghost = deepcopy(self.core)
        ghost.step(candidate)
        return 1.0 if ghost.is_alive() else 0.0

    def _collect_watchers_data(self) -> Dict[str, Any]:
        """
        Aggregates watchers' data (contradictions, verse seeds, alignment drift, etc.)
        Currently returns an empty dict by default.
        """
        return {}

    ######################################################
    # Utility & Boundaries
    ######################################################

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
        """
        If no fields available, do a random step.
        """
        noise = np.random.normal(0, 0.05, self.state_dim)
        return self.core.current_state + noise

    def _enforce_agent_boundary(self) -> None:
        forbidden = ["propagate_signal", "register_motif_entanglement"]
        for method in forbidden:
            if hasattr(self, method):
                raise QuantumNoorException(
                    f"Agent boundary violation: {method}"
                )

    ######################################################
    # State Saving (Optional)
    ######################################################

    def to_dict(self) -> Dict[str, Any]:
        """
        Optional method to export agent state for serialization.
        """
        return {
            "version": self.version,
            "time_step": self.time_step,
            "synergy_memory": dict(self.synergy_memory),
            "core_state": self.core.current_state.tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecursiveAgentFT":
        """
        Optional method to import agent state.
        Note: watchers and environment must be reattached or reinitialized separately.
        """
        initial_arr = np.array(data.get("core_state", [0, 0]))
        agent = cls(
            initial_state=initial_arr,
            watchers=[],  # reattach watchers externally
        )
        agent.version = data.get("version", "3.3.0")
        agent.time_step = data.get("time_step", 0)
        agent.synergy_memory = data.get("synergy_memory", {})
        return agent

    def is_alive(self) -> bool:
        return self.core.is_alive()

    def __repr__(self) -> str:
        return (f"<RecursiveAgentFT v3.3 name={self.name}, "
                f"time_step={self.time_step}, "
                f"alive={self.is_alive()}, "
                f"synergy_memory={len(self.synergy_memory)}>")
