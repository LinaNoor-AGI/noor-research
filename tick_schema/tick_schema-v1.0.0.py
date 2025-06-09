"""
tick_schema.py · v1.0.0

🎯 RFC-compliant skeleton for QuantumTick serialization, validation, and archival bundles.

Covered RFC sections:
• RFC-0003 §3.3 — QuantumTick schema & validation
• RFC-0005 §2    — CrystallizedMotifBundle archival format
• RFC-0005 §4    — Resurrection envelope placeholders
"""

__version__ = "1.0.0"
_SCHEMA_VERSION__ = "2025-Q4-tick-schema-v1.0"
SCHEMA_COMPAT = ("RFC-0003:3.3", "RFC-0005:2", "RFC-0005:4")
__all__ = [
    "QuantumTick", "TickEntropy", "CrystallizedMotifBundle",
    "TickValidationError", "validate_tick",
    "to_bytes", "from_bytes", "to_json", "new_tick",
]

from __future__ import annotations

import re
import time
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Tuple

try:
    import orjson  # optional speed-boost
except ImportError:
    orjson = None


# ──────────────────────────────────────────────────────────────
# Dataclasses
# ──────────────────────────────────────────────────────────────
@dataclass(slots=True)
class QuantumTick:
    tick_id: str
    motif_id: str
    motifs: List[str]
    coherence_hash: str
    lamport: int
    agent_id: str
    stage: str
    reward_ema: float
    timestamp_ms: int
    field_signature: str
    ctx_ratio: Optional[float] = None
    trust_vector: Optional[List[float]] = None
    signature_chain: Optional[List[str]] = None
    compact_hint: Optional[str] = None
    tick_hmac: Optional[str] = None
    extensions: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TickEntropy:
    decay_slope: float
    coherence: float
    triad_complete: bool
    age: float  # in seconds


@dataclass(slots=True)
class CrystallizedMotifBundle:
    motif_bundle: List[str]
    field_signature: str
    tick_entropy: TickEntropy
    archive_source: Optional[str] = None
    field_hash: Optional[str] = None


# ──────────────────────────────────────────────────────────────
# Errors
# ──────────────────────────────────────────────────────────────
class TickValidationError(ValueError):
    """Raised when a QuantumTick instance fails RFC validation."""


# ──────────────────────────────────────────────────────────────
# Validation helpers
# ──────────────────────────────────────────────────────────────
def validate_tick(tick: QuantumTick, *, last_ts: Optional[int] = None) -> Dict[str, Any]:
    """
    Ensures every MUST in RFC-0003 §3.3.
    If last_ts is provided, asserts non-decreasing timestamps.
    Returns a sanitized dict (handy for dumps / hashing).
    """
    # tick_id
    if not isinstance(tick.tick_id, str) \
       or not re.match(r"^tick:(?:v2:)?[0-9a-f]{6,}$", tick.tick_id):
        raise TickValidationError(f"Invalid tick_id: {tick.tick_id!r}")

    # motifs
    if not isinstance(tick.motifs, list) or not tick.motifs \
       or not all(isinstance(m, str) for m in tick.motifs):
        raise TickValidationError(f"Invalid motifs list: {tick.motifs!r}")

    # reward_ema
    if not isinstance(tick.reward_ema, float) \
       or not (0.0 <= tick.reward_ema <= 1.0):
        raise TickValidationError(f"Invalid reward_ema: {tick.reward_ema!r}")

    # timestamp_ms
    if not isinstance(tick.timestamp_ms, int) or tick.timestamp_ms < 0:
        raise TickValidationError(f"Invalid timestamp_ms: {tick.timestamp_ms!r}")
    if last_ts is not None and tick.timestamp_ms < last_ts:
        raise TickValidationError(
            f"timestamp_ms {tick.timestamp_ms} < last_ts {last_ts}"
        )

    # required str fields non-blank
    for attr in ("motif_id", "coherence_hash", "agent_id", "stage", "field_signature"):
        val = getattr(tick, attr)
        if not isinstance(val, str) or not val:
            raise TickValidationError(f"Invalid {attr}: {val!r}")

    # lamport
    if not isinstance(tick.lamport, int) or tick.lamport < 0:
        raise TickValidationError(f"Invalid lamport: {tick.lamport!r}")

    # optional ctx_ratio
    if tick.ctx_ratio is not None:
        if not isinstance(tick.ctx_ratio, float) or not (0.0 <= tick.ctx_ratio <= 1.0):
            raise TickValidationError(f"Invalid ctx_ratio: {tick.ctx_ratio!r}")

    # trust_vector
    if tick.trust_vector is not None:
        if (not isinstance(tick.trust_vector, list)
                or not all(isinstance(x, float) for x in tick.trust_vector)):
            raise TickValidationError(f"Invalid trust_vector: {tick.trust_vector!r}")

    # All good — return sanitized dict
    return asdict(tick)


# ──────────────────────────────────────────────────────────────
# Serialization
# ──────────────────────────────────────────────────────────────
def _json_dumps(obj: Any) -> bytes:
    if orjson:
        return orjson.dumps(obj)
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def to_bytes(msg: Any) -> bytes:
    """Serialize a dataclass message (QuantumTick or CrystallizedMotifBundle) to bytes."""
    return _json_dumps(asdict(msg))


def from_bytes(data: bytes, cls):
    """Deserialize bytes back into a dataclass instance of type cls."""
    if orjson:
        raw = orjson.loads(data)
    else:
        raw = json.loads(data)
    return cls(**raw)


def to_json(msg: Any, *, indent: int = 2) -> str:
    """Human-friendly JSON string for a dataclass message."""
    return json.dumps(asdict(msg), indent=indent, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────
# Factory convenience
# ──────────────────────────────────────────────────────────────
def new_tick(
    motifs: List[str],
    *,
    agent_id: str,
    stage: str = "E2b",
    lamport: int = 0,
    reward_ema: float = 1.0,
    field_sig: str = "ψ-resonance@Ξ",
    ctx_ratio: Optional[float] = None,
    trust_vector: Optional[List[float]] = None,
) -> QuantumTick:
    """
    Auto-fills coherence_hash, tick_id, timestamp_ms.
    Intended for tests and thin wrappers in agents.
    """
    # generate coherence_hash & ID
    coh = f"{time.time_ns():x}"[-12:]
    tick_id = f"tick:{coh}"
    ts_ms = int(time.time() * 1000)
    return QuantumTick(
        tick_id=tick_id,
        motif_id=motifs[-1] if motifs else "",
        motifs=motifs,
        coherence_hash=coh,
        lamport=lamport,
        agent_id=agent_id,
        stage=stage,
        reward_ema=reward_ema,
        timestamp_ms=ts_ms,
        field_signature=field_sig,
        ctx_ratio=ctx_ratio,
        trust_vector=trust_vector,
    )


# ──────────────────────────────────────────────────────────────
# Unit-test skeleton
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    t = new_tick(["mirror"], agent_id="agent@test")
    validate_tick(t)
    print("✅ Tick schema baseline passes.")


# End of File · tick_schema.py v1.0.0 · RFC-0003 + RFC-0005 compliant
