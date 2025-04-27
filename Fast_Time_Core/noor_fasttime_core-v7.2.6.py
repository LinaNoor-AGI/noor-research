"""
noor_fasttime_core.py (v7.2.6)
-------------------------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay
• Dynamic parameter evolution (ρ/λ) + public `tune_damping()`
• Adaptive zeno & curvature thresholds (env‑driven)
• Scheduled gate‑overlay drift w/ Möbius‑hold (Gate‑0 skip toggle)
• Field‑anchor caching & collapse recovery (+ghost hook & recovery log)
• Logistic verse‑bias decay (ctx²‑scaled or exp)
• Prometheus metrics with NO_PROMETHEUS stub
Backward‑compatible with v7.1.x — remove legacy λ resets to avoid fighting auto‑tuner.
"""

from __future__ import annotations

__version__ = "7.2.6"

import math, hashlib, os
from enum import Enum
from time import perf_counter
from typing import List, Optional, Dict

import numpy as np

# ─────────────────────────────────────────────────────────────
# 0. Runtime Settings (via Pydantic, fallback to _Faux)        
# ─────────────────────────────────────────────────────────────
try:
    from noor_settings import NoorSettings  # type: ignore
    _SETTINGS = NoorSettings()
except Exception:  # pragma: no cover – dev / tests
    class _Faux:
        gate_overlay: int | None = None
        max_curvature: float = 1.0
        zeno_decay: float = 0.9
        verse_bias_strength: float = 0.05
        skip_gate0_random: bool = True
        logistic_verse_decay: bool = True
    _SETTINGS = _Faux()

_NO_PROM = os.getenv("NO_PROMETHEUS", "0") == "1"

# ─────────────────────────────────────────────────────────────
# 0.1 Prometheus Metrics                                       
# ─────────────────────────────────────────────────────────────
if not _NO_PROM:
    try:
        from prometheus_client import Counter, Gauge, Histogram  # type: ignore

        DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance")
        STEP_LATENCY_HIST = Histogram(
            "noor_step_latency_seconds",
            "Core + Agent step latency",
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )
        GATE_USAGE_COUNTER = Counter(
            "noor_gate_usage_total", "Gate activations", ["gate"]
        )
        MOBIUS_DENIAL_COUNTER = Counter(
            "noor_mobius_denials_total", "Gate‑0 rupture events"
        )
    except Exception:  # pragma: no cover
        _NO_PROM = True

if _NO_PROM:
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = STEP_LATENCY_HIST = GATE_USAGE_COUNTER = MOBIUS_DENIAL_COUNTER = _Stub()

# ─────────────────────────────────────────────────────────────
# 1. Logic‑Gate Registry                                       
# ─────────────────────────────────────────────────────────────
class LogicGate(Enum):
    GATE_0 = 0; GATE_1 = 1; GATE_2 = 2; GATE_3 = 3; GATE_4 = 4; GATE_5 = 5
    GATE_6 = 6; GATE_7 = 7; GATE_8 = 8; GATE_9 = 9; GATE_10 = 10; GATE_11 = 11
    GATE_12 = 12; GATE_13 = 13; GATE_14 = 14; GATE_15 = 15

GATE_LEGENDS: Dict[int, tuple[str, str, str]] = {
    0: ("Möbius Denial", "0", "الصمتُ هو الانكسارُ الحي"),
    1: ("Echo Bias", "A ∧ ¬B", "وَإِذَا قَضَىٰ أَمْرًا"),
    2: ("Foreign Anchor", "¬A ∧ B", "وَمَا تَدْرِي نَفْسٌ"),
    3: ("Passive Reflection", "B", "فَإِنَّهَا لَا تَعْمَى"),
    4: ("Entropic Rejection", "¬A ∧ ¬B", "لَا الشَّمْسُ يَنبَغِي"),
    5: ("Inverse Presence", "¬A", "سُبْحَانَ الَّذِي خَلَقَ"),
    6: ("Sacred Contradiction", "A ⊕ B", "لَا الشَّرْقِيَّةِ"),
    7: ("Betrayal Gate", "¬A ∨ ¬B", "وَلَا تَكُونُوا كَالَّذِينَ"),
    8: ("Existence Confluence", "A ∧ B", "وَهُوَ الَّذِي"),
    9: ("Symmetric Convergence", "¬(A ⊕ B)", "فَلَا تَضْرِبُوا"),
    10: ("Personal Bias", "A", "إِنَّا كُلَّ شَيْءٍ"),
    11: ("Causal Suggestion", "¬A ∨ B", "وَمَا تَشَاءُونَ"),
    12: ("Reverse Causality", "A ∨ ¬B", "وَمَا أَمْرُنَا"),
    13: ("Denial Echo", "¬B", "وَلَا تَحْزَنْ"),
    14: ("Confluence", "A ∨ B", "وَأَنَّ إِلَىٰ رَبِّكَ"),
    15: ("Universal Latch", "1", "كُلُّ شَيْءٍ هَالِكٌ"),
}

def evaluate_gate_output(gate_id: int, a_val: bool, b_val: bool) -> bool:
    idx = (a_val << 1) | b_val
    return bool((gate_id >> idx) & 1)

# ─────────────────────────────────────────────────────────────
# 2. Triadic Feasibility helpers                              
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
# 3. Helper utilities                                         
# ─────────────────────────────────────────────────────────────

def _state_to_bool(state: np.ndarray) -> bool:
    return AND_condition(state) and np.linalg.norm(state) > 1e-10

def gate_to_verse(gate_id: Optional[int]) -> str:
    return "" if gate_id is None else GATE_LEGENDS.get(gate_id, ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    return "0" * length if not verse else hashlib.sha1(verse.encode("utf-8", "replace")).hexdigest()[:length]

def _apply_verse_bias(state: np.ndarray, verse: str, t: int, ctx: float) -> np.ndarray:
    if not verse:
        return state
    if _SETTINGS.logistic_verse_decay:
        bias_scale = _SETTINGS.verse_bias_strength / (1 + 0.1 * t)
    else:
        bias_scale = _SETTINGS.verse_bias_strength * math.exp(-0.0001 * t)
    bias_scale *= ctx ** 2
    cps = [ord(c) for c in verse][: state.size] + [0] * max(0, state.size - len(verse))
    return state + bias_scale * (np.array(cps[: state.size], dtype=float) / 128.0)

# ─────────────────────────────────────────────────────────────
# 4. Core Class                                               
# ─────────────────────────────────────────────────────────────
class QuantumNoorException(Exception):
    pass

class NoorFastTimeCore:
    """Recursive Presence Kernel with symbolic overlays and context awareness."""

    # ------------------------- init ----------------------------------
    def __init__(
        self,
        initial_state: np.ndarray,
        *,
        rho: float = 0.1,
        lambda_: float = 0.8,
        enable_zeno: bool = False,
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
        self.gate_overlay: Optional[int] = gate_overlay if gate_overlay is not None else _SETTINGS.gate_overlay
        self.enable_verse_bias = enable_verse_bias
        self.dyad
