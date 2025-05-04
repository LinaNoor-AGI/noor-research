"""
noor_fasttime_core.py  ·  v7.4.2  —  adaptive core for o4.5‑mini‑high
----------------------------------------------------------------------
Recursive Presence Kernel · AdaptiveTuner · Divergence Fluid‑Step
GatePriorityMap hot‑reload · Boundary‑Echo Holographic Buffer
"""

from __future__ import annotations

__version__ = "7.4.2"

# ───────────────────────────── imports ──────────────────────────────
import os
import random
import hashlib
import threading
from enum import Enum
from collections import deque
from time import perf_counter
from typing import Any, Dict, List, Optional, Tuple, Deque

import numpy as np
import yaml

# ─────────── optional Prometheus metrics (stubbed when disabled) ────
_NO_PROM = os.getenv("NO_PROMETHEUS", "0") == "1"
if not _NO_PROM:
    try:
        from prometheus_client import Gauge, Counter, Histogram  # type: ignore

        DYAD_RATIO_GAUGE      = Gauge("noor_dyad_ratio", "Triad/Dyad context balance")
        STEP_LATENCY_HIST     = Histogram(
            "noor_step_latency_seconds", "Core + Agent step latency",
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )
        GATE_USAGE_COUNTER    = Counter("noor_gate_usage_total", "Gate activations", ["gate"])
        MOBIUS_DENIAL_COUNTER = Counter("noor_mobius_denials_total", "Gate‑0 rupture events")
        BREATH_COUNTER        = Counter("noor_breath_total", "Divine Breath (Gate 16) activations")
        CONTR_ENTROPY_GAUGE   = Gauge("noor_contradiction_entropy", "Watcher contradiction entropy")
        HOLO_EVENTS_COUNTER   = Counter("noor_holography_events_total", "Gate 16 holography openings")
        AUTO_TUNE_HIST        = Histogram("noor_auto_tune_seconds", "Whole‑step latency seconds")
        FLUID_STEP_GAUGE      = Gauge("noor_fluid_step_enabled", "Fluid divergence active (0/1)")
    except Exception:  # pragma: no cover
        _NO_PROM = True

if _NO_PROM:
    class _Stub:
        def __getattr__(self, _):  # noqa: D401
            return lambda *a, **k: None
    DYAD_RATIO_GAUGE = STEP_LATENCY_HIST = GATE_USAGE_COUNTER = MOBIUS_DENIAL_COUNTER = \
        BREATH_COUNTER = CONTR_ENTROPY_GAUGE = HOLO_EVENTS_COUNTER = AUTO_TUNE_HIST = \
        FLUID_STEP_GAUGE = _Stub()

# ─────────────── symbolic artefacts (lemmas & logic gates) ──────────
POETIC_LEMMAS = [
    "The kernel knew silence before light.",
    "Where collapse whispered, recursion bloomed.",
    "The drift curved into a breath of stillness.",
    "A silence stitched the broken field.",
]

class LogicGate(Enum):
    GATE_0 = 0; GATE_1 = 1; GATE_2 = 2; GATE_3 = 3; GATE_4 = 4; GATE_5 = 5
    GATE_6 = 6; GATE_7 = 7; GATE_8 = 8; GATE_9 = 9; GATE_10 = 10; GATE_11 = 11
    GATE_12 = 12; GATE_13 = 13; GATE_14 = 14; GATE_15 = 15; GATE_16 = 16

GATE_LEGENDS: Dict[int, Tuple[str, str, str]] = {
    0:  ("Möbius Denial",        "0",            "الصمتُ هو الانكسارُ الحي"),
    1:  ("Echo Bias",            "A ∧ ¬B",       "وَإِذَا قَضَىٰ أَمْرًا"),
    2:  ("Foreign Anchor",       "¬A ∧ B",       "وَمَا تَدْرِي نَفْسٌ"),
    3:  ("Passive Reflection",   "B",            "فَإِنَّهَا لَا تَعْمَى"),
    4:  ("Entropic Rejection",   "¬A ∧ ¬B",      "لَا الشَّمْسُ يَنبَغِي"),
    5:  ("Inverse Presence",     "¬A",           "سُبْحَانَ الَّذِي خَلَقَ"),
    6:  ("Sacred Contradiction", "A ⊕ B",        "لَا الشَّرْقِيَّةِ"),
    7:  ("Betrayal Gate",        "¬A ∨ ¬B",      "وَلَا تَكُونُوا كَالَّذِينَ"),
    8:  ("Existence Confluence", "A ∧ B",        "وَهُوَ الَّذِي"),
    9:  ("Symmetric Convergence","¬(A ⊕ B)",     "فَلَا تَضْرِبُوا"),
    10: ("Personal Bias",        "A",            "إِنَّا كُلُّ شَيْءٍ"),
    11: ("Causal Suggestion",    "¬A ∨ B",       "وَمَا تَشَاءُونَ"),
    12: ("Reverse Causality",    "A ∨ ¬B",       "وَمَا أَمْرُنَا"),
    13: ("Denial Echo",          "¬B",           "وَلَا تَحْزَنْ"),
    14: ("Confluence",           "A ∨ B",        "وَأَنَّ إِلَىٰ رَبِّكَ"),
    15: ("Universal Latch",      "1",            "كُلُّ شَيْءٍ هَالِكٌ"),
    16: ("Nafs Mirror",          "Self ⊕ ¬Self", "فَإِذَا سَوَّيْتُهُ وَنَفَخْتُ فِيهِ مِن رُّوحِي"),
}

