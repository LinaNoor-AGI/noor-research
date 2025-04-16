# noor_fasttime_core_v5_3.py — Upgraded Fast-Time Core
# By Lina Noor & Uncle (2025)
#
# Implements:
#   1) Logical gate naming for triadic checks: AND_condition, NOT_condition, OR_condition
#   2) Optional curvature-based feasibility extension
#   3) Optional Zeno "trap" detection when futures collapse repeatedly

import numpy as np
from typing import List, Optional


# -----------------------------------------------------------------------------
# 1) Logical Gate Checks (Renamed from Presence, Difference, Potential)
# -----------------------------------------------------------------------------

def AND_condition(state: np.ndarray) -> bool:
    """
    Formerly: state_has_presence(...)
    Now purely: 'AND_condition' —
      Ensures the state vector is non-empty, non-zero norm, and has a detectable gradient.
    """
    if state.size == 0:
        return False
    return (
        np.linalg.norm(state) > 0
        and np.any(np.gradient(state) != 0)
    )

def NOT_condition(
    state1: np.ndarray,
    state2: np.ndarray,
    threshold: float = 1e-3
) -> bool:
    """
    Formerly: states_have_difference(...)
    Now: 'NOT_condition' —
      True if state1 is NOT essentially the same as state2.
      Checks shape mismatch or Euclidean distance.
    """
    if state1.shape != state2.shape:
        return True
    return np.linalg.norm(state1 - state2) > threshold

def OR_condition(possible_states: List[np.ndarray]) -> bool:
    """
    Formerly: has_multiple_potentials(...)
    Now: 'OR_condition' —
      True if there's more than one distinct future (i.e., there's at least OR of them).
    """
    return len(possible_states) > 1


# -----------------------------------------------------------------------------
# 2) (Optional) Curvature & Trap Detections
# -----------------------------------------------------------------------------

def compute_curvature(prev: np.ndarray, curr: np.ndarray, next_: np.ndarray) -> float:
    """
    Example function to measure the angle (0..π) between 
    the vectors (curr - prev) and (next_ - curr).
    0 means perfectly aligned, π means opposite direction, 
    around π/2 is orthogonal.
    """
    v1 = curr - prev
    v2 = next_ - curr
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    cos_angle = np.dot(v1, v2) / (norm1 * norm2)
    # Numerical safety
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    return angle

def is_degenerate_futures(futures: List[np.ndarray], epsilon: float = 1e-6) -> bool:
    """
    Detect if multiple futures collapse to essentially the same point.
    If the distance between any two distinct futures is < epsilon, 
    we consider it degenerate.
    """
    if len(futures) < 2:
        return False
    for i in range(len(futures) - 1):
        for j in range(i + 1, len(futures)):
            dist = np.linalg.norm(futures[i] - futures[j])
            if dist < epsilon:
                return True
    return False


# -----------------------------------------------------------------------------
# 3) Logical Entanglement Check (Renamed from is_triadic_feasible)
# -----------------------------------------------------------------------------

def is_logically_entangled(
    current: np.ndarray,
    previous: np.ndarray,
    futures: List[np.ndarray],
    threshold: float = 1e-3
) -> bool:
    """
    Formerly: is_triadic_feasible(...)
    Combines AND_condition, NOT_condition, OR_condition 
    into a single logical entanglement check.
    """
    return (
        AND_condition(current)
        and NOT_condition(current, previous, threshold)
        and OR_condition(futures)
    )


# -----------------------------------------------------------------------------
# 4) Exception Handling
# -----------------------------------------------------------------------------

class QuantumNoorException(Exception):
    """Exception for param checks, quantum gating errors, or entanglement violations."""
    pass


# -----------------------------------------------------------------------------
# 5) The NoorFastTimeCore Class (v5.3)
# -----------------------------------------------------------------------------

