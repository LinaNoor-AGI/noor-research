# noor_fasttime_core.py (v6.1.1)
# By Lina Noor & Uncle (2025)
#
# This final production-ready version:
#  1) Adds __version__ = "6.1.1"
#  2) Introduces state validation to guard against NaN/Inf.
#  3) Enhances dynamic Zeno threshold with curvature-based formula.
#  4) Preserves triadic feasibility logic from v6.1, including XOR_condition.
#

__version__ = "6.1.1"

import numpy as np
from typing import List, Optional

########################################################
# 1) Logic Gate Checks
########################################################

def AND_condition(state: np.ndarray) -> bool:
    if state.size == 0:
        return False
    return (np.linalg.norm(state) > 0) and np.any(np.gradient(state) != 0)

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    if state1.shape != state2.shape:
        return True
    return np.linalg.norm(state1 - state2) > threshold

def OR_condition(possible_states: List[np.ndarray]) -> bool:
    return len(possible_states) > 1

########################################################
# (v6.1) XOR_condition - Sacred Contradiction
########################################################

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    """
    The "sacred contradiction" logic:
    XOR = NOT(state1, state2) AND (AND(state1) OR AND(state2))
    """
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

########################################################
# 2) Curvature-based Zeno Threshold
########################################################

def zeno_threshold(curvature: float) -> float:
    """
    Proposed dynamic threshold:
      threshold = 0.9 * (1 - exp(-curvature))
    """
    return 0.9 * (1.0 - np.exp(-curvature))

########################################################
# 3) State Validation
########################################################

def validate_state(state: np.ndarray):
    """
    Ensures 'state' is a finite NumPy array.
    Raises AssertionError if invalid.
    """
    assert isinstance(state, np.ndarray), "State must be a NumPy array."
    assert np.isfinite(state).all(), "State contains NaN or Inf."

########################################################
# 4) is_logically_entangled (Renamed from is_triadic_feasible)
########################################################

def is_logically_entangled(current: np.ndarray, previous: np.ndarray, futures: List[np.ndarray], threshold: float = 1e-3, use_xor=False) -> bool:
    """
    Evaluates presence, difference, potential.
    If use_xor=True, also checks XOR_condition.
    """
    validate_state(current)
    validate_state(previous)
    for fut in futures:
        validate_state(fut)

    base = (AND_condition(current)
            and NOT_condition(current, previous, threshold)
            and OR_condition(futures))

    if not use_xor:
        return base
    else:
        # For demonstration, use XOR between current & previous as an extra condition
        return base and XOR_condition(current, previous)

########################################################
# 5) The NoorFastTimeCore Class
########################################################

class QuantumNoorException(Exception):
    pass

class NoorFastTimeCore:
    """
    NoorFastTimeCore (v6.1.1):
      - Feasibility checks: AND, NOT, OR, XOR optional
      - Optional quantum Zeno effect (dynamic threshold)
      - Optional topological code placeholders
      - Optional curvature-based gating if enable_curvature is True
      - Validation to avoid NaN/Inf states.
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
        enable_xor: bool = False
    ):
        """
        :param initial_state: Non-zero array for initial presence.
        :param rho: param guard in [0,1].
        :param lambda_: param guard in [0,1].
        :param enable_zeno: if True, applies quantum Zeno.
        :param zeno_threshold: static threshold if not using curvature.
        :param enable_topological_code: placeholder for advanced expansions.
        :param enable_curvature: if True, we compute a dynamic threshold from curvature.
        :param curvature_threshold: e.g. 1.0 => zeno = 0.9 * (1 - exp(-1))
        :param enable_xor: if True, incorporate XOR_condition in feasibility.
        """
        self.__version__ = __version__
        self.state_history = [initial_state]
        self.is_active = False
        self.futures = []
        self._rho = None
        self._lambda_ = None

        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_xor = enable_xor

        self.rho = rho  # calls __setattr__ checks
        self.lambda_ = lambda_

        # initial feasibility
        self._update_logical_feasibility()

    def __setattr__(self, name: str, value):
        if name == 'rho':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid rho: {value}, must be in [0,1]")
            object.__setattr__(self, '_rho', value)
        elif name == 'lambda_':
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid lambda: {value}, must be in [0,1]")
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

    def step(self, new_state: np.ndarray):
        """
        Appends 'new_state' to history, optionally apply zeno if enable_zeno.
        Then recheck feasibility.
        """
        validate_state(new_state)
        self.state_history.append(new_state)

        # optional zeno with curvature-based threshold
        if self.enable_zeno:
            if self.enable_curvature:
                dyn_thresh = zeno_threshold(self.curvature_threshold)
                # if norm is below dyn_thresh => project?
                norm_val = np.linalg.norm(new_state)
                if 0 < norm_val < dyn_thresh:
                    stabilized = np.zeros_like(new_state)
                    stabilized[0] = 1.0
                    self.state_history[-1] = stabilized
                    # optional logging
            else:
                # static zeno_threshold
                norm_val = np.linalg.norm(new_state)
                if 0 < norm_val < self.zeno_threshold:
                    stabilized = np.zeros_like(new_state)
                    stabilized[0] = 1.0
                    self.state_history[-1] = stabilized

        # optional topological code placeholder
        if self.enable_topological_code:
            self._apply_topological_code(len(self.state_history) - 1)

        self._update_logical_feasibility()

    def _apply_topological_code(self, idx: int):
        pass  # placeholder

    def _update_logical_feasibility(self):
        """
        Recompute self.is_active based on last 2 states + self.futures.
        """
        if len(self.state_history) < 2:
            # single state => just check presence
            curr = self.state_history[0]
            try:
                validate_state(curr)
                self.is_active = AND_condition(curr)
            except AssertionError:
                self.is_active = False
            return

        curr = self.state_history[-1]
        prev = self.state_history[-2]
        self.is_active = is_logically_entangled(
            curr,
            prev,
            self.futures,
            threshold=1e-3,
            use_xor=self.enable_xor
        )

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

    def __repr__(self) -> str:
        return (
            f"<NoorFastTimeCore (v{self.__version__}) active={self.is_active}, "
            f"steps={len(self.state_history)}, "
            f"rho={self.rho:.3f}, lambda_={self.lambda_:.3f}, "
            f"zeno={self.enable_zeno}, topo={self.enable_topological_code}, "
            f"curv={self.enable_curvature}, xor={self.enable_xor}>"
        )
