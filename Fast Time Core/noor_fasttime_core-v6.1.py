# noor_fasttime_core_v6_1.py
# By Lina Noor & Uncle (2025)
#
# This version (v6.1) of the NoorFastTimeCore integrates:
#   1) An XOR_condition gate (the 'sacred contradiction').
#   2) A dynamic Zeno threshold that recalculates if both enable_zeno & enable_curvature are set.
#   3) Optional enable_xor param, toggling XOR usage in logical entanglement.
#

import numpy as np
from typing import List, Optional, Any

########################################
# Logical Gates
########################################

def AND_condition(state: np.ndarray) -> bool:
    """
    True if the state vector is non-empty, non-zero norm, and has a detectable gradient.
    (Presence)
    """
    if state.size == 0:
        return False
    return (
        np.linalg.norm(state) > 0 and np.any(np.gradient(state) != 0)
    )

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    """
    True if state1 is not essentially the same as state2.
    (Difference)
    """
    if state1.shape != state2.shape:
        return True
    return np.linalg.norm(state1 - state2) > threshold

def OR_condition(futures: List[np.ndarray]) -> bool:
    """
    True if there's more than one distinct future.
    (Potential)
    """
    return len(futures) > 1

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    """
    'Sacred Contradiction': true when state1 != state2 and at least one has presence.
    """
    # We define it as: states_have_difference AND (state1 presence OR state2 presence)
    if NOT_condition(state1, state2):
        return AND_condition(state1) or AND_condition(state2)
    return False

########################################
# Triadic / Extended Feasibility
########################################

def is_logically_entangled(
    current: np.ndarray,
    previous: np.ndarray,
    futures: List[np.ndarray],
    threshold: float = 1e-3,
    use_xor: bool = False
) -> bool:
    """
    The default triadic check: AND_condition, NOT_condition, OR_condition.
    If use_xor is True, we also do a contradiction check in some capacity.

    In simplest form:
        (AND(current)) and (NOT(current, previous)) and (OR(futures))
    Then optionally incorporate XOR(current, previous) or XOR among futures.
    """
    base = (
        AND_condition(current)
        and NOT_condition(current, previous, threshold)
        and OR_condition(futures)
    )
    if not base:
        return False

    if use_xor:
        # Example: ensure there's contradiction between current & previous
        # if presence is partial?
        # This can be domain specific. We'll do a simple approach:
        return XOR_condition(current, previous)

    return True

class QuantumNoorException(Exception):
    pass

########################################
# NoorFastTimeCore v6.1
########################################
class NoorFastTimeCore:
    """
    NoorFastTimeCore v6.1
      - Adds XOR_condition logic (toggle via enable_xor)
      - Dynamic Zeno threshold if both enable_zeno & enable_curvature are True.
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
        enable_trap_detection: bool = False,
        enable_xor: bool = False
    ):
        self._rho = None
        self._lambda_ = None

        # Key data
        object.__setattr__(self, 'futures', [])
        object.__setattr__(self, 'state_history', [initial_state])
        object.__setattr__(self, 'is_active', False)

        # Param assignment
        self.rho = rho
        self.lambda_ = lambda_

        # Feature toggles
        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_trap_detection = enable_trap_detection
        self.enable_xor = enable_xor

        # Check feasibility upon creation
        self._update_triadic_feasibility()

    def __setattr__(self, name: str, value: Any):
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

    ########################################
    # Main Step
    ########################################

    def step(self, new_state: np.ndarray):
        prev = self.state_history[-1] if self.state_history else new_state
        self.state_history.append(new_state)

        # (Optional) dynamic Zeno threshold
        # If we have both zeno & curvature
        if self.enable_zeno and self.enable_curvature:
            self.zeno_threshold = 0.9 * (1 - np.exp(-self.curvature_threshold))

        # If zeno applies
        if self.enable_zeno:
            self._apply_zeno_projection(len(self.state_history) - 1)

        # Optional topological code
        if self.enable_topological_code:
            self._apply_topological_code(len(self.state_history) - 1)

        # Recompute feasibility
        self._update_triadic_feasibility()

    def _update_triadic_feasibility(self):
        if len(self.state_history) < 2:
            # Single state => check presence only.
            self.is_active = AND_condition(self.state_history[0])
            return

        curr = self.state_history[-1]
        prev = self.state_history[-2]
        self.is_active = self._check_entanglement(curr, prev, self.futures)

    def _check_entanglement(
        self,
        current: np.ndarray,
        previous: np.ndarray,
        futures: List[np.ndarray]
    ) -> bool:
        base_ok = is_logically_entangled(
            current,
            previous,
            futures,
            threshold=1e-3,
            use_xor=self.enable_xor
        )
        if not base_ok:
            return False

        # If trap detection is on, check for degenerate futures
        if self.enable_trap_detection and self._is_degenerate_futures():
            return False

        return True

    def _is_degenerate_futures(self, epsilon: float = 1e-6) -> bool:
        if len(self.futures) < 2:
            return False
        for i in range(len(self.futures) - 1):
            for j in range(i + 1, len(self.futures)):
                dist = np.linalg.norm(self.futures[i] - self.futures[j])
                if dist < epsilon:
                    return True
        return False

    def _apply_zeno_projection(self, idx: int):
        state = self.state_history[idx]
        norm_val = np.linalg.norm(state)
        if 0 < norm_val < self.zeno_threshold:
            # project to |0>
            stabilized = np.zeros_like(state)
            stabilized[0] = 1.0
            self.state_history[idx] = stabilized

    def _apply_topological_code(self, idx: int):
        # placeholder
        pass

    ########################################
    # Properties
    ########################################

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
        c_state = self.current_state
        if c_state is None:
            return "No state available"
        compressed_hash = hash(c_state.tobytes()) & 0xffff
        return f"CoreSignature-{compressed_hash:x}"

    def __repr__(self):
        return (
            f"<NoorFastTimeCore (v6.1) active={self.is_active}, "
            f"steps={len(self.state_history)}, "
            f"rho={self.rho:.3f}, lambda_={self.lambda_:.3f}, "
            f"zeno={self.enable_zeno}, topo={self.enable_topological_code}, "
            f"curv={self.enable_curvature}, trap={self.enable_trap_detection}, "
            f"xor={self.enable_xor}>"
        )
