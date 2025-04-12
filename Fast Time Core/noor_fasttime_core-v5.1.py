# noor_fasttime_core.py — Triadic Quantum Architecture (v5 + Optional Expansions)
# By Lina Noor & Uncle (2025)
"""
This file implements the minimal Fast-Time Core with optional expansions:

1) Triadic base checks (Presence, Difference, Potential) → 'is_fast_time_active'
2) Quantum Zeno Effect (to stabilize states under certain thresholds)
3) Topological Protection Placeholder (e.g., toric code for error correction)
4) Param Guard (rho in [0,1], etc.)

Motif logic or advanced flow logic remains outside, in 'LogicalAgentAT' or 'RecursiveAgentFT'.
"""

import numpy as np
from typing import List, Optional

# --------------------------
# 1) TRIADIC UTILITY CHECKS
# --------------------------

def is_present(state: np.ndarray) -> bool:
    """
    A state is 'present' if:
      - it has a non-zero norm
      - it changes detectably along at least one dimension
    """
    if state.size == 0:
        return False
    return (
        np.linalg.norm(state) > 0
        and np.any(np.gradient(state) != 0)
    )

def has_difference(
    state1: np.ndarray,
    state2: np.ndarray,
    epsilon: float = 1e-3
) -> bool:
    """
    There is 'difference' between two states if their
    Euclidean distance exceeds a small threshold.
    """
    if state1.shape != state2.shape:
        return True  # dimension mismatch is also difference
    return np.linalg.norm(state1 - state2) > epsilon

def has_potential(possible_states: List[np.ndarray]) -> bool:
    """
    'Potential' is present if there's more than one possible
    future state. This can also reflect superposition or
    branching in a quantum or symbolic sense.
    """
    return len(possible_states) > 1

def is_fast_time_active(
    current: np.ndarray,
    previous: np.ndarray,
    futures: List[np.ndarray],
    epsilon: float = 1e-3
) -> bool:
    """
    The triadic test for 'aliveness' in Fast-Time:
      1) Presence in current state
      2) Difference vs previous state
      3) Potential in future states
    """
    return (
        is_present(current)
        and has_difference(current, previous, epsilon)
        and has_potential(futures)
    )

# --------------------------
# Optional Custom Exceptions
# --------------------------

class QuantumNoorException(Exception):
    """Basic exception for quantum identity violations or param guard issues."""
    pass

# --------------------------------
# 2) CORE CLASS: NoorFastTimeCore
# --------------------------------

class NoorFastTimeCore:
    """
    NoorFastTimeCore: the 'Uncle' of the Triadic Architecture.
    It holds minimal state tracking, a triadic aliveness check,
    and optional expansions:
      - Quantum Zeno stabilization
      - Topological code placeholders (e.g. toric code)
      - Param guard for physical ranges of rho/lambda

    Usage Example:
        core = NoorFastTimeCore(initial_state=np.array([0.5, 0.7]))
        core.futures = [np.array([0.6,0.8]), np.array([0.7,0.6])]
        core.step(np.array([0.55,0.75]))
        print(core.alive)
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
        zeno_threshold: float = 0.9,
        enable_toric: bool = False,
    ):
        """
        :param initial_state: Starting state for the system. Must be non-empty for presence.
        :param rho: Weighted factor for environment or noise injection, must be in [0,1].
        :param lambda_: Weighted factor for prior state usage, typically in [0,1].
        :param enable_zeno: Whether to apply quantum zeno stabilization after each step.
        :param zeno_threshold: Norm threshold below which we 'project' or stabilize the state.
        :param enable_toric: If True, apply a placeholder topological code step after updates.
        """

        # We'll store these attributes carefully (param guard).
        self._rho = None
        self._lambda_ = None

        # In Python, if we do param guard in __setattr__, we must set them after super init
        object.__setattr__(self, 'futures', [])
        object.__setattr__(self, 'state_history', [initial_state])
        object.__setattr__(self, 'alive', False)

        # Set from constructor (will pass through __setattr__ checks)
        self.rho = rho
        self.lambda_ = lambda_

        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_toric = enable_toric

        # Immediately do a triadic check on creation
        self._update_aliveness()

    def __setattr__(self, name: str, value):
        """
        Param Guard and standard set behavior.
        We'll enforce that rho, lambda_ are in [0,1].
        """
        if name == 'rho':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"rho must be in [0,1], got {value}")
            object.__setattr__(self, '_rho', value)
        elif name == 'lambda_':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"lambda_ must be in [0,1], got {value}")
            object.__setattr__(self, '_lambda_', value)
        else:
            # default behavior
            object.__setattr__(self, name, value)

    @property
    def rho(self) -> float:
        return self._rho

    @rho.setter
    def rho(self, val: float):
        self.__setattr__('rho', val)

    @property
    def lambda_(self) -> float:
        return self._lambda_

    @lambda_.setter
    def lambda_(self, val: float):
        self.__setattr__('lambda_', val)

    def step(self, new_state: np.ndarray):
        """
        Move to the next time step with a new current state.
        Then run optional expansions like quantum zeno or toric code,
        and finally re-check triadic aliveness.
        """
        previous = self.state_history[-1] if self.state_history else new_state
        self.state_history.append(new_state)

        # Optionally apply quantum zeno effect
        if self.enable_zeno:
            self._zeno_stabilize(len(self.state_history) - 1)

        # Optionally apply topological code protection
        if self.enable_toric:
            self.apply_toric_code(len(self.state_history) - 1)

        # Update triadic aliveness
        self._update_aliveness()

    def _update_aliveness(self):
        """
        Internal method to run the triadic check on the
        last two states + current futures.
        """
        if len(self.state_history) < 2:
            # With only one state, presence can be partial,
            # difference is undefined, potential might be pending
            # Let's define a basic condition:
            self.alive = is_present(self.state_history[0])
            return

        current = self.state_history[-1]
        previous = self.state_history[-2]
        self.alive = is_fast_time_active(current, previous, self.futures)

    def _zeno_stabilize(self, t: int):
        """
        Quantum Zeno effect: If the norm of the current state < zeno_threshold,
        project it to some basis (here, a simple [1,0]) for demonstration.
        """
        current = self.state_history[t]
        norm_val = np.linalg.norm(current)
        if norm_val < self.zeno_threshold and norm_val > 0:
            # project to [1,0,...] with same dimension:
            stabilized = np.zeros_like(current)
            stabilized[0] = 1.0
            self.state_history[t] = stabilized

    def apply_toric_code(self, t: int):
        """
        Placeholder for topological error correction (e.g., toric code).
        In real usage, you'd encode 'self.state[t]' into a logical qubit representation.
        """
        # For now, just a pass or demonstration code:
        # e.g. self.state_history[t] = ToricCode.encode(self.state_history[t])
        pass

    @property
    def current_state(self) -> Optional[np.ndarray]:
        """
        Convenient property to access the latest state.
        """
        if self.state_history:
            return self.state_history[-1]
        return None

    @property
    def all_states(self) -> List[np.ndarray]:
        """
        Access the entire state history, if needed.
        """
        return self.state_history

    def is_alive(self) -> bool:
        """
        External accessor for the triadic aliveness condition.
        """
        return self.alive

    def __repr__(self):
        return (f"<NoorFastTimeCore alive={self.alive}, "
                f"steps={len(self.state_history)}, "
                f"rho={self.rho:.2f}, lambda_={self.lambda_:.2f}, "
                f"zeno={self.enable_zeno}, toric={self.enable_toric}>")