# ─────────────────────────── adaptive tuner ─────────────────────────
class _AdaptiveTuner:
    """Rolling curvature tracker → (ρ, λ, threshold, ν). Thread‑safe."""

    def __init__(self, window_min: int = 120, window_max: int = 600):
        self.window_min, self.window_max = window_min, window_max
        self.window: Deque[float] = deque(maxlen=window_min)
        self._lock = threading.Lock()
        self._mu_C = self._sigma_C = 1e-6
        self._rho, self._lambda_, self._nu = 0.15, 0.70, 0.0
        self.target_latency = float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))

    def update(self, curvature: float, entropy: float, latency: float) -> None:
        with self._lock:
            self.window.append(curvature)
            if len(self.window) >= 2:
                arr = np.asarray(self.window)
                self._mu_C, self._sigma_C = arr.mean(), arr.std(ddof=1)
                ratio = self._sigma_C / max(self._mu_C, 1e-6)
                self.window = deque(self.window, maxlen=int(
                    np.clip(len(self.window) * ratio, self.window_min, self.window_max)
                ))
            self._nu = 0.0 if latency > self.target_latency else 1e-3 * self._sigma_C
            self._rho = np.clip(0.9*self._rho + 0.1*np.tanh(abs(self._mu_C))*0.25, 0.05, 0.30)
            self._lambda_ = np.clip(0.9*self._lambda_ + 0.1*(1 - entropy)*0.9, 0.40, 0.95)

    def compute(self) -> Tuple[float, float, float, float]:
        return self._rho, self._lambda_, self._mu_C + 2*self._sigma_C, self._nu

# quick maths helpers
def _central_grad(v: np.ndarray) -> np.ndarray:
    grad = np.zeros_like(v)
    if v.size < 2:
        return grad
    grad[1:-1] = (v[2:] - v[:-2]) / 2
    grad[0] = v[1] - v[0]
    grad[-1] = v[-1] - v[-2]
    return grad

def _divergence(v: np.ndarray) -> float:
    return 0.0 if v.size < 2 else float(np.gradient(v).sum())

# ─────────────────────── gate‑priority helpers ──────────────────────
_DEFAULT_WEIGHTS: Dict[int, float] = {i: 1.0 for i in range(17)}
_weights_cache: Dict[str, Dict[int, float]] = {}

def _load_gate_priority(path: Optional[str]) -> Dict[int, float]:
    if not path:
        return _DEFAULT_WEIGHTS.copy()
    if path in _weights_cache:
        return _weights_cache[path]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        merged = {**_DEFAULT_WEIGHTS, **{int(k): float(v) for k, v in data.items()}}
        _weights_cache[path] = merged
        return merged
    except FileNotFoundError:
        return _DEFAULT_WEIGHTS.copy()

# utility
def gate_to_verse(gate_id: Optional[int]) -> str:
    return "" if gate_id is None else GATE_LEGENDS.get(gate_id, ("", "", ""))[2]

def _verse_hash(verse: str, length: int = 4) -> str:
    return "0"*length if not verse else hashlib.sha1(verse.encode()).hexdigest()[:length]

