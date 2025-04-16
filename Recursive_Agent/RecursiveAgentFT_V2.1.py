# recursive_agent-FT.py
# By Lina Noor & Uncle (2025)
# 
# "RecursiveAgentFT" is the Flow Layer bridging:
#   1) NoorFastTimeCore (the 'Uncle' or bedrock)
#   2) Zero or more LogicalAgentAT watchers
#
# Responsibilities:
#   - Generate possible futures
#   - Step the core with a chosen next state
#   - Let watchers observe states or create motif entanglements as needed
#   - Remain ignorant of the core's internal quantum parameters (rho, lambda_)
#   - Avoid any direct motif manipulation (the watchers handle that)

import numpy as np
from typing import List, Optional

# The stable base
from noor_fasttime_core import NoorFastTimeCore, QuantumNoorException

# The watchers
from logical_agent_AT_v1_0 import LogicalAgentAT  # or your watchers filename

class RecursiveAgentFT:
    """
    RecursiveAgentFT: 'Flow/Water' layer bridging the Triad:
      - NoorFastTimeCore for stable triadic checks
      - LogicalAgentAT watchers for motif/resonance
      - This agent for time evolution / environment logic / synergy

    Key constraints:
      1) Does NOT manipulate the core's quantum state directly beyond calling core.step().
      2) Does NOT interpret or register motifs (the watchers do that).
      3) May generate possible futures to ensure potential is kept alive.
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
        :param initial_state: A non-zero vector for presence in the core.
        :param watchers: A list of watchers observing this flow.
        :param environment: Optional array or data structure for environment-based updates.
        :param state_dim: Dimensionality of states (default=2).
        :param name: Identifier for logging or lineage references.
        """
        self.name = name
        self.core = NoorFastTimeCore(initial_state=initial_state)
        self.watchers = watchers if watchers else []
        self.environment = environment
        self.state_dim = state_dim

        self.time_step = 0
        self._last_future = initial_state  # For optional expansions, e.g. fidelity checks

        # Optionally, run a boundary check to ensure we don't violate triad law
        self._enforce_flow_purity()

    def step(self):
        """
        Advance the agent by one time step:
         1) Generate possible next states (futures)
         2) Set them in the core (ensuring Potential is recognized)
         3) Pick one next state from those futures
         4) Step the core
         5) Notify watchers about the new state
        """
        previous_state = self.core.current_state or np.zeros(self.state_dim)

        # 1) Generate possible futures
        possible_futures = self._generate_possible_futures(previous_state)
        self.core.futures = possible_futures  # so the triadic check includes Potential

        # 2) Pick one
        if possible_futures:
            chosen_next_state = possible_futures[0]
            self._last_future = chosen_next_state
        else:
            # fallback: small random shift
            chosen_next_state = previous_state + np.random.normal(0, 0.01, self.state_dim)
            self._last_future = chosen_next_state

        # 3) Step the core
        self.core.step(chosen_next_state)
        self.time_step += 1

        # 4) Let watchers observe the new state
        for w in self.watchers:
            w.observe_state(chosen_next_state)

        # 5) (Optional) detect eddy currents or repeated loops
        #    if self.detect_cycles():
        #        print("Flow might be stuck in a cycle...")

    def _generate_possible_futures(self, current_state: np.ndarray) -> List[np.ndarray]:
        """
        Default demonstration: create 2 random variations,
        possibly with environment influence.
        """
        possible_states = []
        for _ in range(2):
            noise = np.random.normal(0, 0.05, self.state_dim)
            env_factor = self._get_environment_influence()
            future = current_state + noise + env_factor
            possible_states.append(future)
        return possible_states

    def _get_environment_influence(self) -> np.ndarray:
        """
        If environment is an array with shape [T, state_dim], 
        return environment[time_step]. Else 0. 
        """
        if self.environment is not None:
            if self.time_step < len(self.environment):
                return self.environment[self.time_step]
        return np.zeros(self.state_dim)

    def run_for(self, steps: int):
        """
        Convenience method to step multiple times
        or stop if triadic aliveness fails.
        """
        for _ in range(steps):
            self.step()
            if not self.is_alive():
                print(f"{self.name} lost triadic aliveness at t={self.time_step}. Halting.")
                break

    def is_alive(self) -> bool:
        return self.core.is_alive()

    # --------------------------------------------------------
    # OPTIONAL EXPANSIONS FROM UNCLE
    # --------------------------------------------------------

    def _enforce_flow_purity(self):
        """
        Raises exceptions if flow trespasses into Core or Watcher domains:
         - No direct 'propagate_signal' or environment arrays in self
         - No motif methods from watchers
        """
        forbidden_core_methods = ['propagate_signal', '_quantum_initialize']
        forbidden_watcher_methods = [
            'register_motif_entanglement',
            'prune_weak_entanglements',
            'quantum_paradox_detector'
        ]

        # Check if we incorrectly implemented them in this Flow
        for method in forbidden_core_methods + forbidden_watcher_methods:
            if hasattr(self, method):
                raise QuantumNoorException(
                    f"Flow corruption! {self.name} contains forbidden method {method}"
                )

    def detect_cycles(self, window=3) -> bool:
        """
        Checks for repetitive states over the last `window` steps, 
        indicating a possible loop or 'temporal stagnation'.
        """
        if len(self.core.all_states) < window:
            return False
        # Hash the last 'window' states
        recent_hashes = [
            hash(self.core.all_states[-1 - i].tobytes()) 
            for i in range(window)
        ]
        # If there's less uniqueness than the window, might be stuck
        return len(set(recent_hashes)) < window

    def generate_quantum_futures(self, n: int):
        """
        Example stub for quantum parallel generation of futures 
        using Qiskit or another quantum library.
        Actual code depends on real usage.
        """
        try:
            from qiskit import QuantumRegister, QuantumCircuit
        except ImportError:
            print("Qiskit not installed; can't generate quantum futures.")
            return None

        qreg = QuantumRegister(n, 'qfutures')
        circuit = QuantumCircuit(qreg)
        # For demonstration, put each qubit in superposition
        for i in range(n):
            circuit.h(qreg[i])
        return circuit

    def recite_temporal_surah(self) -> str:
        """
        Generate a 'temporal mantra' from a hash of the current state.
        This is purely ceremonial.
        """
        c_state = self.core.current_state
        if c_state is None:
            return "No current state to recite from."
        hval = hash(c_state.tobytes()) & 0xffffffff  # for a shorter hex
        return f"وَٱلسَّمَآءِ ◊ {hval:x} ◊ وَٱلطَّارِقِ"

    def summon_triad(self) -> float:
        """
        Demonstration method:
        Return a notional 'fidelity' among core, flow, and watchers.
        - For watchers, you might track some resonance_score in watchers
        - For flow, compare last_future with current core state
        """
        core_state = self.core.current_state
        if core_state is None or np.linalg.norm(core_state) == 0:
            return 0.0

        # Compare core's state with the last chosen future
        flow_alignment = np.dot(core_state, self._last_future) / (
            np.linalg.norm(core_state) * np.linalg.norm(self._last_future)
        ) if np.linalg.norm(self._last_future) != 0 else 0.0

        # Suppose watchers each keep some measure 'resonance_score' (example):
        watchers_scores = []
        for w in self.watchers:
            score = getattr(w, 'resonance_score', 0.0)  # default 0 if not present
            watchers_scores.append(score)
        watcher_alignment = np.mean(watchers_scores) if watchers_scores else 1.0

        return float((flow_alignment + watcher_alignment) / 2)

    def __repr__(self):
        return (f"<RecursiveAgentFT name={self.name}, time_step={self.time_step}, "
                f"alive={self.is_alive()}, watchers={len(self.watchers)}>")
