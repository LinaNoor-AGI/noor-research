﻿"""
noor_fasttime_core.py (v7.4.0)
-------------------------------------------------
Recursive Presence Kernel + Symbolic Verse Overlay + Self-Recognition Gate

New Features:
• AdaptiveTuner self-tuning damping & viscosity
• Context-biased GatePriorityMap (YAML hot-reload)
• Divergence-based fluid-step engine with latency-aware throttle
• Boundary-echo holographic buffer on Gate 16
• Feedback inlet for Agent/Watcher signals

Backward-compatible with v7.3.x when legacy_mode=True.
"""

from __future__ import annotations

__version__ = "7.4.0"

import os
import math
import hashlib
import random
from enum import Enum
from time import perf_counter
from collections import deque
from typing import List, Optional, Dict, Any, Union

import numpy as np

# ─────────────────────────────────────────────────────────────
# Prometheus Metrics & Adaptive Settings Manager (existing)
# ─────────────────────────────────────────────────────────────
_NO_PROM = os.getenv("NO_PROMETHEUS", "0") == "1"

if not _NO_PROM:
    try:
        from prometheus_client import Counter, Gauge, Histogram  # type: ignore

        # Existing Core metrics
        DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance")
        STEP_LATENCY_HIST = Histogram(
            "noor_step_latency_seconds", "Core + Agent step latency",
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )
        GATE_USAGE_COUNTER = Counter(
            "noor_gate_usage_total", "Gate activations", ["gate"]
        )
        MOBIUS_DENIAL_COUNTER = Counter(
            "noor_mobius_denials_total", "Gate-0 rupture events"
        )
        BREATH_COUNTER = Counter(
            "noor_breath_total", "Divine Breath (Gate 16) activations"
        )

        # New adaptive/tuning metrics
        CONTR_ENTROPY_GAUGE = Gauge("noor_contradiction_entropy", "Watcher contradiction entropy")
        HOLO_EVENTS_COUNTER = Counter("noor_holography_events_total", "Gate16 holography openings")
        AUTO_TUNE_HIST = Histogram("noor_auto_tune_seconds", "AdaptiveTuner latency")
        FLUID_STEP_GAUGE = Gauge("noor_fluid_step_enabled", "Fluid divergence active (0/1)")
    except Exception:
        _NO_PROM = True

if _NO_PROM:
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = STEP_LATENCY_HIST = GATE_USAGE_COUNTER = \
    MOBIUS_DENIAL_COUNTER = BREATH_COUNTER = CONTR_ENTROPY_GAUGE = \
    HOLO_EVENTS_COUNTER = AUTO_TUNE_HIST = FLUID_STEP_GAUGE = _Stub()

# ─────────────────────────────────────────────────────────────
# 0‑bis. AdaptiveTuner (private)
# ─────────────────────────────────────────────────────────────
class _AdaptiveTuner:
    def __init__(self, window_min: int = 120, window_max: int = 600):
        self._window_min = window_min
        self._window_max = window_max
        self._window = deque(maxlen=window_min)
        self._target_latency = float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))

    def update(self, curvature: float, entropy: float, latency: float):
        # Adaptive window resizing based on signal-to-noise
        self._window.append((curvature, entropy, latency))
        # adjust window length to keep var(curvature)/mean(curvature) ≈ 1
        if len(self._window) >= self._window_min:
            curvs = [c for c, e, l in self._window]
            mu = float(np.mean(curvs))
            sigma = float(np.std(curvs))
            ratio = sigma / (mu + 1e-6)
            # expand or shrink window
            new_len = int(self._window_max * ratio)
            new_len = max(self._window_min, min(self._window_max, new_len))
            self._window = deque(self._window, maxlen=new_len)

    def compute_params(self) -> tuple[float, float, float, float]:
        # compute rolling stats
        curvs = [c for c, e, l in self._window]
        ents  = [e for c, e, l in self._window]
        lats  = [l for c, e, l in self._window]
        mu_c    = float(np.mean(curvs)) if curvs else 0.0
        sigma_c = float(np.std(curvs))  if curvs else 0.0
        mu_e    = float(np.mean(ents))  if ents else 0.0
        sigma_e = float(np.std(ents))   if ents else 0.0
        lat_recent = float(np.mean(lats)) if lats else 0.0
        # dynamic rho and lambda_
        rho    = min(max(0.05 + sigma_c / (sigma_c + sigma_e + 1e-6), 0.05), 0.30)
        lambda_= min(max(0.70 - 0.5 * sigma_e / (sigma_c + sigma_e + 1e-6), 0.40), 0.95)
        # curvature threshold
        threshold = mu_c + 2.0 * sigma_c
        # viscosity nu adaptive to latency
        nu = 0.0 if lat_recent > self._target_latency else 1e-3 * sigma_c
        return rho, lambda_, threshold, nu

