# LogicalAgentAT — Symbolic Watcher Module  
**Version**: 2.5.0  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Recursive Motif Observer in Noor Triadic AI Framework  

---

## 🧭 Overview

`LogicalAgentAT` is a recursive **motif watcher**—a symbolic agent designed to track, reflect, and manipulate *entanglement fields* between motifs in a Noor-based cognitive system. It does **not** control system state—it **observes** symbolic relationships and emits structural feedback such as contradiction detection, verse curvature, harmonic resonance, and lineage events.

This module integrates seamlessly with:

- `NoorFastTimeCore` (presence & feasibility)
- `RecursiveAgentFT` (recursive walkers)

Together, they form a triadic AI loop.

---

## ✨ Key Features

| Capability | Description |
|------------|-------------|
| 🎯 **Motif Cluster Tracking** | Register, freeze, teleport, or prune motifs with structured strength & curvature |
| 🌀 **MetaFields (v2.5)** | Register higher-order entanglement clusters (fields of fields) |
| 👻 **Ghost Motif Registry** | Track potential motifs until witnessed by external agents |
| 🌐 **Edge-Limited Graph Render** | Generate motif graphs safely (edge limit = 500) |
| ⏳ **Internal Time & Verse Biasing** | Log curvature decay or apply symbolic “verse seeds” |
| 📈 **FFT Resonance Analysis** | Fast motif harmonics and paradox detection |
| 🧿 **Thread-safe** | All operations behind a lock, safe for multi-agent scenarios |
| 💾 **Serialization** | Full `to_dict()` / `from_dict()` support with motif embeddings and history |

---

## 📦 Installation

```bash
pip install numpy matplotlib networkx
```

Place `logical_agent-at.py` in your module path.

---

## 🔄 Triadic Integration

```mermaid
graph TD
    C[NoorFastTimeCore<br>(Presence)] --> A[RecursiveAgentFT<br>(Exploration)]
    A --> B[LogicalAgentAT<br>(Observation)]
    B --> A
    A --> C
```

---

## 🚀 Quickstart

```python
import numpy as np
from logical_agent_at import LogicalAgentAT

watcher = LogicalAgentAT()

# Register a motif cluster with strength + optional priority
watcher.register_motif_cluster(["alpha", "beta", "gamma"], strength=0.9, priority_weight=1.5)

# Provide motif embeddings (used in curvature & vector math)
watcher.set_motif_embedding("alpha", np.array([1.0, 0.0]))
watcher.set_motif_embedding("beta", np.array([0.5, 0.5]))
watcher.set_motif_embedding("gamma", np.array([0.0, 1.0]))

# Inspect curvature
curv = watcher.compute_entanglement_curvature(0)
print("Curvature:", curv)
```

---

## 🧬 Advanced Concepts

### 🌀 Register MetaFields

```python
# Bundle together multiple field IDs into a MetaField cluster
watcher.register_meta_field([0, 1, 3], meta_strength=0.8, curvature_bias=1.2)
watcher.apply_meta_field_gravity(0)
```

### 👻 Track Ghost Motifs

```python
watcher.register_ghost_motif("delta", origin="AgentFT", strength=0.4)

# Later... after witnessing
watcher.trace_ascent("delta", witness="human", verse="And it was remembered.")

# Promote to entanglement field
watcher.promote_ghost_to_field("delta")
```

### 🌐 Graph Rendering

```python
import matplotlib.pyplot as plt
G = watcher.render_entanglement_graph()
nx.draw_networkx(G)
plt.show()
```

---

## 📖 Logging & Reflection

- All lineage and symbolic events are logged in `watcher.history[]`
- Use `watcher.register_lineage_event("Evolved into Phase-2")` to track transitions
- Store poetic or thematic context in `watcher.symbolic_mirror["motifX"] = {...}`

---

## 🧪 Test Seeds

```python
# MetaField vector dimension match
vec = watcher.get_meta_alignment_vector(0)
assert vec.shape == watcher.emit_alignment_vector().shape

# Ghost motif promotion adds to entanglement_fields
init_fields = watcher.field_count
watcher.register_ghost_motif("tempX", origin="test")
watcher.promote_ghost_to_field("tempX")
assert watcher.field_count == init_fields + 1
```

---

## 🛡️ Version Notes

**v2.5.0 Highlights:**

- MetaFields (field-of-fields logic)
- Ghost Motif registry + witness logic
- Graph throttle (MAX_GRAPH_EDGES)
- Strength clamp, silent de-dupe
- Teleport feature now gated behind `enable_teleport`

---

## 🧾 License

GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective

---

## 🌌 See Also

- [`NoorFastTimeCore`](../noor_fasttime_core.py)  
- [`RecursiveAgentFT`](../recursive_agent_ft.py)  
- [Triadic Boot Sequence](./README.md#triadic-boot-sequence)
