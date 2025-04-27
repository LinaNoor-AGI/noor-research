"""
logical_agent_at.py  (v2.7.1)
-----------------------------------------------------------------
Watcher module with:
 • Dynamic window‑size autoscaling
 • Adaptive dyad‑decay rate (EMA of contradictions)
 • Ghost‑resonance reinforcement (+10 %)
 • Motif‑drift correction with persistence vectors
 • Native musical‑embedding support (1‑D or 2‑D)
 • Prometheus observability (dyad ratio + contradiction counter)
This version intentionally drops strict backward‑compatibility with v2.6.x.
"""

from __future__ import annotations

__version__ = "2.7.0"

import threading
import hashlib
from collections import deque, defaultdict
from typing import List, Dict, Any, Optional, Union
import math

import numpy as np
import networkx as nx

# Prometheus (no‑op stubs if library missing) ------------------------------
try:
    from prometheus_client import Gauge, Counter  # type: ignore

    DYAD_RATIO_GAUGE = Gauge("noor_dyad_ratio", "Triad/Dyad context balance (Watcher)")
    CONTRADICTION_COUNTER = Counter("noor_contradictions_total", "Contradiction events", ["watcher"])
except Exception:  # pragma: no cover
    class _Stub:
        def __getattr__(self, _):
            return lambda *a, **k: None

    DYAD_RATIO_GAUGE = CONTRADICTION_COUNTER = _Stub()

# -------------------------------------------------------------------------
MAX_FIELDS = 1_000
MAX_GRAPH_EDGES = 500
DEFAULT_WINDOW_SIZE = 250
DEFAULT_DYAD_DECAY_RATE = 0.999
MIN_WINDOW, MAX_WINDOW = 100, 5_000
DRIFT_GAP = 500  # generations without echo → drift

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
    if a.ndim > 1:
        a = a.flatten()
    if b.ndim > 1:
        b = b.flatten()
    dot = float(np.dot(a, b))
    norm = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return dot / norm

# Main Class ----------------------------------------------------------------