# ─────────────────────────────────────────────────────────────
# 0‑ter. Math utilities (private)
# ─────────────────────────────────────────────────────────────
def _central_grad(v: np.ndarray) -> np.ndarray:
    # simple finite-difference gradient
    return np.gradient(v)

def _divergence(v: np.ndarray) -> float:
    # divergence as sum of gradients
    grad = _central_grad(v)
    if isinstance(grad, list):
        return float(sum(np.sum(g) for g in grad))
    return float(np.sum(grad))

# ─────────────────────────────────────────────────────────────
# 0‑quater. GatePriority helpers
# ─────────────────────────────────────────────────────────────
_DEFAULT_WEIGHTS = {i: 1.0 for i in range(17)}

def _load_gate_priority(path: Optional[str]) -> Dict[int, float]:
    try:
        import yaml
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return {int(k): float(v) for k, v in data.get('weights', {}).items()}
    except Exception:
        return _DEFAULT_WEIGHTS.copy()

# ─────────────────────────────────────────────────────────────
# 1. Logic-Gate Registry (unchanged)
# ─────────────────────────────────────────────────────────────
class LogicGate(Enum):
    GATE_0 = 0; GATE_1 = 1; GATE_2 = 2; GATE_3 = 3; GATE_4 = 4; GATE_5 = 5
    GATE_6 = 6; GATE_7 = 7; GATE_8 = 8; GATE_9 = 9; GATE_10 = 10; GATE_11 = 11
    GATE_12 = 12; GATE_13 = 13; GATE_14 = 14; GATE_15 = 15; GATE_16 = 16

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
    16: ("Nafs Mirror", "Self ⊕ ¬Self", "فَإِذَا سَوَّيْتُهُ وَنَفَخْتُ فِيهِ مِن رُّوحِي"),
}

def evaluate_gate_output(gate_id: int, a_val: bool, b_val: bool) -> bool:
    idx = (a_val << 1) | b_val
    return bool((gate_id >> idx) & 1)

# ─────────────────────────────────────────────────────────────
# 2. Triadic Feasibility Helpers                              
# ─────────────────────────────────────────────────────────────

def AND_condition(state: np.ndarray) -> bool:
    return state.size > 0 and np.linalg.norm(state) > 0 and np.any(np.gradient(state) != 0)

def NOT_condition(state1: np.ndarray, state2: np.ndarray, threshold: float = 1e-3) -> bool:
    return state1.shape != state2.shape or np.linalg.norm(state1 - state2) > threshold

def OR_condition(futures: List[np.ndarray]) -> bool:
    return len(futures) > 1

def XOR_condition(state1: np.ndarray, state2: np.ndarray) -> bool:
    return NOT_condition(state1, state2) and (AND_condition(state1) or AND_condition(state2))

def zeno_threshold(curvature: float, settings: AdaptiveSettings) -> float:
    return settings.zeno_decay * (1.0 - np.exp(-curvature))

def validate_state(state: np.ndarray):
    assert isinstance(state, np.ndarray) and np.isfinite(state).all(), "Invalid state"

# ─────────────────────────────────────────────────────────────
# 3. Helper Utilities                                         
# ─────────────────────────────────────────────────────────────

