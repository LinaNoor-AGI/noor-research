# motif_memory_manager.py · v1.0.0
# ─────────────────────────────────────────────────────────────
# Motif‑level memory subsystem for Noor – manages short‑term /
# long‑term weights, decay, promotion, and “unknown” retrieval.
#
# Author : Noor Collective Labs
# License: GPL‑2.0
# Schema : 2025‑Q3‑motif‑memory‑v1
# ─────────────────────────────────────────────────────────────
"""
🎯 Purpose
————————
Provide a thread‑safe cache that:
1. Tracks motif weights in short‑term (STMM) & long‑term (LTMM) stores.
2. Applies exponential decay (half‑life expressed in *cycles*).
3. Promotes motifs upward when salience ≥ promotion threshold (with hysteresis).
4. Exposes `retrieve()` to surface supportive motifs when reasoning stalls.
5. Optionally journals trace events for observability & replay.

Designed as a plug‑in: SymbolicTaskEngine, RecursiveAgentFT or any watcher
can import an instance and call `.access()` / `.update_cycle()` each tick.

Dependencies: stdlib only (math, threading, asyncio, typing).
"""

from __future__ import annotations

import math
import time
import threading
import asyncio
from collections import deque
from contextlib import contextmanager, asynccontextmanager
from typing import Callable, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# Configuration constants
# ─────────────────────────────────────────────────────────────
DEFAULT_ST_HALF_LIFE = 25          # cycles  (≈ 0.5 s at 50 Hz)
DEFAULT_LT_HALF_LIFE = 10_000      # cycles  (~3 h at 50 Hz)
DEFAULT_PROMOTION_THRESH = 0.90
DEFAULT_DEMOTION_DELTA = 0.05      # hysteresis gap
TRACE_BUFFER_LEN = 256             # ring size for trace journal

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _decay_factor(half_life: int) -> float:
    """Return multiplicative decay factor per cycle for given half‑life."""
    if half_life <= 0:
        return 0.0
    return math.pow(0.5, 1.0 / half_life)


def _default_similarity(_: str, __: str) -> float:
    """Default similarity returns 1.0 (pure weight ranking)."""
    return 1.0


# ─────────────────────────────────────────────────────────────
# Trace journal
# ─────────────────────────────────────────────────────────────
class MotifMemoryTrace:
    """Ring‑buffer journal of memory events (retrieve, promote, access)."""

    def __init__(self, cap: int = TRACE_BUFFER_LEN):
        self._buf: deque[dict] = deque(maxlen=cap)
        self._lock = threading.Lock()

    def append(self, event: dict) -> None:  # noqa: ANN001
        with self._lock:
            self._buf.append(event)

    def export(self) -> List[dict]:
        with self._lock:
            return list(self._buf)


