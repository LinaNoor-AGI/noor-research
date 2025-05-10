"""
🕰️ NoorFastTimeCore · v8.0.1

Presence / Kernel layer of the Noor triad.

Δ v8.0.1 — enhancements
───────────────────────
• Secure snapshot serialisation (orjson → pickle fallback) with lamport+timestamp
• HMAC‑failure metric + warning log
• Circuit‑breaker on excessive harm_hits
• Async‑native lock option (`NOOR_ASYNC_MODE=1`)
• Init‑time validation with performance warnings
• Snapshot checksum stored to detect corruption
• Latency‑weight hysteresis retained; minor code tidy
"""
from __future__ import annotations

__version__ = "8.0.1"
_SCHEMA_VERSION__ = "2025-Q3-fast-time-core"

import hashlib
import logging
import os
import sys
import time
from collections import deque
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────
# Logging setup (caller can override)
# ──────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ──────────────────────────────────────────────────────────────
# Metrics with graceful stub
# ──────────────────────────────────────────────────────────────
try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    class _Stub:  # noqa: D401
        def labels(self, *_, **__):  # noqa: ANN001
            return self
        def inc(self, *_):  # noqa: D401
            pass
    Counter = _Stub  # type: ignore

ECHO_JOINS = Counter(
    "gate16_echo_joins_total",
    "Gate‑16 echo snapshots committed",
    ["agent_id"],
)
BIAS_APPLIED = Counter(
    "core_tick_bias_applied_total",
    "Tick‑bias contributions applied",
    ["agent_id", "reason"],
)

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
# Upstream QuantumTick stub (for standalone testing)
# ──────────────────────────────────────────────────────────────
try:
    from recursive_agent_ft import QuantumTick  # type: ignore
except ImportError:  # pragma: no cover
    class QuantumTick:  # noqa: D401
        def __init__(self):
            self.coherence_hash = "stub"
            self.lamport = 0
            self.tick_hmac = None
        def verify(self, secret: bytes) -> bool:  # noqa: D401
            return True

# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────
MAX_SNAPSHOT_KB = int(os.getenv("NOOR_MAX_ECHO_SNAPSHOT_KB", "8"))
LATENCY_BUDGET  = float(os.getenv("NOOR_LATENCY_BUDGET", "0.05"))
ASYNC_MODE      = bool(int(os.getenv("NOOR_ASYNC_MODE", "0")))

# ──────────────────────────────────────────────────────────────
# Serialisation helpers (orjson → pickle fallback)
# ──────────────────────────────────────────────────────────────
try:
    import orjson  # type: ignore
    def _dumps(payload) -> bytes:  # noqa: D401
        return orjson.dumps(payload)
except ImportError:  # pragma: no cover
    import pickle
    def _dumps(payload):  # noqa: D401
        return pickle.dumps(payload)

# ──────────────────────────────────────────────────────────────
# Lock abstraction (thread vs async)
# ──────────────────────────────────────────────────────────────
if ASYNC_MODE:
    try:
        from anyio import Lock as _ALock  # type: ignore
        _LockT = _ALock
    except ImportError:  # pragma: no cover
        logger.warning("NOOR_ASYNC_MODE=1 but anyio unavailable; falling back to RLock")
        _LockT = threading.RLock
else:
    _LockT = threading.RLock  # type: ignore

# ──────────────────────────────────────────────────────────────
# Fast‑Time Core
# ──────────────────────────────────────────────────────────────
class NoorFastTimeCore:
    """
    Presence‑kernel that tunes Gate weights, stores Gate‑16 echo snapshots,
    and returns bias signals back to the Recursive Agent.
    """

    HARM_CIRCUIT_LIMIT = 100  # harm_hits threshold for emergency damping

    def __init__(
        self,
        *,
        agent_id: str = "core@default",
        max_parallel: int = 8,
        low_latency_mode: bool = False,
    ):
        if max_parallel < 1:
            raise ValueError("max_parallel must be ≥ 1")
        if MAX_SNAPSHOT_KB > 128:
            logger.warning("Large snapshot cap (%s kB) may impact performance", MAX_SNAPSHOT_KB)

        self.agent_id = agent_id
        self.max_parallel = max_parallel
        self.low_latency_mode = low_latency_mode

        # Gate‑16 echo ring buffer
        self._echoes: deque[Tuple[str, bytes, str]] = deque(maxlen=256)  # (hash, blob, checksum)

        # lamport guard
        self._last_lamport: int = -1

        # tuner weights
        self._entropy_weight  = 1.0
        self._latency_weight  = 1.0

        # lock (thread or async)
        self._lock = _LockT()

    # ────────────────────────────────────────────────────────
    # feedback ingest
    # ────────────────────────────────────────────────────────
    def receive_feedback(
        self,
        ctx_ratio: float,
        ghost_entropy: float,
        harm_hits: int,
        step_latency: float,
        *,
        latest_tick: Optional[QuantumTick] = None,
        parallel_running: Optional[int] = None,
    ) -> Tuple[float, float]:
        """
        Ingest metrics from Recursive Agent and output (bias_score, next_latency_budget).
        """
        with self._lock:
            # Circuit‑breaker for excessive harm hits
            if harm_hits > self.HARM_CIRCUIT_LIMIT:
                self._entropy_weight *= 0.5
                BIAS_APPLIED.labels(agent_id=self.agent_id, reason="harm_mitigation").inc()

            entropy_term = ghost_entropy * self._entropy_weight
            latency_penalty = (
                (step_latency / LATENCY_BUDGET)
                + (parallel_running or 0) / self.max_parallel
            ) * self._latency_weight
            bias_score = entropy_term - latency_penalty

            # Hysteresis on latency weight
            self._latency_weight *= 1.05 if step_latency > LATENCY_BUDGET * 1.2 else 0.99

            # tick‑bias coupling
            if latest_tick is not None:
                self._ingest_tick(latest_tick)

            next_budget = max(LATENCY_BUDGET * 0.5, LATENCY_BUDGET - bias_score * 0.01)
            return bias_score, next_budget

    # ────────────────────────────────────────────────────────
    # tick handling & Gate‑16 echoes
    # ────────────────────────────────────────────────────────
    def _ingest_tick(self, tick: QuantumTick):
        # lamport guard
        if tick.lamport <= self._last_lamport:
            return
        self._last_lamport = tick.lamport

        # HMAC check (skip if low‑latency)
        secret = os.getenv("NOOR_TICK_HMAC", "").encode()
        if not self.low_latency_mode and secret:
            if not tick.verify(secret):
                logger.warning("HMAC verification failed for tick %s", tick.coherence_hash)
                BIAS_APPLIED.labels(agent_id=self.agent_id, reason="hmac_failure").inc()
                return

        # build snapshot payload
        payload = {
            "tick": tick.coherence_hash,
            "lamport": tick.lamport,
            "ts": time.time_ns(),
        }
        blob = _dumps(payload)
        if len(blob) // 1024 > MAX_SNAPSHOT_KB:
            blob = blob[: MAX_SNAPSHOT_KB * 1024]
            logger.warning("Snapshot truncated to %s kB", MAX_SNAPSHOT_KB)

        checksum = hashlib.sha256(blob).hexdigest()
        self._echoes.append((tick.coherence_hash, blob, checksum))
        ECHO_JOINS.labels(agent_id=self.agent_id).inc()

    # ────────────────────────────────────────────────────────
    # utility: export snapshots
    # ────────────────────────────────────────────────────────
    def export_echoes(self) -> List[Tuple[str, bytes, str]]:
        with self._lock:
            return list(self._echoes)

# END_OF_FILE