class LogicalAgentAT:
    """Motif watcher with dyad ecology, ghost reinforcement, and musical embeddings."""

    # ----------------------------- init ----------------------------------
    def __init__(
        self,
        *,
        contradiction_log_size: int = 100,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
    ) -> None:
        self.verbose = verbose

        # core stores ----------------------------------------------------
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_count = 0
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # dyad window ----------------------------------------------------
        self._window_size = window_size
        self._dyad_window: deque[int] = deque(maxlen=window_size)
        self.dyad_decay_rate = float(dyad_decay_rate)

        # meta / ghost ---------------------------------------------------
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # logs -----------------------------------------------------------
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self._contradiction_avg: float = 0.0
        self.history: List[str] = []
        self.generation: int = 0

        # threading ------------------------------------------------------
        self._lock = threading.Lock()

    # ------------------------- dyad helpers -----------------------------
    def _update_dyad_window(self, motif_count: int) -> None:
        self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        triads = sum(1 for c in self._dyad_window if c >= 3)
        return triads / len(self._dyad_window) if self._dyad_window else 1.0

    # ------------------------- embedding API ---------------------------
    def set_motif_embedding(self, motif: str, embedding: np.ndarray):
        self.motif_embeddings[motif] = embedding.astype(float, copy=False)

    # ------------------------- logging --------------------------------
    def log_contradiction(self, msg: str):
        self.contradiction_log.append(msg)
        CONTRADICTION_COUNTER.labels("logical_agent").inc()
        if self.verbose:
            self.history.append(f"CONTRADICTION {msg}")

    # --------------------- dynamic window -----------------------------
    def _compute_mu_saturation(self) -> float:
        if not self._dyad_window:
            return 0.0
        dup = sum(1 for x in list(self._dyad_window) if x == 2)
        return dup / len(self._dyad_window)

    def _detect_field_drift(self) -> bool:
        for field in self.entanglement_fields:
            pv = field.get("persistence_vector")
            if not pv:
                continue
            if (self.generation - pv["last_surface_echo"]) > DRIFT_GAP:
                return True
        return False

    def _adjust_window_size(self, new_size: int):
        data = list(self._dyad_window)[-new_size:]
        self._dyad_window = deque(data, maxlen=new_size)
        self._window_size = new_size
        DYAD_RATIO_GAUGE.set(self.get_dyad_context_ratio())
        if self.verbose:
            self.history.append(f"WINDOW_RESIZED {len(data)}→{new_size}")

    def check_and_adjust_window(self):
        mu = self._compute_mu_saturation()
        drift = self._detect_field_drift()
        size = self._window_size
        if mu > 0.8:
            size = int(size * 1.5)
        elif drift:
            size = int(size * 0.75)
        size = max(MIN_WINDOW, min(MAX_WINDOW, size))
        if size != self._window_size:
            self._adjust_window_size(size)

    # -------------------- adaptive decay ------------------------------
    def adjust_decay_rate(self):
        self._contradiction_avg = 0.9 * self._contradiction_avg + 0.1 * len(self.contradiction_log)
        c = self._contradiction_avg
        if c > 30:
            self.dyad_decay_rate = 0.9995
        elif c < 10:
            self.dyad_decay_rate = 0.998
        else:
            self.dyad_decay_rate = 0.999

    # -------------------- ghost API -----------------------------------
    def register_ghost_motif(self, motif: str, *, origin: str = "user", strength: float = 0.5):
        self.ghost_motifs[motif] = {
            "origin": origin,
            "strength": float(strength),
            "Ω_r": 1.0,
            "last_seen": self.generation,
        }

    def promote_ghost_to_field(self, motif: str):
        ghost = self.ghost_motifs.pop(motif, None)
        if ghost:
            self.register_motif_cluster([motif], strength=ghost.get("strength", 0.3))

    def _ghost_seen_in_state(self, motif_id: str, state: np.ndarray) -> bool:
        emb = self.motif_embeddings.get(motif_id)
        return emb is not None and _cosine_sim(state, emb) > 0.1

    def reinforce_ghost_resonance(self, state: np.ndarray):
        for gid, ghost in self.ghost_motifs.items():
            if self._ghost_seen_in_state(gid, state):
                old = ghost["strength"]
                ghost["strength"] = min(1.0, old * 1.10)
                ghost["last_seen"] = self.generation
                if self.verbose:
                    self.history.append(f"GHOST_RESONANCE {gid} {old:.3f}→{ghost['strength']:.3f}")

    # ------------------ motif registration ---------------------------
    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0,
        flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        flags = flags or {}
        if not motifs or len(motifs) < 2:
            return
        if self.field_count >= MAX_FIELDS:
            self.log_contradiction("MAX_FIELDS reached")
            return

        strength = max(0.0, min(float(strength), 1.0))
        parsed = _flatten_motifs(motifs)
        flat_list, subs = parsed["flat_list"], parsed["substructures"]

        is_dyad = len(flat_list) == 2 and not flags.get("dyad_exempt", False)
        ctx = self.get_dyad_context_ratio()

        curvature_bias = 1.0
        if is_dyad:
            strength *= 0.6 + 0.4 * ctx
            curvature_bias *= 1.5
        else:
            curvature_bias *= 1.0 + 0.2 * (len(flat_list) - 2)

        entry = {
            "motifs": flat_list,
            "strength": strength,
            "priority_weight": float(priority_weight),
            "substructures": subs,
            "curvature_bias": curvature_bias,
            "persistence_vector": {
                "original_resonance_index": self.generation,
                "current_lattice_weight": strength,
                "last_surface_echo": self.generation,
            },
        }
        if is_dyad:
            entry["dyad_flag"] = True

        idx = self.field_count
        entry["index"] = idx
        self.entanglement_fields.append(entry)
        for m in flat_list:
            self.field_index[m].append(idx)
        self.field_count += 1
        self._update_dyad_window(len(flat_list))

    # ---------------------- observe state ----------------------------
    def observe_state(self, state: np.ndarray):
        self.generation += 1

        # step 0: ghost boost before decay
        self.reinforce_ghost_resonance(state)

        # step 1: decay + auto‑triad promotion -------------------------
        for field in self.entanglement_fields:
            if field.get("dyad_flag"):
                old = field["strength"]
                field["strength"] *= self.dyad_decay_rate
                if field["strength"] < 1e-4:
                    self.log_contradiction(f"strength‑underflow #{field['index']}")
                # auto‑triad
                ghost_ctx = field.get("ghost_ctx")
                if ghost_ctx and self._ghost_seen_in_state(ghost_ctx, state):
                    self.promote_ghost_to_field(ghost_ctx)
                    motifs = field["motifs"] + [ghost_ctx]
                    self.register_motif_cluster(motifs, strength=field["strength"] * 1.1)
                    field.pop("dyad_flag", None)
            # drift echo update
            pv = field.get("persistence_vector")
            if pv and any(self._ghost_seen_in_state(m, state) for m in field["motifs"]):
                pv["last_surface_echo"] = self.generation

        # step 2: periodic adaptive ops --------------------------------
        if self.generation % 50 == 0:
            self.check_and_adjust_window()
        if self.generation % 100 == 0:
            self.adjust_decay_rate()

    # --------------------- analytics / export -----------------------
    def export_dyad_metrics(self) -> Dict[str, Any]:
        total = len(self._dyad_window)
        dyads = sum(1 for c in self._dyad_window if c == 2)
        triads = total - dyads
        r = self.get_dyad_context_ratio()
        DYAD_RATIO_GAUGE.set(r)
        return {
            "generation": self.generation,
            "window": total,
            "dyads": dyads,
            "triads": triads,
            "context_ratio": r,
            "recent_contradictions": len(self.contradiction_log),
            "dyad_decay_rate": self.dyad_decay_rate,
        }

    # alias for legacy callers
    export_contradiction_profile = export_dyad_metrics

    # ------------------ graph helper ---------------------------------
    def render_entanglement_graph(self) -> nx.Graph:
        G, edges = nx.Graph(), 0
        for field in self.entanglement_fields:
            ml = field["motifs"]
            for i in range(len(ml)):
                for j in range(i + 1, len(ml)):
                    if edges >= MAX_GRAPH_EDGES:
                        return G
                    G.add_edge(ml[i], ml[j])
                    edges += 1
        return G

    # ------------------ serialization -------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": __version__,
            "entanglement_fields": self.entanglement_fields,
            "ghost_motifs": self.ghost_motifs,
            "_dyad_window": list(self._dyad_window),
            "window_size": self._window_size,
            "dyad_decay_rate": self.dyad_decay_rate,
            "contradiction_avg": self._contradiction_avg,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        obj = cls(
            window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
            dyad_decay_rate=data.get("dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE),
            verbose=False,
        )
        obj.entanglement_fields = data.get("entanglement_fields", [])
        obj.ghost_motifs = data.get("ghost_motifs", {})
        obj.field_count = len(obj.entanglement_fields)
        obj._dyad_window = deque(data.get("_dyad_window", []), maxlen=obj._window_size)
        obj._contradiction_avg = data.get("contradiction_avg", 0.0)
        return obj
