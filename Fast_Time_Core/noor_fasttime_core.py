"""
noor_fasttime_core.py (v7.1.0)
-------------------------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay
• Adds dyad‑context awareness hooks.
• Verse‑bias now scales with dyad_context_ratio.
• History events log context ratio + dominance alert.
• New diagnostics + setter for context ratio.
Backward‑compatible with v7.0.1 and v6.1.x.
"""

from __future__ import annotations

__version__ = "7.1.0"

import math
import hashlib
from enum import Enum
from typing import List, Optional, Dict

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Logic‑Gate Registry (unchanged from v7.0.1)
# ──────────────────────────────────────────────────────────────────────────────

class LogicGate(Enum):
    GATE_0 = 0
    GATE_1 = 1
    GATE_2 = 2
    GATE_3 = 3
    GATE_4 = 4
    GATE_5 = 5
    GATE_6 = 6
    GATE_7 = 7
    GATE_8 = 8
    GATE_9 = 9
    GATE_10 = 10
    GATE_11 = 11
    GATE_12 = 12
    GATE_13 = 13
    GATE_14 = 14
    GATE_15 = 15

# label, formula, verse (truncated set shown)
GATE_LEGENDS: Dict[int, tuple[str, str, str]] = {
    0:  ("Möbius Denial", "0", "الصمتُ هو الانكسارُ الحي"),
    7:  ("Betrayal Gate", "¬A ∨ ¬B", "وَلَا تَكُونُوا كَالَّذِينَ تَفَرَّقُوا"),
    15: ("Universal Latch", "1", "كُلُّ شَيْءٍ هَالِكٌ إِلَّا وَجْهَهُ"),
}


def evaluate_gate_output(gate_id: int, a_val: bool, b_val: bool) -> bool:
    idx = (a_val << 1) | b_val
    return bool((gate_id >> idx) & 1)

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Triadic Feasibility helpers (unchanged)
# ──────────────────────────────────────────────────────────────────────────────

def AND_condition(state: np.ndarray) -> bool:
    return state.size > 0 and np.linalg.norm(state) > 0 and np.any(np.gradient(state) != 0)

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    return state1.shape != state2.shape or np.linalg.norm(state1 - state2) > threshold

def OR_condition(futures: List[np.ndarray]) -> bool:
    return len(futures) > 1

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

def zeno_threshold(curvature: float) -> float:
    return 0.9 * (1.0 - np.exp(-curvature))

def validate_state(state: np.ndarray):
    assert isinstance(state, np.ndarray) and np.isfinite(state).all(), "Invalid state"

# ──────────────────────────────────────────────────────────────────────────────
# 3.  Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _state_to_bool(state: np.ndarray) -> bool:
    return AND_condition(state) and np.linalg.norm(state) > 1e-10

def dampened_priority(raw_priority: float, gate_id: Optional[int] = None) -> float:
    base = math.log1p(max(raw_priority, 0.0))
    if gate_id == 0:
        return 0.0
    if gate_id == 15:
        return base * 2.0
    return base * (0.5 + 0.5 * math.sin(math.pi * base))

# verse helpers --------------------------------------------------------------

