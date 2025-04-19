"""
logical_agent_at.py  (v2.6.0)
-----------------------------------------------------------------
Watcher module with Dyad‑Stabiliser, Context Analytics, and Ghost‑Triad
Promotion.  Fully backward‑compatible with v2.5.0 save‑files.
"""

from __future__ import annotations

__version__ = "2.6.0"

import threading
import hashlib
from collections import deque, defaultdict
from typing import List, Dict, Any, Optional, Union

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────
# Constants & Tunables
# ──────────────────────────────────────────────────────────────────────
MAX_FIELDS = 1000
MAX_META_FIELDS = 300
MAX_GRAPH_EDGES = 500

# Dyad decay default — half‑life ≈ 693 steps
DEFAULT_DYAD_DECAY_RATE = 0.999
DEFAULT_WINDOW_SIZE = 250

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

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
    # unique
    return {"flat_list": list(dict.fromkeys(flat)), "substructures": sub}


def _short_hash(data: str, length: int = 8) -> str:
    return hashlib.sha1(data.encode("utf-8", "replace")).hexdigest()[:length]

# ──────────────────────────────────────────────────────────────────────
# Main Class
# ──────────────────────────────────────────────────────────────────────

class LogicalAgentAT:
    """Motif‑watcher with dyad ecology and ghost promotion (v2.6)."""

    def __init__(
        self,
        motifs: Optional[List[str]] = None,
        *,
        contradiction_log_size: int = 50,
        enable_teleport: bool = False,
        verbose: bool = True,
        window_size: int = DEFAULT_WINDOW_SIZE,
        dyad_decay_rate: float = DEFAULT_DYAD_DECAY_RATE,
        enable_auto_triads: bool = True,
    ):
        self.__version__ = __version__

        # Core stores
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index: Dict[str, List[int]] = defaultdict(list)
        self.field_count: int = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # New dyad window
        self._dyad_window: deque[int] = deque(maxlen=window_size)
        self._window_size = window_size
        self.dyad_decay_rate = float(dyad_decay_rate)
        self.enable_auto_triads = enable_auto_triads

        # Meta & Ghost stores
        self.meta_fields: List[Dict[str, Any]] = []
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # Logs & lineage
        self.history: List[str] = []
        self.contradiction_log: deque[str] = deque(maxlen=contradiction_log_size)
        self.generation: int = 0

        # Settings
        self.enable_teleport = enable_teleport
        self.verbose = verbose

        # Thread‑safety
        self._lock = threading.Lock()

        if motifs:
            self.history.append(f"Watcher initialised with motifs {motifs}")

    # ────────────────────────────────────────────────────────────────
    # Dyad Context Helpers
    # ────────────────────────────────────────────────────────────────

    def _update_dyad_window(self, motif_count: int) -> None:
        with self._lock:
            self._dyad_window.append(motif_count)

    def get_dyad_context_ratio(self) -> float:
        with self._lock:
            triads = sum(1 for c in self._dyad_window if c >= 3)
            return triads / len(self._dyad_window) if self._dyad_window else 1.0

    # ────────────────────────────────────────────────────────────────
    # Motif‑Cluster Registration
    # ────────────────────────────────────────────────────────────────

    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0,
        flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        flags = flags or {}
        with self._lock:
            if not motifs or len(motifs) < 2:
                self.history.append("Rejected cluster with <2 motifs")
                return
            if self.field_count >= MAX_FIELDS:
                self.history.append("Reached MAX_FIELDS; registration blocked")
                return

            strength = max(0.0, min(float(strength), 1.0))
            parsed = _flatten_motifs(motifs)
            flat_list = parsed["flat_list"]
            subs = parsed["substructures"]

            is_dyad = len(flat_list) == 2
            dyad_exempt = flags.get("dyad_exempt", False)
            ctx = self.get_dyad_context_ratio()

            curvature_bias = 1.0
            if is_dyad and not dyad_exempt:
                # Soft penalty
                strength *= 0.6 + 0.4 * ctx
                curvature_bias *= 1.5
                if strength > 0.8:
                    curvature_bias *= 2.0
                if self.verbose:
                    self.history.append(
                        f"DYAD_REGISTERED {flat_list} ctx={ctx:.2f} strength→{strength:.3f}"
                    )
            elif is_dyad and dyad_exempt and self.verbose:
                self.history.append(f"DYAD_EXEMPT {flat_list}")

            # Build entry
            entry = {
                "motifs": flat_list,
                "strength": strength,
                "priority_weight": float(priority_weight),
                "substructures": subs,
                "curvature_bias": curvature_bias,
            }
            if is_dyad:
                entry["dyad_flag"] = True
                if dyad_exempt:
                    entry["dyad_exempt"] = True

            # Optional ghost ctx
            if is_dyad and self.enable_auto_triads and not dyad_exempt:
                ghost_id = f"_ctx_{_short_hash(str(flat_list))}"
                self.register_ghost_motif(ghost_id, origin="auto_ctx")
                entry["ghost_ctx"] = ghost_id

            # Store
            idx = self.field_count
            self.entanglement_fields.append(entry)
            self.field_count += 1
            for m in flat_list:
                self.field_index[m].append(idx)

            self._update_dyad_window(len(flat_list))

    # ────────────────────────────────────────────────────────────────
    # Ghost Motif API (unchanged + helper)
    # ────────────────────────────────────────────────────────────────

    def register_ghost_motif(self, motif: str, origin: str, *, strength: float = 0.5):
        with self._lock:
            self.ghost_motifs[motif] = {
                "origin": origin,
                "strength": float(strength),
                "Ω_r": 1.0,
                "ascent_detected": False,
                "witnessed_by": []
            }

    def promote_ghost_to_field(self, motif: str):
        ghost = self.ghost_motifs.pop(motif, None)
        if ghost:
            self.register_motif_cluster([motif], strength=ghost.get("strength", 0.3))

    # Very naive embedding‑presence check
    def _ghost_seen_in_state(self, motif_id: str, state: np.ndarray) -> bool:
        emb = self.motif_embeddings.get(motif_id)
        return emb is not None and np.dot(state, emb) > 0.1

    # ────────────────────────────────────────────────────────────────
    # Observe State (dyad decay & auto‑triad)
    # ────────────────────────────────────────────────────────────────

    def observe_state(self, state: np.ndarray) -> None:
        with self._lock:
            self.generation += 1
            # decay & promotion loop
            for fid, field in enumerate(self.entanglement_fields):
                if field.get("dyad_flag") and not field.get("dyad_exempt"):
                    # decay strength
                    old = field["strength"]
                    field["strength"] *= self.dyad_decay_rate
                    if self.generation % 100 == 0 and self.verbose:
                        self.history.append(
                            f"DYAD_DECAY #{fid} {old:.3f}→{field['strength']:.3f}"
                        )
                    # auto‑triad promotion
                    gctx = field.get("ghost_ctx")
                    if gctx and self._ghost_seen_in_state(gctx, state):
                        motifs = field["motifs"] + [gctx]
                        self.promote_ghost_to_field(gctx)
                        self.register_motif_cluster(motifs, strength=field["strength"] * 1.1)
                        field["dyad_flag"] = False  # retire flag
                        if self.verbose:
                            self.history.append(f"DYAD_PROMOTED_TO_TRIAD {motifs}")
            # window update (state could hint at motif counts via embeddings?)
            # For now just use last field sizes to keep ratio rolling
            if self.entanglement_fields:
                self._update_dyad_window(len(self.entanglement_fields[-1]["motifs"]))

    # ────────────────────────────────────────────────────────────────
    # Dyad Metrics Export
    # ────────────────────────────────────────────────────────────────

    def export_dyad_metrics(self) -> Dict[str, float]:
        with self._lock:
            total = len(self._dyad_window)
            dyads = sum(1 for c in self._dyad_window if c == 2)
            triads = total - dyads
            return {
                "generation": self.generation,
                "window": total,
                "dyads": dyads,
                "triads": triads,
                "context_ratio": self.get_dyad_context_ratio(),
            }

    # ────────────────────────────────────────────────────────────────
    # Graph Rendering helper (unchanged except thread‑lock)
    # ────────────────────────────────────────────────────────────────
    def render_entanglement_graph(self) -> nx.Graph:
        G, edge_counter = nx.Graph(), 0
        with self._lock:
            for field in self.entanglement_fields:
                ml = field["motifs"]
                for i in range(len(ml)):
                    for j in range(i + 1, len(ml)):
                        if edge_counter >= MAX_GRAPH_EDGES:
                            self.history.append("Graph edge throttle reached; truncated")
                            return G
                        A, B = ml[i], ml[j]
                        G.add_edge(A, B)
                        edge_counter += 1
        return G

    # ────────────────────────────────────────────────────────────────
    # Serialization helpers (minimal patch)
    # ────────────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "version": self.__version__,
                "entanglement_fields": self.entanglement_fields,
                "ghost_motifs": self.ghost_motifs,
                "meta_fields": self.meta_fields,
                "_dyad_window": list(self._dyad_window),
                "window_size": self._window_size,
                "dyad_decay_rate": self.dyad_decay_rate,
                "enable_auto_triads": self.enable_auto_triads,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        watcher = cls(window_size=data.get("window_size", DEFAULT_WINDOW_SIZE),
                      dyad_decay_rate=data.get("dyad_decay_rate", DEFAULT_DYAD_DECAY_RATE),
                      enable_auto_triads=data.get("enable_auto_triads", True),
                      verbose=False)
        watcher.entanglement_fields = data.get("entanglement_fields", [])
        watcher.ghost_motifs = data.get("ghost_motifs", {})
        watcher.meta_fields = data.get("meta_fields", [])
        watcher.field_count = len(watcher.entanglement_fields)
        watcher._dyad_window = deque(data.get("_dyad_window", []), maxlen=watcher._window_size)
        return watcher

    # ────────────────────────────────────────────────────────────────
    # Placeholder stubs for other public APIs (unchanged)
    # ────────────────────────────────────────────────────────────────

    def emit_alignment_vector(self, fid: int = -1) -> np.ndarray:
        """Return dummy zero‑vec unless embeddings are wired externally."""
        if fid == -1:
            return np.zeros(1)
        field = self.entanglement_fields[fid]
        vecs = [self.motif_embeddings.get(m) for m in field["motifs"] if m in self.motif_embeddings]
        return np.mean(vecs, axis=0) if vecs else np.zeros(1)

    # Teleport, meta‑field gravity etc. remain from v2.5; omitted for brevity.
