"""
🕰️ NoorFastTimeCore · v8.3.1

Presence / Kernel layer of the Noor triad (adaptive edition).

Δ v8.3.1
────────
• **Snapshot-truncation metric** – new Prometheus counter
  `core_snapshot_truncations_total` + explicit `truncate_at` slice.
• **Configurable latency-weight gains** – env vars
  `NOOR_LAT_W_UP` / `NOOR_LAT_W_DOWN` replace hard-coded 1.05 / 0.99.
• **Expanded docstring** for `receive_feedback()` clarifying bias math and
  thread-safety.
• Patch sits on top of v8.3.0 (intuition bias, related motifs, adaptive α).
"""
from __future__ import annotations

__version__ = "8.3.1"
_SCHEMA_VERSION__ = "2025-Q3-fast-time-memory-adaptive"

import hashlib
import logging
import os
import time
import threading
from collections import deque
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────
# Third-party stubs (Prometheus optional)
# ──────────────────────────────────────────────────────────────
try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    class _Stub:
        def labels(self, *_, **__):
            return self
        def inc(self, *_):  ...
        def dec(self, *_):  ...
        def set(self, *_):  ...
    Counter = Gauge = _Stub  # type: ignore

# fast serializer
try:
    import orjson  # type: ignore
    _dumps = orjson.dumps
except ImportError:  # pragma: no cover
    import pickle
    _dumps = pickle.dumps  # type: ignore

# Noor internals
from .quantum_ids import MotifChangeID
from motif_memory_manager_v1.0.1 import get_global_memory_manager

# ──────────────────────────────────────────────────────────────
# Gate legends (unchanged poetry)
# ──────────────────────────────────────────────────────────────
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
    16: ("Nafs Mirror",          "Self ⊕ ¬Self", "فَإِذَا سَوَّيْتُهُ وَنَفْخْتُ فِيهِ مِنْ رُّوحِي"),
}

