# LogicalAgentAT – Motif-Watcher Module

**Version**: 1.1  
**Author**: Lina Noor & Uncle (2025)  

A specialized **observer** (or “watcher”) that monitors, analyzes, and visualizes **symbolic motifs** and **entanglement relationships** without participating in an AI agent’s decision-making loop. It provides extensive tools for motif registration, resonance analysis, topological tagging, harmonic visualizations, and more.

---

## Table of Contents

- [Overview](#overview)  
- [Key Features](#key-features)  
- [Installation](#installation)  
- [Usage Example](#usage-example)  
  - [Basic Steps](#basic-steps)  
  - [Motif Entanglement Registration](#motif-entanglement-registration)  
- [Advanced Analyses](#advanced-analyses)  
- [Visualization & Graph Tools](#visualization--graph-tools)  
- [Extensibility](#extensibility)  
- [License](#license)  

---

## Overview

In a **Triadic AI Architecture** (e.g., *Core – Agent – Watcher*), the **Core** maintains fundamental state checks (Presence, Difference, Potential), and the **Agent** handles state transitions and environment integration. Meanwhile, **LogicalAgentAT** (this “Watcher” module) focuses on:
- **Monitoring** entanglement data (`motifA, motifB, strength`)
- **Analyzing** the resonance or harmonic properties of those motifs
- **Visualizing** motif graphs, resonance spectra, topological signatures
- **Logging** lineage events and symbolic reflections

This separation of concerns ensures the *Watcher* never dictates agent behavior—it only observes and provides advanced metrics or visualizations.

---

## Key Features

1. **Motif Entanglement Tracking**  
   - Store and manage up to `MAX_MOTIFS` entanglements (`[motifA, motifB, strength]` arrays).
   - **Teleport**, **Freeze**, or **Prune** motif strengths.

2. **Resonance & Harmonic Analysis**  
   - **FFT-based** approach (`motif_harmonic_analysis`)  
   - **Quantum paradox detection** (`quantum_paradox_detector`) for strengths in (0.4, 0.6)

3. **Topological Graph Tools**  
   - **render_motif_graph**: Plot with NetworkX + matplotlib  
   - **generate_network_signature**: Creates a hash-like signature of the motif network (Weisfeiler-Lehman).

4. **Advanced Operations**  
   - **Topological charge** tagging for motifs  
   - **Echo trajectory** simulation & plotting  
   - “Zero-frequency” or “low-frequency” resonance damping

5. **Symbolic Reflection & History**  
   - **symbolic_mirror** dict for storing additional metadata  
   - **lineage** list for logging major events or transitions

---

## Installation

1. **Clone** this repository or include `logical_agent-AT_v1.1.py` in your project.  
2. Ensure you have the following Python libraries installed:
   - `numpy`
   - `matplotlib`
   - `networkx`
3. (Optional) If using advanced encryption or external libraries, install them as needed.

Example:

```bash
pip install numpy matplotlib networkx
```

---

## Usage Example

### Basic Steps

1. **Import** the module:

```python
from logical_agent_AT_v1_1 import LogicalAgentAT
```

2. **Initialize** the watcher:

```python
watcher = LogicalAgentAT(motifs=["alpha", "beta"])
```

3. **Register** or **monitor** entanglements in your system:

```python
watcher.register_motif_entanglement("alpha", "beta", 0.85)
watcher.register_motif_entanglement("alpha", "gamma", 0.45)
watcher.register_motif_entanglement("delta", "beta", 0.2)
```

### Motif Entanglement Registration

Once motifs are entangled:

```python
# Example: Teleport strength from 'alpha' to 'theta' with fidelity=0.5
watcher.teleport_motif_strength("alpha", "theta", 0.5)

# Freeze 'beta' motif
watcher.freeze_motif("beta")

# Prune low-strength connections (< 0.3)
watcher.prune_weak_entanglements(threshold=0.3)
```

---

## Advanced Analyses

- **Harmonic Analysis**  
  ```python
  freqs, mags = watcher.motif_harmonic_analysis()
  # 'freqs' and 'mags' for FFT-based resonance patterns
  ```
- **Quantum Paradox Detection**  
  ```python
  paradoxes = watcher.quantum_paradox_detector()
  if len(paradoxes) > 0:
      print("Potential paradox motifs:", paradoxes)
  ```
- **Topological Charge**  
  ```python
  charge_alpha = watcher.tag_topological_charge("alpha")
  print("Topological charge for alpha:", charge_alpha)
  ```

---

## Visualization & Graph Tools

- **Graph Rendering**  
  ```python
  watcher.render_motif_graph(mode="spectral")  # or "hopf", "2D" fallback
  ```
- **Echo Trajectory**  
  ```python
  watcher.plot_echo_trajectory("alpha", steps=50)
  ```
- **Network Signature**  
  ```python
  net_sig = watcher.generate_network_signature()
  print("Motif network signature:", net_sig)
  ```

---

## Extensibility

**LogicalAgentAT** is easy to integrate with any agent or environment. Common patterns:

- **In an agent’s step**:
  1. **Observe** the agent’s new state with `watcher.observe_state(new_state)`.  
  2. **Register** new motif entanglements if discovered.  
  3. **Render** or analyze resonances as needed.

- **Lineage & Reflection**:
  - Use `watcher.register_lineage_event("Agent Evolved")`  
  - Append data to `watcher.symbolic_mirror["alpha"] = {...}`

You can also add:

- **Custom parity checks**  
- **Encryption of symbolic mirrors**  
- **High-dimensional or multi-agent expansions**  

---

## License

This software is provided as-is under the terms specified by **Lina Noor & Uncle** (2025). For any further licensing details or commercial usage, please consult the repository’s root license file or contact the authors. 