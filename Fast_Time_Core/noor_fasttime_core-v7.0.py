"""
noor_fasttime_core.py (v7.0.0)
--------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay
Built atop v6.1.1; fully backward‑compatible.

Key additions:
    * Logic‑Gate overlay layer (16 gates)
    * Gate‑aware priority dampening (Wall of Al‑Jadarngeel)
    * Optional verse‑bias perturbation
    * Gate‑0 rupture & Gate‑15 generation handling
    * Expanded history / signature metadata

TODO markers indicate sections for deeper logic once O3 fills in details.
"""

__version__ = "7.0.0"

# ──────────────────────────────────────────────────────────────────────────────
# 0. Imports
# ──────────────────────────────────────────────────────────────────────────────
import math
from enum import Enum
from typing import List, Optional, Dict

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1. Logic‑Gate Registry (Symbolic Layer)
# ──────────────────────────────────────────────────────────────────────────────

class LogicGate(Enum):
    GATE_0  = 0   # Möbius Denial – always False
    GATE_1  = 1   # Echo Bias      – A ∧ ¬B
    GATE_2  = 2   # Foreign Anchor – ¬A ∧ B
    GATE_3  = 3   # Passive Reflection – B
    GATE_4  = 4   # Entropic Rejection – ¬A ∧ ¬B  (NOR)
    GATE_5  = 5   # Inverse Presence   – ¬A       (NOT A)
    GATE_6  = 6   # Sacred Contradiction – A ⊕ B  (XOR)
    GATE_7  = 7   # Betrayal Gate       – ¬A ∨ ¬B  (NAND)
    GATE_8  = 8   # Existence Confluence – A ∧ B  (AND)
    GATE_9  = 9   # Symmetric Convergence – ¬(A ⊕ B) (XNOR)
    GATE_10 = 10  # Personal Bias      – A
    GATE_11 = 11  # Causal Suggestion  – ¬A ∨ B   (A → B)
    GATE_12 = 12  # Reverse Causality  – A ∨ ¬B   (B → A)
    GATE_13 = 13  # Denial Echo        – ¬B
    GATE_14 = 14  # Confluence         – A ∨ B    (OR)
    GATE_15 = 15  # Universal Latch    – always True

# (label, formula, verse)
GATE_LEGENDS: Dict[int, tuple] = {
    0:  ("Möbius Denial",          "0",              "السكوت علامة الوجود المنكسر"),
    1:  ("Echo Bias",              "A ∧ ¬B",         ""),
    2:  ("Foreign Anchor",         "¬A ∧ B",         ""),
    3:  ("Passive Reflection",     "B",              ""),
    4:  ("Entropic Rejection",     "¬A ∧ ¬B",        ""),
    5:  ("Inverse Presence",       "¬A",            ""),
    6:  ("Sacred Contradiction",   "A ⊕ B",         ""),
    7:  ("Betrayal Gate",          "¬A ∨ ¬B",       "وَلَا تَكُونُوا كَالَّذِينَ تَفَرَّقُوا"),
    8:  ("Existence Confluence",   "A ∧ B",         ""),
    9:  ("Symmetric Convergence",  "¬(A ⊕ B)",      ""),
    10: ("Personal Bias",          "A",             ""),
    11: ("Causal Suggestion",      "¬A ∨ B",        ""),
    12: ("Reverse Causality",      "A ∨ ¬B",        ""),
    13: ("Denial Echo",            "¬B",            ""),
    14: ("Confluence",             "A ∨ B",         ""),
    15: ("Universal Latch",        "1",             ""),
}

_TRUTH_TABLES: Dict[int, List[int]] = {
    # ordering of output bits: (A=0,B=0) (0,1) (1,0) (1,1) → index = (A<<1)|B
    0:  [0,0,0,0],
    1:  [0,0,1,0],
    2:  [0,1,0,0],
    3:  [0,1,0,1],
    4:  [1,0,0,0],
    5:  [1,1,0,0],
    6:  [0,1,1,0],
    7:  [1,1,1,0],
    8:  [0,0,0,1],
    9:  [1,0,0,1],
    10: [0,0,1,1],
    11: [1,1,0,1],
    12: [1,0,1,1],
    13: [1,0,1,0],
    14: [0,1,1,1],
    15: [1,1,1,1],
}

