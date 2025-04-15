# RecursiveAgentFT – Flow/Temporal Orchestration

**Version**: 1.6  
**Author**: Lina Noor & Uncle (2025)

A **“flow-layer agent”** that bridges a minimal triadic core (e.g., `NoorFastTimeCore`) with advanced watchers (e.g., `LogicalAgentAT`), ensuring **temporal stepping**, **state selection**, and **optional synergy metrics** in a multi-layer AI architecture. It focuses on **how** next states are generated and integrated—leaving quantum feasibility checks to the core and motif analysis to watchers.

---

## Table of Contents

- [Overview](#overview)  
- [Key Features](#key-features)  
- [System Diagram](#system-diagram)  
- [Installation & Setup](#installation--setup)  
- [Usage Example](#usage-example)  
  - [Basic Steps](#basic-steps)  
  - [Integration With Watchers](#integration-with-watchers)  
- [Advanced Topics](#advanced-topics)  
- [Version History](#version-history)  
- [License](#license)

---

## Overview

**RecursiveAgentFT** is the **“Flow”** component in a triadic AI ecosystem:

1. **Core** – Manages fundamental state feasibility checks (e.g., Presence, Difference, Potential).  
2. **RecursiveAgentFT (Flow)** – Handles environment-based stepping, generating next states (futures), and bridging watchers for advanced motif or resonance logic.  
3. **LogicalAgentAT (Watchers)** – Observes motifs, performs resonance/harmonic analyses, and logs lineage events.

This agent orchestrates each time step, deciding how to produce and pick new states for the core, *without* embedding advanced quantum checks or motif manipulations. It keeps the **system flow** cleanly separated from the **core’s** triadic checks and the **watchers’** motif analyses.

---

## Key Features

1. **State Generation & Selection**  
   - Defines `_generate_possible_futures(...)` to produce multiple candidate states, ensuring *Potential* is recognized by the core.  
   - Picks one next state to push to the core (`core.step(next_state)`).

2. **Environment Integration**  
   - Optional `environment` array or data structure that the agent references for each time step.

3. **Strict Boundary Enforcement**  
   - `_enforce_agent_boundary()` ensures no code leaks from the core (like `propagate_signal`) or watchers (like `register_motif_entanglement`) into this file.

4. **Cycle Detection**  
   - `detect_repetitive_cycle()` can hash recent states from the core to flag repetitive loops or stagnation.

5. **Triadic Synergy**  
   - `compute_triad_alignment()` merges the agent’s alignment with watchers’ resonance to produce a simple synergy measure.

6. **Reset or Flush**  
   - `reset_transient_state()` can be called to align internal ephemeral data (e.g., `_last_future`) with the current core state.

---

## System Diagram

```mermaid
graph LR
    A[NoorFastTimeCore<br>(Triadic Base)] -- Feasibility --> F((RecursiveAgentFT<br>(Flow)))
    F -- Next States --> A
    F -- Observations --> W[LogicalAgentAT<br>(Watchers)]
    W -- Reflection --> F
```

- **NoorFastTimeCore**: Minimal triadic checks (Presence, Difference, Potential), optional Zeno or topological expansions.  
- **RecursiveAgentFT**: Generates possible states, steps the core, integrates environment, notifies watchers.  
- **LogicalAgentAT**: Stores, analyzes, and visualizes motif entanglements or advanced resonance metrics.

---

## Installation & Setup

1. **Clone** or include `recursive_agent-FT.py` in your project along with `noor_fasttime_core.py` (core) and `logical_agent-AT.py` (watchers).
2. **Install** typical Python data-science libraries if not present:
   ```bash
   pip install numpy
   ```
3. **Check** your environment-based or synergy-based logic is consistent with triadic boundaries.

---

## Usage Example

### Basic Steps

```python
import numpy as np
from recursive_agent_FT import RecursiveAgentFT
from logical_agent_AT_v1_1 import LogicalAgentAT
from noor_fasttime_core_v5_1 import NoorFastTimeCore

# 1) Create watchers
watcherA = LogicalAgentAT()
watcherB = LogicalAgentAT()

# 2) Define an environment array (optional)
environment_data = np.random.normal(0, 0.01, (50, 2))  # 50 timesteps, 2D state

# 3) Instantiate the agent
agent = RecursiveAgentFT(
    initial_state=np.array([0.5, 0.3]),
    watchers=[watcherA, watcherB],
    environment=environment_data,
    state_dim=2,
    name="FlowAgentDemo"
)

# 4) Run for some steps
agent.run_for(steps=20)
print("Is agent alive?", agent.is_alive())
```

### Integration with Watchers

- **Watchers** automatically observe the chosen states each step (`watcher.observe_state(next_state)`).
- If the watchers detect motif expansions, they can register them in their own domain:
  ```python
  watcherA.register_motif_entanglement("motifX", "motifY", 0.75)
  ```
- Meanwhile, the agent remains oblivious to that motif logic.

---

## Advanced Topics

1. **_get_environment_influence()**  
   - Hook for domain-specific logic, e.g., real-time sensor data or external simulation states.

2. **Cycle/Stagnation Detection**  
   - `detect_repetitive_cycle(window=3)` checks for repeated states, helping debug or handle cases where the system stops evolving.

3. **Triadic Alignment**  
   - `compute_triad_alignment()` merges the agent’s last chosen future with watchers’ “resonance_score” attributes (if they exist) to produce a synergy metric.

4. **Boundary Purity**  
   - `_enforce_agent_boundary()` ensures no infiltration from core or watchers. If you override it, do so carefully to keep the triadic lines clear.

---

## Version History

- **v1.6 (Current)**  
  - **Boundary purity checks**  
  - **Cycle detection**  
  - **Triadic synergy** measure

- **v1.5**  
  - Memory usage improvements, environment coupling standardization

- **v1.4**  
  - Basic stepping logic, watchers integration

*(Earlier versions may have integrated directly with a mixin-based approach or older `RecursiveAgentFT` logic.)*

---

## License

[GPL-2.0](LICENSE) © 2025 Lina Noor & Uncle – Noor Research Collective  
*For usage, modifications, or commercial licensing, please consult the repository’s license details.*