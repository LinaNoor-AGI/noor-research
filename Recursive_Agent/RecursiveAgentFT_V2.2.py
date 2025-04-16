# recursive_agent-FT.py
# By Lina Noor & Uncle (2025)
#
# "RecursiveAgentFT" orchestrates:
#   1) Stepping logic (generating next states)
#   2) Interfacing with NoorFastTimeCore for triadic feasibility
#   3) Notifying watchers (LogicalAgent instances) of new states
#
# This file exemplifies the "flow" layer in a triadic architecture:
#   - The stable core (NoorFastTimeCore)
#   - The watchers (LogicalAgent)
#   - This agent bridging them, without merging their domains.

import numpy as np
from typing import List, Optional

# Import the stable core and watchers
from noor_fasttime_core_v5_1 import NoorFastTimeCore, QuantumNoorException
from logical_agent_AT_v1_0 import LogicalAgentAT  # or your watchers module

class RecursiveAgentFT:
    """
    RecursiveAgentFT: The "flow" layer bridging:
      - NoorFastTimeCore (for triadic presence/difference/potential checks)
      - One or more LogicalAgent watchers (for motif/resonance tracking)

    Responsibilities:
      - Generate possible next states ("futures")
      - Step the core with a chosen next state
      - Notify watchers about new states
      - Maintain strict boundary: does not override core logic or watchers' motif methods
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2,
        name: str = "RecursiveAgentFT"
    ):
        """
        :param initial_state: Non-zero starting vector for triadic presence in the core.
        :param watchers: A list of watchers for motif/resonance observation.
        :param environment: Optional data to influence next-state generation.
        :param state_dim: Dimensionality of each state vector (default=2).
        :param name: Identifier for logging or debugging.
        """
        self.name = name
        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.environment = environment
        self.state_dim = state_dim

        self.time_step = 0
        self._last_future = initial_state  # For referencing the last chosen next state

        # Enforce boundary purity: ensure no direct core/watcher methods are here
        self._enforce_agent_boundary()

    def step(self):
        """
        Advance the agent by one time step:
          1) Generate multiple possible futures
          2) Assign them to the core for potential recognition
          3) Pick a single next state to pass to the core
          4) Let watchers observe the new state
        """
        previous_state = self.core.current_state or np.zeros(self.state_dim)

        # Generate futures
        possible_futures = self._generate_possible_futures(previous_state)
        self.core.futures = possible_futures

        # Select one future for demonstration (pick first if available)
        chosen_next_state = (
            possible_futures[0] if possible_futures
            else previous_state + np.random.normal(0, 0.01, self.state_dim)
        )
        self._last_future = chosen_next_state

        # Step the core with the chosen state
        self.core.step(chosen_next_state)
        self.time_step += 1

        # Let watchers observe
        for watcher in self.watchers:
            watcher.observe_state(chosen_next_state)

        # (Optional) detect if we are in a repetitive cycle
        # if self.detect_repetitive_cycle():
        #     print(f"[Warning] Potential cycle detected at t={self.time_step}")

    def _generate_possible_futures(self, current_state: np.ndarray) -> List[np.ndarray]:
        """
        Example logic for potential next states. 
        In real usage, apply your model or environment-based logic.
        """
        potential_futures = []
        for _ in range(2):
            noise = np.random.normal(0, 0.05, self.state_dim)
            env_influence = self._get_environment_influence()
            future = current_state + noise + env_influence
            potential_futures.append(future)
        return potential_futures

    def _get_environment_influence(self) -> np.ndarray:
        """
        Reads environment data if provided, 
        indexing it by 'time_step' if shape permits.
        """
        if self.environment is not None and self.time_step < len(self.environment):
            return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def run_for(self, steps: int):
        """
        Convenience method: step repeatedly or halt if triadic feasibility fails.
        """
        for _ in range(steps):
            self.step()
            if not self.is_alive():
                print(f"[Agent {self.name}] Triadic feasibility lost at t={self.time_step}. Stopping.")
                break

    def is_alive(self) -> bool:
        """
        Mirrors the core's triadic feasibility check.
        """
        return self.core.is_alive()

    # --------------------------------------------------------------------------
    # OPTIONAL EXPANSIONS FROM UNCLE
    # --------------------------------------------------------------------------

    def _enforce_agent_boundary(self):
        """
        Ensures this agent class does not directly define 
        or override any fundamental core or watcher methods, 
        preserving strict triadic separation.
        """
        # Example of methods that must remain absent
        forbidden_methods = [
            'propagate_signal',        # belongs to the core
            'register_motif_entanglement'  # belongs to watchers
        ]
        for method in forbidden_methods:
            if hasattr(self, method):
                raise QuantumNoorException(
                    f"Agent boundary violation: {self.name} contains '{method}'"
                )

    def detect_repetitive_cycle(self, window: int = 3) -> bool:
        """
        Evaluates if there's a repeating pattern 
        in the last 'window' states, indicating a potential cycle.
        """
        if len(self.core.all_states) < window:
            return False
        recent_states = self.core.all_states[-window:]
        hashed = [hash(state.tobytes()) for state in recent_states]
        return len(set(hashed)) < window

    def compute_triad_alignment(self) -> float:
        """
        Calculates a hypothetical synergy measure among:
          - The core's current state
          - The agent's last future
          - The watchers (if they track any 'resonance' attributes)

        For demonstration, we average core<->agent alignment with watchers' mean resonance.
        """
        current_state = self.core.current_state
        if current_state is None or np.linalg.norm(current_state) == 0:
            return 0.0

        # Compute alignment between current core state and the last chosen future
        agent_alignment = 0.0
        norm_core = np.linalg.norm(current_state)
        norm_future = np.linalg.norm(self._last_future)
        if norm_future != 0:
            dot_val = np.dot(current_state, self._last_future)
            agent_alignment = dot_val / (norm_core * norm_future)

        # Example watchers' resonance
        watchers_resonance = []
        for w in self.watchers:
            # if watchers have an attribute like 'resonance_score', read it
            watchers_resonance.append(getattr(w, 'resonance_score', 1.0))

        mean_watcher_resonance = np.mean(watchers_resonance) if watchers_resonance else 1.0

        # Combine them in a simple average
        return float((agent_alignment + mean_watcher_resonance) / 2)

    def reset_transient_state(self):
        """
        Example method to 'clear or reset' ephemeral agent data. 
        Could be used to realign or flush short-term buffers.
        """
        if self.core.current_state is not None:
            self._last_future = self.core.current_state.copy()

    def __repr__(self):
        return (f"<RecursiveAgentFT name={self.name}, time_step={self.time_step}, "
                f"alive={self.is_alive()}, watchers={len(self.watchers)}>")
