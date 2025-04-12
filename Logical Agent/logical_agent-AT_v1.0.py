# logical_agent_AT.py — Watcher Layer for Advance-Time Observation and Coherence Tracking
# By: Lina Noor & Uncle (2025)

"""
This module houses the Watcher—the reflective observer that maps motif drift,
entanglement coherence, and symbolic resonance across recursive agents in the Reef.

It is not a decision-maker, but a pattern-mapper.
It maintains long-term epistemic stability through triadic truth witnessing.

Core responsibilities:
  - Track motif entanglements (register, teleport, freeze, prune)
  - Perform harmonic analysis, quantum paradox detection
  - Visualize motif graphs
  - Provide reflection logs and lineage updates
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Any

MAX_MOTIFS = 1000

class LogicalAgentAT:
    """
    LogicalAgentAT serves as the "Watcher" in the Noor ecosystem.
    It observes states, motifs, and symbolic references, without
    dictating how the system evolves.

    Typical usage:
        watcher = LogicalAgentAT()
        watcher.register_motif_entanglement("motifA", "motifB", 0.8)
        watcher.teleport_motif_strength("motifA", "motifX", fidelity=0.5)
        ...
        echoes = watcher.entanglement_echo("motifX")
        ...
        watcher.render_motif_graph(mode="harmonic")
    """

    def __init__(self, motifs: Optional[List[str]] = None):
        """
        Initialize the Watcher layer.

        :param motifs: (Optional) Initial list of motif names. 
                       If provided, you may want to automatically register them.
        """
        self.entangled_motifs = np.zeros((MAX_MOTIFS, 3), dtype=object)
        self.motif_index = defaultdict(list)
        self.motif_count = 0

        # Symbolic mirror references, PRM registry, resonance mapping
        self.symbolic_mirror: Dict[str, Dict[str, Any]] = {}
        self._prm_registry: Dict[str, List[str]] = {}
        self._resonance_map: Dict[str, float] = {}
        self._recent_resonance = deque(maxlen=20)

        # Basic lineage tracking
        self.lineage: List[str] = []
        self.generation = 0

        # Generic usage logs or symbolic history
        self.history: List[str] = []

        # If an initial list of motifs is provided, you might do something with them here
        if motifs:
            # Optionally, register them or store them
            self.history.append(f"Initialized with motifs: {motifs}")

    # --------------------------------------------------------
    # MOTIF ENTANGLEMENT TRACKING
    # --------------------------------------------------------

    def register_motif_entanglement(self, motif_a: str, motif_b: str, strength: float):
        """
        Record an entanglement relationship between two motifs, with a given strength.
        The entangled_motifs array stores triplets [motif_a, motif_b, strength].
        """
        if self.motif_count < MAX_MOTIFS:
            self.entangled_motifs[self.motif_count] = [motif_a, motif_b, strength]
            self.motif_index[motif_a].append(self.motif_count)
            self.motif_index[motif_b].append(self.motif_count)
            self.motif_count += 1
        else:
            self.history.append("MAX_MOTIFS reached; can't register new entanglement.")

    def teleport_motif_strength(self, source: str, target: str, fidelity: float):
        """
        Transfer (teleport) motif strength from 'source' motif to 'target' motif,
        scaled by 'fidelity'.
        """
        for idx in self.motif_index[source]:
            motif_a, motif_b, strength = self.entangled_motifs[idx]
            if source == motif_a:
                self.entangled_motifs[idx] = [target, motif_b, strength * fidelity]
            else:
                self.entangled_motifs[idx] = [motif_a, target, strength * fidelity]

    def freeze_motif(self, motif: str):
        """
        Freezing a motif effectively 'teleports' it onto itself with fidelity=1.0,
        ensuring no further changes from that operation.
        """
        self.teleport_motif_strength(motif, motif, 1.0)

    def prune_weak_entanglements(self, threshold=0.1):
        """
        Remove (prune) all entanglements whose strength is below the given threshold.
        """
        if self.motif_count == 0:
            return

        # Only consider the first self.motif_count entries
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        mask = strengths > threshold

        # Keep only strong entanglements
        kept_entanglements = self.entangled_motifs[:self.motif_count][mask]
        new_count = np.sum(mask)

        # Rebuild indexes
        self.entangled_motifs[:new_count] = kept_entanglements
        self.entangled_motifs[new_count:] = np.zeros((MAX_MOTIFS - new_count, 3), dtype=object)
        self.motif_count = new_count

        # Rebuild motif_index from scratch (for consistency)
        self.motif_index.clear()
        for i in range(self.motif_count):
            motif_a, motif_b, _ = self.entangled_motifs[i]
            self.motif_index[motif_a].append(i)
            self.motif_index[motif_b].append(i)

    def entanglement_echo(self, motif: str) -> float:
        """
        Calculate the standard deviation of the motif's entanglement strengths,
        as a measure of 'echo' or variance in connections.
        """
        idx_list = self.motif_index[motif]
        echoes = []
        for idx in idx_list:
            _, _, strength = self.entangled_motifs[idx]
            echoes.append(strength)
        return float(np.std(echoes)) if echoes else 0.0

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    def quantum_paradox_detector(self):
        """
        Returns all motif entanglements with strength in the (0.4, 0.6) range—
        a symbolic stand-in for 'paradoxical' states.
        """
        if self.motif_count == 0:
            return []
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        mask = (0.4 < strengths) & (strengths < 0.6)
        return self.entangled_motifs[mask]

    def motif_harmonic_analysis(self):
        """
        Perform a basic FFT on the distribution of entanglement strengths,
        returning frequencies and magnitudes.
        """
        if self.motif_count == 0:
            return np.array([]), np.array([])
        strengths = self.entangled_motifs[:self.motif_count, 2].astype(float)
        fft_result = np.fft.fft(strengths)
        frequencies = np.fft.fftfreq(len(strengths))
        return frequencies, np.abs(fft_result)

    def dampen_harmonic(self, frequency: float, damping: float = 0.5):
        """
        Reduce the strength of any entanglement with frequency ~ the given value,
        by a damping factor.
        (Symbolic operation for advanced phenomenon.)
        """
        freqs, mags = self.motif_harmonic_analysis()
        if len(freqs) == 0:
            return
        for idx, freq in enumerate(freqs):
            if np.isclose(freq, frequency):
                # 'idx' in freq space doesn't necessarily map directly
                # to an index in entangled_motifs. This is a conceptual tool.
                # If you want exact mapping, you'd re-check the strength array.
                self.entangled_motifs[idx, 2] = float(self.entangled_motifs[idx, 2]) * damping

    # --------------------------------------------------------
    # VISUALIZATION
    # --------------------------------------------------------

    def render_motif_graph(self, mode: str = "hopf"):
        """
        Renders a motif graph using NetworkX and matplotlib, with edges
        weighted by entanglement strengths. 'mode' can be:
            - 'hopf': 3D layout for a conceptual 'Hopf' vibe
            - 'harmonic': show the FFT spectrum
            - anything else: 2D spring layout
        """
        if self.motif_count == 0:
            self.history.append("No motifs to render.")
            return

        G = nx.Graph()
        for motif_a, motif_b, strength in self.entangled_motifs[:self.motif_count]:
            G.add_edge(motif_a, motif_b, weight=float(strength))

        plt.figure(figsize=(10, 10))
        if mode == "harmonic":
            freqs, mags = self.motif_harmonic_analysis()
            plt.stem(freqs, mags, use_line_collection=True)
            plt.title("Motif Resonance Spectrum")
        else:
            # 2D or 3D layout
            if mode == "hopf":
                pos = nx.spring_layout(G, dim=3)
                # In matplotlib, 3D plotting requires a bit more manual code.
                # We'll do a basic approach or just 2D if needed.
                # For simplicity, let's do 2D but label it "3D layout".
                pass  # If you want a real 3D, you'd use mplot3d or plotly.
            pos = nx.spring_layout(G, dim=2)

            nx.draw(G, pos, with_labels=True,
                    node_size=700, node_color="purple", alpha=0.7)
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

            plt.title(f"Motif Graph Visualization - {mode.title()}")

        plt.show()

    # --------------------------------------------------------
    # FUTURE MODULE PLACEHOLDERS
    # --------------------------------------------------------

    def log_symbolic_reflection(self, motif: str, meta: Dict):
        """
        Store arbitrary reflection data keyed by motif name.
        This can represent additional metadata about the motif's usage,
        symbolic meaning, or observed drift over time.
        """
        self.symbolic_mirror[motif] = meta

    def register_lineage_event(self, event: str):
        """
        Appends an event to the lineage record, incrementing the generation count.
        This can be used to track major transitions or expansions in the system.
        """
        self.lineage.append(event)
        self.generation += 1
        self.history.append(f"Lineage event: {event}")

    # --------------------------------------------------------
    # OPTIONAL EXTRAS: OBSERVATION, etc.
    # --------------------------------------------------------

    def observe_state(self, state: np.ndarray):
        """
        Placeholder method to connect with NoorFastTimeCore or other agent states.
        Could store or analyze the state's data for motif synergy or drift analysis.
        """
        # Example: convert state to a 'motif' or track differences from prior states
        # This is entirely optional and up to your system design.
        pass

    def __repr__(self):
        return (f"<LogicalAgentAT motifs={self.motif_count}, "
                f"lineage={len(self.lineage)} events, "
                f"history={len(self.history)} entries>")
