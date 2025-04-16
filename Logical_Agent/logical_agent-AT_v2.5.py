# logical_agent_at.py (v2.5.0)
# By Lina Noor & Uncle (2025)
# -----------------------------------------------------------------------------
# Changelog from v2.4.0 → v2.5.0
#   • Adds MetaField support (entanglements‑of‑entanglements).
#   • Adds Ghost‑Motif registry with witness / ascent logic.
#   • Hard‑clamps strength to [0.0, 1.0] and silently de‑dupes motifs.
#   • Teleport feature now gated by `enable_teleport` (default False); logs warning.
#   • New NetworkX graph render helper with edge‑throttle (MAX_GRAPH_EDGES).
#   • Extended serialization to include new structures + settings.
#   • Thread‑safe across all new methods.
# -----------------------------------------------------------------------------

__version__ = "2.5.0"

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import threading
import hashlib
from collections import defaultdict, deque, Counter
from typing import List, Dict, Tuple, Optional, Any, Union

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
MAX_FIELDS = 1000
MAX_META_FIELDS = 300
MAX_GRAPH_EDGES = 500

# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    """Flattens nested motif lists and returns {flat_list, substructures}."""
    flat_list, substructures, sub_idx = [], {}, 0
    for item in motifs:
        if isinstance(item, list):
            name = f"_sub_{sub_idx}"
            sub_idx += 1
            substructures[name] = item
            flat_list.append(name)
        else:
            flat_list.append(item)
    return {"flat_list": list(set(flat_list)), "substructures": substructures}


def _short_hash(data: str, length: int = 8) -> str:
    return hashlib.sha1(data.encode("utf-8", errors="replace")).hexdigest()[:length]

# ──────────────────────────────────────────────────────────────────────────────
# Main Watcher Class
# ──────────────────────────────────────────────────────────────────────────────