# ──────────────────────────────────────────────────────────────
# Metrics
# ──────────────────────────────────────────────────────────────
ECHO_JOINS = Counter(
    "gate16_echo_joins_total",
    "Gate-16 echo snapshots committed",
    ["agent_id"],
)
BIAS_APPLIED = Counter(
    "core_tick_bias_applied_total",
    "Tick-bias contributions applied",
    ["agent_id", "reason"],
)
INTUITION_ALPHA_GAUGE = Gauge(
    "core_intuition_alpha",
    "Current intuition-bias alpha",
    ["agent_id"],
)
SNAPSHOT_TRUNC = Counter(
    "core_snapshot_truncations_total",
    "Snapshots truncated due to size cap",
    ["agent_id"],
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ──────────────────────────────────────────────────────────────
# Fast-Time Core
# ──────────────────────────────────────────────────────────────
class NoorFastTimeCore:
    """Presence-kernel that stores echo snapshots and returns bias signals."""

    def __init__(
        self,
        *,
        agent_id: str = "core@default",
        max_parallel: int = 8,
        snapshot_cap_kb: int | None = None,
        latency_budget: float | None = None,
        hmac_secret: bytes | None = None,
        async_mode: bool = False,
        low_latency_mode: bool = False,
    ):
        # env fallbacks
        if snapshot_cap_kb is None:
            snapshot_cap_kb = int(os.getenv("NOOR_MAX_ECHO_SNAPSHOT_KB", "8"))
        if latency_budget is None:
            latency_budget = float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
        if hmac_secret is None:
            env = os.getenv("NOOR_TICK_HMAC")
            hmac_secret = env.encode() if env else None

        if snapshot_cap_kb > 128:
            logger.warning("Snapshot cap over 128 kB may hurt performance.")

        self.agent_id = agent_id
        self.max_parallel = max_parallel
        self.snapshot_cap_kb = snapshot_cap_kb
        self.latency_budget = latency_budget
        self.hmac_secret = hmac_secret
        self.low_latency_mode = low_latency_mode

        self._echoes: deque[Tuple[str, bytes, str]] = deque(maxlen=256)
        self._last_lamport = -1

        # locks
        if async_mode:
            try:
                from anyio import Lock as _ALock  # type: ignore
                self._lock = _ALock()
            except ImportError:  # pragma: no cover
                self._lock = threading.RLock()
        else:
            self._lock = threading.RLock()

        # ── Latency-weight gain / decay (env-tunable) ──────────
        self._lat_w_up   = float(os.getenv("NOOR_LAT_W_UP",   "1.05"))
        self._lat_w_down = float(os.getenv("NOOR_LAT_W_DOWN", "0.99"))

        # bias tuners
        self._entropy_weight = 1.0
        self._latency_weight = 1.0

        # ── Adaptive intuition knobs ───────────────────────────
        self._intuition_alpha = float(
            os.getenv("NOOR_INTUITION_ALPHA_INIT", "0.10")
        )
        self._alpha_min, self._alpha_max = 0.0, 0.30
        self._alpha_decay = 0.995
        self._alpha_growth = 1.002
        self._last_bias_sign: int = 0
        self._rolling_reward: deque[float] = deque(maxlen=32)

    # ────────────────────────────────
    # Feedback ingest
    # ────────────────────────────────
    def receive_feedback(
        self,
        ctx_ratio: float,
        ghost_entropy: float,
        harm_hits: int,
        step_latency: float,
        *,
        latest_tick,
        parallel_running: int,
        change_id: Optional[MotifChangeID] = None,
    ) -> Tuple[float, float]:
        """
        Evaluate agent metrics, apply adaptive bias, and return updated latency
        budget.

        Thread-safety
        -------------
        Entire method runs under ``self._lock``; bias math and snapshot ingest
        are atomic with respect to concurrent feedback calls.

        Bias Formula
        ------------
        ``bias_score = (ghost_entropy * _entropy_weight)
                     – (latency_penalty * _latency_weight)
                     + (LTMM_weight * _intuition_alpha)``

        The latency-weight gain/decay factors are env-overrideable via
        ``NOOR_LAT_W_UP`` / ``NOOR_LAT_W_DOWN``.
        """
        with self._lock:
            entropy_term = ghost_entropy * self._entropy_weight
            latency_penalty = (
                (step_latency / self.latency_budget)
                + parallel_running / self.max_parallel
            ) * self._latency_weight
            bias_score = entropy_term - latency_penalty

            # Intuition bias from LTMM
            try:
                ltmm = get_global_memory_manager().export_state()[1]
                intuition_w = ltmm.get(latest_tick.motif_id, 0.0)
                bias_score += intuition_w * self._intuition_alpha
            except Exception as exc:  # pragma: no cover
                logger.warning("Intuition bias skipped: %s", exc)
                intuition_w = 0.0

            # Adaptive α update
            reward_signal = -latency_penalty
            current_sign = (
                1 if intuition_w * reward_signal > 0
                else -1 if intuition_w * reward_signal < 0
                else 0
            )
            if current_sign == self._last_bias_sign == 1:
                self._intuition_alpha = min(
                    self._alpha_max, self._intuition_alpha * self._alpha_growth
                )
            elif current_sign == self._last_bias_sign == -1:
                self._intuition_alpha = max(
                    self._alpha_min, self._intuition_alpha * self._alpha_decay
                )
            self._last_bias_sign = current_sign
            self._rolling_reward.append(reward_signal)
            try:
                INTUITION_ALPHA_GAUGE.labels(
                    agent_id=self.agent_id
                ).set(self._intuition_alpha)
            except Exception:  # pragma: no cover
                pass

            # latency-weight self-tuning
            if step_latency > self.latency_budget * 1.2:
                self._latency_weight *= self._lat_w_up
            else:
                self._latency_weight *= self._lat_w_down

            # ingest snapshot
            self._ingest_tick(latest_tick, change_id)

            next_budget = max(
                0.001,  # hard floor = 1 ms
                max(
                    self.latency_budget * 0.5,
                    self.latency_budget - bias_score * 0.01,
                ),
            )
            return bias_score, next_budget

    # ────────────────────────────────
    # Tick ingest & Gate-16 snapshot
    # ────────────────────────────────
    def _ingest_tick(self, tick, change_id: Optional[MotifChangeID]):
        if tick.lamport <= self._last_lamport:
            return
        self._last_lamport = tick.lamport

        if self.hmac_secret and not self.low_latency_mode:
            if not tick.verify(self.hmac_secret):
                logger.warning("HMAC mismatch for tick %s", tick.coherence_hash)
                BIAS_APPLIED.labels(
                    agent_id=self.agent_id, reason="hmac_failure"
                ).inc()
                return

        payload = {
            "tick": tick.coherence_hash,
            "lamport": tick.lamport,
            "ts": time.time_ns(),
            "change_id": change_id.__dict__ if change_id else None,
        }

        # related motifs
        try:
            mm = get_global_memory_manager()
            k = 1 + int(len(mm.export_state()[1]) ** 0.25)
            payload["related_motifs"] = mm.retrieve(tick.motif_id, top_k=k)
            logger.debug(
                "Echo %s tagged with related motifs: %s",
                tick.coherence_hash,
                payload["related_motifs"],
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Related-motif tagging failed: %s", exc)

        blob = _dumps(payload)
        truncate_at = self.snapshot_cap_kb * 1024
        if len(blob) > truncate_at:
            SNAPSHOT_TRUNC.labels(agent_id=self.agent_id).inc()
            blob = blob[:truncate_at]
            logger.warning(
                "Snapshot truncated to %s kB", self.snapshot_cap_kb
            )

        checksum = hashlib.sha256(blob).hexdigest()
        self._echoes.append((tick.coherence_hash, blob, checksum))
        ECHO_JOINS.labels(agent_id=self.agent_id).inc()

    # ────────────────────────────────
    # Echo utilities
    # ────────────────────────────────
    def export_echoes(self) -> List[Tuple[str, bytes, str]]:
        with self._lock:
            return list(self._echoes)

    def verify_echoes(self) -> List[str]:
        """
        Re-hash stored blobs; return list of tick hashes whose checksum mismatched.
        """
        bad: List[str] = []
        with self._lock:
            for tick_hash, blob, saved_sum in self._echoes:
                if hashlib.sha256(blob).hexdigest() != saved_sum:
                    bad.append(tick_hash)
        return bad

# End of File
