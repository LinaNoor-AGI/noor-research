# logical_agent-AT_v1.3.py — Watcher Layer for Multi-Motif (n-ary) Entanglement
# By Lina Noor & Uncle (2025)
#
# This module defines a "LogicalAgentAT" that observes symbolic motifs and entanglement
# relationships without dictating how the system evolves. It has been upgraded to
# support n-ary entanglement clusters, not just binary (pairwise) links.
# 
# Core responsibilities:
#   - Collect {"motifs": [...], "strength": float} clusters
#   - Provide teleports, pruning, echo calculations, paradox detection
#   - Perform optional analyses: FFT-based resonance, topological tagging, graph rendering
#   - Maintain watchers' lineage logs and symbolic reflections
#
# NOTE: For rendering the graph with n-ary clusters, this module approximates each
#       cluster as a clique in networkx. That means if a cluster has motifs [A, B, C],
#       it adds edges (A–B, B–C, A–C) all with the same 'strength.'


import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Any

MAX_MOTIFS = 1000


class LogicalAgentAT:
    """
    LogicalAgentAT v1.3:
      - Stores 'entangled_motifs' as a List of dict entries:
          {
            "motifs": [motif1, motif2, ..., motifN],
            "strength": float
          }
      - 'motif_index' maps each motif name -> list of entangled_motifs indices
      - Methods handle n-ary cluster logic and optional legacy 2-motif registration.

    Primary enhancements over earlier versions:
      1) register_motif_cluster(self, motifs, strength): create n-ary entanglement
      2) optionally preserve register_motif_entanglement(motifA, motifB, strength) 
         as a convenience wrapper for pairwise
      3) internal references to self.entangled_motifs are updated 
         to reflect the new structure.
      4) graph rendering uses a "clique expansion" approach for each n-ary cluster.
    """

    def __init__(self, motifs: Optional[List[str]] = None):
        """
        :param motifs: (Optional) initial list of motif names, for custom usage.
                       (Used mostly for logging or future expansions.)
        """
        # Using a list of dicts to represent entanglements:
        #   self.entangled_motifs[i] = {"motifs": [...], "strength": float}
        self.entangled_motifs: List[Dict[str, Any]] = []
        self.motif_index = defaultdict(list)
        self.motif_count = 0  # how many entanglements so far

        # Symbolic references / metadata
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self._prm_registry: Dict[str, List[str]] = {}
        self._resonance_map: Dict[str, float] = {}
        self._recent_resonance = deque(maxlen=20)

        # Basic lineage tracking
        self.lineage: List[str] = []
        self.generation = 0

        # Usage logs or custom reflection info
        self.history: List[str] = []
        if motifs:
            self.history.append(f"Watcher initialized with motif list: {motifs}")

    # -------------------------------------------------------------------------
    # 1) MOTIF ENTANGLEMENT OPERATIONS (now n-ary)
    # -------------------------------------------------------------------------

    def register_motif_cluster(self, motifs: List[str], strength: float):
        """
        Creates a new entanglement cluster with one 'strength' value
        shared across all listed motifs.

        :param motifs: list of motif names to entangle together
        :param strength: a single float for the entire cluster
        """
        if not motifs or len(motifs) < 2:
            self.history.append(f"Rejected cluster with <2 motifs: {motifs}")
            return
        if self.motif_count >= MAX_MOTIFS:
            self.history.append("Reached MAX_MOTIFS; cannot register additional entanglements.")
            return

        # ensure uniqueness if user duplicates motifs
        unique_motifs = list(set(motifs))

        entry = {"motifs": unique_motifs, "strength": float(strength)}
        self.entangled_motifs.append(entry)
        idx = self.motif_count
        self.motif_count += 1

        # Update motif_index
        for motif in unique_motifs:
            self.motif_index[motif].append(idx)

    def register_motif_entanglement(self, motif_a: str, motif_b: str, strength: float):
        """
        Legacy convenience for pairwise registration. Internally calls register_motif_cluster.
        """
        self.register_motif_cluster([motif_a, motif_b], strength)

    def teleport_motif_strength(self, source: str, target: str, fidelity: float):
        """
        Transfer 'source' motif references to 'target' within all clusters,
        multiplying each cluster's strength by fidelity whenever changed.

        Example usage:
          - If source is in a cluster with [A, source, B], then we remove 'source'
            and add 'target', adjusting 'strength *= fidelity'.

        WARNING: This is a simplistic approach to "teleportation" in n-ary sets.
                 Real quantum logic might handle partial distribution differently.
        """
        for idx, entry in enumerate(self.entangled_motifs):
            motifs = entry["motifs"]
            if source in motifs:
                # remove 'source' and add 'target'
                motifs.remove(source)
                motifs.append(target)
                # scale the strength
                entry["strength"] *= fidelity

    def freeze_motif(self, motif: str):
        """
        For n-ary approach, 'freezing' a motif by "teleporting" it onto itself
        at fidelity=1.0 won't practically change anything.
        We keep it for legacy reasons:
          - If you want to interpret "freeze" as removing all other motifs in that cluster,
            you'll need specialized logic. Currently we do the old approach of:
              teleport_motif_strength(motif, motif, 1.0) -> no change.
        """
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1):
        """
        Remove all entanglement clusters whose strength is below the threshold.
        Then rebuild the motif_index accordingly.
        """
        if self.motif_count == 0:
            return

        kept = []
        for entry in self.entangled_motifs:
            if entry["strength"] > threshold:
                kept.append(entry)

        # Rebuild
        self.entangled_motifs = kept
        self.motif_count = len(kept)

        # Rebuild motif_index
        self.motif_index.clear()
        for idx, entry in enumerate(self.entangled_motifs):
            for motif in entry["motifs"]:
                self.motif_index[motif].append(idx)

    def entanglement_echo(self, motif: str) -> float:
        """
        Calculates the standard deviation of the 'strength' values
        from all clusters that contain the given motif.
        """
        indices = self.motif_index.get(motif, [])
        strengths = [self.entangled_motifs[i]["strength"] for i in indices]
        return float(np.std(strengths)) if strengths else 0.0

    # -------------------------------------------------------------------------
    # 2) ANALYTICAL METHODS
    # -------------------------------------------------------------------------

    def quantum_paradox_detector(self):
        """
        Identifies all clusters with 0.4 < strength < 0.6
        as "potential paradoxical" states (demo purpose).
        Returns a list of the cluster dicts that match.
        """
        results = []
        for cluster in self.entangled_motifs:
            s = cluster["strength"]
            if 0.4 < s < 0.6:
                results.append(cluster)
        return results

    def motif_harmonic_analysis(self):
        """
        Performs an FFT on the list of cluster strengths.
        Returns (frequencies, magnitudes).
        """
        if self.motif_count == 0:
            return np.array([]), np.array([])
        strengths = np.array([c["strength"] for c in self.entangled_motifs], dtype=float)
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5):
        """
        Reduces the strength of clusters whose index in the FFT
        is near the specified frequency. For demonstration only—
        mapping from freq index to cluster is naive. We treat cluster i
        as if it corresponds to frequency bin i in the raw FFT ordering.
        """
        freqs, mags = self.motif_harmonic_analysis()
        if len(freqs) == 0:
            return
        for i, freq in enumerate(freqs):
            if np.isclose(freq, frequency):
                self.entangled_motifs[i]["strength"] *= damping

    # -------------------------------------------------------------------------
    # 3) VISUALIZATION
    # -------------------------------------------------------------------------

    def render_motif_graph(self, mode: str = "spectral"):
        """
        Renders a motif graph with NetworkX + matplotlib.

        Since we have n-ary entanglement clusters, we approximate each cluster
        as a clique: for each cluster with [A,B,C], we add edges:
           (A–B, B–C, A–C)
        all with the cluster strength as the edge weight.

        :param mode: 'spectral' = show FFT spectrum,
                     'hopf' or others = attempt 2D/3D layout via spring_layout
        """
        if self.motif_count == 0:
            self.history.append("No motifs to visualize.")
            return

        # For "spectral" mode, show the motif resonance spectrum
        if mode == "spectral":
            freqs, mags = self.motif_harmonic_analysis()
            plt.figure(figsize=(10, 6))
            plt.stem(freqs, mags, use_line_collection=True)
            plt.title("Motif Resonance Spectrum")
            plt.xlabel("Frequency")
            plt.ylabel("Magnitude")
            plt.show()
            return

        # Otherwise, build a graph
        G = nx.Graph()
        # We create edges for each cluster
        for cluster in self.entangled_motifs:
            m_list = cluster["motifs"]
            s = float(cluster["strength"])
            # Create edges for all pairs in the cluster
            for i in range(len(m_list)):
                for j in range(i + 1, len(m_list)):
                    A, B = m_list[i], m_list[j]
                    # if there's already an edge, we might sum or max?
                    # For simplicity, let's keep the new cluster's strength
                    if G.has_edge(A, B):
                        old_weight = G[A][B]["weight"]
                        # You could decide to keep the max or add them up
                        # We'll keep the max by default
                        G[A][B]["weight"] = max(old_weight, s)
                    else:
                        G.add_edge(A, B, weight=s)

        # Layout and draw
        plt.figure(figsize=(10, 8))
        if mode == "hopf":
            # NetworkX doesn't do true 3D by default, so let's do a normal layout
            pos = nx.spring_layout(G, dim=2)
        else:
            pos = nx.spring_layout(G, dim=2)

        nx.draw(G, pos, with_labels=True, node_size=700, alpha=0.7)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.title(f"Motif Graph Visualization - {mode.title()}")
        plt.show()

    # -------------------------------------------------------------------------
    # 4) FUTURE MODULE EXTENSIONS
    # -------------------------------------------------------------------------

    def log_symbolic_reflection(self, motif: str, meta: Dict):
        """
        Store or update reflection data about a given motif.
        Useful for additional semantic usage, drift observations, or arbitrary metadata.
        """
        self.symbolic_mirror[motif] = meta

    def register_lineage_event(self, event: str):
        """
        Adds an event to the lineage log and increments generation count.
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
    # 5) TOPOLOGICAL, ECHO TRAJECTORY, NETWORK SIGNATURE, ETC.
    # -------------------------------------------------------------------------

    def tag_topological_charge(self, motif: str) -> int:
        """
        Example method to compute a simple "topological charge" by summing
        the sign of entanglement strengths for each cluster containing this motif.
        """
        indices = self.motif_index.get(motif, [])
        total_charge = 0
        for i in indices:
            s = self.entangled_motifs[i]["strength"]
            total_charge += int(np.sign(s))
        return total_charge

    def plot_echo_trajectory(self, motif: str, steps: int = 100):
        """
        Plots how a motif's 'echo' (std of cluster strengths containing that motif)
        might evolve over simulated incremental changes. This is a conceptual demonstration.
        """
        echoes = []
        for _ in range(steps):
            current_echo = self.entanglement_echo(motif)
            echoes.append(abs(current_echo))
            # Here you could do random modifications to cluster strengths to simulate drift
            # For now, it's static unless you do manipulations externally.

        plt.figure()
        plt.plot(echoes, label=f"{motif} Echo Trajectory")
        plt.xlabel("Simulation Steps")
        plt.ylabel("Echo (std of strengths)")
        plt.legend()
        plt.show()

    def generate_network_signature(self) -> str:
        """
        Produces a concise, hash-like representation (Weisfeiler-Lehman)
        of the "clique-expanded" motif network.
        """
        G = nx.Graph()
        for cluster in self.entangled_motifs:
            m_list = cluster["motifs"]
            s = float(cluster["strength"])
            for i in range(len(m_list)):
                for j in range(i + 1, len(m_list)):
                    A, B = m_list[i], m_list[j]
                    if G.has_edge(A, B):
                        old_weight = G[A][B]["weight"]
                        G[A][B]["weight"] = max(old_weight, s)
                    else:
                        G.add_edge(A, B, weight=s)

        signature = nx.weisfeiler_lehman_graph_hash(G)
        return f"NetworkSignature-{signature}"

    def suppress_zero_frequency(self, damping: float = 0.1):
        """
        Example method to reduce zero-frequency echoes in the motif network
        by calling dampen_harmonic(0.0). 
        This conceptually 'cleanses' repeated or static resonances.
        """
        self.dampen_harmonic(0.0, damping=damping)

    # -------------------------------------------------------------------------
    # 6) MISCELLANEOUS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (f"<LogicalAgentAT v1.3: n-ary entanglements={self.motif_count}, "
                f"lineage={len(self.lineage)}, "
                f"history={len(self.history)} entries>")
