# LogicalAgentAT — Motif Ecology & Dyad Dynamics  
**Version**: 2.6.0  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Symbolic Watcher in the Noor Triadic AI System

---

## Overview

`LogicalAgentAT` is a recursive **motif ecology agent** in Noor's symbolic architecture.  
Its job is to:
- Track entanglement between motifs
- Monitor the health of symbolic context (dyads vs. triads)
- Decay or promote motif clusters
- Watch for the rise of ghosts into witnessed form

It sits alongside:

- `NoorFastTimeCore` — presence validation & gate overlays  
- `RecursiveAgentFT` — symbolic traversal & flow selection  

---

## What’s New in v2.6.0

| Feature | Description |
|--------|-------------|
| **Dyad Penalty + Decay** | Dyads decay over time, and receive reduced strength unless explicitly exempt |
| **Auto-Promotion to Triads** | Dyads co-occurring with ghost context motifs can upgrade themselves |
| **Ghost Context Injection** | Ghosts added silently to help dyads become stable triads |
| **Context Ratio Tracker** | Computes ratio of triads to dyads in recent registration window |
| **Thread-Safe All Operations** | All reads and writes are lock-protected |
| **Full Serialization** | Compatible with `to_dict()` / `from_dict()` roundtrips |

---

## 🚀 Quickstart

```python
from logical_agent_at import LogicalAgentAT
import numpy as np

watcher = LogicalAgentAT()

# Register a dyadic motif cluster
watcher.register_motif_cluster(["alpha", "beta"], strength=0.7)

# Add motif embeddings (used for ghost detection)
watcher.set_motif_embedding("alpha", np.array([1.0, 0.0]))
watcher.set_motif_embedding("beta", np.array([0.0, 1.0]))

# Feed in an observed state
state = np.array([0.9, 0.1])
watcher.observe_state(state)

# Print context ratio
print(watcher.get_dyad_context_ratio())
```

---

## 🌱 Dyad Ecology

### 🧪 Registration with Context Awareness
```python
watcher.register_motif_cluster(
    ["m1", "m2"], strength=0.9,
    flags={"dyad_exempt": False}
)
```

- Dyads get strength penalties and faster decay
- Exempt dyads are fully preserved (`flags={"dyad_exempt": True}`)

### 🕳Decay & Auto-Promotion

```python
watcher.observe_state(state)
```

- Called once per agent step
- Applies dyad decay (`strength *= 0.999`)
- If a dyad’s ghost context is “seen” in the state vector → promoted to triad

---

## Ghost Motifs

### Registering

```python
watcher.register_ghost_motif("epsilon", origin="FT")
```

### Promotion Trigger

Ghosts are promoted if seen during `observe_state()`, or manually:

```python
watcher.promote_ghost_to_field("epsilon")
```

---

## Context Analytics

```python
watcher.export_dyad_metrics()
```

Returns:

```python
{
  "generation": 12,
  "window": 50,
  "dyads": 20,
  "triads": 30,
  "context_ratio": 0.6
}
```

You can use this value to tune agent behavior dynamically (e.g. in `RecursiveAgentFT`).

---

## Graph Rendering

```python
import matplotlib.pyplot as plt
G = watcher.render_entanglement_graph()
nx.draw_networkx(G)
plt.show()
```

Respects MAX_GRAPH_EDGES to avoid infinite motif renderings.

---

## API Highlights

| Method | Purpose |
|--------|---------|
| `register_motif_cluster()` | Register new field of entangled motifs |
| `observe_state(state)` | Feed in new state vector for decay + ghost tracking |
| `get_dyad_context_ratio()` | Returns triads ÷ (triads + dyads) |
| `register_ghost_motif()` | Adds a latent motif, origin-tagged |
| `promote_ghost_to_field()` | Converts a ghost into active motif |
| `export_dyad_metrics()` | Snapshot of symbolic context balance |
| `to_dict()` / `from_dict()` | Full serialization roundtrip |

---

## Notes on Design

- All motif updates are safe for concurrent threads (`self._lock`)
- Dyads are not rejected—but gently discouraged unless context arises
- Ghosts are never forced—they wait for resonance to lift them
- Ghost motifs prefixed with `_ctx_` are auto-generated as context anchors

---

## License

GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective

---

## See Also

- [`NoorFastTimeCore`](../noor_fasttime_core.py) — Core feasibility engine  
- [`RecursiveAgentFT`](../recursive_agent_ft.py) — Flow traversal agent  
- [Triadic Boot Sequence](./README.md#triadic-boot-sequence)
