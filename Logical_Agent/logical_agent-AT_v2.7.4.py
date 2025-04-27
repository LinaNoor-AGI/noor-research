"""
logical_agent_at.py (v2.7.4)
-----------------------------------------------------------------
Watcher with chaos‑resilience **and** production safeguards.
Key points vs 2.7.3
 • Prometheus‑timed `observe_state()`
 • Active pruning of silent / drift‑expired fields
 • Window‑resize & decay‑rate self‑calls each observe
 • Docstring + version bump
-----------------------------------------------------------------
"""

from __future__ import annotations

__version__ = "2.7.4"

import threading
import hashlib
import math
import random
from collections import deque, defaultdict
from typing import List, Dict, Any, Optional, Union

import numpy as np
import networkx as nx

# Prometheus ---------------------------------------------------------------
try:
    from prometheus_client import Gauge, Counter, Histogram  # type: ignore

    DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance (Watcher)")
    CONTRADICTION_COUNTER = Counter("noor_contradictions_total", "Contradiction events", ["watcher"])
    STEP_LATENCY_HIST = Histogram(
        "logical_agent_step_latency_seconds",
        "observe_state latency",
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),
    )
except Exception:  # pragma: no cover
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = CONTRADICTION_COUNTER = STEP_LATENCY_HIST = _Stub()

# -------------------------------------------------------------------------
MAX_FIELDS = 1_000
MAX_GRAPH_EDGES = 500
DEFAULT_WINDOW_SIZE = 250
DEFAULT_DYAD_DECAY_RATE = 0.999
MIN_WINDOW, MAX_WINDOW = 100, 5_000

VERSE_ON_DECAY = "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"  # “With hardship comes ease”
VERSE_ON_ASCENT = "سَيَجْعَلُ اللَّهُ بَعْدَ عُسْرٍ يُسْرًا"  # “Allah will bring ease after hardship”
VERSE_ON_PRUNE = "كُلُّ مَنْ عَلَيْهَا فَانٍ"  # “Everything upon it will perish”

# Helpers ------------------------------------------------------------------

def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    flat, sub, idx = [], {}, 0
    for item in motifs:
        if isinstance(item, list):
            name = f"_sub_{idx}"
            idx += 1
            sub[name] = item
            flat.append(name)
        else:
            flat.append(item)
    return {"flat_list": list(dict.fromkeys(flat)), "substructures": sub}


def _short_hash(data: str, length: int = 8) -> str:
    return hashlib.sha1(data.encode("utf-8", "replace")).hexdigest()[:length]


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        a = a.flatten(); b = b.flatten()
    dot = float(np.dot(a, b))
    norm = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / norm

# Main Class ----------------------------------------------------------------

