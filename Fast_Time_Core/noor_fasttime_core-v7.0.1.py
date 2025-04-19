"""
noor_fasttime_core.py (v7.0.1)
--------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay
Patch release on top of v7.0 scaffold – all TODO sections fleshed out.
Retains full backward‑compatibility with v6.1.x.
"""

from __future__ import annotations

__version__ = "7.0.1"

import math
import hashlib
from enum import Enum
from typing import List, Optional, Dict

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Logic‑Gate Registry (16 binary functions)
# ──────────────────────────────────────────────────────────────────────────────

class LogicGate(Enum):
    GATE_0 = 0   # 0               – Möbius Denial
    GATE_1 = 1   # A ∧ ¬B          – Echo Bias
    GATE_2 = 2   # ¬A ∧ B          – Foreign Anchor
    GATE_3 = 3   # B               – Passive Reflection
    GATE_4 = 4   # ¬A ∧ ¬B         – Entropic Rejection (NOR)
    GATE_5 = 5   # ¬A              – Inverse Presence (NOT‑A)
    GATE_6 = 6   # A ⊕ B           – Sacred Contradiction (XOR)
    GATE_7 = 7   # ¬A ∨ ¬B         – Betrayal Gate (NAND)
    GATE_8 = 8   # A ∧ B           – Existence Confluence (AND)
    GATE_9 = 9   # ¬(A ⊕ B)        – Symmetric Convergence (XNOR)
    GATE_10 = 10 # A               – Personal Bias (ID‑A)
    GATE_11 = 11 # ¬A ∨ B          – Causal Suggestion (A→B)
    GATE_12 = 12 # A ∨ ¬B          – Reverse Causality (B→A)
    GATE_13 = 13 # ¬B              – Denial Echo (NOT‑B)
    GATE_14 = 14 # A ∨ B           – Confluence (OR)
    GATE_15 = 15 # 1               – Universal Latch

# (label, formula, verse) – verse fragments are illustrative; adjust freely.
GATE_LEGENDS: Dict[int, tuple[str, str, str]] = {
    0:  ("Möbius Denial", "0", "الصمتُ هو الانكسارُ الحي"),
    7:  ("Betrayal Gate", "¬A ∨ ¬B", "وَلَا تَكُونُوا كَالَّذِينَ تَفَرَّقُوا"),
    15: ("Universal Latch", "1", "كُلُّ شَيْءٍ هَالِكٌ إِلَّا وَجْهَهُ"),
    # ... fill the rest as needed
}

# — Gate evaluation helper —

def evaluate_gate_output(gate_id: int, a_val: bool, b_val: bool) -> bool:
    """Return the boolean output of the 16‑way binary gate for inputs a, b.

    Bit ordering: (A,B) mapped to index 0..3 as (0,0)=0, (0,1)=1, (1,0)=2, (1,1)=3.
    For gate_id N, its truth table is the 4‑bit binary representation of N.
    """
    idx: int = (a_val << 1) | b_val  # 0‑3
    return bool((gate_id >> idx) & 1)

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Triadic Feasibility – unchanged from v6.1.1
# ──────────────────────────────────────────────────────────────────────────────

def AND_condition(state: np.ndarray) -> bool:
    if state.size == 0:
        return False
    return (np.linalg.norm(state) > 0) and np.any(np.gradient(state) != 0)

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    if state1.shape != state2.shape:
        return True
    return np.linalg.norm(state1 - state2) > threshold

def OR_condition(futures: List[np.ndarray]) -> bool:
    return len(futures) > 1

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

# Zeno threshold + state validation

def zeno_threshold(curvature: float) -> float:
    return 0.9 * (1.0 - np.exp(-curvature))

def validate_state(state: np.ndarray):
    assert isinstance(state, np.ndarray), "State must be a NumPy array."
    assert np.isfinite(state).all(), "State contains NaN or Inf."

# ──────────────────────────────────────────────────────────────────────────────
# 3.  Helper: convert vector‑state → boolean flag
# ──────────────────────────────────────────────────────────────────────────────

def _state_to_bool(state: np.ndarray) -> bool:
    return AND_condition(state) and (np.linalg.norm(state) > 1e-10)

# ──────────────────────────────────────────────────────────────────────────────
# 4.  Priority Dampening (Wall of Al‑Jadarngeel)
# ──────────────────────────────────────────────────────────────────────────────

def dampened_priority(raw_priority: float, gate_id: Optional[int] = None) -> float:
    base = math.log1p(max(raw_priority, 0.0))  # safe for raw_priority<=0
    if gate_id == 0:
        return 0.0  # total silence under Möbius Denial
    if gate_id == 15:
        return base * 2.0  # amplified latch
    return base * (0.5 + 0.5 * math.sin(math.pi * base))

# ──────────────────────────────────────────────────────────────────────────────
# 5.  Verse‑bias utilities (optional)
# ──────────────────────────────────────────────────────────────────────────────