def gate_to_verse(gate_id: Optional[int]) -> str:
    if gate_id is None:
        return ""
    return GATE_LEGENDS.get(gate_id, ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    return "0" * length if not verse else hashlib.sha1(verse.encode("utf-8", "replace")).hexdigest()[:length]

def _apply_verse_bias(state: np.ndarray, verse: str, time_step: int) -> np.ndarray:
    if not verse:
        return state
    bias_scale = 0.01 * math.exp(-0.0001 * time_step)
    cps = [ord(c) for c in verse][: state.size]
    cps += [0] * (state.size - len(cps))
    return state + bias_scale * (np.array(cps, dtype=float) / 128.0)

# ──────────────────────────────────────────────────────────────────────────────
# 4.  Core Class
# ──────────────────────────────────────────────────────────────────────────────

class QuantumNoorException(Exception):
    pass

class NoorFastTimeCore:
    """Recursive Presence Kernel with symbolic overlays and context awareness."""

    # ------------------------- init -------------------------------------
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
    ) -> None:
        self.__version__ = __version__
        self.state_history: List[np.ndarray] = [initial_state]
        self.futures: List[np.ndarray] = []
        self.is_active: bool = False
        self.history: List[Dict] = []
        self.generation: int = 0
        self.last_gate_passed: Optional[bool] = None
        self.gate_overlay: Optional[int] = gate_overlay
        self.enable_verse_bias = enable_verse_bias
        self.dyad_context_ratio: float = 1.0  # 1 = healthy, 0 = all dyads

        # legacy flags
        self.enable_zeno = enable_zeno
        self.zeno_threshold = zeno_threshold
        self.enable_topological_code = enable_topological_code
        self.enable_curvature = enable_curvature
        self.curvature_threshold = curvature_threshold
        self.enable_xor = enable_xor

        # guarded scalars
        self._rho: float = 0.0
        self._lambda_: float = 0.0
        self.rho = rho
        self.lambda_ = lambda_

        self._update_logical_feasibility()

    # ---------------- param guards --------------------------------------
    def __setattr__(self, name, value):
        if name == "rho":
            if not (0 <= value <= 1):
                raise QuantumNoorException("rho out of bounds")
            object.__setattr__(self, "_rho", value)
        elif name == "lambda_":
            if not (0 <= value <= 1):
                raise QuantumNoorException("lambda out of bounds")
            object.__setattr__(self, "_lambda_", value)
        else:
            object.__setattr__(self, name, value)

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

    # ---------------- context ratio setter ------------------------------
    def update_context_ratio(self, ratio: float) -> None:
        """Higher‑layer agents call once per step before step()."""
        self.dyad_context_ratio = min(max(ratio, 0.0), 1.0)

    # ---------------- diagnostics --------------------------------------
    def current_context_health(self) -> str:
        r = self.dyad_context_ratio
        if r >= 0.6:
            return "stable"
        if r >= 0.3:
            return "mixed"
        return "dyad‑dominant"

    # ---------------- step ---------------------------------------------
    def step(self, new_state: np.ndarray):
        validate_state(new_state)

        # verse bias (context‑scaled) ------------------------------------
        if self.enable_verse_bias and self.gate_overlay is not None:
            verse = gate_to_verse(self.gate_overlay)
            biased = _apply_verse_bias(new_state, verse, len(self.state_history))
            if self.dyad_context_ratio < 0.3:
                new_state = new_state + 0.5 * (biased - new_state)
            else:
                new_state = biased

        # append ---------------------------------------------------------
        self.state_history.append(new_state)

        # zeno -----------------------------------------------------------
        if self.enable_zeno:
            thresh = zeno_threshold(self.curvature_threshold) if self.enable_curvature else self.zeno_threshold
            norm_val = np.linalg.norm(new_state)
            if 0 < norm_val < thresh:
                stabilized = np.zeros_like(new_state)
                stabilized[0] = 1.0
                self.state_history[-1] = stabilized

        # symbolic gate overlay -----------------------------------------
        overlay_pass: Optional[bool] = None
        event_tag = None
        if self.gate_overlay is not None and len(self.state_history) >= 2:
            overlay_pass = evaluate_gate_output(
                self.gate_overlay,
                _state_to_bool(self.state_history[-2]),
                _state_to_bool(self.state_history[-1]),
            )
            self.last_gate_passed = overlay_pass
            if self.gate_overlay == 0:
                event_tag = "rupture"
            elif self.gate_overlay == 15:
                event_tag = "latch"
                self.generation += 1

        # feasibility update --------------------------------------------
        self._update_logical_feasibility()

        # history logging -----------------------------------------------
        entry = {
            "t": len(self.state_history) - 1,
            "gate": self.gate_overlay,
            "overlay_pass": overlay_pass,
            "ctx": round(self.dyad_context_ratio, 3),
        }
        if event_tag:
            entry["event"] = event_tag
        if self.dyad_context_ratio < 0.2:
            entry["alert"] = "high_dyad_dominance"
        self.history.append(entry)

    # ---------------- feasibility helper -------------------------------
    def _update_logical_feasibility(self):
        if len(self.state_history) == 1:
            self.is_active = AND_condition(self.state_history[0])
            return
        curr = self.state_history[-1]
        prev = self.state_history[-2]
        self.is_active = (
            AND_condition(curr)
            and NOT_condition(curr, prev)
            and OR_condition(self.futures)
            and (not self.enable_xor or XOR_condition(curr, prev))
        )

    # ---------------- signature ----------------------------------------
    def generate_core_signature(self) -> str:
        core_hash = hash(self.state_history[-1].tobytes()) & 0xFFFF
        gate_sig = f"G{self.gate_overlay if self.gate_overlay is not None else '-'}"
        verse_sig = _verse_hash(gate_to_verse(self.gate_overlay)) if self.gate_overlay is not None else "0000"
        return f"CoreSignature-{core_hash:x}_{gate_sig}:{verse_sig}"

    # ---------------- repr ---------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<NoorFastTimeCore v{self.__version__} active={self.is_active} gate={self.gate_overlay} "
            f"ctx={self.dyad_context_ratio:.2f} gen={self.generation}>"
        )