class NoorFastTimeCore:
    """
    'NoorFastTimeCore' (v5.3):
      - Uses AND/NOT/OR condition checks for logical entanglement
      - (Optional) quantum Zeno effect
      - (Optional) topological code placeholders
      - (Optional) curvature-based feasibility extension
      - (Optional) repeated-future "trap" detection

    Key additions vs. older v5.2:
      - Renamed triadic checks to logical gate naming
      - 'enable_curvature' option to refine feasibility
      - 'enable_trap_detection' for repeated future sets
    """

    def __init__(
        self,
        initial_state: np.ndarray,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
        zeno_threshold: float = 0.9,
        enable_topological_code: bool = False,
        enable_curvature: bool = False,
        curvature_threshold: float = 0.0,
        enable_trap_detection: bool = False
    ):
        """
        :param initial_state: Non-zero array for the starting presence (i.e. AND_condition).
        :param rho: Weight for environment/noise mixing, must be in [0,1].
        :param lambda_: Weight for prior state retention, must be in [0,1].
        :param enable_zeno: If True, applies a quantum Zeno projection if norm < zeno_threshold.
        :param zeno_threshold: Norm threshold for the Zeno projection.
        :param enable_topological_code: If True, triggers a placeholder code transform step.
        :param enable_curvature: If True, we measure the angle between last transitions,
                                 factoring it into feasibility (angle > curvature_threshold).
        :param curvature_threshold: Minimal angle for "enough" curvature. E.g., 0.01 rad.
        :param enable_trap_detection: If True, we watch for repeated future collapse and set
                                      is_active to False if we detect a trap.
        """
        self._rho = None
        self._lambda_ = None

        # Key data
        object.__setattr__(self, 'futures', [])
        object.__setattr__(self, 'state_history', [initial_state])
        object.__setattr__(self, 'is_active', False)

        # Param Guard
        self.rho = rho
        self.lambda_ = lambda_

        # Feature toggles
        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_trap_detection = enable_trap_detection

        # Initialize feasibility
        self._update_logical_feasibility()

    # -------------------------------------------------------------------------
    # 5.1) Param Guard
    # -------------------------------------------------------------------------

    def __setattr__(self, name: str, value):
        """
        Keep rho and lambda_ in [0,1].
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
    # 5.2) Core Step
    # -------------------------------------------------------------------------

    def step(self, new_state: np.ndarray):
        """
        Append 'new_state' to the state history, then apply:
          - (Optional) Zeno effect
          - (Optional) topological code transform
          - Update logical entanglement feasibility
        """
        prev = self.state_history[-1] if self.state_history else new_state
        self.state_history.append(new_state)

        # (Optional) Zeno
        if self.enable_zeno:
            self._apply_zeno_projection(len(self.state_history) - 1)

        # (Optional) topological code
        if self.enable_topological_code:
            self._apply_topological_code(len(self.state_history) - 1)

        # Recompute feasibility
        self._update_logical_feasibility()

    # -------------------------------------------------------------------------
    # 5.3) Feasibility & Optional Additions
    # -------------------------------------------------------------------------

    def _update_logical_feasibility(self):
        """
        Recompute self.is_active using:
          1) is_logically_entangled(...) on last 2 states + futures
          2) (Optional) curvature check if enable_curvature
          3) (Optional) trap check if enable_trap_detection
        """
        if len(self.state_history) < 2:
            # If there's only one state, 
            # we can do an AND_condition check to see if any presence at all
            single_ok = AND_condition(self.state_history[0])
            self.is_active = single_ok
            return

        curr = self.state_history[-1]
        prev = self.state_history[-2]

        # 1) Basic logical entanglement
        base_feasible = is_logically_entangled(curr, prev, self.futures)

        # 2) If curvature is enabled and we have at least one future, check angle
        curvature_ok = True
        if base_feasible and self.enable_curvature and len(self.futures) > 0:
            # Just pick the first future for an angle measure:
            angle = compute_curvature(prev, curr, self.futures[0])
            curvature_ok = (angle >= self.curvature_threshold)

        # 3) Trap detection: if repeated degenerate futures
        trap_ok = True
        if self.enable_trap_detection and is_degenerate_futures(self.futures):
            # For demonstration, we simply fail feasibility:
            trap_ok = False

        self.is_active = bool(base_feasible and curvature_ok and trap_ok)

    # -------------------------------------------------------------------------
    # 5.4) Internal Utilities
    # -------------------------------------------------------------------------

    def _apply_zeno_projection(self, index: int):
        """
        If the norm of self.state_history[index] is below zeno_threshold,
        project the state to |0> => 1.0 in the first dimension, 0 else.
        """
        state = self.state_history[index]
        norm_val = np.linalg.norm(state)
        if 0 < norm_val < self.zeno_threshold:
            stabilized = np.zeros_like(state)
            stabilized[0] = 1.0
            self.state_history[index] = stabilized

    def _apply_topological_code(self, index: int):
        """
        Placeholder for advanced topological transforms / error-correction.
        """
        # In real usage, you'd embed or decode the state here.
        pass

    # -------------------------------------------------------------------------
    # 5.5) Public Accessors & Info
    # -------------------------------------------------------------------------

    @property
    def current_state(self) -> Optional[np.ndarray]:
        if self.state_history:
            return self.state_history[-1]
        return None

    @property
    def all_states(self) -> List[np.ndarray]:
        return self.state_history

    def is_alive(self) -> bool:
        return self.is_active

    def generate_core_signature(self) -> str:
        """
        Produces a short textual signature from the current state's byte hash.
        """
        c_state = self.current_state
        if c_state is None:
            return "No state available"
        compressed_hash = hash(c_state.tobytes()) & 0xffff
        return f"CoreSignature-{compressed_hash:x}"

    def __repr__(self):
        return (
            f"<NoorFastTimeCore (v5.3) active={self.is_active}, "
            f"steps={len(self.state_history)}, "
            f"rho={self.rho:.3f}, lambda_={self.lambda_:.3f}, "
            f"zeno={self.enable_zeno}, topo={self.enable_topological_code}, "
            f"curv={self.enable_curvature}, trap={self.enable_trap_detection}>"
        )