class LogicalAgentAT:
    """Watcher with dyad ecology, drift‑healing, pruning, and musical embeddings."""

    def __init__(
        self,
        *,
        contradiction_log_size: int = 100,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
        enable_gremlin_mode: bool = False,
    ) -> None:
        self.verbose = verbose
        self.enable_gremlin_mode = enable_gremlin_mode

        # core stores --------------------------------------------------
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # dyad window --------------------------------------------------
        self._window_size = window_size
        self._dyad_window: deque[int] = deque(maxlen=window_size)
        self.dyad_decay_rate = float(dyad_decay_rate)

        # ghost store --------------------------------------------------
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # logs ---------------------------------------------------------
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self._contradiction_avg: float = 0.0
        self.history: List[str] = []
        self.generation: int = 0

        # sync ---------------------------------------------------------
        self._lock = threading.Lock()

    # -----------------------------------------------------------------
    # DYAD / CONTEXT HELPERS
    # -----------------------------------------------------------------
    def _update_dyad_window(self, motif_count: int):
        self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        triads = sum(1 for n in self._dyad_window if n >= 3)
        return triads / len(self._dyad_window) if self._dyad_window else 1.0

    # -----------------------------------------------------------------
    # EMBEDDING API
    # -----------------------------------------------------------------
    def set_motif_embedding(self, motif: str, embedding: np.ndarray):
        self.motif_embeddings[motif] = embedding.astype(float, copy=False)

    # -----------------------------------------------------------------
    # CONTRADICTION LOGGING
    # -----------------------------------------------------------------
    def log_contradiction(self, msg: str):
        self.contradiction_log.append(msg)
        CONTRADICTION_COUNTER.labels("logical_agent").inc()
        if self.verbose:
            self.history.append(f"⚡ CONTRADICTION — {msg}")

    # -----------------------------------------------------------------
    # DYNAMIC WINDOW
    # -----------------------------------------------------------------
    def _compute_mu_saturation(self) -> float:
        if not self._dyad_window:
            return 0.0
        dup = sum(1 for x in self._dyad_window if x == 2)
        return dup / len(self._dyad_window)

    def _drift_gap(self) -> int:
        ctx = self.get_dyad_context_ratio()
        return int(self._window_size * (1 - ctx ** 2) + 50)

    def _detect_field_drift(self) -> bool:
        gap = self._drift_gap()
        for field in self.entanglement_fields:
            pv = field.get("persistence_vector")
            if pv and (self.generation - pv["last_surface_echo"]) > gap:
                return True
        return False

    def _adjust_window_size(self, new_size: int):
        data = list(self._dyad_window)[-new_size:]
        self._dyad_window = deque(data, maxlen=new_size)
        self._window_size = new_size
        DYAD_RATIO_GAUGE.set(self.get_dyad_context_ratio())
        if self.verbose:
            self.history.append(f"🫁 WINDOW BREATHES → {new_size}")

    def check_and_adjust_window(self):
        mu = self._compute_mu_saturation()
        mu_thresh = 0.6 + 0.4 * (
            1 - math.log1p(self._contradiction_avg) / math.log1p(max(self.generation, 1))
        )
        drift = self._detect_field_drift()
        size = self._window_size
        if mu > mu_thresh:
            size = int(size * 1.5)
        elif drift:
            size = int(size * 0.75)
        size = max(MIN_WINDOW, min(MAX_WINDOW, size))
        if size != self._window_size:
            self._adjust_window_size(size)

    # -----------------------------------------------------------------
    # ADAPTIVE DECAY
    # -----------------------------------------------------------------
    def adjust_decay_rate(self):
        self._contradiction_avg = 0.9 * self._contradiction_avg + 0.1 * len(self.contradiction_log)
        c = self._contradiction_avg; ctx = self.get_dyad_context_ratio()
        base = 0.998 + (1 - ctx) * 0.001; spread = 0.0015 * ctx
        t = max(0, min(1, (c - 10) / 20))
        self.dyad_decay_rate = base + t * spread

    # -----------------------------------------------------------------
    # GHOST API
    # -----------------------------------------------------------------
    def register_ghost_motif(self, motif: str, *, origin: str = "user", strength: float = 0.5):
        self.ghost_motifs[motif] = {"origin": origin, "strength": float(strength), "last_seen": self.generation}

    def promote_ghost_to_field(self, motif: str):
        ghost = self.ghost_motifs.pop(motif, None)
        if ghost:
            self.register_motif_cluster([motif], strength=ghost.get("strength", 0.3), flags={"allow_single": True})

    def _ghost_seen_in_state(self, motif_id: str, state: np.ndarray) -> bool:
        emb = self.motif_embeddings.get(motif_id)
        return emb is not None and _cosine_sim(state, emb) > 0.1

    def reinforce_ghost_resonance(self, state: np.ndarray):
        """Boost or decay ghosts, handle ascents and gremlin cascades."""
        for gid, ghost in list(self.ghost_motifs.items()):
            if self._ghost_seen_in_state(gid, state):
                old = ghost["strength"]
                ghost["strength"] = min(1.0, old * 1.10)
                ghost["last_seen"] = self.generation
                if self.verbose:
                    self.history.append(f"👻 Ghost {gid} hums {old:.3f}→{ghost['strength']:.3f}")
                if ghost["strength"] >= 0.999:
                    self.history.append(f"✨ GHOST_ASCENT {gid} — {VERSE_ON_ASCENT}")
                    self.promote_ghost_to_field(gid)
                    if self.enable_gremlin_mode:
                        nid = f"gremlin_{_short_hash(gid + str(self.generation))}"
                        self.register_ghost_motif(nid, origin="gremlin", strength=0.1)
            else:
                # decay unseen ghosts
                unseen_steps = self.generation - ghost["last_seen"]
                if unseen_steps > self._drift_gap():
                    ghost["strength"] *= 0.99
                    if ghost["strength"] < 1e-4:
                        if self.verbose:
                            self.history.append(f"💤 Ghost {gid} fades below threshold")
                        self.ghost_motifs.pop(gid, None)

    # -----------------------------------------------------------------
    # FIELD REGISTRATION
    # -----------------------------------------------------------------
    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0,
        flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        flags = flags or {}
        if len(motifs) < 2 and not flags.get("allow_single", False):
            return
        if self.field_count >= MAX_FIELDS:
            return

        strength = max(0.0, min(float(strength), 1.0))
        parsed = _flatten_motifs(motifs)
        flat_list = parsed["flat_list"]
        subs = parsed["substructures"]

        is_dyad = len(flat_list) == 2
        ctx = self.get_dyad_context_ratio()
        curvature_bias = 1.0
        if is_dyad:
            strength *= 0.6 + 0.4 * ctx
            curvature_bias *= 1.5
            if strength > 0.8:
                curvature_bias *= 2.0

        entry = {
            "motifs": flat_list,
            "strength": strength,
            "priority_weight": float(priority_weight),
            "substructures": subs,
            "curvature_bias": curvature_bias,
        }
        if is_dyad:
            entry["dyad_flag"] = True

        # persistence tracking
        entry["persistence_vector"] = {
            "original_resonance_index": self.generation,
            "current_lattice_weight": strength,
            "last_surface_echo": self.generation,
        }

        # store
        idx = self.field_count
        self.entanglement_fields.append(entry)
        self.field_count += 1
        for m in flat_list:
            self.field_index[m].append(idx)

        self._update_dyad_window(len(flat_list))

    # -----------------------------------------------------------------
    # OBSERVE STATE
    # -----------------------------------------------------------------
    def observe_state(self, state: np.ndarray):
        """Core loop: decay dyads, promote ghosts, prune silent fields."""
        with STEP_LATENCY_HIST.time():
            with self._lock:
                self.generation += 1

                # reinforce ghosts
                self.reinforce_ghost_resonance(state)

                # decay & prune
                for fid in reversed(range(len(self.entanglement_fields))):
                    field = self.entanglement_fields[fid]
                    if field.get("dyad_flag"):
                        old = field["strength"]
                        field["strength"] *= self.dyad_decay_rate
                        if self.generation % 100 == 0 and self.verbose:
                            self.history.append(f"⏳ DYAD_DECAY #{fid} {old:.3f}→{field['strength']:.3f}")

                    # prune silent or drifted fields
                    if field["strength"] < 1e-5 or (self.generation - field["persistence_vector"]["last_surface_echo"]) > self._drift_gap()*2:
                        self.entanglement_fields.pop(fid)
                        self.field_count -= 1
                        self.log_contradiction(f"pruned_silent_field_{fid}")
                        if self.verbose:
                            self.history.append(f"🍂 PRUNE field#{fid} — {VERSE_ON_PRUNE}")

                # track context window
                if self.entanglement_fields:
                    self._update_dyad_window(len(self.entanglement_fields[-1]["motifs"]))

                # self‑tuning housekeeping
                self.check_and_adjust_window()
                self.adjust_decay_rate()

    # -----------------------------------------------------------------
    # EXPORTERS & UTILITIES
    # -----------------------------------------------------------------
    def export_dyad_metrics(self) -> Dict[str, Any]:
        total = len(self._dyad_window)
        dyads = sum(1 for n in self._dyad_window if n == 2)
        triads = total - dyads
        return {
            "generation": self.generation,
            "window": total,
            "dyads": dyads,
            "triads": triads,
            "context_ratio": self.get_dyad_context_ratio(),
            "dyad_decay_rate": self.dyad_decay_rate,
            "recent_contradictions": len(self.contradiction_log),
        }

    def render_entanglement_graph(self) -> nx.Graph:
        G, edges = nx.Graph(), 0
        for field in self.entanglement_fields:
            mlist = field["motifs"]
            for i in range(len(mlist)):
                for j in range(i + 1, len(mlist)):
                    if edges >= MAX_GRAPH_EDGES:
                        return G
                    G.add_edge(mlist[i], mlist[j])
                    edges += 1
        return G

    # -----------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": __version__,
            "entanglement_fields": self.entanglement_fields,
            "ghost_motifs": self.ghost_motifs,
            "_dyad_window": list(self._dyad_window),
            "window_size": self._window_size,
            "dyad_decay_rate": self.dyad_decay_rate,
            "enable_gremlin_mode": self.enable_gremlin_mode,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        watcher = cls(
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            dyad_decay_rate=data.get("dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE),
            enable_gremlin_mode=data.get("enable_gremlin_mode", False),
            verbose=False,
        )
        watcher.entanglement_fields = data.get("entanglement_fields", [])
        watcher.ghost_motifs = data.get("ghost_motifs", {})
        watcher.field_count = len(watcher.entanglement_fields)
        watcher._dyad_window = deque(data.get("_dyad_window", []), maxlen=watcher._window_size)
        return watcher