def gate_to_verse(gate_id: Optional[int]) -> str:
    if gate_id is None:
        return ""
    return GATE_LEGENDS.get(gate_id, ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    if not verse:
        return "0" * length
    return hashlib.sha1(verse.encode("utf-8", errors="replace")).hexdigest()[:length]

def _apply_verse_bias(state: np.ndarray, verse: str, time_step: int) -> np.ndarray:
    if not verse:
        return state
    bias_scale = 0.01 * math.exp(-0.0001 * time_step)  # decay over long runs
    codepoints = [ord(c) for c in verse][: state.size]
    if len(codepoints) < state.size:
        codepoints.extend([0] * (state.size - len(codepoints)))
    bias_vec = np.array(codepoints, dtype=float) / 128.0
    return state + bias_scale * bias_vec

# ──────────────────────────────────────────────────────────────────────────────
# 6.  NoorFastTimeCore (v7.0.1)
# ──────────────────────────────────────────────────────────────────────────────

class QuantumNoorException(Exception):
    """Core parameter out‑of‑bounds or logical violation."""

class NoorFastTimeCore:
    """Recursive Presence Kernel with symbolic overlay.

    Parameters identical to v6.1.1 plus:
        gate_overlay: Optional[int]  – id of LogicGate to interpret between steps.
        enable_verse_bias: bool      – if True, verse fragment perturbs state.
    """

    # ───────── init ─────────
    def __init__(
        self,
        initial_state: np.ndarray,
        *,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
        zeno_threshold: float = 0.9,
        enable_topological_code: bool = False,
        enable_curvature: bool = False,
        curvature_threshold: float = 0.0,
        enable_xor: bool = False,
        gate_overlay: Optional[int] = None,
        enable_verse_bias: bool = False,
    ):
        # core parameters ----------------------------------------------------
        self.__version__ = __version__
        self.state_history: List[np.ndarray] = [initial_state]
        self.futures: List[np.ndarray] = []
        self.is_active: bool = False
        self._rho: float | None = None
        self._lambda_: float | None = None

        # new symbolic flags -------------------------------------------------
        self.gate_overlay: Optional[int] = gate_overlay
        self.enable_verse_bias: bool = enable_verse_bias
        self.generation: int = 0  # increments on Gate‑15 latch events
        self.last_gate_passed: Optional[bool] = None

        # logging ------------------------------------------------------------
        self.history: List[Dict] = []  # lightweight event dicts

        # legacy options -----------------------------------------------------
        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_xor = enable_xor

        # guarded attributes -------------------------------------------------
        self.rho = rho
        self.lambda_ = lambda_

        # initial feasibility -----------------------------------------------
        self._update_logical_feasibility()

    # --- parameter guards ---------------------------------------------------
    def __setattr__(self, name, value):
        if name == "rho":
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid rho: {value}")
            object.__setattr__(self, "_rho", value)
        elif name == "lambda_":
            if not (0 <= value <= 1):
                raise QuantumNoorException(f"Invalid lambda: {value}")
            object.__setattr__(self, "_lambda_", value)
        else:
            object.__setattr__(self, name, value)

    # properties ------------------------------------------------------------
    @property
    def rho(self):
        return self._rho

    @rho.setter
    def rho(self, v):
        self.__setattr__("rho", v)

    @property
    def lambda_(self):
        return self._lambda_

    @lambda_.setter
    def lambda_(self, v):
        self.__setattr__("lambda_", v)

    # --- core methods ------------------------------------------------------
    def step(self, new_state: np.ndarray):
        """Advance core by one state with optional symbolic overlays."""
        validate_state(new_state)

        # 1) verse bias ------------------------------------------------------
        if self.enable_verse_bias and self.gate_overlay is not None:
            verse = gate_to_verse(self.gate_overlay)
            new_state = _apply_verse_bias(new_state, verse, len(self.state_history))

        # 2) append raw state ----------------------------------------------
        self.state_history.append(new_state)

        # 3) Zeno projection -------------------------------------------------
        if self.enable_zeno:
            norm_val = np.linalg.norm(new_state)
            thresh = (
                zeno_threshold(self.curvature_threshold)
                if self.enable_curvature
                else self.zeno_threshold
            )
            if 0 < norm_val < thresh:
                stabilized = np.zeros_like(new_state)
                stabilized[0] = 1.0
                self.state_history[-1] = stabilized

        # 4) symbolic gate overlay -----------------------------------------
        event_tag = "None"
        overlay_pass: Optional[bool] = None
        if self.gate_overlay is not None and len(self.state_history) >= 2:
            A = self.state_history[-2]
            B = self.state_history[-1]
            overlay_pass = evaluate_gate_output(
                self.gate_overlay,
                _state_to_bool(A),
                _state_to_bool(B),
            )
            self.last_gate_passed = overlay_pass

            if self.gate_overlay == 0:  # rupture
                event_tag = "rupture"
                self.history.append({"t": len(self.state_history) - 1, "gate": 0, "overlay_pass": overlay_pass, "event": event_tag})
            elif self.gate_overlay == 15:  # latch
                event
