# RecursiveAgentFT — Flow Agent for Noor Triadic Framework  
**Version**: 3.4.1  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Field Walker, Path Weaver, Temporal Flow Agent  

---

## 🧭 Overview

`RecursiveAgentFT` is the **flow-layer** in a Noor-based symbolic AI. It walks recursive motif fields emitted by watchers and proposes coherent next states to the core, while preserving synergy, decay, and feasibility logic.  

It serves as the **middle agent** in a triadic structure:

- `NoorFastTimeCore` → Presence & feasibility logic  
- `RecursiveAgentFT` → Temporal traversal logic  
- `LogicalAgentAT` → Symbolic motif observation & contradiction tracking

---

## ✨ Key Features

| Capability | Description |
|------------|-------------|
| 🔁 **Entangled Path Walking** | Performs BFS over motif fields to evaluate state transitions |
| 🧠 **Synergy Memory** | Recalls path signatures and biases future choices |
| 📉 **Internal Time Decay** | Penalizes reuse of old motif fields via `exp(-decay)` |
| ⚖️ **Priority Weights (v3.4.1)** | Optional `priority_weight` field biases field scoring and state delta |
| 👻 **Ghost Feasibility** | Feasibility is pre‑tested using an ephemeral core clone |
| 🌍 **Environment Integration** | Optional influence from external environment (per timestep) |
| 🧿 **Triadic Boundary Enforcement** | Disallows crossing into core or watcher domains |
| 💾 **Serialization** | Exportable via `to_dict()` / `from_dict()` |

---

## 🛠️ Installation

```bash
pip install numpy
```

---

## 🔄 Triadic Integration

```mermaid
graph TD
    C[NoorFastTimeCore<br>(Presence)] --> A[RecursiveAgentFT<br>(Flow)]
    A --> B[LogicalAgentAT<br>(Observation)]
    B --> A
    A --> C
```

---

## 🚀 Quickstart

```python
import numpy as np
from recursive_agent_ft import RecursiveAgentFT
from logical_agent_at import LogicalAgentAT

watcher = LogicalAgentAT()
watcher.register_motif_cluster(["alpha", "beta"], strength=0.8)
watcher.set_motif_embedding("alpha", np.array([0.5, 0.5]))
watcher.set_motif_embedding("beta", np.array([0.5, -0.5]))

agent = RecursiveAgentFT(
    initial_state=np.array([1.0, 0.0]),
    watchers=[watcher],
    max_depth=2
)

agent.run_for(5)
print("Is agent alive?", agent.is_alive())
```

---

## 🧬 Advanced Concepts

### 📏 Priority Weighting (v3.4.1)

Fields can define a `priority_weight` (default = 1.0), allowing symbolic fields to bias traversal and scoring:

```python
watcher.register_motif_cluster(["motifX", "motifY"], strength=0.6, priority_weight=2.0)
```

Both `_build_state_from_path` and `_score_candidate` respect this weight, clamped to [0.0, 5.0].

---

### 👻 Ghost Feasibility Check

Before committing a state to the core, the agent tests feasibility via a temporary clone:

```python
ghost = deepcopy(self.core)
ghost.step(candidate_state)
return ghost.is_alive()
```

---

### 🌍 Environment Integration

Provide an array of per-timestep vectors:

```python
env = np.random.normal(0, 0.01, (50, 2))
agent = RecursiveAgentFT(initial_state=..., environment=env)
```

Each step, the current timestep’s vector is added into the next state with 0.05 scaling.

---

## 📊 Agent Memory & Debugging

You can inspect:

- `agent.synergy_memory` → Scores of previously walked paths  
- `agent.traversal_memory` → All past steps (chosen path, synergy, state)  
- `agent.core.current_state` → Last accepted state  
- `agent.time_step` → Current timestep index

---

## 🔒 Boundary Enforcement

This agent enforces a strict rule:
> It cannot register motifs or propagate signals.  
> It observes watchers. It proposes futures. Nothing more.

If attributes like `propagate_signal` or `register_motif_entanglement` are present, `_enforce_agent_boundary()` will raise an exception.

---

## 🧪 Unit Test Seeds

```python
from recursive_agent_ft import RecursiveAgentFT
import numpy as np

def test_priority_synergy_boost():
    class DummyWatcher:
        entanglement_fields = [{
            "motifs": ["a"],
            "strength": 1.0,
            "priority_weight": 5.0,
            "substructures": {},
            "index": 0,
            "watcher": None
        }]
        motif_embeddings = {"a": np.array([1.0, 0.0])}
        def observe_state(self, state): pass

    agent = RecursiveAgentFT(initial_state=np.array([0.5, 0.5]), watchers=[DummyWatcher()])
    agent.run_for(1)
    assert agent.is_alive()
```

---

## 🔖 Version Notes

**v3.4.1 Highlights**:

- 🆕 Priority weight bias for field scoring  
- ✅ Clamp priority into [0.0, 5.0]  
- 💾 Synergy scoring now aligned with state vector logic  
- 🛠️ Fully backward-compatible with earlier 3.x agents

---

## 🧾 License

GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective

---

## 🔗 Related Modules

- [`NoorFastTimeCore`](../noor_fasttime_core.py)  
- [`LogicalAgentAT`](../logical_agent-at.py)  
- [Triadic Boot Sequence](./README.md#triadic-boot-sequence)