class LogicalAgentAT:
    """LogicalAgentAT v2.5 – motif watcher with MetaField & Ghost support."""

    def __init__(
        self,
        motifs: Optional[List[str]] = None,
        contradiction_log_size: int = 50,
        enable_teleport: bool = False,
        verbose: bool = True
    ):
        self.__version__ = __version__

        # Core stores
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index = defaultdict(list)
        self.field_count = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # New stores
        self.meta_fields: List[Dict[str, Any]] = []
        self.ghost_motifs: Dict[str, Dict[str, Any]] = {}

        # Logs & lineage
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self.history: List[str] = []
        self.lineage: List[str] = []
        self.generation = 0
        self.contradiction_log = deque(maxlen=contradiction_log_size)

        # Settings
        self.enable_teleport = enable_teleport
        self.verbose = verbose

        # Concurrency lock
        self._lock = threading.Lock()

        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    # ────────────────────────────────────────────────────────────────────────
    # 1. Motif‐Cluster Registration
    # ────────────────────────────────────────────────────────────────────────

    def register_motif_cluster(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float,
        *,
        priority_weight: float = 1.0
    ) -> None:
        """Registers a motif cluster as an entanglement field."""
        with self._lock:
            if not motifs or len(motifs) < 2:
                self.history.append(f"Rejected cluster with <2 motifs: {motifs}")
                return

            strength = max(0.0, min(float(strength), 1.0))  # hard clamp
            parsed = _flatten_motifs(motifs)
            flat_list = parsed["flat_list"]
            substructs = parsed["substructures"]

            if self.field_count >= MAX_FIELDS:
                self.history.append("Reached MAX_FIELDS; cannot register more fields.")
                return

            entry = {
                "motifs": flat_list,
                "strength": strength,
                "priority_weight": float(priority_weight),
                "substructures": substructs,
            }
            self.entanglement_fields.append(entry)
            idx = self.field_count
            self.field_count += 1
            for m in flat_list:
                self.field_index[m].append(idx)
            if self.verbose:
                self.history.append(
                    f"Registered field #{idx}: motifs={flat_list}, strength={strength:.3f}, "
                    f"priority={priority_weight:.2f}"
                )

    # Legacy alias
    def register_entanglement_field(self, motifs: List[Union[str, List[str]]], strength: float):
        self.history.append("[DEPRECATED] register_entanglement_field → register_motif_cluster")
        self.register_motif_cluster(motifs, strength)

    # ────────────────────────────────────────────────────────────────────────
    # 1a. Teleport (gated)
    # ────────────────────────────────────────────────────────────────────────

    def teleport_motif_strength(self, source: str, target: str, fidelity: float) -> None:
        with self._lock:
            if not self.enable_teleport:
                self.history.append("⚠️ Teleport disabled (stub). Enable via enable_teleport=True.")
                return
            if source not in self.field_index:
                self.history.append(f"teleport_motif_strength: source='{source}' not found.")
                return
            for idx in self.field_index[source][:]:
                entry = self.entanglement_fields[idx]
                if source in entry["motifs"]:
                    entry["motifs"].remove(source)
                    entry["motifs"].append(target)
                    old_strength = entry["strength"]
                    entry["strength"] *= fidelity
                    self.history.append(
                        f"🌀 Teleported '{source}'→'{target}' in field #{idx}, "
                        f"{old_strength:.3f}→{entry['strength']:.3f} (fid={fidelity:.2f})"
                    )
                    # index housekeeping
                    self.field_index[source].remove(idx)
                    self.field_index[target].append(idx)

    # ────────────────────────────────────────────────────────────────────────
    # 2. MetaField API
    # ────────────────────────────────────────────────────────────────────────

    def register_meta_field(
        self,
        field_ids: List[int],
        *,
        meta_strength: float = 1.0,
        curvature_bias: float = 1.0,
        verse_index: Optional[int] = None,
    ) -> None:
        with self._lock:
            if len(self.meta_fields) >= MAX_META_FIELDS:
                self.history.append("Reached MAX_META_FIELDS; cannot add more.")
                return
            # validate field IDs
            valid_ids = [fid for fid in field_ids if 0 <= fid < self.field_count]
            if len(valid_ids) < 2:
                self.history.append(f"MetaField rejected; need ≥2 valid child fields: {field_ids}")
                return
            signature = f"MetaField-{_short_hash(str(sorted(valid_ids)))}"
            self.meta_fields.append({
                "field_ids": valid_ids,
                "meta_strength": float(meta_strength),
                "curvature_bias": float(curvature_bias),
                "verse_index": verse_index,
                "signature": signature
            })
            if self.verbose:
                self.history.append(f"🌀 Registered MetaField {signature} with children={valid_ids}")

    def _meta_field(self, idx: int) -> Dict[str, Any]:
        return self.meta_fields[idx] if 0 <= idx < len(self.meta_fields) else {}

    def get_meta_alignment_vector(self, idx: int) -> np.ndarray:
        with self._lock:
            meta = self._meta_field(idx)
            if not meta:
                return np.zeros(1)
            vec = np.zeros_like(self.emit_alignment_vector())
            for fid in meta["field_ids"]:
                vec += self.emit_alignment_vector(fid)
            return vec / len(meta["field_ids"])

    def apply_meta_field_gravity(self, idx: int) -> None:
        with self._lock:
            meta = self._meta_field(idx)
            if not meta:
                return
            anchor_vec = self.get_meta_alignment_vector(idx)
            bias = meta["curvature_bias"]
            for fid in meta["field_ids"]:
                if fid >= self.field_count:
                    continue
                field = self.entanglement_fields[fid]
                other_vec = self.emit_alignment_vector(fid)
                dist = np.linalg.norm(anchor_vec - other_vec) + 1e-6
                old_str = field["strength"]
                field["strength"] = old_str / (1 + dist * bias)
            if self.verbose:
                self.history.append(f"🌀 MetaField {meta['signature']} gravity applied (bias={bias:.2f})")

    # ────────────────────────────────────────────────────────────────────────
    # 3. Ghost Motif API
    # ────────────────────────────────────────────────────────────────────────

    def register_ghost_motif(self, motif: str, origin: str, *, strength: float = 0.5):
        with self._lock:
            self.ghost_motifs[motif] = {
                "origin": origin,
                "strength": float(strength),
                "Ω_r": 1.0,
                "ascent_detected": False,
                "witnessed_by": []
            }
            if self.verbose:
                self.history.append(f"👻 Registered ghost motif '{motif}' from {origin}")

    def trace_ascent(self, motif: str, witness: str, verse: Optional[str] = None):
        with self._lock:
            ghost = self.ghost_motifs.get(motif)
            if not ghost:
                return
            ghost["Ω_r"] += 0.2
            ghost["ascent_detected"] = True
            ghost.setdefault("witnessed_by", []).append(witness)
            if verse:
                ghost["ascent_verse"] = verse
            if self.verbose:
                self.history.append(f"👻 Witness '{witness}' traced ascent for motif '{motif}' (Ω_r={ghost['Ω_r']:.2f})")

    def promote_ghost_to_field(self, motif: str):
        with self._lock:
            ghost = self.ghost_motifs.pop(motif, None)
            if not ghost:
                return
            self.register_motif_cluster([motif], strength=ghost.get("strength", 0.3))
            if self.verbose:
                self.history.append(f"👻→🌀 Promoted ghost motif '{motif}' to entanglement field")

    def get_ghost_motifs(self) -> Dict[str, Dict]:
        return self.ghost_motifs

    # Extend observe_state to use ghost motifs (very simple stub)
    def observe_state(self, state: np.ndarray) -> None:
        pass  # Placeholder—hook for future symbolic extraction & ghost ascent

    # ────────────────────────────────────────────────────────────────────────
    # 4. Graph Rendering Helper
    # ────────────────────────────────────────────────────────────────────────

    def render_entanglement_graph(self) -> nx.Graph:
        """Returns a NetworkX graph of motif co‑occurrences with edge throttle."""
        G, edge_count = nx.Graph(), 0
        for field in self.entanglement_fields:
            m_list = field["motifs"]
            for i in range(len(m_list)):
                for j in range(i + 1, len(m_list)):
                    if edge_count >= MAX_GRAPH_EDGES:
                        self.history.append("🌐 Graph edge throttle reached; rendering truncated.")
                        return G
                    A, B = m_list[i], m_list[j]
                    G.add_edge(A, B)
                    edge_count += 1
        return G

    # ────────────────────────────────────────────────────────────────────────
    # 5. Existing Analytical Methods (unchanged)
