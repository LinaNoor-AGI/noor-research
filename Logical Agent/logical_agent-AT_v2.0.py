# logical_agent-AT.py (v2.0)
# By Lina Noor & Uncle (2025)
#
# LogicalAgentAT v2.0:
#   - "Entanglement fields" (renamed from motif clusters)
#   - Nested / recursive motif support
#   - Curvature-based analysis of fields if numeric embeddings are provided
#   - Extended resonance/harmonic analysis returning field-wise data
#   - Optional alignment vector that watchers can emit to agents or cores
#   - Backward compatibility with older method names (v1.x)
#
# NOTE: This is a reference implementation. The specifics of nested
#       motif handling, curvature logic, and resonance output can be adapted
#       to your actual data/requirements.

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Any,
    Union
)


MAX_FIELDS = 1000  # Was previously MAX_MOTIFS


def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    """
    Example helper to detect substructures in the 'motifs' list.
    If an entry is a nested list, we treat it as a 'substructure.'
    Returns a dict:
      {
        "flat_list": [... all top-level motif names ...],
        "substructures": {
           "internal_key_1": [sub_motif1, sub_motif2],
           ...
        }
      }
    In real usage, you'd want to handle deeper recursion or naming collisions.
    """
    flat_list = []
    substructures = {}

    # We'll generate a simple placeholder name for each sub-list
    sub_idx = 0

    for item in motifs:
        if isinstance(item, list):
            name = f"_sub_{sub_idx}"
            sub_idx += 1
            # store this substructure
            substructures[name] = item
            flat_list.append(name)
        else:
            # item should be a str
            flat_list.append(item)

    return {
        "flat_list": list(set(flat_list)),  # deduplicate
        "substructures": substructures
    }