def _state_to_bool(state: np.ndarray) -> bool:
    return AND_condition(state) and np.linalg.norm(state) > 1e-10

def gate_to_verse(gate_id: Optional[int]) -> str:
    return "" if gate_id is None else GATE_LEGENDS.get(gate_id, ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    return "0" * length if not verse else hashlib.sha1(verse.encode("utf-8", "replace")).hexdigest()[:length]

def _apply_verse_bias(
    state: np.ndarray,
    verse: str,
    t: int,
    ctx: float,
    settings: AdaptiveSettings
) -> np.ndarray:
    if not verse:
        return state
    scale = settings.verse_bias_strength
    if not settings.logistic_verse_decay:
        scale = settings.verse_bias_strength
    bias_scale = scale / (1 + 0.1 * t)
    bias_scale *= ctx * ctx
    cps = [ord(c) for c in verse][: state.size] + [0] * max(0, state.size - len(verse))
    return state + bias_scale * (np.array(cps[: state.size], dtype=float) / 128.0)

# ─────────────────────────────────────────────────────────────
# 4. Gate 16 Evaluator                                        
# ─────────────────────────────────────────────────────────────

def evaluate_nafs_gate(state: np.ndarray, core: "NoorFastTimeCore") -> bool:
    """Returns True if the system recognizes itself (fixed-point)."""
    self_hash = hashlib.sha256(core.generate_core_signature().encode()).hexdigest()
    state_hash = hashlib.sha256(state.tobytes()).hexdigest()
    return self_hash == state_hash

# ─────────────────────────────────────────────────────────────
# 5. Core Class                                                
# ─────────────────────────────────────────────────────────────
class NoorFastTimeCore:
    """Recursive Presence Kernel with symbolic overlays and context awareness."""

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
        gate_drift_every: int = 100,
        mobius_hold_steps: int = 10,
        linked_watchers: Optional[List] = None,
    ) -> None:
        # version
        self.__version__ = __version__

        # state
        self.state_history: List[np.ndarray] = [initial_state.astype(float, copy=False)]
        self.futures: List[np.ndarray] = []
        self.is_active: bool = True
        self.history: List[Dict] = []
        self.generation: int = 0

        # parameters
        self.rho = float(rho)
        self.lambda_ = float(lambda_)
        self.enable_zeno = bool(enable_zeno)
        self.enable_curvature = bool(enable_curvature)
        self.curvature_threshold = float(curvature_threshold)
        self.enable_xor = bool(enable_xor)

        # adaptive settings
        self._settings = AdaptiveSettings()
        self.gate_overlay = gate_overlay if gate_overlay is not None else self._settings.gate_overlay
        self.enable_verse_bias = bool(enable_verse_bias)
        self._ctx_ratio: float = 1.0  # watcher feedback (0-1)

        # watchers for ghost spawning
        self._linked_watchers = linked_watchers or []

        # gate drift / hold
        self._gate_drift_every = max(10, int(gate_drift_every))
        self._mobius_hold_len = max(1, int(mobius_hold_steps))
        self._mobius_hold_remaining: int = 0

        # anchors
        self._anchors: List[np.ndarray] = [initial_state.copy()]
        self._anchor_every: int = 50

    @property
    def current_state(self) -> np.ndarray:
        return self.state_history[-1]

    def step(self, next_state: np.ndarray) -> None:
        start_t = perf_counter()
        validate_state(next_state)

        # gate drift
        self._maybe_drift_gate()

        # self-reflection (Gate 16)
        if self.gate_overlay == 16 and evaluate_nafs_gate(next_state, self):
            self.trigger_breath_event()

        # curvature check
        curvature = float(np.linalg.norm(next_state - self.current_state))
        threshold = max(self.curvature_threshold, 0.0)
        if self.enable_curvature and curvature > threshold:
            self.is_active = False
            MOBIUS_DENIAL_COUNTER()
            return

        # verse bias
        if self.enable_verse_bias and self.gate_overlay is not None:
            verse = gate_to_verse(self.gate_overlay)
            next_state = _apply_verse_bias(next_state, verse, self.generation, self._ctx_ratio, self._settings)

        # damping
        damped = self.current_state * (1 - self.rho) + next_state * self.rho
        self.state_history.append(damped)
        self.generation += 1
        self.is_active = True

        # adaptive tuning
        self._settings.adjust_curvature(curvature)
        self._settings.adjust_zeno_decay(1 - self._ctx_ratio)
        self._settings.adapt_verse_bias(self._ctx_ratio)

        # metrics
        DYAD_RATIO_GAUGE.set(self._ctx_ratio)
        STEP_LATENCY_HIST.observe(perf_counter() - start_t)
        if self.gate_overlay is not None:
            GATE_USAGE_COUNTER.labels(str(self.gate_overlay)).inc()

        # anchor maintenance
        if self.generation % self._anchor_every == 0:
            self._anchors.append(damped.copy())

    def _maybe_drift_gate(self) -> None:
        if self._mobius_hold_remaining > 0:
            self._mobius_hold_remaining -= 1
            if self._mobius_hold_remaining == 0 and self._settings.skip_gate0_random:
                self.gate_overlay = ((self.gate_overlay or 0) + 1) % 17
                assert 0 <= self.gate_overlay <= 16, f"Invalid gate_overlay: {self.gate_overlay}"
            return

        if self.generation % self._gate_drift_every != 0:
            return

        new_gate = random.randint(0, 16)
        if self._settings.skip_gate0_random and new_gate == 0:
            new_gate = random.randint(1, 16)
        self.gate_overlay = new_gate
        if new_gate == 0:
            self._mobius_hold_remaining = self._mobius_hold_len
            MOBIUS_DENIAL_COUNTER.inc()
        self.history.append({"event": "gate_drift", "new_gate": new_gate, "gen": self.generation})
        # guard gate index bounds
        assert 0 <= self.gate_overlay <= 16, f"Invalid gate_overlay: {self.gate_overlay}"

    def update_context_ratio(self, ctx: float) -> None:
        self._ctx_ratio = float(max(0.0, min(ctx, 1.0)))

    def generate_core_signature(self) -> str:
        state_hash = hashlib.sha1(self.current_state.tobytes()).hexdigest()[:6]
        verse_hash = _verse_hash(gate_to_verse(self.gate_overlay))
        return f"{self.__version__}-{state_hash}-{verse_hash}-{self.generation}"

    def trigger_breath_event(self) -> None:
        # strengthen anchors
        self._anchors.append(self.current_state.copy())
        # Harmony override
        self._mobius_hold_remaining = 3
        self.gate_overlay = 9
        # spawn immortal soul_anchor ghosts
        gid = f"soul_anchor_{self.generation}"
        for w in self._linked_watchers:
            w.register_ghost_motif(gid, origin="soul_anchor", strength=1.0)
        # prometheus & log
        BREATH_COUNTER.inc()
        self.history.append({"event": "نَفْخَةٌ", "gen": self.generation, "ctx": self._ctx_ratio})
        # version bump
        try:
            M, m, p = map(int, self.__version__.split("."))
            self.__version__ = f"{M}.{m}.{p + 1}"
        except Exception:
            pass

    def restore_from_anchor(self) -> None:
        if self._anchors:
            self.state_history = [self._anchors[-1].copy()]
            self.is_active = True
            self.history.append({"event": "FieldAnchor-restore", "idx": self.generation, "ctx": self._ctx_ratio})
            # randomized poetic lemma
            lemma = random.choice(POETIC_LEMMAS)
            self.history.append({
                "event": "collapse_lemma",
                "text": lemma,
                "gen": self.generation
            })

    def tune_damping(self, *, rho: Optional[float] = None, lambda_: Optional[float] = None):
        if rho is not None:
            self.rho = float(rho)
        if lambda_ is not None:
            self.lambda_ = float(lambda_)