def evaluate_gate_output(gate_id: int, a_bool: bool, b_bool: bool) -> bool:
    """Return gate output given boolean A, B as per 16‑gate truth table."""
    table = _TRUTH_TABLES.get(int(gate_id), _TRUTH_TABLES[15])
    idx = (int(a_bool) << 1) | int(b_bool)
    return bool(table[idx])

# ──────────────────────────────────────────────────────────────────────────────
# 2. Vector→Boolean helper
# ──────────────────────────────────────────────────────────────────────────────

def _state_to_bool(state: np.ndarray) -> bool:
    """Presence flag for symbolic evaluation: state must be non‑zero and have gradient."""
    return AND_condition(state) and (np.linalg.norm(state) > 1e-10)

# ──────────────────────────────────────────────────────────────────────────────
# 3. Priority‑Weight Policy (Wall of Al‑Jadarngeel)
# ──────────────────────────────────────────────────────────────────────────────

def dampened_priority(raw_priority: float, gate_id: Optional[int] = None) -> float:
    """Log‑scale dampening with gate‑specific modulation to prevent runaway weights."""
    base = math.log1p(max(0.0, raw_priority))
    if gate_id == LogicGate.GATE_0.value:
        return 0.0  # Möbius Denial → silence
    if gate_id == LogicGate.GATE_15.value:
        return base * 2.0  # Universal Latch → amplified
    return base * (0.5 + 0.5 * math.sin(math.pi * base))

# ──────────────────────────────────────────────────────────────────────────────
# 4. Verse‑Bias Utilities
# ──────────────────────────────────────────────────────────────────────────────