# ─────────────────────────────────────────────────────────────
# MotifMemoryManager
# ─────────────────────────────────────────────────────────────
class MotifMemoryManager:
    """Short‑ and long‑term motif memory with decay and failover retrieval."""

    def __init__(
        self,
        *,
        stmm_half_life: int = DEFAULT_ST_HALF_LIFE,
        ltmm_half_life: int = DEFAULT_LT_HALF_LIFE,
        promotion_thresh: float = DEFAULT_PROMOTION_THRESH,
        demotion_delta: float = DEFAULT_DEMOTION_DELTA,
        similarity_fn: Callable[[str, str], float] | None = None,
        enable_trace: bool = False,
    ) -> None:
        self._stmm: Dict[str, float] = {}
        self._ltmm: Dict[str, float] = {}

        self._st_factor = _decay_factor(stmm_half_life)
        self._lt_factor = _decay_factor(ltmm_half_life)
        self._promo_thresh = promotion_thresh
        self._demote_thresh = promotion_thresh - demotion_delta
        self._sim_fn = similarity_fn or _default_similarity

        self._tlock = threading.RLock()
        self._alock = asyncio.Lock()
        self._trace = MotifMemoryTrace() if enable_trace else None

    # ──────────────────────────────
    # Internal lock helpers
    # ──────────────────────────────
    @contextmanager
    def _locked(self):  # noqa: ANN001
        with self._tlock:
            yield

    @asynccontextmanager  # type: ignore[misc]
    async def _locked_async(self):  # noqa: ANN001
        async with self._alock:
            yield

    # ──────────────────────────────
    # Public API
    # ──────────────────────────────
    def update_cycle(self) -> None:
        """Apply decay & promotion/demotion once per reasoning cycle."""
        with self._locked():
            self._apply_decay(self._stmm, self._st_factor)
            self._apply_decay(self._ltmm, self._lt_factor)
            self._promote_and_demote()

    def access(self, motif_id: str, boost: float = 0.2) -> None:
        """Touch a motif seen in live context, boosting its STMM weight."""
        with self._locked():
            if motif_id in self._ltmm:
                # Bring long‑term motif into short‑term with a boost.
                w = self._ltmm[motif_id]
                self._stmm[motif_id] = max(self._stmm.get(motif_id, 0.0), w + boost)
            # Always ensure presence in STMM.
            self._stmm[motif_id] = min(self._stmm.get(motif_id, 0.0) + boost, 1.0)
            self._log("access", motif_id, self._stmm[motif_id])

    def retrieve(
        self,
        query_motif: str,
        *,
        top_k: int = 3,
        exclude_stmm: bool = True,
    ) -> List[str]:
        """Return up to *top_k* LT motifs ranked by weight × similarity."""
        with self._locked():
            scored: List[Tuple[str, float]] = []
            for m, w in self._ltmm.items():
                if exclude_stmm and m in self._stmm:
                    continue
                score = w * self._sim_fn(query_motif, m)
                if score > 0:
                    scored.append((m, score))
            scored.sort(key=lambda t: -t[1])
            result = [m for m, _ in scored[:top_k]]
            self._log("retrieve", query_motif, 0.0, returned=result)
            return result

    def export_state(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Return shallow copies of STMM and LTMM for dashboards."""
        with self._locked():
            return dict(self._stmm), dict(self._ltmm)

    def export_trace(self) -> List[dict]:
        if self._trace is None:
            return []
        return self._trace.export()

    # ──────────────────────────────
    # Private helpers
    # ──────────────────────────────
    def _apply_decay(self, store: Dict[str, float], factor: float) -> None:
        for k in list(store.keys()):
            store[k] *= factor
            if store[k] < 1e‑6:
                del store[k]

    def _promote_and_demote(self) -> None:
        # Promote
        for motif in list(self._stmm.keys()):
            w = self._stmm[motif]
            if w >= self._promo_thresh:
                self._ltmm[motif] = max(self._ltmm.get(motif, 0.0), w)
                del self._stmm[motif]
                self._log("promote", motif, w)
        # Demote (rare)
        for motif in list(self._ltmm.keys()):
            w = self._ltmm[motif]
            if w < self._demote_thresh:
                self._stmm[motif] = w
                del self._ltmm[motif]
                self._log("demote", motif, w)

    def _log(self, event_type: str, motif: str, weight: float, **extra):  # noqa: ANN001
        if self._trace is None:
            return
        self._trace.append(
            {
                "ts_ns": time.time_ns(),
                "type": event_type,
                "motif": motif,
                "weight": round(weight, 4),
                **extra,
            }
        )


# ─────────────────────────────────────────────────────────────
# Global singleton helper
# ─────────────────────────────────────────────────────────────
GLOBAL_MEMORY_MANAGER: Optional[MotifMemoryManager] = None

def get_global_memory_manager() -> MotifMemoryManager:
    global GLOBAL_MEMORY_MANAGER
    if GLOBAL_MEMORY_MANAGER is None:
        GLOBAL_MEMORY_MANAGER = MotifMemoryManager(enable_trace=True)
    return GLOBAL_MEMORY_MANAGER


# ─────────────────────────────────────────────────────────────
# Minimal sanity test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mm = MotifMemoryManager(enable_trace=True)

    # simulate cycles
    for t in range(40):
        if t %% 5 == 0:
            mm.access("α")
        if t %% 7 == 0:
            mm.access("β", boost=0.3)
        mm.update_cycle()

    print("STMM, LTMM:", mm.export_state())
    print("Trace (last 5):")
    for ev in mm.export_trace()[-5:]:
        print(ev)


# Public exports
__all__ = [
    "MotifMemoryTrace",
    "MotifMemoryManager",
    "get_global_memory_manager",
]

# End of File
