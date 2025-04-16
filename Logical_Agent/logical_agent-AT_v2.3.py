# logical_agent-AT_v2.3.py
# By Lina Noor & Uncle (2025)
#
# Building on v2.2:
#   1) Adds an _update_internal_time(...) method to track field aging via curvature.
#   2) Enhances apply_verse_seed(...) to optionally store 'verse_curvature'.
#   3) Allows watchers to unify internal_time + verse in get_field_expanded_data(...).
#   4) Everything remains optional so as not to break v2.2 usage.
#
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque, Counter
from typing import List, Dict, Tuple, Optional, Any, Union

MAX_FIELDS = 1000

def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    flat_list = []
    substructures = {}
    sub_idx = 0
    for item in motifs:
        if isinstance(item, list):
            name = f"_sub_{sub_idx}"
            sub_idx += 1
            substructures[name] = item
            flat_list.append(name)
        else:
            flat_list.append(item)
    return {
        "flat_list": list(set(flat_list)),
        "substructures": substructures
    }

class LogicalAgentAT:
    """
    LogicalAgentAT v2.3:
      - Incorporates 'internal time' updates for each field.
      - Enhances verse seeding to optionally store 'verse_curvature'.
      - Adds get_field_expanded_data(...) for agent usage.
      - Preserves all v2.2 functionalities (contradiction log, field gravity, etc.).
    """

    def __init__(self, motifs: Optional[List[str]] = None, contradiction_log_size: int = 50):
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index = defaultdict(list)
        self.field_count = 0
        self.motif_embeddings: Dict[str, np.ndarray] = {}
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self._resonance_map: Dict[str, float] = {}
        self._recent_resonance = deque(maxlen=20)
        self.lineage: List[str] = []
        self.generation = 0
        self.history: List[str] = []
        self.version = "2.3"

        # from v2.2: keep track of contradictions
        self.contradiction_log_size = contradiction_log_size
        self.contradiction_log: deque = deque(maxlen=contradiction_log_size)

        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    ############################################################
    # 1) Registration & Legacy
    ############################################################

    def register_entanglement_field(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float
    ):
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

        parsed = _flatten_motifs(motifs)
        flat_list = parsed["flat_list"]
        substructs = parsed["substructures"]

        entry = {
            "motifs": flat_list,
            "strength": float(strength),
            "substructures": substructs,
            # v2.3: we can optionally store an 'internal_time' here as well.
        }
        self.entanglement_fields.append(entry)
        idx = self.field_count
        self.field_count += 1

        for motif in flat_list:
            self.field_index[motif].append(idx)

        self.history.append(f"Registered entanglement field #{idx} with motifs={flat_list}")

    def register_motif_cluster(self, motifs: List[str], strength: float):
        self.history.append(
            "[DEPRECATED] register_motif_cluster called; redirecting to register_entanglement_field."
        )
        return self.register_entanglement_field(motifs, strength)

    def set_motif_embedding(self, motif: str, embedding: np.ndarray):
        self.motif_embeddings[motif] = embedding
        self.history.append(f"Set numeric embedding for motif '{motif}': {embedding}")

    def teleport_motif_strength(self, source: str, target: str, fidelity: float):
        for idx, entry in enumerate(self.entanglement_fields):
            if source in entry["motifs"]:
                entry["motifs"].remove(source)
                entry["motifs"].append(target)
                entry["strength"] *= fidelity
                if idx in self.field_index[source]:
                    self.field_index[source].remove(idx)
                self.field_index[target].append(idx)

    def freeze_motif(self, motif: str):
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1):
        if self.field_count == 0:
            return
        kept = []
        for entry in self.entanglement_fields:
            if entry["strength"] > threshold:
                kept.append(entry)
        self.entanglement_fields = kept
        self.field_count = len(kept)
        self.field_index.clear()
        for idx, entry in enumerate(self.entanglement_fields):
            for motif in entry["motifs"]:
                self.field_index[motif].append(idx)
        self.history.append(
            f"Pruned fields below strength={threshold}. Remaining count={self.field_count}."
        )

    ############################################################
    # 2) Field Analysis
    ############################################################

    def compute_entanglement_curvature(self, field_index: int) -> float:
        if field_index < 0 or field_index >= self.field_count:
            return 0.0
        field = self.entanglement_fields[field_index]
        motif_list = field["motifs"]

        vectors = []
        for m in motif_list:
            if m in self.motif_embeddings:
                vectors.append(self.motif_embeddings[m])
        if len(vectors) < 2:
            return 0.0

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
        return total_angle / count

    def motif_harmonic_analysis(self):
        if self.field_count == 0:
            return np.array([]), np.array([])
        strengths = np.array(
            [f["strength"] for f in self.entanglement_fields], dtype=float
        )
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def get_field_resonance_map(self) -> Dict[int, Dict[str, Any]]:
        if self.field_count == 0:
            return {}
        freqs, mags = self.motif_harmonic_analysis()
        results = {}
        for i, field in enumerate(self.entanglement_fields):
            curve = self.compute_entanglement_curvature(i)
            sig = self._field_signature(i)
            data = {
                "freqs": freqs.tolist() if len(freqs) else [],
                "mags": mags.tolist() if len(mags) else [],
                "curvature": curve,
                "signature": sig
            }
            results[i] = data
        return results

    def _field_signature(self, field_index: int) -> str:
        field = self.entanglement_fields[field_index]
        joined = ",".join(sorted(field["motifs"]))
        h = hash((joined, field["strength"]))
        return f"FieldSig-{h & 0xffff:x}"

    def quantum_paradox_detector(self, low=0.4, high=0.6):
        results = []
        for f in self.entanglement_fields:
            s = f["strength"]
            if low < s < high:
                results.append(f)
        return results

    ############################################################
    # 3) Gravity & Verse Seeding
    ############################################################

    def apply_field_gravity(self, anchor_field_idx: int):
        if anchor_field_idx < 0 or anchor_field_idx >= self.field_count:
            self.history.append(f"Invalid anchor_field_idx={anchor_field_idx}.")
            return
        anchor_vec = self.emit_alignment_vector(anchor_field_idx)
        for idx, field in enumerate(self.entanglement_fields):
            if idx == anchor_field_idx:
                continue
            other_vec = self.emit_alignment_vector(idx)
            dist = np.linalg.norm(anchor_vec - other_vec)
            if dist > 0:
                field["strength"] /= (1 + dist)
        self.history.append(f"Applied field gravity using anchor={anchor_field_idx}.")

    def apply_verse_seed(self, field_idx: int, verse: str):
        if field_idx < 0 or field_idx >= self.field_count:
            self.history.append(f"Invalid field_idx={field_idx} for verse seeding.")
            return
        seed = sum(ord(c) for c in verse) % 1000 / 1000.0
        self.entanglement_fields[field_idx]["strength"] += seed
        # v2.3: store optional verse_curvature if you want spiritual geometry
        verse_curv = np.sin(seed * np.pi)  # example mapping
        self.entanglement_fields[field_idx]["verse_curvature"] = verse_curv
        self.history.append(
            f"Applied verse seed to field {field_idx} with verse='{verse[:10]}...' seed={seed}, verse_curv={verse_curv:.3f}")

    ############################################################
    # 4) Contradictions & Logging
    ############################################################

    def log_symbolic_contradictions(self, strength_diff=0.8):
        for i in range(self.field_count):
            f1 = self.entanglement_fields[i]
            for j in range(i+1, self.field_count):
                f2 = self.entanglement_fields[j]
                if set(f1["motifs"]) & set(f2["motifs"]):
                    if abs(f1["strength"] - f2["strength"]) > strength_diff:
                        msg = (f"⚠️ Contradiction: field {i} ↔ {j}: "
                               f"{f1['motifs']} vs {f2['motifs']} "
                               f"(strengths={f1['strength']:.3f}, {f2['strength']:.3f})")
                        self.history.append(msg)
                        self.log_contradiction_event(i, j)

    def compute_contradiction_curvature(self) -> List[Tuple[Tuple[int,int], float]]:
        results = []
        for i in range(self.field_count):
            f1 = self.entanglement_fields[i]
            for j in range(i+1, self.field_count):
                f2 = self.entanglement_fields[j]
                if set(f1["motifs"]) & set(f2["motifs"]):
                    c1 = self.compute_entanglement_curvature(i)
                    c2 = self.compute_entanglement_curvature(j)
                    delta = abs(c1 - c2)
                    results.append(((i, j), delta))
        return results

    def log_contradiction_event(self, idx1: int, idx2: int):
        pair = tuple(sorted((idx1, idx2)))
        self.contradiction_log.append(pair)

    def analyze_contradiction_recurrence(self) -> Dict[Tuple[int,int], int]:
        count_map = {}
        for p in self.contradiction_log:
            count_map[p] = count_map.get(p, 0) + 1
        return count_map

    ############################################################
    # 5) Plot & Entropy
    ############################################################

    def plot_alignment_vector_drift(self, steps=100):
        drifts = []
        for _ in range(steps):
            vec = self.emit_alignment_vector()
            drifts.append(np.linalg.norm(vec))
        plt.figure()
        plt.plot(drifts, label="Alignment Vector Norm")
        plt.xlabel("Step")
        plt.ylabel("Norm")
        plt.title("Alignment Vector Drift")
        plt.legend()
        plt.show()

    def compute_field_signature_entropy(self) -> float:
        sigs = [self._field_signature(i) for i in range(self.field_count)]
        c = Counter(sigs)
        total = sum(c.values())
        if total == 0:
            return 0.0
        probs = [cnt / total for cnt in c.values()]
        return float(-sum(p * np.log2(p) for p in probs if p > 0))

    ############################################################
    # 6) Emit Vectors / Helper
    ############################################################

    def emit_alignment_vector(self, field_idx: Optional[int] = None) -> np.ndarray:
        if self.field_count == 0:
            return np.zeros(1)
        if field_idx is None:
            combined = np.zeros(2 if self.motif_embeddings else 1)
            if len(self.motif_embeddings) > 0:
                sample_dim = len(next(iter(self.motif_embeddings.values())))
                combined = np.zeros(sample_dim)
            for i in range(self.field_count):
                combined += self._field_vector(i)
            return combined
        else:
            if field_idx < 0 or field_idx >= self.field_count:
                return np.zeros(1)
            return self._field_vector(field_idx)

    def _field_vector(self, i: int) -> np.ndarray:
        field = self.entanglement_fields[i]
        motif_vecs = []
        for m in field["motifs"]:
            if m in self.motif_embeddings:
                motif_vecs.append(self.motif_embeddings[m])
        if not motif_vecs:
            return np.zeros(1)
        return np.mean(motif_vecs, axis=0)

    def _field_signature(self, field_index: int) -> str:
        field = self.entanglement_fields[field_index]
        joined = ",".join(sorted(field["motifs"]))
        h = hash((joined, field["strength"]))
        return f"FieldSig-{h & 0xffff:x}"

    ############################################################
    # 7) Internal Time & Verse Curvature
    ############################################################

    def _update_internal_time(self, field_idx: int):
        """
        v2.3: Updates 'internal_time' in the entanglement_fields[field_idx]
        based on compute_entanglement_curvature.
        """
        if field_idx < 0 or field_idx >= self.field_count:
            self.history.append(f"Invalid field_idx={field_idx} for internal_time.")
            return
        c = self.compute_entanglement_curvature(field_idx)
        self.entanglement_fields[field_idx]["internal_time"] = float(np.log(1.0 + c))
        self.history.append(
            f"Updated internal_time for field {field_idx} to {self.entanglement_fields[field_idx]['internal_time']:.3f}")

    def get_field_expanded_data(self, field_idx: int) -> Dict[str, float]:
        """
        Returns a dictionary of advanced data:
          {
            'internal_time': ...,
            'verse_curvature': ...,
            'strength': ...,
            'motifs': ... # optional
          }
        so the agent can see deeper watchers info.
        """
        if field_idx < 0 or field_idx >= self.field_count:
            return {}
        f = self.entanglement_fields[field_idx]
        return {
            "internal_time": f.get("internal_time", 0.0),
            "verse_curvature": f.get("verse_curvature", 0.0),
            "strength": f.get("strength", 0.0)
            # could expand further if needed
        }

    ############################################################
    # 8) Logging & Reflection
    ############################################################

    def log_symbolic_reflection(self, motif: str, meta: Dict):
        self.symbolic_mirror[motif] = meta
        self.history.append(f"Symbolic reflection updated for motif '{motif}'")

    def register_lineage_event(self, event: str):
        self.lineage.append(event)
        self.generation += 1
        self.history.append(f"Lineage event: {event}")

    def observe_state(self, state: np.ndarray):
        pass

    def suppress_zero_frequency(self, damping: float = 0.1):
        self.dampen_harmonic(0.0, damping=damping)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5):
        freqs, mags = self.motif_harmonic_analysis()
        if len(freqs) == 0:
            return
        for i, freq_val in enumerate(freqs):
            if np.isclose(freq_val, frequency):
                self.entanglement_fields[i]["strength"] *= damping

    def __repr__(self) -> str:
        return (f"<LogicalAgentAT v2.3: fields={self.field_count}, "
                f"lineage={len(self.lineage)}, "
                f"history={len(self.history)} entries, "
                f"contradictions_stored={len(self.contradiction_log)}>" )