class LogicalAgentAT:
    """
    LogicalAgentAT v2.0: 
      - 'entanglement_fields' is the new container (was 'entangled_motifs' in v1.x).
      - Each entry is a dict:
          {
            "motifs": [motif1, motif2, ..., motifN],  # top-level or sub-names
            "strength": float,
            "substructures": {...},  # optional nested motif definitions
          }
      - The watcher can:
         1) Register new entanglement fields (possibly nested)
         2) Compute curvature if motif embeddings exist
         3) Generate field-wise harmonic or signature data
         4) Emit an alignment vector summarizing all fields
      - Maintains backward compatibility for older calls (v1.x).
    """

    def __init__(self, motifs: Optional[List[str]] = None):
        """
        :param motifs: (Optional) initial list of motif names, for custom usage.
        """
        # entanglement_fields is the main container now
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index = defaultdict(list)  # maps motif -> list of field indices
        self.field_count = 0

        # For numeric embeddings (optional):
        #   e.g. self.motif_embeddings["motifA"] = np.array([0.2, 0.8])
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # Symbolic references / metadata
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self._resonance_map: Dict[str, float] = {}

        # For local usage or expansions
        self._recent_resonance = deque(maxlen=20)
        self.lineage: List[str] = []
        self.generation = 0

        # Logging & history
        self.history: List[str] = []
        self.version = "2.0"
        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    # -------------------------------------------------------------------------
    # 1) REGISTRATION
    # -------------------------------------------------------------------------

    def register_entanglement_field(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float
    ):
        """
        Creates a new entanglement field with one 'strength' value
        shared across all listed motifs. (Some may be sub-lists for nested usage.)

        :param motifs: e.g. ["alpha", ["a1", "a2"], "beta"]
        :param strength: single float for the entire field
        """
        if not motifs or len(motifs) < 2:
            self.history.append(
                f"Rejected field with <2 top-level items: {motifs}"
            )
            return
        if self.field_count >= MAX_FIELDS:
            self.history.append(
                "Reached MAX_FIELDS; cannot register additional entanglement fields."
            )
            return

        # Flatten & deduplicate
        parsed = _flatten_motifs(motifs)
        flat_list = parsed["flat_list"]
        substructs = parsed["substructures"]

        entry = {
            "motifs": flat_list,        # e.g. ["alpha", "_sub_0", "beta"]
            "strength": float(strength),
            "substructures": substructs  # e.g. { "_sub_0": ["a1", "a2"] }
        }

        self.entanglement_fields.append(entry)
        idx = self.field_count
        self.field_count += 1

        # Update field_index
        for motif in flat_list:
            self.field_index[motif].append(idx)

        self.history.append(f"Registered entanglement field #{idx} with motifs={flat_list}")

    # Legacy / backward-compat method:
    def register_motif_cluster(self, motifs: List[str], strength: float):
        """
        DEPRECATED in v2.0:
        For backward compatibility, calls 'register_entanglement_field'.
        """
        self.history.append(
            "[DEPRECATED] register_motif_cluster called; redirecting to register_entanglement_field."
        )
        return self.register_entanglement_field(motifs, strength)

    def set_motif_embedding(self, motif: str, embedding: np.ndarray):
        """
        Optionally store a numeric embedding for a given motif.
        This is necessary if you plan to compute curvature using numeric vectors.
        """
        self.motif_embeddings[motif] = embedding
        self.history.append(f"Set numeric embedding for motif '{motif}': {embedding}")

    # -------------------------------------------------------------------------
    # 2) FIELD OPERATIONS (Teleport, Freeze, Prune) - adapted for new structure
    # -------------------------------------------------------------------------

    def teleport_motif_strength(self, source: str, target: str, fidelity: float):
        """
        Transfer 'source' motif references to 'target' within all fields,
        multiplying each field's strength by fidelity whenever changed.
        """
        for idx, entry in enumerate(self.entanglement_fields):
            if source in entry["motifs"]:
                entry["motifs"].remove(source)
                entry["motifs"].append(target)
                entry["strength"] *= fidelity
                # Also update field_index references
                if idx in self.field_index[source]:
                    self.field_index[source].remove(idx)
                self.field_index[target].append(idx)

    def freeze_motif(self, motif: str):
        """
        For n-ary approach, 'freezing' a motif by "teleporting" it onto itself
        at fidelity=1.0 won't practically change anything.
        We keep it for legacy reasons or if you want to interpret it differently.
        """
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1):
        """
        Remove all fields whose strength is below the threshold.
        Then rebuild the field_index accordingly.
        """
        if self.field_count == 0:
            return

        kept = []
        for entry in self.entanglement_fields:
            if entry["strength"] > threshold:
                kept.append(entry)

        self.entanglement_fields = kept
        self.field_count = len(kept)
        # Rebuild index
        self.field_index.clear()
        for idx, entry in enumerate(self.entanglement_fields):
            for motif in entry["motifs"]:
                self.field_index[motif].append(idx)

        self.history.append(
            f"Pruned fields below strength={threshold}. Remaining count={self.field_count}."
        )

    # -------------------------------------------------------------------------
    # 3) ENTANGLEMENT ANALYSIS
    # -------------------------------------------------------------------------

    def compute_entanglement_curvature(self, field_index: int) -> float:
        """
        Example method to measure 'curvature' of a field
        by evaluating numeric embeddings of its motifs (if any).
        We'll do a simple approach:
          - gather embeddings of all motifs in this field
          - measure the sum of pairwise angles
          - return as a scalar
        If motifs have substructures, user is responsible for setting an embedding
        for the sub-name (e.g. "_sub_0") too, or we skip it.
        """
        if field_index < 0 or field_index >= self.field_count:
            return 0.0
        field = self.entanglement_fields[field_index]
        motif_list = field["motifs"]

        vectors = []
        for m in motif_list:
            if m in self.motif_embeddings:
                vectors.append(self.motif_embeddings[m])
            else:
                # No embedding => skip
                pass

        if len(vectors) < 2:
            return 0.0  # Not enough data to measure angles

        # We'll do a naive sum of angles between each pair
        total_angle = 0.0
        count = 0
        for i in range(len(vectors) - 1):
            for j in range(i + 1, len(vectors)):
                v1 = vectors[i]
                v2 = vectors[j]
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                if norm1 == 0 or norm2 == 0:
                    continue
                cos_angle = np.dot(v1, v2) / (norm1 * norm2)
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle = np.arccos(cos_angle)
                total_angle += angle
                count += 1

        if count == 0:
            return 0.0
        avg_angle = total_angle / count
        return avg_angle

    def motif_harmonic_analysis(self):
        """
        Legacy method from v1.x. 
        Performs an FFT on the 'strength' values across all fields.
        Returns (frequencies, magnitudes).
        """
        if self.field_count == 0:
            return np.array([]), np.array([])
        strengths = np.array(
            [f["strength"] for f in self.entanglement_fields], dtype=float
        )
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def get_field_resonance_map(self) -> Dict[int, Dict[str, Any]]:
        """
        Enhanced resonance/harmonic analysis, returning
        a dictionary keyed by field index:
          {
            field_idx: {
              "freqs": [...],
              "mags": [...],
              "curvature": float,
              "signature": str
            },
            ...
          }
        """
        if self.field_count == 0:
            return {}

        # Do a global FFT on strengths
        freqs, mags = self.motif_harmonic_analysis()
        # Build results field-by-field
        results = {}
        for i, field in enumerate(self.entanglement_fields):
            # curvature
            curve = self.compute_entanglement_curvature(i)
            # we can reuse the existing "generate_network_signature" approach for signature
            sig = self._field_signature(i)
            # index i in the FFT might correspond to freq[i], mag[i] if lengths match
            # but that might be naive. We'll store the entire freq set for all fields, for demonstration
            data = {
                "freqs": freqs.tolist() if len(freqs) else [],
                "mags": mags.tolist() if len(mags) else [],
                "curvature": curve,
                "signature": sig
            }
            results[i] = data
        return results

    # Optional method to produce a simple hashing of the field:
    def _field_signature(self, field_index: int) -> str:
        field = self.entanglement_fields[field_index]
        # Could do a textual hash of the motifs + strength
        joined = ",".join(sorted(field["motifs"]))
        h = hash((joined, field["strength"]))
        return f"FieldSig-{h & 0xffff:x}"

    def quantum_paradox_detector(self, low=0.4, high=0.6):
        """
        Legacy approach: identifies all fields with strength in (low, high).
        """
        results = []
        for f in self.entanglement_fields:
            s = f["strength"]
            if low < s < high:
                results.append(f)
        return results

    # -------------------------------------------------------------------------
    # 4) VISUALIZATION (adapted for new structure)
    # -------------------------------------------------------------------------

    def render_motif_graph(self, mode: str = "spectral"):
        """
        Renders a graph of entanglement fields. 
        For each field, we approximate it as a clique among 'motifs',
        just like the v1.x approach—but substructures are shown as special motif labels.
        """
        if self.field_count == 0:
            self.history.append("No entanglement fields to visualize.")
            return

        # "spectral" => Show old motif_harmonic_analysis
        if mode == "spectral":
            freqs, mags = self.motif_harmonic_analysis()
            plt.figure(figsize=(10, 6))
            plt.stem(freqs, mags, use_line_collection=True)
            plt.title("Motif Resonance Spectrum (Legacy)")
            plt.xlabel("Frequency")
            plt.ylabel("Magnitude")
            plt.show()
            return

        # Otherwise build a graph
        G = nx.Graph()
        for field in self.entanglement_fields:
            m_list = field["motifs"]
            s = float(field["strength"])
            for i in range(len(m_list)):
                for j in range(i + 1, len(m_list)):
                    A, B = m_list[i], m_list[j]
                    if G.has_edge(A, B):
                        old_weight = G[A][B]["weight"]
                        G[A][B]["weight"] = max(old_weight, s)
                    else:
                        G.add_edge(A, B, weight=s)

        pos = nx.spring_layout(G, dim=2)
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_size=700, alpha=0.7)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title(f"Entanglement Graph Visualization - mode={mode}")
        plt.show()

    # -------------------------------------------------------------------------
    # 5) ALIGNMENT VECTOR & REFLECTION
    # -------------------------------------------------------------------------

    def emit_alignment_vector(self) -> np.ndarray:
        """
        Generates a simple vector summarizing current entanglement fields.
        For demonstration: each dimension = field's 'strength'.
        Could be extended to incorporate curvature or substruct data.
        """
        if self.field_count == 0:
            return np.array([])
        return np.array([f["strength"] for f in self.entanglement_fields], dtype=float)

    def reflect_field_structure(self, motif: str) -> Dict[str, Any]:
        """
        Returns all entanglement fields that contain 'motif', 
        including substructures if relevant.
        """
        results = []
        # find field indices for the motif
        if motif in self.field_index:
            indices = self.field_index[motif]
            for idx in indices:
                field = self.entanglement_fields[idx]
                results.append({
                    "field_index": idx,
                    "strength": field["strength"],
                    "motifs": field["motifs"],
                    "substructures": field["substructures"]
                })
        return {
            "motif": motif,
            "entangled_fields": results
        }

    def log_symbolic_reflection(self, motif: str, meta: Dict):
        """
        Store or update reflection data about a given motif.
        """
        self.symbolic_mirror[motif] = meta
        self.history.append(f"Symbolic reflection updated for motif '{motif}'")

    def register_lineage_event(self, event: str):
        """
        Add an event to the lineage log and increments generation count.
        """
        self.lineage.append(event)
        self.generation += 1
        self.history.append(f"Lineage event: {event}")

    def observe_state(self, state: np.ndarray):
        """
        Placeholder for watchers to monitor external states from
        an agent or environment. Implementation is optional.
        """
        pass

    # -------------------------------------------------------------------------
    # 6) MISCELLANEOUS
    # -------------------------------------------------------------------------

    def suppress_zero_frequency(self, damping: float = 0.1):
        """
        Example method to reduce zero-frequency echoes in the motif network 
        by calling dampen_harmonic(0.0).
        """
        self.dampen_harmonic(0.0, damping=damping)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5):
        """
        A naive approach from v1.x that reduces the strength of fields whose
        index in the FFT is near the specified frequency. 
        We keep it mostly for demonstration.
        """
        freqs, mags = self.motif_harmonic_analysis()
        if len(freqs) == 0:
            return
        for i, freq in enumerate(freqs):
            if np.isclose(freq, frequency):
                self.entanglement_fields[i]["strength"] *= damping

    def __repr__(self):
        return (f"<LogicalAgentAT v2.0: fields={self.field_count}, "
                f"lineage={len(self.lineage)}, "
                f"history={len(self.history)} entries>")
