"""
quantum_ids.py · v0.1.0

Shared definitions for motif‑level change tracking across the Noor triad.
"""

from __future__ import annotations

__version__ = "0.1.0"
_SCHEMA_VERSION__ = "2025‑Q3‑quantum‑ids"

import time
from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────
# Public dataclass
# ──────────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class MotifChangeID:
    """
    Immutable marker identifying a structural change to a motif.

    Fields
    ------
    motif_id   : canonical motif name (e.g. “ψ‑merge@τ”)
    tick_hash  : QuantumTick.coherence_hash that triggered the change
    quantum_ts : 24‑hex timestamp = 16‑hex (µs since epoch) + 8‑hex lamport
    """
    motif_id: str
    tick_hash: str
    quantum_ts: str

# ──────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────
def make_change_id(tick, motif_id: str) -> MotifChangeID:
    """
    Generate a MotifChangeID given a QuantumTick and motif name.

    Parameters
    ----------
    tick      : QuantumTick  (must expose .coherence_hash and .lamport)
    motif_id  : str

    Returns
    -------
    MotifChangeID
    """
    # collapse physical time (µs) + lamport into 24 hex chars
    phys_hex = f"{int(time.time() * 1_000_000):016x}"
    lam_hex  = f"{getattr(tick, 'lamport', 0):08x}"
    return MotifChangeID(motif_id, tick.coherence_hash, phys_hex + lam_hex)

# END_OF_FILE