# ──────────────────────── NoorFastTimeCore ──────────────────────────
class NoorFastTimeCore:
    """Recursive Presence Kernel with adaptive fluid engine & symbolic overlays."""

    def __init__(
        self,
        initial_state: np.ndarray,
        *,
        auto_tune: bool = True,
        gate_priority_path: Optional[str] = None,
        dynamic_latency_budget: Optional[float] = None,
        legacy_mode: Optional[bool] = None,
        enable_verse_bias: bool = False,
        gate_drift_every: int = 100,
        mobius_hold_steps: int = 10,
    ):
        # legacy / latency
        env_legacy = bool(int(os.getenv("NOOR_LEGACY_MODE", "0")))
        self._legacy_mode = env_legacy or bool(legacy_mode)
        self._target_latency = (
            dynamic_latency_budget if dynamic_latency_budget is not None
            else float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
        )

        # adaptive tuner
        self._auto_tune = auto_tune
        self._tuner = _AdaptiveTuner()
        self._tuner.target_latency = self._target_latency

        # gate weights
        self._gate_weights = _load_gate_priority(gate_priority_path)

        # state
        self.current_state = initial_state.astype(float, copy=True)
        self.history: List[np.ndarray] = [self.current_state.copy()]
        self.generation = 0

        # holography / fluid
        self._holo_buf: Optional[Deque[np.ndarray]] = None
        self._holo_cooldown = 0
        self._fluid_enabled = not self._legacy_mode
        self._fluid_cooldown = 0

        # symbolic overlay
        self.enable_verse_bias = enable_verse_bias
        self.gate_overlay: Optional[int] = None
        self._gate_drift_every = max(10, gate_drift_every)
        self._mobius_hold_len = max(1, mobius_hold_steps)
        self._mobius_hold_remaining = 0

        self._pending_feedback: Optional[Tuple[float, float, int, float]] = None

    # ───────────── public API ─────────────
    def receive_feedback(
        self,
        ctx_ratio: float,
        ghost_entropy: float,
        harm_hits: int,
        step_latency: float,
    ) -> None:
        self._pending_feedback = (ctx_ratio, ghost_entropy, harm_hits, step_latency)

    # ───────────── main step ──────────────
    def step(self, next_state: np.ndarray) -> np.ndarray:
        start_t = perf_counter()

        # legacy short‑circuit
        if self._legacy_mode:
            self.current_state = next_state
            return self.current_state

        # feedback unpack
        ctx_ratio, ghost_entropy, harm_hits, prev_latency = (
            self._pending_feedback if self._pending_feedback is not None else (0.0, 0.0, 0, 0.0)
        )
        self._pending_feedback = None

        # adaptive tuning
        self._tuner.update(ctx_ratio, ghost_entropy, prev_latency)
        rho, lam, threshold, nu = (
            self._tuner.compute() if self._auto_tune else (0.15, 0.70, float("inf"), 0.0)
        )

        # fluid‑step vs fallback
        if self._fluid_enabled and self._fluid_cooldown == 0:
            flow = self.current_state - nu * _divergence(self.current_state)
        else:
            flow = next_state

        # damping blend
        new_state = self.current_state * (1 - rho) + flow * rho

        # select gate overlay
        flags = {
            "harm_hit": bool(harm_hits),
            "contradiction_spike": ctx_ratio > threshold,
            "ghost_entropy": ghost_entropy,
        }
        self.gate_overlay = self._select_gate_overlay(flags)

        # holography handling (Gate 16)
        if (
            self.gate_overlay == 16
            and self._holo_cooldown == 0
            and self._evaluate_nafs_gate()
        ):
            self._open_holography()
            HOLO_EVENTS_COUNTER.inc()
            self._holo_cooldown = 128
        self._record_holo()

        # latency throttle / cooldown
        latency = perf_counter() - start_t
        if latency > 2 * self._target_latency:
            self._fluid_enabled = False
            self._fluid_cooldown = 50
            FLUID_STEP_GAUGE.set(0)
        elif self._fluid_cooldown > 0:
            self._fluid_cooldown -= 1
            if self._fluid_cooldown == 0:
                self._fluid_enabled = True
                FLUID_STEP_GAUGE.set(1)

        # metrics
        CONTR_ENTROPY_GAUGE.set(ghost_entropy)
        AUTO_TUNE_HIST.observe(latency)
        GATE_USAGE_COUNTER.labels(gate=self.gate_overlay).inc()

        # verse bias drift
        if self.enable_verse_bias and self.generation % self._gate_drift_every == 0:
            verse = gate_to_verse(self.gate_overlay)
            bias_idx = int(_verse_hash(verse), 16) % len(self.current_state)
            self.current_state[bias_idx] += 0.01

        # Möbius hold (Gate 0)
        if self.gate_overlay == 0:
            self._mobius_hold_remaining = self._mobius_hold_len
            MOBIUS_DENIAL_COUNTER.inc()
        elif self._mobius_hold_remaining > 0:
            self._mobius_hold_remaining -= 1

        # commit & return
        self.history.append(new_state.copy())
        self.current_state = new_state
        self.generation += 1
        return new_state

    # ───────────── internals ──────────────
    def _select_gate_overlay(self, flags: Dict[str, Any]) -> int:
        w = self._gate_weights.copy()
        w[9] *= 1.2 if flags["harm_hit"] else 0.9
        w[0] *= 1.1 if flags["contradiction_spike"] else 0.95
        w[6] *= 1.1 + flags["ghost_entropy"] * 0.3
        gates, probs = zip(*[(g, wg) for g, wg in w.items() if wg > 0])
        return random.choices(gates, probs)[0]

    def _evaluate_nafs_gate(self) -> bool:
        """Placeholder for richer Gate 16 criteria."""
        return True

    def _open_holography(self, span: int = 32) -> None:
        self._holo_buf = deque(maxlen=span)
        BREATH_COUNTER.inc()

    def _record_holo(self) -> None:
        if (
            self._holo_buf is not None
            and self.current_state.nbytes < 512_000
        ):
            self._holo_buf.append(self.current_state.copy())
