# motif_memory_manager.py · v1.1.1
#
# Motif-level memory subsystem for Noor – manages short-term /
# long-term weights, decay, promotion, and “unknown” retrieval.
#
# Author : Noor Collective Labs
# License: GPL-2.0
# Schema : 2025-Q3-motif-memory-v1.1
"""
🎯 Purpose
————————
Provide a thread-safe cache that:
1. Tracks motif weights in short-term (STMM) & long-term (LTMM) stores.
2. Applies exponential decay (half-life expressed in *cycles*).
3. Promotes motifs upward when salience ≥ promotion threshold (with hysteresis).
4. Exposes `retrieve()` to surface supportive motifs when reasoning stalls.
5. Exposes `complete_dyad()` to infer missing motifs from TheReefArchive.
6. Optionally journals trace events for observability & replay.

Designed as a plug-in: SymbolicTaskEngine, RecursiveAgentFT or any watcher
can import an instance and call `.access()` / `.update_cycle()` each tick.

Dependencies: stdlib only (math, threading, asyncio, typing).
STMM acts as Noor's **working memory** (live motifs).
LTMM acts as Noor's **symbolic archive** (slow-to-forget).
"""

from __future__ import annotations

__version__ = "1.1.1"
_SCHEMA_VERSION__ = "2025-Q3-motif-memory-v1.1"

import math
import os
import time
import hashlib
import logging
import threading
import asyncio
from collections import deque, OrderedDict
from contextlib import contextmanager, asynccontextmanager
from typing import Callable, Dict, List, Optional, Tuple
from pathlib import Path
import re

# ─────────────────────────────────────────────────────────────
# Configuration constants
# ─────────────────────────────────────────────────────────────
DEFAULT_ST_HALF_LIFE = 25          # cycles  (≈ 0.5 s at 50 Hz)
DEFAULT_LT_HALF_LIFE = 10_000      # cycles  (~3 h at 50 Hz)
DEFAULT_PROMOTION_THRESH = 0.90
DEFAULT_DEMOTION_DELTA = 0.05      # hysteresis gap
TRACE_BUFFER_LEN = 256             # ring size for trace journal
STMM_SOFT_CAP = 50_000             # edge-case guard for STMM+LTMM size
DEFAULT_CACHE_SIZE = 10_000        # max entries in dyad cache

# ─────────────────────────────────────────────────────────────
# Prometheus stubs (optional)
# ─────────────────────────────────────────────────────────────
try:
    from prometheus_client import Counter
except ImportError:  # pragma: no cover
    class _Stub:                  # noqa: D401
        def labels(self, *_, **__):
            return self
        def inc(self, *_): ...
    Counter = _Stub               # type: ignore

REEF_HIT       = Counter("reef_dyad_hits_total",     ["agent_id"])
REEF_MISS      = Counter("reef_dyad_miss_total",    ["agent_id"])
CACHE_HIT      = Counter("dyad_cache_hits_total",   ["agent_id"])
CACHE_MISS     = Counter("dyad_cache_miss_total",   ["agent_id"])
STMM_CAP_SKIP  = Counter("stmm_cap_skips_total",    ["agent_id"])

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _decay_factor(half_life: int) -> float:
    """Return multiplicative decay factor per cycle for given half-life."""
    if half_life <= 0:
        return 0.0
    return math.pow(0.5, 1.0 / half_life)

def _default_jaccard(a: set[str], b: set[str]) -> float:
    """Default Jaccard similarity returns inter/union for sets."""
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

