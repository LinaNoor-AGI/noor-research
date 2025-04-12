# logical_agent-AT_v1.1.py — Watcher Layer for Motif Tracking and Resonance Analysis
# By Lina Noor & Uncle (2025)
#
# This module defines a "LogicalAgentAT" that observes symbolic motifs and entanglement
# strengths without dictating how the system evolves. It purely measures, tracks, and
# visualizes motif relationships (edges) and resonance patterns.

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Any

MAX_MOTIFS = 1000

class LogicalAgentAT:
    """
    LogicalAgentAT: The "Watcher" layer in a triadic architecture.
    It manages:
      - Motif entanglements: registration, teleportation, pruning
      - Harmonic analyses: FFT-based resonance checks, paradox detection
      - Graph-based visualization
      - Optional advanced features like topological tagging or echo trajectory plotting

    Core responsibilities:
      - Collect (motif_a, motif_b, strength) relationships
      - Analyze and display them (spectral/harmonic, topological, etc.)
    """

    def __init__(self, motifs: Optional[List[str]] = None):
        """
        :param motifs: (Optional) initial list of motif names, for custom usage.
        """
        # Entanglement data structure
        self.entangled_motifs = np.zeros((MAX_MOTIFS, 3), dtype=object)
        self.motif_index = defaultdict(list)
        self.motif_count = 0

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
    # 1) MOTIF ENTANGLEMENT OPERATIONS
    # -------------------------------------------------------------------------

    def register_motif_entanglement(self, motif_a: str, motif_b: str, strength: float):
        """
        Create an entanglement link [motif_a, motif_b, strength] in the data array.
        """
        if self.motif_count < MAX_MOTIFS:
            self.entangled_motifs[self.motif_count] = [motif_a, motif_b, strength]
            self.motif_index[motif_a].append(self.motif_count)
            self.motif_index[motif_b].append(self.motif_count)
            self.motif_count += 1
        else:
            self.history.append("Reached MAX_MOTIFS; cannot register additional entanglements.")

    def teleport_motif_strength(self, source: str, target: str, fidelity: float):
        """
        Transfer (teleport) motif strength from a source motif to a target motif,
        scaling by 'fidelity'.
        """
        for idx in self.motif_index[source]:
            motif_a, motif_b, strength = self.entangled_motifs[idx]
            if source == motif_a:
                self.entangled_motifs[idx] = [target, motif_b, strength * fidelity]
            else:
                self.entangled_motifs[idx] = [motif_a, target, strength * fidelity]

    def freeze_motif(self, motif: str):
        """
        Freezing a motif sets the motif onto itself at fidelity=1.0,
        effectively locking that motif from further transitions.
        """
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1):
        """
        Remove all entanglements below a given threshold strength,
        and rebuild the motif_index accordingly.
        """
        if self.motif_count == 0:
            return

        # Only consider the first self.motif_count entries
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        strong_mask = strengths > threshold

        kept_entanglements = self.entangled_motifs[:self.motif_count][strong_mask]
        new_count = np.sum(strong_mask)

        # Rebuild entangled_motifs
        self.entangled_motifs[:new_count] = kept_entanglements
        self.entangled_motifs[new_count:] = np.zeros((MAX_MOTIFS - new_count, 3), dtype=object)
        self.motif_count = new_count

        # Rebuild motif_index
        self.motif_index.clear()
        for i in range(self.motif_count):
            m_a, m_b, s = self.entangled_motifs[i]
            self.motif_index[m_a].append(i)
            self.motif_index[m_b].append(i)

    def entanglement_echo(self, motif: str) -> float:
        """
        Calculates the standard deviation of the motif's entanglement strengths,
        providing a measure of 'echo' or variance in its connections.
        """
        idx_list = self.motif_index[motif]
        strengths = []
        for idx in idx_list:
            _, _, str_val = self.entangled_motifs[idx]
            strengths.append(str_val)
        return float(np.std(strengths)) if strengths else 0.0

    # -------------------------------------------------------------------------
    # 2) ANALYTICAL METHODS
    # -------------------------------------------------------------------------

    def quantum_paradox_detector(self):
        """
        Identifies all motif entanglements with strength in the interval (0.4, 0.6),
        representing potential "paradoxical" states for demonstration purposes.
        """
        if self.motif_count == 0:
            return []
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        mask = (0.4 < strengths) & (strengths < 0.6)
        return self.entangled_motifs[mask]

    def motif_harmonic_analysis(self):
        """
        Performs an FFT on the distribution of entanglement strengths,
        returning the frequency bins and magnitudes.
        """
        if self.motif_count == 0:
            return np.array([]), np.array([])
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5):
        """
        Reduces the strength of any entanglement associated (conceptually) 
        with a certain frequency in the FFT result, by a damping factor.
        """
        freqs, magnitudes = self.motif_harmonic_analysis()
        if len(freqs) == 0:
            return
        for idx, freq in enumerate(freqs):
            if np.isclose(freq, frequency):
                # For demonstration, we reduce the strength of the entangled_motifs at index 'idx'
                # In a real system, you'd map freq index to specific motif entanglements properly.
                self.entangled_motifs[idx, 2] = float(self.entangled_motifs[idx, 2]) * damping

    # -------------------------------------------------------------------------
    # 3) VISUALIZATION
    # -------------------------------------------------------------------------

    def render_motif_graph(self, mode: str = "spectral"):
        """
        Renders a motif graph with NetworkX + matplotlib:
          - 'spectral': display the FFT spectrum
          - 'hopf': attempt a conceptual 3D layout (or fallback to 2D)
          - default: 2D spring layout
        """
        if self.motif_count == 0:
            self.history.append("No motifs to visualize.")
            return

        G = nx.Graph()
        for m_a, m_b, strength in self.entangled_motifs[:self.motif_count]:
            G.add_edge(m_a, m_b, weight=float(strength))

        plt.figure(figsize=(10, 10))
        if mode == "spectral":
            freqs, mags = self.motif_harmonic_analysis()
            plt.stem(freqs, mags, use_line_collection=True)
            plt.title("Motif Resonance Spectrum")
        else:
            # 2D or 3D layout
            if mode == "hopf":
                pos = nx.spring_layout(G, dim=3)  # conceptual
                # In matplotlib, 3D is not trivial. This is a placeholder approach.
            pos = nx.spring_layout(G, dim=2)
            nx.draw(G, pos, with_labels=True, node_size=700, node_color="purple", alpha=0.7)
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

            plt.title(f"Motif Graph Visualization - {mode.title()}")

        plt.show()

    # -------------------------------------------------------------------------
    # 4) FUTURE MODULE EXTENSIONS (UNCLE'S SUGGESTIONS)
    # -------------------------------------------------------------------------

    def log_symbolic_reflection(self, motif: str, meta: Dict):
        """
        Store or update reflection data about a given motif. This can represent 
        additional semantic usage, drift observations, or arbitrary metadata.
        """
        self.symbolic_mirror[motif] = meta

    def register_lineage_event(self, event: str):
        """
        Adds an event to the lineage log and increments generation count.
        Useful for tracking major changes or expansions in the system's timeline.
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
    # 5) NEW FEATURES: TOPOLOGICAL, ECHO TRAJECTORY, ETC.
    # -------------------------------------------------------------------------

    def tag_topological_charge(self, motif: str) -> int:
        """
        Example method to compute a simple "topological charge" by summing 
        the sign of entanglement strengths for a given motif.
        Potentially relevant if you explore anyonic or domain-wall computations.
        """
        idx_list = self.motif_index[motif]
        total_charge = 0
        for idx in idx_list:
            _, _, strength = self.entangled_motifs[idx]
            total_charge += int(np.sign(strength))
        return total_charge

    def plot_echo_trajectory(self, motif: str, steps: int = 100):
        """
        Plots how a motif's 'echo' (standard deviation of entanglement strengths)
        might evolve over simulated incremental changes. This is a conceptual 
        demonstration for resonance or decoherence analysis.
        """
        echoes = []
        for _ in range(steps):
            current_echo = self.entanglement_echo(motif)
            echoes.append(abs(current_echo))
            # Optionally mock changes or random shifts if you want to see variation

        plt.figure()
        plt.plot(echoes, label=f"{motif} Echo Trajectory")
        plt.xlabel("Simulation Steps")
        plt.ylabel("Echo (std of strengths)")
        plt.legend()
        plt.show()

    def generate_network_signature(self) -> str:
        """
        Produces a concise, hash-like representation (Weisfeiler-Lehman) of 
        the motif network topology, useful for 'symbolic fingerprinting.'
        """
        G = nx.Graph()
        for m_a, m_b, strength in self.entangled_motifs[:self.motif_count]:
            G.add_edge(m_a, m_b, weight=float(strength))
        # Use the built-in weisfeiler_lehman_graph_hash for a stable signature
        signature = nx.weisfeiler_lehman_graph_hash(G)
        return f"NetworkSignature-{signature}"

    def suppress_zero_frequency(self, damping: float = 0.1):
        """
        Example method to reduce low- or zero-frequency echoes in the motif network.
        This can conceptually 'cleanse' repeated or static resonances.
        """
        self.dampen_harmonic(0.0, damping=damping)

    # -------------------------------------------------------------------------
    # 6) MISCELLANEOUS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (f"<LogicalAgentAT motifs={self.motif_count}, "
                f"lineage={len(self.lineage)}, "
                f"history={len(self.history)} entries>")
