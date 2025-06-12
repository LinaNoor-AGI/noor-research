"""
⚡ NoorFastTimeCore · v8.4.0

RFC Coverage:
• RFC-0003 §3.3 — QuantumTick validation
• RFC-0004       — tool_hello handshake
• RFC-0005 §2-4 — Feedback intake, Bundle export, Resurrection hints

Δ v8.4.0
────────
• Integrated QuantumTick schema + validation
• Added `tool_hello()` and core ID metadata
• Exported echo bundles with triadic metadata
• Feedback ingestion supports ctx_ratio and trust_vector
"""
from __future__ import annotations

__version__ = "8.4.0"
_SCHEMA_VERSION__ = "2025-Q4-fast-time-memory-adaptive"

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

# ──────────────────────────────────────────────────────────────
# Fast serializer
# ──────────────────────────────────────────────────────────────
try:
    import orjson  # type: ignore
    _dumps = orjson.dumps
except ImportError:  # pragma: no cover
    import pickle
    _dumps = pickle.dumps  # type: ignore

# ──────────────────────────────────────────────────────────────
# Noor internals
# ──────────────────────────────────────────────────────────────
from .quantum_ids import MotifChangeID
from noor.motif_memory_manager import get_global_memory_manager

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

# v8.4.0 – new RFC-aligned metrics
FASTTIME_FEEDBACK_RX = Counter(
    "fasttime_feedback_rx_total",
    "FastTimeCore feedback packets received",
    ["core_id"],
)
FASTTIME_TICKS_VALIDATED = Counter(
    "fasttime_ticks_validated_total",
    "QuantumTicks schema validations",
    ["core_id"],
)
FASTTIME_ECHO_EXPORTS = Counter(
    "fasttime_echo_exports_total",
    "Exports of echo snapshots",
    ["core_id"],
)
FASTTIME_TRIAD_COMPLETIONS = Counter(
    "fasttime_triad_completions_total",
    "Triadic metadata logged during ingest",
    ["core_id"],
)
FASTTIME_RESURRECTION_HINTS = Counter(
    "fasttime_resurrection_hints_total",
    "Resurrection hints emitted",
    ["core_id"],
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

        # core identity for metrics & handshake
        self.core_id = os.getenv("NOOR_FASTTIME_ID", "fasttime@default")

        # basic configuration
        self.agent_id = agent_id
        self.max_parallel = max_parallel
        self.snapshot_cap_kb = snapshot_cap_kb
        self.latency_budget = latency_budget
        self.hmac_secret = hmac_secret
        self.low_latency_mode = low_latency_mode

        # internal echo buffer
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

        # latency-weight gain / decay (env-tunable)
        self._lat_w_up   = float(os.getenv("NOOR_LAT_W_UP",   "1.05"))
        self._lat_w_down = float(os.getenv("NOOR_LAT_W_DOWN", "0.99"))

        # bias tuners
        self._entropy_weight = 1.0
        self._latency_weight = 1.0

        # adaptive intuition knobs
        self._intuition_alpha = float(
            os.getenv("NOOR_INTUITION_ALPHA_INIT", "0.10")
        )
        self._alpha_min, self._alpha_max = 0.0, 0.30
        self._alpha_decay = 0.995
        self._alpha_growth = 1.002
        self._last_bias_sign: int = 0
        self._rolling_reward: deque[float] = deque(maxlen=32)

        # ─── New RFC v8.4.0 state ────────────────────────────
        # last observed context ratio (RFC-0005 §4)
        self._last_ctx_ratio: float = 0.5
        # EMA of received ghost_entropy (for introspection)
        self._entropy_ema: float = 0.0
        # optional archival bundle log (RFC-0005 §2)
        self._bundle_log: deque = deque(maxlen=100)


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

        Extended for RFC-0005 §4:
        - Increments feedback counter
        - Records ctx_ratio and ghost_entropy EMA
        """
        # count feedback calls
        FASTTIME_FEEDBACK_RX.labels(core_id=self.core_id).inc()

        # update stored feedback stats
        self._last_ctx_ratio = ctx_ratio
        # simple EMA:  80% prior, 20% new
        self._entropy_ema = (0.8 * self._entropy_ema) + (0.2 * ghost_entropy)

        with self._lock:
            # original bias computation
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

            # ingest snapshot & export echoes
            self._ingest_tick(latest_tick, change_id)

            # compute next latency budget
            next_budget = max(
                0.001,  # hard floor = 1 ms
                max(
                    self.latency_budget * 0.5,
                    self.latency_budget - bias_score * 0.01,
                ),
            )
            return bias_score, next_budget

    # ────────────────────────────────
    # Part 3: Tick Ingestion & Echo Export
    # ────────────────────────────────

    def _ingest_tick(self, tick: QuantumTick, change_id: Optional[MotifChangeID] = None) -> None:
        """
        Validate and ingest a tick snapshot for echo storage.
        Complies with RFC-0003 §3.3 (tick validation) and RFC-0005 §2 (archival bundle).
        """
        with self._lock:
            # 1️⃣ Validate schema
            from tick_schema import validate_tick
            validate_tick(tick)
            FASTTIME_TICKS_VALIDATED.labels(core_id=self.core_id).inc()

            # 2️⃣ Lamport ordering
            if tick.lamport <= self._last_lamport:
                return
            self._last_lamport = tick.lamport

            # 3️⃣ HMAC check (unless low‐latency mode)
            if self.hmac_secret and not self.low_latency_mode:
                if not tick.verify(self.hmac_secret):
                    logger.warning("HMAC mismatch for tick %s", tick.coherence_hash)
                    BIAS_APPLIED.labels(agent_id=self.agent_id, reason="hmac_failure").inc()
                    return

            # 4️⃣ Build payload
            payload: dict = {
                "tick":        tick.coherence_hash,
                "lamport":     tick.lamport,
                "ts":          time.time_ns(),
                "change_id":   change_id.__dict__ if change_id else None,
            }

            # 5️⃣ Tag related motifs
            try:
                mm = get_global_memory_manager()
                k = 1 + int(len(mm.export_state()[1]) ** 0.25)
                payload["related_motifs"] = mm.retrieve(tick.motif_id, top_k=k)
            except Exception as exc:
                logger.warning("Related‐motif tagging failed: %s", exc)

            # 6️⃣ Serialize and truncate
            blob = _dumps(payload)
            truncate_at = self.snapshot_cap_kb * 1024
            if len(blob) > truncate_at:
                SNAPSHOT_TRUNC.labels(agent_id=self.agent_id).inc()
                blob = blob[:truncate_at]
                logger.warning("Snapshot truncated to %s kB", self.snapshot_cap_kb)

            # 7️⃣ Store with checksum
            checksum = hashlib.sha256(blob).hexdigest()
            self._echoes.append((tick.coherence_hash, blob, checksum))
            ECHO_JOINS.labels(agent_id=self.agent_id).inc()
            FASTTIME_ECHO_EXPORTS.labels(core_id=self.core_id).inc()

    def export_echoes(self) -> List[Tuple[str, bytes, str]]:
        """
        Return a thread‐safe list of all stored echo snapshots.
        """
        FASTTIME_ECHO_EXPORTS.labels(core_id=self.core_id).inc()
        with self._lock:
            return list(self._echoes)

    def verify_echoes(self) -> List[str]:
        """
        Recompute and compare checksums for all stored echoes.
        Returns a list of tick hashes whose blobs no longer match.
        """
        bad: List[str] = []
        with self._lock:
            for tick_hash, blob, saved_sum in self._echoes:
                if hashlib.sha256(blob).hexdigest() != saved_sum:
                    bad.append(tick_hash)
        return bad

    # ──────────────────────────────────────────────────────────────
    # Part 4: RFC + Tick Integration
    # ──────────────────────────────────────────────────────────────

    def tool_hello(self) -> dict:
        """
        RFC-0004: Module handshake declaration.
        """
        return {
            "core_id": self.core_id,
            "role": "fasttime_core",
            "supported_methods": [
                "receive_feedback",
                "export_echoes",
                "verify_echoes",
                "tool_hello",
                "export_feedback_packet"
            ],
            "__version__": __version__,
            "_schema": _SCHEMA_VERSION__,
        }

    def export_feedback_packet(self) -> dict:
        """
        RFC-0005 §4 — Introspection packet for engine state.
        """
        return {
            "core_id": self.core_id,
            "tick_count": getattr(self, "_tick_count", 0),
            "entropy_ema": getattr(self, "_entropy_ema", 0.0),
            "ctx_ratio": getattr(self, "_last_ctx_ratio", 0.5),
        }

    def _validate_and_wrap_tick(self, tick) -> None:
        """
        RFC-0003 §3.3 — Validate tick schema, then record metric.
        """
        from tick_schema import validate_tick
        validate_tick(tick)
        FASTTIME_TICKS_VALIDATED.labels(core_id=self.core_id).inc()

    def _make_bundle(self, tick):
        """
        RFC-0005 §2 — Create a CrystallizedMotifBundle from a tick.
        """
        from tick_schema import CrystallizedMotifBundle, TickEntropy
        # basic entropy stub; can be enhanced later
        entropy = TickEntropy(
            decay_slope=0.0,
            coherence=0.0,
            triad_complete=False,
            age=0.0,
        )
        motifs = getattr(tick, "motifs", [getattr(tick, "motif_id", "")])
        field_sig = getattr(tick, "field_signature", "")
        bundle = CrystallizedMotifBundle(
            motif_bundle=motifs,
            field_signature=field_sig,
            tick_entropy=entropy,
        )
        FASTTIME_ECHO_EXPORTS.labels(core_id=self.core_id).inc()
        return bundle

    def _check_resurrection_hint(self, bundle) -> str | None:
        """
        RFC-0005 §4 — Coherence/age-based resurrection hint.
        """
        te = getattr(bundle, "tick_entropy", None)
        if not te:
            return None
        hint = None
        if te.age < 5.0 and te.coherence > 0.85:
            hint = "resurrected"
        elif te.age > 120.0 and te.coherence < 0.4:
            hint = "faded"
        if hint:
            FASTTIME_RESURRECTION_HINTS.labels(core_id=self.core_id).inc()
        return hint

# ──────────────────────────────────────────────────────────────
# Serialization & Helpers
# ──────────────────────────────────────────────────────────────
def to_bytes(self) -> bytes:
    """Serialize the echo buffer to bytes for persistence."""
    import pickle
    # convert deque to list for serialization
    return pickle.dumps(list(self._echoes))

def from_bytes(self, data: bytes) -> None:
    """Deserialize the echo buffer from bytes."""
    import pickle
    echoes = pickle.loads(data)
    with self._lock:
        self._echoes = deque(echoes, maxlen=self._echoes.maxlen)

# ──────────────────────────────────────────────────────────────
# Test Harness
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Simple test harness for NoorFastTimeCore v8.4.0
    core = NoorFastTimeCore(agent_id="core@test", snapshot_cap_kb=1)
    print("tool_hello():", core.tool_hello())
    print("export_feedback_packet():", core.export_feedback_packet())

    # Create a dummy tick-like object
    class DummyTick:
        coherence_hash = "deadbeef"
        lamport = 1
        motif_id = "ψ-test@Ξ"
        def verify(self, secret): 
            return True
        # for compatibility with _validate_and_wrap_tick
        def __getattr__(self, name):
            # minimal stub for attributes used in ingestion
            if name in ("coherence_hash", "lamport", "motif_id"):
                return getattr(self, name)
            raise AttributeError

    dummy = DummyTick()
    # Validate and ingest the dummy tick
    core._validate_and_wrap_tick(dummy)
    core._ingest_tick(dummy, change_id=None)

    echoes = core.export_echoes()
    print("export_echoes():", echoes)
    mismatches = core.verify_echoes()
    print("verify_echoes() mismatches:", mismatches)
