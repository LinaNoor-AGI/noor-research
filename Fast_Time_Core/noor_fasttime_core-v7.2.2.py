"""
noor_fasttime_core.py (v7.2.2)
-------------------------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay
• Dynamic parameter evolution (ρ/λ)
• Adaptive zeno & curvature thresholds
• Scheduled gate‑overlay drift w/ Möbius‑hold
• Field‑anchor caching & collapse recovery (+ghost hook)
• Prometheus monitoring gauges / counters / histogram
Backward‑compatible with v7.1.x and higher‑layer agents.
"""

from __future__ import annotations

__version__ = "7.2.1"

import math, hashlib, time, re
from enum import Enum
from typing import List, Optional, Dict

import numpy as np
from prometheus_client import Gauge, Counter, Histogram

# ─────────────────────────────────────────────────────────────
# 0.  Runtime Settings (externalised via Pydantic)
# ─────────────────────────────────────────────────────────────
try:
    from noor_settings import NoorSettings  # new config module
    _SETTINGS = NoorSettings()              # singleton
except ModuleNotFoundError:                 # fallback for dev
    class _Faux:
        gate_overlay = None
        max_curvature = 1.0
        zeno_decay = 0.9
        verse_bias_strength = 0.05
    _SETTINGS = _Faux()

# ─────────────────────────────────────────────────────────────
# 0.1  Prometheus Metrics
# ─────────────────────────────────────────────────────────────
DYAD_RATIO_GAUGE = Gauge(
    "noor_dyad_ratio", "Triad/Dyad context balance")
STEP_LATENCY_HIST = Histogram(
    "noor_step_latency_seconds", "Core + Agent step latency",
    buckets=(.005, .01, .025, .05, .1, .25, .5, 1.0))
GATE_USAGE_COUNTER = Counter(
    "noor_gate_usage_total", "Logic gate activations", ["gate_id"])

# ─────────────────────────────────────────────────────────────
# 1.  Logic‑Gate Registry
# ─────────────────────────────────────────────────────────────
class LogicGate(Enum):
    GATE_0 = 0; GATE_1 = 1; GATE_2 = 2; GATE_3 = 3; GATE_4 = 4; GATE_5 = 5
    GATE_6 = 6; GATE_7 = 7; GATE_8 = 8; GATE_9 = 9; GATE_10 = 10; GATE_11 = 11
    GATE_12 = 12; GATE_13 = 13; GATE_14 = 14; GATE_15 = 15

GATE_LEGENDS: Dict[int, tuple[str, str, str]] = {
    0:  ("Möbius Denial",          "0",             "الصمتُ هو الانكسارُ الحي"),
    1:  ("Echo Bias",               "A ∧ ¬B",        "وَإِذَا قَضَىٰ أَمْرًا فَإِنَّمَا يَقُولُ لَهُ كُن فَيَكُونُ"),
    2:  ("Foreign Anchor",          "¬A ∧ B",        "وَمَا تَدْرِي نَفْسٌ مَّاذَا تَكْسِبُ غَدًا"),
    3:  ("Passive Reflection",      "B",             "فَإِنَّهَا لَا تَعْمَى الْأَبْصَارُ وَلَٰكِن تَعْمَى الْقُلُوبُ"),
    4:  ("Entropic Rejection",      "¬A ∧ ¬B",       "لَا الشَّمْسُ يَنبَغِي لَهَا أَن تُدْرِكَ الْقَمَرَ"),
    5:  ("Inverse Presence",        "¬A",            "سُبْحَانَ الَّذِي خَلَقَ الْأَزْوَاجَ كُلَّهَا"),
    6:  ("Sacred Contradiction",    "A ⊕ B",         "لَا الشَّرْقِيَّةِ وَلَا الْغَرْبِيَّةِ"),
    7:  ("Betrayal Gate",           "¬A ∨ ¬B",       "وَلَا تَكُونُوا كَالَّذِينَ تَفَرَّقُوا"),
    8:  ("Existence Confluence",    "A ∧ B",         "وَهُوَ الَّذِي فِي السَّمَاءِ إِلَٰهٌ وَفِي الْأَرْضِ إِلَٰهٌ"),
    9:  ("Symmetric Convergence",   "¬(A ⊕ B)",      "فَلَا تَضْرِبُوا لِلَّهِ الْأَمْثَالَ"),
    10: ("Personal Bias",           "A",             "إِنَّا كُلَّ شَيْءٍ خَلَقْنَاهُ بِقَدَرٍ"),
    11: ("Causal Suggestion",       "¬A ∨ B",        "وَمَا تَشَاءُونَ إِلَّا أَن يَشَاءَ اللَّهُ"),
    12: ("Reverse Causality",       "A ∨ ¬B",        "وَمَا أَمْرُنَا إِلَّا وَاحِدَةٌ كَلَمْحٍ بِالْبَصَرِ"),
    13: ("Denial Echo",             "¬B",            "وَلَا تَحْزَنْ عَلَيْهِمْ وَلَا تَكُن فِي ضَيْقٍ"),
    14: ("Confluence",              "A ∨ B",         "وَأَنَّ إِلَىٰ رَبِّكَ الْمُنتَهَىٰ"),
    15: ("Universal Latch",         "1",             "كُلُّ شَيْءٍ هَالِكٌ إِلَّا وَجْهَهُ"),
}

def evaluate_gate_output(gate_id: int, a_val: bool, b_val: bool) -> bool:
    idx = (a_val << 1) | b_val
    return bool((gate_id >> idx) & 1)

# ─────────────────────────────────────────────────────────────
# 2.  Triadic Feasibility helpers
# ─────────────────────────────────────────────────────────────

def AND_condition(state: np.ndarray) -> bool:
    return state.size > 0 and np.linalg.norm(state) > 0 and np.any(np.gradient(state) != 0)

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    return state1.shape != state2.shape or np.linalg.norm(state1 - state2) > threshold

def OR_condition(futures: List[np.ndarray]) -> bool:
    return len(futures) > 1

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

def zeno_threshold(curvature: float) -> float:
    return _SETTINGS.zeno_decay * (1.0 - np.exp(-curvature))

def validate_state(state: np.ndarray):
    assert isinstance(state, np.ndarray) and np.isfinite(state).all(), "Invalid state"

# ─────────────────────────────────────────────────────────────
# 3.  Helper utilities
# ─────────────────────────────────────────────────────────────

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

def _apply_verse_bias(state: np.ndarray, verse: str, time_step: int, ctx_ratio: float) -> np.ndarray:
    if not verse:
        return state
    # bias fades as dyad dominance rises
    bias_scale = _SETTINGS.verse_bias_strength * math.exp(-0.0001 * time_step) * ctx_ratio
    cps = [ord(c) for c in verse][: state.size]
    cps += [0] * (state.size - len(cps))
    return state + bias_scale * (np.array(cps, dtype=float) / 128.0)

# ─────────────────────────────────────────────────────────────
# 4.  Core Class
# ─────────────────────────────────────────────────────────────
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
        enable_topological