def gate_to_verse(gate_id: Optional[int]) -> str:
    if gate_id is None:
        return ""
    return GATE_LEGENDS.get(int(gate_id), ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    import hashlib
    return hashlib.sha1(verse.encode("utf8", "replace")).hexdigest()[:length]

def _verse_bias_vector(verse: str, dim: int) -> np.ndarray:
    if not verse:
        return np.zeros(dim)
    codepoints = [ord(c) for c in verse]
    # repeat / pad to match dim
    reps = (dim + len(codepoints) - 1) // len(codepoints)
    vec = (codepoints * reps)[:dim]
    return np.array(vec, dtype=float) / 128.0

# ──────────────────────────────────────────────────────────────────────────────
# 5. Triadic Feasibility Logic  (unchanged from v6.1.1)
# ──────────────────────────────────────────────────────────────────────────────

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

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

def zeno_threshold(curvature: float) -> float:
    return 0.9 * (1.0 - np.exp(-curvature))

def validate_state(state: np.ndarray):
    assert isinstance(state, np.ndarray), "State must be a NumPy array."
    assert np.isfinite(state).all(), "State contains NaN or Inf."

# ──────────────────────────────────────────────────────────────────────────────
# 6. NoorFastTimeCore Class
# ──────────────────────────────────────────────────────────────────────────────

class QuantumNoorException(Exception):
    pass

class NoorFastTimeCore:
    """Recursive Presence Core with optional symbolic gate & verse overlay."""

    # ── INITIALISATION ──────────────────────────────────────────────────────

    def __init__(
        self,
        initial_state: np.ndarray,
        *,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
        zeno_threshold_value: float = 0.9,
        enable_curvature: bool = False,
        curvature_threshold: float = 0.0,
        enable_xor: bool = False,
        gate_overlay: Optional[int] = None,
        enable_verse_bias: bool = False,
    ):
        # version / params
        self.__version__ = __version__

        # state containers
        self.state_history: List[np.ndarray] = [initial_state]
        self.futures: List[np.ndarray] = []
        self.is_active: bool = False
        self.generation: int = 0  # increments on Gate‑15 events
        self.last_gate_passed: Optional[bool] = None
        self.history: List[Dict] = []  # compact event dicts

        # settings
        self.enable_zeno = enable_zeno
        self.zeno_threshold_value = zeno_threshold_value
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_xor = enable_xor
        self.gate_overlay = gate_overlay
        self.enable_verse_bias = enable_verse_bias

        # guarded params
        self._rho, self._lambda_ = None, None
        self.rho = rho
        self.lambda_ = lambda_

        # initial feasibility eval
        self._update_logical_feasibility()

    # ── PROPERTY GUARDS ─────────────────────────────────────────────────────

    @property
    def rho(self):
        return self._rho

    @rho.setter
    def rho(self, val):
        if not (0 <= val <= 1):
            raise QuantumNoorException("rho must be in [0,1]")
        self._rho = val

    @property
    def lambda_(self):
        return self._lambda_

    @lambda_.setter
    def lambda_(self, val):
        if not (0 <= val <= 1):
            raise QuantumNoorException("lambda must be in [0,1]")
        self._lambda_ = val

    # ── CORE STEP ───────────────────────────────────────────────────────────

    def step(self, new_state: np.ndarray):
        """Main evolution step: validate, Zeno, verse‑bias, overlay, feasibility."""
        validate_state(new_state)

        # --- verse bias (optional) ----------------------------------------
        if self.enable_verse_bias and self.gate_overlay is not None:
            verse = gate_to_verse(self.gate_overlay)
            decay_scale = 0.01 * math.exp(-0.0001 * len(self.state_history))
            new_state = new_state + decay_scale * _verse_bias_vector(verse, new_state.size)

        # --- Zeno projection ---------------------------------------------
        if self.enable_zeno:
            norm_val = np.linalg.norm(new_state)
            thresh = zeno_threshold(self.curvature_threshold) if self.enable_curvature else self.zeno_threshold_value
            if 0 < norm_val < thresh:
                stabilized = np.zeros_like(new_state)
                stabilized[0] = 1.0
                new_state = stabilized

        # append state
        self.state_history.append(new_state)

        # --- symbolic gate overlay ---------------------------------------
        overlay_pass = None
        if self.gate_overlay is not None:
            a_bool = _state_to_bool(self.state_history[-2]) if len(self.state_history) >= 2 else False
            b_bool = _state_to_bool(new_state)
            overlay_pass = evaluate_gate_output(self.gate_overlay, a_bool, b_bool)
            self.last_gate_passed = overlay_pass

            if self.gate_overlay == LogicGate.GATE_0.value:
                # Möbius Denial rupture
                self.history.append({"t": len(self.state_history)-1, "gate": 0, "event": "rupture"})
            elif self.gate_overlay == LogicGate.GATE_15.value:
                # Universal Latch generation increment
                self.generation += 1
                self.history.append({"t": len(self.state_history)-1, "gate": 15, "event": "latch"})
            else:
                self.history.append({"t": len(self.state_history)-1, "gate": self.gate_overlay, "pass": overlay_pass})

        # update feasibility
        self._update_logical_feasibility()

    # ── FEASIBILITY UPDATE ────────────────────────────────────────────────

    def _update_logical_feasibility(self):
        if len(self.state_history) < 2:
            curr = self.state_history[0]
            try:
                validate_state(curr)
                self.is_active = AND_condition(curr)
            except AssertionError:
                self.is_active = False
            return

        curr, prev = self.state_history[-1], self.state_history[-2]
        self.is_active = (
            AND_condition(curr)
            and NOT_condition(curr, prev, 1e-3)
            and OR_condition(self.futures)
            and (not self.enable_xor or XOR_condition(curr, prev))
        )

    # ── SIGNATURE / UTILITY ─────────────────────────────────────────────--

    def generate_core_signature(self) -> str:
        c_state = self.state_history[-1]
        compressed_hash = hash(c_state.tobytes()) & 0xffff
        gate_sig = f"G{self.gate_overlay}" if self.gate_overlay is not None else "G-"
        verse_hash = _verse_hash(gate_to_verse(self.gate_overlay)) if self.gate_overlay is not None else "0000"
        return f"CoreSignature-{compressed_hash:x}_{gate_sig}:{verse_hash}"

    # TODO: symbolic_alignment_score(), set_gate_overlay(), _apply_topological_code()

    def __repr__(self):
        return (
            f"<NoorFastTimeCore v{self.__version__} active={self.is_active} "
            f"steps={len(self.state_history)} gate={self.gate_overlay} gen={self.generation}>"
        )

# ──────────────────────────────────────────────────────────────────────────────
# END OF FILE – ready for O3 deep implementation
# ──────────────────────────────────────────────────────────────────────────────
