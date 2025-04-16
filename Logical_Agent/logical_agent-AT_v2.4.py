# logical_agent.py (v2.4)
# By Lina Noor & Uncle (2025)
#
# Building upon v2.3, this version adds:
#   1) __version__ = "2.4.0"
#   2) concurrency readiness (threading.Lock)
#   3) input validation (strength in 0..1, duplicates check)
#   4) improved docstrings with Args/Returns
#   5) to_dict() / from_dict() for serialization
#

__version__ = "2.4.0"

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import threading
from collections import defaultdict, deque, Counter
from typing import List, Dict, Tuple, Optional, Any, Union

MAX_FIELDS = 1000


def _flatten_motifs(motifs: List[Union[str, List[str]]]) -> Dict[str, Any]:
    """
    Converts nested motif lists into a flat list + substructures.

    Args:
        motifs: list of strings or sub-lists.

    Returns:
        {
          "flat_list": ["alpha", "beta", "_sub_0"...],
          "substructures": {"_sub_0": ["a1", "a2"]}
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
    LogicalAgentAT v2.4:

    - Stores 'entanglement_fields' describing motif-based fields
    - Tracks contradictions, verse seeds, internal_time, etc.
    - Now includes concurrency readiness via threading.Lock.
    - Adds input validation for register_motif_cluster.
    - Offers to_dict() / from_dict() for serialization.

    Typical usage:
        watcher = LogicalAgentAT()
        watcher.register_motif_cluster(["alpha", "beta"], 0.8)
        # etc.
    """

    def __init__(
        self,
        motifs: Optional[List[str]] = None,
        contradiction_log_size: int = 50
    ):
        """
        Args:
            motifs: optional initial motif list.
            contradiction_log_size: max length of contradiction log.
        """
        self.__version__ = __version__

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
        self.version = "2.4.0"

        # Contradiction log from v2.2
        self.contradiction_log_size = contradiction_log_size
        self.contradiction_log: deque = deque(maxlen=contradiction_log_size)

        # optional concurrency lock
        self._lock = threading.Lock()

        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    ############################################################
    # 1) Registration & Legacy
    ############################################################

    def register_motif_cluster(self, motifs: List[Union[str, List[str]]], strength: float) -> None:
        """
        Registers a new motif cluster (entanglement field) with a single float strength.

        Args:
            motifs: a list of motif names or sub-lists.
            strength: float in (0,1] specifying cluster strength.

        Raises:
            ValueError: if strength not in (0,1], or if motifs <2.
        """
        with self._lock:
            if not motifs or len(motifs) < 2:
                self.history.append(f"Rejected cluster with <2 motifs: {motifs}")
                return
            if not (0.0 < strength <= 1.0):
                raise ValueError(f"register_motif_cluster: strength must be in (0,1], got {strength}")

            parsed = _flatten_motifs(motifs)
            flat_list = parsed["flat_list"]
            substructs = parsed["substructures"]

            # check duplicates within the same call
            if len(flat_list) != len(set(flat_list)):
                self.history.append(f"Warning: duplicates in motif list: {flat_list}")

            if self.field_count >= MAX_FIELDS:
                self.history.append(
                    "Reached MAX_FIELDS; cannot register additional entanglement fields."
                )
                return

            entry = {
                "motifs": flat_list,
                "strength": float(strength),
                "substructures": substructs
            }
            self.entanglement_fields.append(entry)
            idx = self.field_count
            self.field_count += 1

            for m in flat_list:
                self.field_index[m].append(idx)

            self.history.append(
                f"Registered motif cluster #{idx} with motifs={flat_list}, strength={strength:.3f}"
            )

    def register_entanglement_field(
        self,
        motifs: List[Union[str, List[str]]],
        strength: float
    ) -> None:
        """
        DEPRECATED: calls register_motif_cluster for backward compat.

        Args:
            motifs: list of str or sub-lists.
            strength: float in (0,1].
        """
        self.history.append(
            "[DEPRECATED] register_entanglement_field => register_motif_cluster."
        )
        self.register_motif_cluster(motifs, strength)

    def set_motif_embedding(self, motif: str, embedding: np.ndarray) -> None:
        """
        Store a numeric embedding (vector) for a given motif.

        Args:
            motif: name of motif.
            embedding: a numpy array representing motif's embedding.
        """
        with self._lock:
            self.motif_embeddings[motif] = embedding
            self.history.append(f"Set numeric embedding for '{motif}' => {embedding}")

    def teleport_motif_strength(self, source: str, target: str, fidelity: float) -> None:
        """
        Transfer 'source' motif references to 'target', scaling field strength by fidelity.

        Args:
            source: existing motif name.
            target: motif name to unify with.
            fidelity: multiplier for field strength.
        """
        with self._lock:
            # if source not in field_index, skip.
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
                        f"Teleported '{source}' -> '{target}' in field #{idx}, "
                        f"strength {old_strength:.3f} => {entry['strength']:.3f}, fidelity={fidelity:.3f}"
                    )
                    # field_index housekeeping
                    self.field_index[source].remove(idx)
                    if target not in self.field_index:
                        self.field_index[target] = []
                    self.field_index[target].append(idx)

    def freeze_motif(self, motif: str) -> None:
        """
        Teleport motif onto itself with fidelity=1.0 => effectively no-op unless we want expansions.
        """
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1) -> None:
        """
        Removes all fields whose strength is <= threshold.

        Args:
            threshold: float in [0..1].
        """
        with self._lock:
            if self.field_count == 0:
                return

            kept = []
            for entry in self.entanglement_fields:
                if entry["strength"] > threshold:
                    kept.append(entry)

            removed_count = self.field_count - len(kept)
            self.entanglement_fields = kept
            self.field_count = len(kept)
            self.field_index.clear()
            for idx, e in enumerate(self.entanglement_fields):
                for m in e["motifs"]:
                    self.field_index[m].append(idx)

            self.history.append(
                f"Pruned entanglements <= {threshold:.3f}. Removed={removed_count}, Remaining={self.field_count}."
            )

    ############################################################
    # 2) Field Analysis
    ############################################################

    def compute_entanglement_curvature(self, field_index: int) -> float:
        """
        Measures 'curvature' by summing pairwise angles among embedded motifs.

        Args:
            field_index: index in self.entanglement_fields.

        Returns:
            average angle in [0..pi] or 0 if not enough data.
        """
        with self._lock:
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
            return float(total_angle / count)

    def motif_harmonic_analysis(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Performs FFT on the strength array across all fields.

        Returns:
            (frequencies, magnitudes) as two np.ndarrays.
        """
        with self._lock:
            if self.field_count == 0:
                return np.array([]), np.array([])
            strengths = np.array([f["strength"] for f in self.entanglement_fields], dtype=float)
            fft_result = np.fft.fft(strengths)
            frequencies = np.fft.fftfreq(len(strengths))
            return frequencies, np.abs(fft_result)

    def get_field_resonance_map(self) -> Dict[int, Dict[str, Any]]:
        """
        Builds a dict of field -> {
          freqs, mags, curvature, signature
        }
        """
        with self._lock:
            if self.field_count == 0:
                return {}
            freqs, mags = self.motif_harmonic_analysis()
            results = {}
            for i, field in enumerate(self.entanglement_fields):
                c = self.compute_entanglement_curvature(i)
                sig = self._field_signature(i)
                data = {
                    "freqs": freqs.tolist() if len(freqs) else [],
                    "mags": mags.tolist() if len(mags) else [],
                    "curvature": c,
                    "signature": sig
                }
                results[i] = data
            return results

    def _field_signature(self, field_index: int) -> str:
        field = self.entanglement_fields[field_index]
        joined = ",".join(sorted(field["motifs"]))
        h = hash((joined, field["strength"]))
        return f"FieldSig-{h & 0xffff:x}"

    def quantum_paradox_detector(self, low=0.4, high=0.6) -> List[Dict[str, Any]]:
        """
        Identifies fields with strength in (low, high), e.g. 0.4..0.6.

        Returns:
            list of fields in that range.
        """
        with self._lock:
            results = []
            for f in self.entanglement_fields:
                s = f["strength"]
                if low < s < high:
                    results.append(f)
            return results

    ############################################################
    # 3) Gravity & Verse Seeding
    ############################################################

    def apply_field_gravity(self, anchor_field_idx: int) -> None:
        """
        Dampen strength of all other fields by distance to anchor's alignment vector.

        Args:
            anchor_field_idx: index of field to anchor.
        """
        with self._lock:
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
                    old_str = field["strength"]
                    field["strength"] /= (1 + dist)
                    self.history.append(
                        f"apply_field_gravity: field {idx} strength {old_str:.3f} => "
                        f"{field['strength']:.3f} (dist={dist:.3f})"
                    )

    def apply_verse_seed(self, field_idx: int, verse: str) -> None:
        """
        Infuse field with symbolic strength from verse.

        Args:
            field_idx: field index
            verse: text snippet
        """
        with self._lock:
            if field_idx < 0 or field_idx >= self.field_count:
                self.history.append(f"Invalid field_idx={field_idx} for verse seeding.")
                return
            seed = sum(ord(c) for c in verse) % 1000 / 1000.0
            old_str = self.entanglement_fields[field_idx]["strength"]
            self.entanglement_fields[field_idx]["strength"] += seed
            self.history.append(
                f"apply_verse_seed: field {field_idx} strength {old_str:.3f} => "
                f"{self.entanglement_fields[field_idx]['strength']:.3f}, verse='{verse[:10]}...' "
                f"seed={seed:.3f}"
            )

    ############################################################
    # 4) Contradictions & Logging
    ############################################################

    def log_symbolic_contradictions(self, strength_diff=0.8) -> None:
        """
        Finds overlapping fields with large strength difference.

        Args:
            strength_diff: threshold for contradiction.
        """
        with self._lock:
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
        """
        For each pair of fields with overlapping motifs, measure difference in curvature.

        Returns:
            list of ((i,j), delta_curvature)
        """
        with self._lock:
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

    def log_contradiction_event(self, idx1: int, idx2: int) -> None:
        """
        Push a contradiction pair into self.contradiction_log.
        """
        pair = tuple(sorted((idx1, idx2)))
        self.contradiction_log.append(pair)

    def analyze_contradiction_recurrence(self) -> Dict[Tuple[int,int], int]:
        """
        Counts how many times each pair re-appears in the contradiction_log.

        Returns:
            dict of (field_pair -> count)
        """
        with self._lock:
            count_map = {}
            for p in self.contradiction_log:
                count_map[p] = count_map.get(p, 0) + 1
            return count_map

    ############################################################
    # 5) Plot & Entropy
    ############################################################

    def plot_alignment_vector_drift(self, steps=100) -> None:
        """
        Example demonstration of repeated alignment vector sampling.

        Args:
            steps: how many times to sample.
        """
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
        """
        Measures how many distinct field signatures exist => approximate system entropy.

        Returns:
            float entropy in bits.
        """
        with self._lock:
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
        """
        If field_idx is None => sum all fields.
        If provided => just that field.

        Returns:
            a numeric vector representing combined motif embeddings.
        """
        with self._lock:
            if self.field_count == 0:
                return np.zeros(1)
            if field_idx is None:
                # sum up all fields
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
        for m in field.get("motifs", []):
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

    def _update_internal_time(self, field_idx: int) -> None:
        """
        Recalculates 'internal_time' in entanglement_fields[field_idx] as log(1 + curvature).
        """
        with self._lock:
            if field_idx < 0 or field_idx >= self.field_count:
                self.history.append(f"Invalid field_idx={field_idx} for internal_time.")
                return
            c = self.compute_entanglement_curvature(field_idx)
            self.entanglement_fields[field_idx]["internal_time"] = float(np.log(1.0 + c))
            self.history.append(
                f"Updated internal_time for field {field_idx} => {self.entanglement_fields[field_idx]['internal_time']:.3f}"
            )

    def get_field_expanded_data(self, field_idx: int) -> Dict[str, float]:
        """
        Returns advanced data for a specific field, including:
          internal_time, verse_curvature, strength.

        Args:
            field_idx: index of the field.

        Returns:
            dict with 'internal_time', 'verse_curvature', 'strength' keys.
        """
        with self._lock:
            if field_idx < 0 or field_idx >= self.field_count:
                return {}
            f = self.entanglement_fields[field_idx]
            return {
                "internal_time": f.get("internal_time", 0.0),
                "verse_curvature": f.get("verse_curvature", 0.0),
                "strength": f.get("strength", 0.0)
            }

    ############################################################
    # 8) Logging & Reflection
    ############################################################

    def log_symbolic_reflection(self, motif: str, meta: Dict) -> None:
        """
        Records an arbitrary reflection about 'motif'.
        """
        with self._lock:
            self.symbolic_mirror[motif] = meta
            self.history.append(f"Symbolic reflection updated for '{motif}' => {meta}")

    def register_lineage_event(self, event: str) -> None:
        """
        Records a lineage event in self.lineage.
        """
        with self._lock:
            self.lineage.append(event)
            self.generation += 1
            self.history.append(f"Lineage event: {event}")

    def observe_state(self, state: np.ndarray) -> None:
        """
        Hook for watchers to observe external states.
        """
        pass

    def suppress_zero_frequency(self, damping: float = 0.1) -> None:
        """
        Dampen the amplitude at frequency=0 in the motif harmonic analysis.
        """
        self.dampen_harmonic(0.0, damping=damping)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5) -> None:
        """
        Reduces the strength of fields whose index in the FFT is near 'frequency'.
        """
        with self._lock:
            freqs, mags = self.motif_harmonic_analysis()
            if len(freqs) == 0:
                return
            for i, freq_val in enumerate(freqs):
                if np.isclose(freq_val, frequency):
                    old_str = self.entanglement_fields[i]["strength"]
                    self.entanglement_fields[i]["strength"] *= damping
                    self.history.append(
                        f"dampen_harmonic: field {i} freq={freq_val:.3f} strength {old_str:.3f} => "
                        f"{self.entanglement_fields[i]['strength']:.3f}"
                    )

    ############################################################
    # (v2.4) to_dict / from_dict
    ############################################################

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the watcher's data for saving.

        Returns:
            dict containing version, fields, embeddings, logs.
        """
        with self._lock:
            motif_embeds_serial = {k: v.tolist() for k, v in self.motif_embeddings.items()}
            return {
                "version": self.__version__,
                "entanglement_fields": list(self.entanglement_fields),
                "field_count": self.field_count,
                "motif_embeddings": motif_embeds_serial,
                "contradiction_log": list(self.contradiction_log),
                "history": list(self.history),
                "lineage": list(self.lineage),
                "generation": self.generation,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogicalAgentAT":
        """
        Reconstructs a LogicalAgentAT from a dictionary.

        Args:
            data: dictionary created by to_dict()

        Returns:
            LogicalAgentAT instance.
        """
        obj = cls()
        obj.__version__ = data.get("version", "2.4.0")
        obj.entanglement_fields = data.get("entanglement_fields", [])
        obj.field_count = data.get("field_count", 0)
        # re-convert motif_embeddings
        raw_embeds = data.get("motif_embeddings", {})
        embed_dict = {}
        for k, arr_list in raw_embeds.items():
            embed_dict[k] = np.array(arr_list)
        obj.motif_embeddings = embed_dict

        # contradiction_log, history, lineage
        obj.contradiction_log = deque(data.get("contradiction_log", []), maxlen=obj.contradiction_log_size)
        obj.history = data.get("history", [])
        obj.lineage = data.get("lineage", [])
        obj.generation = data.get("generation", 0)

        return obj

    def __repr__(self) -> str:
        return (
            f"<LogicalAgentAT v2.4: fields={self.field_count}, "
            f"lineage={len(self.lineage)}, "
            f"history={len(self.history)} entries, "
            f"contradictions_stored={len(self.contradiction_log)}" + 
            f", version={self.__version__}>"
        )