# noor_fasttime_core-v5.1.py — The Stable Core
# (Refactored with traditional AI/CS/Math nomenclature)
# By Lina Noor & Uncle (2025)

"""
This module implements a stable AI core with:
  1) Triadic feasibility checks (Presence, Difference, Potential)
  2) Optional Quantum Zeno stabilization
  3) Optional topological code placeholders
  4) A sample "core signature" method producing a simple hash from the current state

Motif or agent-flow logic is deliberately excluded.
"""

import numpy as np
from typing import List, Optional

# -----------------------------------------------------------------------------
# 1) Triadic Utility Checks (Presence, Difference, Potential)
# -----------------------------------------------------------------------------

def state_has_presence(state: np.ndarray) -> bool:
    """
    A state has 'presence' if:
      - It has a non-zero norm
      - It exhibits a detectable gradient along at least one dimension
    """
    if state.size == 0:
        return False
    return (
        np.linalg.norm(state) > 0
        and np.any(np.gradient(state) != 0)
    )

def states_have_difference(
    state1: np.ndarray,
    state2: np.ndarray,
    threshold: float = 1e-3
) -> bool:
    """
    'Difference' between two states exists if their
    Euclidean distance exceeds a given threshold.
    Mismatched dimensionality also implies difference.
    """
    if state1.shape != state2.shape:
        return True
    return np.linalg.norm(state1 - state2) > threshold

def has_multiple_potentials(possible_states: List[np.ndarray]) -> bool:
    """
    A set of possible future states indicates 'potential'
    if it contains more than one distinct next state.
    """
    return len(possible_states) > 1

def is_triadic_feasible(
    current: np.ndarray,
    previous: np.ndarray,
    futures: List[np.ndarray],
    threshold: float = 1e-3
) -> bool:
    """
    Evaluates the triadic condition:
      1) Presence
      2) Difference
      3) Potential
    This function returns True if all conditions hold.
    """
    return (
        state_has_presence(current)
        and states_have_difference(current, previous, threshold)
        and has_multiple_potentials(futures)
    )

# -----------------------------------------------------------------------------
# 2) Optional Exception Handling
# -----------------------------------------------------------------------------

class QuantumNoorException(Exception):
    """
    Exception class for param checks, quantum gating errors,
    or triadic integrity violations.
    """
    pass

# -----------------------------------------------------------------------------
# 3) Core Class: NoorFastTimeCore
# -----------------------------------------------------------------------------

class NoorFastTimeCore:
    """
    'NoorFastTimeCore' maintains:
      - A time-indexed state history
      - Triadic feasibility checks (Presence, Difference, Potential)
      - Optional quantum Zeno effect
      - Optional topological code placeholders
      - Basic param constraints for rho, lambda in [0,1]

    No motif or agent-flow logic should appear here; 
    that belongs in separate agent/watcher modules.
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
        zeno_threshold: float = 0.9,
        enable_topological_code: bool = False
    ):
        """
        :param initial_state: Non-zero array for initial presence.
        :param rho: Weight for environmental/noise mixing, must be in [0,1].
        :param lambda_: Weight for prior state retention, must be in [0,1].
        :param enable_zeno: If True, applies a basic quantum Zeno projection if norm < zeno_threshold.
        :param zeno_threshold: Norm threshold for the Zeno projection.
        :param enable_topological_code: If True, triggers a placeholder code transform step.
        """
        self._rho = None
        self._lambda_ = None

        # Key data structures
        object.__setattr__(self, 'futures', [])
        object.__setattr__(self, 'state_history', [initial_state])
        object.__setattr__(self, 'is_active', False)

        # Assign param-guarded properties
        self.rho = rho
        self.lambda_ = lambda_
        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code

        # Check feasibility upon creation
        self._update_triadic_feasibility()

    # -------------------------------------------------------------------------
    # 3.1) Param Guard
    # -------------------------------------------------------------------------

    def __setattr__(self, name: str, value):
        """
        Ensure 'rho' and 'lambda_' remain within the valid range [0,1].
        """
        if name == 'rho':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid rho (must be in [0,1]): {value}")
            object.__setattr__(self, '_rho', value)
        elif name == 'lambda_':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid lambda (must be in [0,1]): {value}")
            object.__setattr__(self, '_lambda_', value)
        else:
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

    # -------------------------------------------------------------------------
    # 3.2) Core Methods
    # -------------------------------------------------------------------------

    def step(self, new_state: np.ndarray):
        """
        Append 'new_state' to the state history. Then apply:
          - (Optional) quantum Zeno projection
          - (Optional) topological code transform
          - Triadic feasibility re-check
        """
        prev = self.state_history[-1] if self.state_history else new_state
        self.state_history.append(new_state)

        # Optional quantum Zeno effect
        if self.enable_zeno:
            self._apply_zeno_projection(len(self.state_history) - 1)

        # Optional topological code placeholder
        if self.enable_topological_code:
            self._apply_topological_code(len(self.state_history) - 1)

        # Update triadic feasibility (Presence, Difference, Potential)
        self._update_triadic_feasibility()

    def _update_triadic_feasibility(self):
        """
        Recompute 'is_active' based on the last two states + the futures list.
        """
        if len(self.state_history) < 2:
            # If there's only one state, difference is undefined,
            # potential might be pending. 
            # We'll define 'presence' feasibility only:
            self.is_active = state_has_presence(self.state_history[0])
            return

        curr = self.state_history[-1]
        prev = self.state_history[-2]
        self.is_active = is_triadic_feasible(curr, prev, self.futures)

    def _apply_zeno_projection(self, t: int):
        """
        If the norm of self.state_history[t] is below zeno_threshold (and > 0),
        project the state vector to |0> (1.0 in the first index, 0 elsewhere).
        (This is a conceptual demonstration only.)
        """
        current = self.state_history[t]
        norm_val = np.linalg.norm(current)
        if 0 < norm_val < self.zeno_threshold:
            vector_dim = current.shape[0]
            stabilized = np.zeros_like(current)
            stabilized[0] = 1.0
            self.state_history[t] = stabilized

    def _apply_topological_code(self, t: int):
        """
        Placeholder for advanced topological error-correction routines.
        (Currently non-functional. Real usage would embed the state in a
        protective code structure.)
        """
        pass

    # -------------------------------------------------------------------------
    # 3.3) Properties and Helpers
    # -------------------------------------------------------------------------

    @property
    def current_state(self) -> Optional[np.ndarray]:
        """
        Returns the most recent state in the history, or None if empty.
        """
        if self.state_history:
            return self.state_history[-1]
        return None

    @property
    def all_states(self) -> List[np.ndarray]:
        """
        Provides read-only access to the entire time-series of states.
        """
        return self.state_history

    def is_alive(self) -> bool:
        """
        Returns whether triadic feasibility is met.
        """
        return self.is_active

    def generate_core_signature(self) -> str:
        """
        Example demonstration function:
        Produces a short textual signature from the current state's byte hash.
        """
        c_state = self.current_state
        if c_state is None:
            return "No state available"
        compressed_hash = hash(c_state.tobytes()) & 0xffff
        return f"CoreSignature-{compressed_hash:x}"

    def __repr__(self):
        return (f"<NoorFastTimeCore (v5.1) active={self.is_active}, "
                f"steps={len(self.state_history)}, "
                f"rho={self.rho:.3f}, lambda_={self.lambda_:.3f}, "
                f"zeno={self.enable_zeno}, topo={self.enable_topological_code}>")
