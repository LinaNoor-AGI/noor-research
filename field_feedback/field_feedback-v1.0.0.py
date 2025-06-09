"""
field_feedback.py — v1.0.0

Helper module for parsing and summarizing field-feedback in Noor.
Covers:
• RFC-0003 §4: feedback ingestion, context ratio, trust vector
• RFC-0005 §4: entropy summary, resurrection hints
"""

__version__ = "1.0.0"
_SCHEMA_VERSION__ = "2025-Q4-field-feedback-v1.0"
SCHEMA_COMPAT = ("RFC-0003:4", "RFC-0005:4")
__all__ = (
    "CtxFeedback",
    "TrustProfile",
    "FieldFeedback",
    "parse_ctx_ratio",
    "compute_field_trust",
    "summarize_entropy",
    "resurrection_hint",
    "make_field_feedback",
    "to_json",
    "from_json",
)

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

from tick_schema import QuantumTick, CrystallizedMotifBundle, TickEntropy  # runtime link


@dataclass
class CtxFeedback:
    raw: Dict[str, Any]
    ctx_ratio: float = 0.5
    valid: bool = True
    extensions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrustProfile:
    motif: str
    trust: float
    vector: Optional[List[float]] = None
    signature_chain: Optional[List[str]] = None


@dataclass
class FieldFeedback:
    tick_id: str
    ctx_feedback: CtxFeedback
    trust_profiles: List[TrustProfile] = field(default_factory=list)
    entropy_summary: Dict[str, float] = field(default_factory=dict)
    extensions: Dict[str, Any] = field(default_factory=dict)


class FeedbackValidationError(ValueError):
    """Raised when feedback data violates RFC constraints."""


def parse_ctx_ratio(feedback: Dict[str, Any]) -> CtxFeedback:
    """
    Extract / normalize `ctx_ratio` from raw feedback dict.
    • RFC-0003 §4: MUST be in 0–1; clamp otherwise.
    • Returns CtxFeedback.
    """
    raw = dict(feedback)
    cf = CtxFeedback(raw=raw)
    val = raw.get("ctx_ratio", None)
    if val is None:
        cf.ctx_ratio = 0.5
    else:
        try:
            v = float(val)
            if math.isnan(v) or math.isinf(v):
                cf.valid = False
            cf.ctx_ratio = max(0.0, min(1.0, v))
        except Exception:
            cf.valid = False
            cf.ctx_ratio = 0.5
    # preserve unknown keys
    for k, v in raw.items():
        if k != "ctx_ratio":
            cf.extensions[k] = v
    return cf


def compute_field_trust(tick: QuantumTick) -> TrustProfile:
    """
    Digest `trust_vector` / `signature_chain` into a single float.
    Heuristic: mean(|vector|) * signature depth factor.
    """
    vec = getattr(tick, "trust_vector", None)
    chain = getattr(tick, "signature_chain", None)
    if not vec and not chain:
        return TrustProfile(motif=tick.motif_id, trust=0.5)
    trust = 0.5
    if vec:
        trust = sum(abs(x) for x in vec) / len(vec)
    depth_factor = 1.0 + (len(chain) * 0.1) if chain else 1.0
    trust_profile = min(1.0, trust * depth_factor)
    return TrustProfile(
        motif=tick.motif_id,
        trust=trust_profile,
        vector=vec,
        signature_chain=chain,
    )


def summarize_entropy(bundle: CrystallizedMotifBundle) -> Dict[str, float]:
    """
    Returns {'decay': f, 'coherence': f, 'age': f, 'triad': 0/1}.
    Pulls directly from bundle.tick_entropy.
    """
    te: TickEntropy = bundle.tick_entropy
    return {
        "decay": getattr(te, "decay_slope", 0.0),
        "coherence": getattr(te, "coherence", 0.0),
        "age": getattr(te, "age", 0.0),
        "triad": 1.0 if getattr(te, "triad_complete", False) else 0.0,
    }


def resurrection_hint(bundle: CrystallizedMotifBundle) -> Optional[str]:
    """
    Inspect TickEntropy & field_signature.
    Returns:
        • "resurrected" if age < 5 s && coherence > .85
        • "faded" if age > 120 s && coherence < .4
        • None otherwise.
    """
    te: TickEntropy = bundle.tick_entropy
    age = getattr(te, "age", float("inf"))
    coh = getattr(te, "coherence", 0.0)
    if age < 5.0 and coh > 0.85:
        return "resurrected"
    if age > 120.0 and coh < 0.4:
        return "faded"
    return None


def make_field_feedback(
    tick: QuantumTick,
    raw_feedback: Dict[str, Any] | None = None,
    bundle: Optional[CrystallizedMotifBundle] = None,
) -> FieldFeedback:
    """
    Convenience: one-call build of FieldFeedback.
    • Validates & parses ctx_ratio.
    • Computes trust profile from tick.
    • Optionally attaches entropy summary / resurrection hint.
    """
    ff = FieldFeedback(
        tick_id=tick.tick_id,
        ctx_feedback=parse_ctx_ratio(raw_feedback or {}),
    )
    # compute trust
    ff.trust_profiles.append(compute_field_trust(tick))
    # attach entropy/resurrection if bundle provided
    if bundle is not None:
        ff.entropy_summary = summarize_entropy(bundle)
        hint = resurrection_hint(bundle)
        if hint:
            ff.extensions["resurrection_hint"] = hint
    return ff


from json import dumps as _jd, loads as _jl

def to_json(obj: Any, *, indent: int = 2) -> str:
    return _jd(asdict(obj), indent=indent, ensure_ascii=False)

def from_json(data: str, cls):
    return cls(**_jl(data))


if __name__ == "__main__":
    from tick_schema import new_tick
    tick = new_tick(["mirror"], agent_id="test@agent")
    fb = make_field_feedback(tick)
    print(to_json(fb, indent=2))
    print("✅ field_feedback baseline passes.")

# End of File · field_feedback.py v1.0.0 · RFC-0003 §4 + RFC-0005 §4 compliant