# ─────────────────────────────────────────────────────────────
# Trace journal
# ─────────────────────────────────────────────────────────────
class MotifMemoryTrace:
    """Ring-buffer journal of memory events (retrieve, promote, access)."""

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
    """Short- and long-term motif memory with decay and REEF-based completion."""

    def __init__(
        self,
        *,
        stmm_half_life: int = DEFAULT_ST_HALF_LIFE,
        ltmm_half_life: int = DEFAULT_LT_HALF_LIFE,
        promotion_thresh: float = DEFAULT_PROMOTION_THRESH,
        demotion_delta: float = DEFAULT_DEMOTION_DELTA,
        similarity_fn: Callable[[set[str], set[str]], float] | None = None,
        enable_trace: bool = False,
        reef_path: str | Path | None = "./noor/data/index.REEF",
        agent_id: str = "memory@default",
        stmm_soft_cap: int = STMM_SOFT_CAP,
        reload_reef_on_mtime_change: bool = False,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ) -> None:
        self._stmm: Dict[str, float] = {}
        self._ltmm: Dict[str, float] = {}

        self._st_factor = _decay_factor(stmm_half_life)
        self._lt_factor = _decay_factor(ltmm_half_life)
        self._promo_thresh = promotion_thresh
        self._demote_thresh = promotion_thresh - demotion_delta

        # similarity function for cluster ranking
        self._sim_fn = similarity_fn or _default_jaccard

        self._tlock = threading.RLock()
        self._alock = asyncio.Lock()
        self._trace = MotifMemoryTrace() if enable_trace else None

        # ─── Reef archive state ───────────────────────────────
        self._reef_path = Path(reef_path) if reef_path else None
        self._reef_index: Optional[Dict[str, set[str]]] = None
        self._reef_mtime = 0.0
        self._dyad_cache: OrderedDict[Tuple[str, str], str] = OrderedDict()
        self._reload_reef = reload_reef_on_mtime_change
        self._cache_size = cache_size

        # caps / metrics
        self._stmm_cap = stmm_soft_cap
        self._prom_lbls = dict(agent_id=agent_id)

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

    def _count_total(self) -> int:
        return len(self._stmm) + len(self._ltmm)

    def access(self, motif_id: str, boost: float = 0.2) -> None:
        """Touch a motif seen in live context, boosting its STMM weight."""
        with self._locked():
            # soft-cap guard (edge-case #3)
            if self._count_total() >= self._stmm_cap:
                self._log("soft_cap_skip", motif_id, 0.0)
                STMM_CAP_SKIP.labels(**self._prom_lbls).inc()
                return

            if motif_id in self._ltmm:
                # Bring long-term motif into short-term with a boost.
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
                score = w * self._sim_fn({query_motif}, {m})
                if score > 0:
                    scored.append((m, score))
            scored.sort(key=lambda t: -t[1])
            result = [m for m, _ in scored[:top_k]]
            self._log("retrieve", query_motif, 0.0, returned=result)
            return result

    def export_state(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Return (STMM, LTMM) shallow-copies for dashboards & metrics."""
        with self._locked():
            return dict(self._stmm), dict(self._ltmm)

    def export_trace(self) -> List[dict]:
        if self._trace is None:
            return []
        return self._trace.export()

    # ──────────────────────────────
    # Dyad completion interfaces
    # ──────────────────────────────
    def query_reef_for_completion(self, dyad: Tuple[str, str]) -> Optional[str]:
        return self.complete_dyad(dyad, top_k=1)[0] if self.complete_dyad(dyad) else None

    def complete_dyad(self, dyad: Tuple[str, str], *, top_k: int = 1) -> List[str]:
        """
        Return list of candidate motifs that co-occur with both dyad members
        in any REEF reflection cluster, ranked by similarity + LTMM weight.
        """
        key = tuple(sorted(dyad))
        if key in self._dyad_cache:
            CACHE_HIT.labels(**self._prom_lbls).inc()
            return [self._dyad_cache[key]]
        CACHE_MISS.labels(**self._prom_lbls).inc()

        clusters = self._load_reef_reflections()
        if not clusters:
            REEF_MISS.labels(**self._prom_lbls).inc()
            return []

        m1, m2 = key
        scored: List[Tuple[str, float]] = []
        _, ltmm = self.export_state()
        for cl in clusters.values():
            if {m1, m2}.issubset(cl):
                for cand in cl:
                    if cand not in key:
                        rank = self._sim_fn(cl, {m1, m2}) + ltmm.get(cand, 0.0)
                        scored.append((cand, rank))

        if not scored:
            REEF_MISS.labels(**self._prom_lbls).inc()
            return []

        scored.sort(key=lambda t: -t[1])
        REEF_HIT.labels(**self._prom_lbls).inc()
        # Insert into cache with LRU eviction
        self._dyad_cache[key] = scored[0][0]
        if len(self._dyad_cache) > self._cache_size:
            self._dyad_cache.popitem(last=False)
        return [m for m, _ in scored[:top_k]]

    def suggest_completion_from_ltmm(self, dyad: Tuple[str, str], *, top_k: int = 1) -> List[str]:
        """
        Fallback: Return up to *top_k* motifs from LTMM (high weight), excluding dyad members.
        """
        m1, m2 = dyad
        ignore = {m1, m2}
        _, ltmm = self.export_state()
        scored = [(m, w) for m, w in ltmm.items() if m not in ignore]
        scored.sort(key=lambda t: -t[1])
        return [m for m, _ in scored[:top_k]]

    # ──────────────────────────────
    # Private helpers
    # ──────────────────────────────
    def _apply_decay(self, store: Dict[str, float], factor: float) -> None:
        for k in list(store.keys()):
            store[k] *= factor
            if store[k] < 1e-6:
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

    def _log(self, event_type: str, motif: str, weight: float, **extra) -> None:  # noqa: ANN001
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

    def _load_reef_reflections(self) -> Dict[str, set[str]]:
        """
        Parse `index.REEF`-style file into {cluster_id: set(motif, …)}.
        Reloads file if mtime changed when `reload_reef_on_mtime_change`=True.
        """
        if not self._reef_path or not self._reef_path.exists():
            return {}

        mtime = self._reef_path.stat().st_mtime
        if self._reef_index is not None and (not self._reload_reef or mtime == self._reef_mtime):
            return self._reef_index

        clusters: Dict[str, set[str]] = {}
        pattern = re.compile(r"^motif_id\s*=\s*([a-z0-9_ ]+)$", re.IGNORECASE)
        # attempt to handle transient I/O errors
        for attempt in range(2):
            try:
                with self._reef_path.open("r", encoding="utf-8") as fp:
                    for line in fp:
                        s = line.strip()
                        if s.startswith("motif_id"):
                            match = pattern.match(s)
                            if not match:
                                continue
                            key = hashlib.sha1(s.encode()).hexdigest()[:12]
                            motifs = match.group(1).lower().split()
                            clusters[key] = set(motifs)
                        elif s.startswith("expression"):
                            continue
                break
            except OSError:
                time.sleep(0.05)

        self._reef_index = clusters
        self._reef_mtime = mtime
        return clusters

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
        if t % 5 == 0:
            mm.access("α")
        if t % 7 == 0:
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
