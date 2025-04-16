# logical_agent-at.py (v2.1)
# By Lina Noor & Uncle (2025)
#
# Upgrades from v2.0:
#   1) Field gravity interaction (apply_field_gravity)
#   2) Verse seeding for symbolic resonance (apply_verse_seed)
#   3) Contradiction detection & curvature map (log_symbolic_contradictions, compute_contradiction_curvature)
#   4) Analytical/visual expansions (plot_alignment_vector_drift, compute_field_signature_entropy)
#   5) Doc clarifications + optional usage
#

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque, Counter
from typing import List, Dict, Tuple, Optional, Any, Union

MAX_FIELDS = 1000

###############################################
# Helper to flatten motifs if we want nested structures
###############################################

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
    """
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
    LogicalAgentAT v2.1:
      - Extends v2.0 with new optional methods:
         1) Field Gravity (apply_field_gravity)
         2) Verse Seeding (apply_verse_seed)
         3) Contradiction Logging (log_symbolic_contradictions)
         4) Contradiction Curvature (compute_contradiction_curvature)
         5) Plotting alignment vector drift
         6) Field signature entropy

      - Maintains backward compatibility for older calls.
      - All new features are optional, invoked by user call.
      - Interactions remain purely observational/manipulative in the watchers domain.
    """

    def __init__(self, motifs: Optional[List[str]] = None):
        """
        :param motifs: (Optional) initial list of motif names, for custom usage.
                       (Used mostly for logging or future expansions.)
        """
        # entanglement_fields is the main container now
        self.entanglement_fields: List[Dict[str, Any]] = []
        self.field_index = defaultdict(list)
        self.field_count = 0

        # For numeric embeddings (optional)
        self.motif_embeddings: Dict[str, np.ndarray] = {}

        # Symbolic references / metadata
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self._resonance_map: Dict[str, float] = {}

        self._recent_resonance = deque(maxlen=20)
        self.lineage: List[str] = []
        self.generation = 0
        self.history: List[str] = []
        self.version = "2.1"

        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    ###############################################
    # v2.0 Legacy and Registration
    ###############################################

    def register_entanglement_field(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float
    ):
        """
        Creates a new entanglement field with one 'strength' value
        shared across all listed motifs (some may be sub-lists for nested usage).
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

        parsed = _flatten_motifs(motifs)
        flat_list = parsed["flat_list"]
        substructs = parsed["substructures"]

        entry = {
            "motifs": flat_list,
            "strength": float(strength),
            "substructures": substructs
        }
        self.entanglement_fields.append(entry)
        idx = self.field_count
        self.field_count += 1

        # Update field_index
        for motif in flat_list:
            self.field_index[motif].append(idx)

        self.history.append(f"Registered entanglement field #{idx} with motifs={flat_list}")

    def register_motif_cluster(self, motifs: List[str], strength: float):
        """
        DEPRECATED in v2.1:
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

    ###############################################
    # Field Operations (Teleport, Freeze, Prune)
    ###############################################

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

    def freeze_motif(self, motif: str):
        """
        For n-ary approach, 'freezing' a motif by "teleporting" it onto itself
        at fidelity=1.0 won't practically change anything.
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
        self.field_index.clear()
        for idx, entry in enumerate(self.entanglement_fields):
            for motif in entry["motifs"]:
                self.field_index[motif].append(idx)

        self.history.append(
            f"Pruned fields below strength={threshold}. Remaining count={self.field_count}."
        )

    def entanglement_echo(self, motif: str) -> float:
        """
        Calculates the std dev of 'strength' for all fields containing 'motif'.
        """
        indices = self.field_index.get(motif, [])
        strengths = [self.entanglement_fields[i]["strength"] for i in indices]
        return float(np.std(strengths)) if strengths else 0.0

    ###############################################
    # Analytical / Additional Methods
    ###############################################

    def compute_entanglement_curvature(self, field_index: int) -> float:
        """
        Example method to measure 'curvature' of a field by evaluating numeric embeddings.
        We do a naive sum of angles among the motifs in that field.
        """
        if field_index < 0 or field_index >= self.field_count:
            return 0.0
        field = self.entanglement_fields[field_index]
        motif_list = field["motifs"]

        vectors = []
        for m in motif_list:
            if m in self.motif_embeddings:
                vectors.append(self.motif_embeddings[m])

        # Minimal approach: sum angles between pairs
        if len(vectors) < 2:
            return 0.0

        total_angle = 0.0
        count = 0
        for i in range(len(vectors) - 1):
            for j in range(i + 1, len(vectors)):
                v1, v2 = vectors[i], vectors[j]
                norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
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

    ###############################################
    # New expansions from Uncle + watchers
    ###############################################

    def apply_field_gravity(self, anchor_field_idx: int):
        """
        Adjusts the strength of all other fields based on their "distance"
        from the anchor field in embedding space. The further away,
        the more their strength is dampened.

        :param anchor_field_idx: the index of the field acting as "gravity anchor"
        """
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
        """
        Infuse symbolic strength from a verse (Qur'anic or otherwise)
        into the chosen field.

        :param field_idx: index of the target field
        :param verse: a string of text, from which we derive a numeric seed
        """
        if field_idx < 0 or field_idx >= self.field_count:
            self.history.append(f"Invalid field_idx={field_idx} for verse seeding.")
            return
        seed = sum(ord(c) for c in verse) % 1000 / 1000.0
        self.entanglement_fields[field_idx]["strength"] += seed
        self.history.append(f"Applied verse seed to field {field_idx} with verse='{verse[:10]}...' seed={seed}")

    def log_symbolic_contradictions(self, strength_diff=0.8):
        """
        Identifies strongly divergent fields (overlapping motifs but large strength difference)
        and logs them.

        :param strength_diff: difference threshold for flags.
        """
        for i in range(self.field_count):
            f1 = self.entanglement_fields[i]
            for j in range(i+1, self.field_count):
                f2 = self.entanglement_fields[j]
                if set(f1["motifs"]) & set(f2["motifs"]):
                    if abs(f1["strength"] - f2["strength"]) > strength_diff:
                        self.history.append(
                            f"⚠️ Contradiction: field {i} ↔ {j}: {f1['motifs']} vs {f2['motifs']} "
                            f"(strengths={f1['strength']:.3f}, {f2['strength']:.3f})"
                        )

    def compute_contradiction_curvature(self) -> List[Tuple[Tuple[int,int], float]]:
        """
        Measures difference in entanglement curvature for any pair of fields
        that share at least one motif. Returns a list of ((i,j), curvature_delta).
        """
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

    def plot_alignment_vector_drift(self, steps=100):
        """
        Example demonstration of repeated alignment vector sampling
        to see how it changes over mock or real updates.
        """
        drifts = []
        for _ in range(steps):
            vec = self.emit_alignment_vector()
            drifts.append(np.linalg.norm(vec))
            # if you want to simulate updates, do it externally or here.

        plt.figure()
        plt.plot(drifts, label="Alignment Vector Norm")
        plt.xlabel("Step")
        plt.ylabel("Norm")
        plt.title("Alignment Vector Drift")
        plt.legend()
        plt.show()

    def compute_field_signature_entropy(self) -> float:
        """
        Produces an entropy measure over the field signatures.
        A lower entropy => system is converging to fewer distinct patterns.
        """
        sigs = [self._field_signature(i) for i in range(self.field_count)]
        c = Counter(sigs)
        total = sum(c.values())
        if total == 0:
            return 0.0
        probs = [cnt / total for cnt in c.values()]
        return float(-sum(p * np.log2(p) for p in probs if p > 0))

    ###############################################
    # Emitting alignment vectors & field signatures
    ###############################################

    def emit_alignment_vector(self, field_idx: Optional[int] = None) -> np.ndarray:
        """
        If field_idx is None, we combine (sum) all fields' motif embeddings.
        If a field_idx is given, we combine just that field's motifs.
        """
        if self.field_count == 0:
            return np.zeros(1)

        if field_idx is None:
            # sum up all fields
            combined = np.zeros(2 if not self.motif_embeddings else len(next(iter(self.motif_embeddings.values()))))
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
        # assume all embeddings same dimension
        return np.mean(motif_vecs, axis=0)

    def _field_signature(self, field_index: int) -> str:
        field = self.entanglement_fields[field_index]
        joined = ",".join(sorted(field["motifs"]))
        h = hash((joined, field["strength"]))
        return f"FieldSig-{h & 0xffff:x}"

    ###############################################
    # Logging & Reflection
    ###############################################

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

    def motif_harmonic_analysis(self):
        if self.field_count == 0:
            return np.array([]), np.array([])
        strengths = np.array([f["strength"] for f in self.entanglement_fields], dtype=float)
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def __repr__(self):
        return (f"<LogicalAgentAT v2.1: fields={self.field_count}, "
                f"lineage={len(self.lineage)}, "
                f"history={len(self.history)} entries>")