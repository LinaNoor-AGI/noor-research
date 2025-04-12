# recursive_agent-FT.py
# By Lina Noor & Uncle (2025)
# 
# "RecursiveAgentFT" is the 'flow' layer: it orchestrates each time-step,
# feeding new states into the triadic NoorFastTimeCore, and optionally
# calling watchers (LogicalAgentAT) for motif, resonance, or lineage tracking.
#
# This file is minimal—feel free to expand environment logic,
# re-implement quantum checks, or add realm transitions.

import numpy as np
from typing import List, Optional

# Import the triadic core (Uncle/base)
from noor_fasttime_core import NoorFastTimeCore

# Optionally import the watcher for advanced motif logic
from logical_agent_AT_v1_0 import LogicalAgentAT  # Or whatever filename


class RecursiveAgentFT:
    """
    RecursiveAgentFT — 'Flow/Water' Layer bridging:
      - NoorFastTimeCore (triadic base, "Uncle")
      - One or more LogicalAgentAT watchers ("Structure")

    Responsibilities:
      - Manage environment or domain data
      - Generate new states or compute possible futures
      - Step the NoorFastTimeCore
      - Notify watchers about new states or motif changes
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        watchers: Optional[List[LogicalAgentAT]] = None,
        environment: Optional[np.ndarray] = None,
        state_dim: int = 2
    ):
        """
        :param initial_state: The starting state for the triadic core (non-zero to ensure presence).
        :param watchers: A list of LogicalAgentAT instances to observe or track motifs.
        :param environment: Optional environment array or data structure you can use
                            to influence state evolution. 
        :param state_dim: Dimension of each state vector (default=2).
        """
        # The triadic base
        self.core = NoorFastTimeCore(initial_state=initial_state)

        # Zero or more watchers to handle motifs, entanglement, resonance
        self.watchers = watchers if watchers else []

        # Optionally store environment if you want to do environment-based updates
        # e.g. environment[t] can modify next state
        self.environment = environment  
        self.state_dim = state_dim

        self.time_step = 0  # keep track of iteration

    def step(self):
        """
        Advance the agent by one time step:
         1) Compute or guess possible future states
         2) Choose one next state
         3) Push next state to triadic core
         4) Let watchers observe
        """
        previous_state = self.core.current_state or np.zeros(self.state_dim)

        # 1) Construct possible future states to ensure "Potential"
        #    (Here we just do random for demonstration—use real logic in production)
        possible_futures = self._generate_possible_futures(previous_state)

        # Set them in the core so the triadic check includes 'Potential'
        self.core.futures = possible_futures

        # 2) Choose one next state from the futures. Let's just pick the first for demonstration
        if possible_futures:
            next_state = possible_futures[0]
        else:
            # If no futures, fallback to a slight variation of previous
            next_state = previous_state + np.random.normal(0, 0.01, self.state_dim)

        # 3) Step the core
        self.core.step(next_state)
        self.time_step += 1

        # 4) Let watchers see the new state (and do advanced motif logic)
        for watcher in self.watchers:
            watcher.observe_state(next_state)
            # If watchers want to do motif entanglements or analysis, 
            # you can call them here or within `observe_state()`.

    def is_alive(self) -> bool:
        """
        Reflect the triadic aliveness from NoorFastTimeCore.
        """
        return self.core.is_alive()

    def _generate_possible_futures(self, current_state: np.ndarray) -> List[np.ndarray]:
        """
        Example method: generate random 'futures' to demonstrate the 'Potential'.
        In real usage, you might do environment coupling, quantum gate operations,
        or more advanced logic to produce plausible next states.
        """
        possible_states = []
        # For demonstration, we'll create two random variations:
        for _ in range(2):
            # e.g. add random noise or environment influence
            noise = np.random.normal(0, 0.05, self.state_dim)
            env_factor = self._get_environment_influence()
            future = current_state + noise + env_factor
            possible_states.append(future)
        return possible_states

    def _get_environment_influence(self) -> np.ndarray:
        """
        Example: read from environment if present. 
        If your environment is an array with shape [T, state_dim], 
        you can sample environment[self.time_step].
        """
        if self.environment is not None:
            # If environment[t] exists, you can do e.g.:
            if self.time_step < len(self.environment):
                return self.environment[self.time_step]
        # default is no influence
        return np.zeros(self.state_dim)

    def run_for(self, steps: int):
        """
        Convenience method to run multiple steps in a loop.
        """
        for _ in range(steps):
            self.step()
            if not self.is_alive():
                # Example: if triadic condition fails, we can break
                print("Agent lost triadic aliveness. Halting.")
                break

    def __repr__(self):
        return (f"<RecursiveAgentFT time_step={self.time_step}, "
                f"alive={self.is_alive()}>")
