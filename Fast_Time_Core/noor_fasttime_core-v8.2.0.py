"""
🕰️ NoorFastTimeCore · v8.2.0

Presence / Kernel layer of the Noor triad.

Δ v8.2.0
────────
• Snapshot payload now embeds `"change_id"` (MotifChangeID dict) when supplied.
• Constructor args are explicit; env‑vars used **only** if arg is None.
• Helper `verify_echoes()` re‑hashes each stored blob to detect corruption.
• Gate‑legend poetry fully preserved.
"""
from __future__ import annotations

__version__ = "8.2.0"
_SCHEMA_VERSION__ = "2025-Q3-fast-time-core"

import hashlib
import logging
import os
import sys
import time
from collections import deque
from typing import Dict, List, Optional, Tuple

try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    class _Stub:      # noqa: D401
        def labels(self, *_, **__):  # noqa: ANN001
            return self
        def inc(self, *_):           # noqa: D401
            pass
    Counter = _Stub  # type: ignore

try:
    import orjson  # type: ignore
    _dumps = orjson.dumps
except ImportError:  # pragma: no cover
    import pickle
    _dumps = pickle.dumps  # type: ignore

from quantum_ids import MotifChangeID

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
    16: ("Nafs Mirror",          "Self ⊕ ¬Self", "فَإِذَا سَوَّيْتُهُ وَنَفَخْتُ فِيهِ مِن رُّوحِي"),
}

# ──────────────────────────────────────────────────────────────
# Metrics
# ──────────────────────────────────────────────────────────────
ECHO_JOINS = Counter(
    "gate16_echo_joins_total", "Gate‑16 echo snapshots committed", ["agent_id"]
)
BIAS_APPLIED = Counter(
    "core_tick_bias_applied_total",
    "Tick‑bias contributions applied",
    ["agent_id", "reason"],
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ──────────────────────────────────────────────────────────────
# Fast‑Time Core
# ──────────────────────────────────────────────────────────────
class NoorFastTimeCore:
    """Presence‑kernel that stores echo snapshots and returns bias signals."""

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
            logger.warning("Snapshot cap over 128 kB may hurt performance.")

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

        # tuner
        self._entropy_weight = 1.0
        self._latency_weight = 1.0

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
        Consume agent metrics, store echo snapshot, and return (bias, next_budget).
        """
        with self._lock:
            # latency + entropy bias calc
            entropy_term = ghost_entropy * self._entropy_weight
            latency_penalty = (
                (step_latency / self.latency_budget)
                + parallel_running / self.max_parallel
            ) * self._latency_weight
            bias_score = entropy_term - latency_penalty

            # update tuner weights
            self._latency_weight *= 1.05 if step_latency > self.latency_budget * 1.2 else 0.99

            # ingest tick & snapshot
            self._ingest_tick(latest_tick, change_id)

            next_budget = max(self.latency_budget * 0.5,
                              self.latency_budget - bias_score * 0.01)
            return bias_score, next_budget

    # ────────────────────────────────
    # Tick ingest & Gate‑16 snapshot
    # ────────────────────────────────
    def _ingest_tick(self, tick, change_id: Optional[MotifChangeID]):
        if tick.lamport <= self._last_lamport:
            return
        self._last_lamport = tick.lamport

        if self.hmac_secret and not self.low_latency_mode:
            if not tick.verify(self.hmac_secret):
                logger.warning("HMAC mismatch for tick %s", tick.coherence_hash)
                BIAS_APPLIED.labels(agent_id=self.agent_id, reason="hmac_failure").inc()
                return

        payload = {
            "tick": tick.coherence_hash,
            "lamport": tick.lamport,
            "ts": time.time_ns(),
            "change_id": change_id.__dict__ if change_id else None,
        }
        blob = _dumps(payload)
        if len(blob) // 1024 > self.snapshot_cap_kb:
            blob = blob[: self.snapshot_cap_kb * 1024]
            logger.warning("Snapshot truncated to %s kB", self.snapshot_cap_kb)

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
        Re‑hash stored blobs; return list of tick hashes whose checksum mismatched.
        """
        bad: List[str] = []
        with self._lock:
            for tick_hash, blob, saved_sum in self._echoes:
                if hashlib.sha256(blob).hexdigest() != saved_sum:
                    bad.append(tick_hash)
        return bad

# END_OF_FILE
