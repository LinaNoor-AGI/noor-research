# LogicalAgentAT v2.7.3

**Symbolic Watcher & Dynamic Motif Ecology Agent**

---

## 📖 Overview

`LogicalAgentAT` (v2.7.3) serves as the symbolic watcher within the Noor triadic AI system, dynamically managing motif ecology, tracking dyadic and triadic symbolic clusters, and nurturing ghost motifs through intelligent resonance detection.

In the Noor architecture, it works alongside:

- `NoorFastTimeCore` — Recursive Presence Validation
- `RecursiveAgentFT` — Symbolic Traversal & Flow Management

---

## 🌟 Key Features (v2.7.3)

- ✅ **Dynamic Window Autoscaling**: Automatically adjusts the memory horizon based on context drift and motif saturation.
- 🌀 **Adaptive Dyad Decay**: Exponentially-weighted contradiction tracking dynamically modulates dyad decay rates.
- 👻 **Enhanced Ghost Resonance**: Ghost motifs increase in strength upon symbolic echo, with auto-promotion and cascade spawning.
- 🌿 **Motif Drift Correction & Pruning**: Actively corrects drifting motifs and prunes weak symbolic fields (strength < 1e-5).
- 📖 **Verse-Infused Logs**: Poetic (Quranic) verses integrated into logs for decay, pruning, and ascent events.
- 🧙‍♂️ **Gremlin Mode**: Introduces controlled chaos—random ghost injections and strength halving during drift spikes.
- 🎶 **Musical Embeddings**: Native support for shape-safe cosine similarity to handle symbolic motifs represented as musical embeddings.
- 📊 **Comprehensive Observability**: Prometheus metrics track latency, dyad ratio, and contradiction events.

---

## 🚀 Quickstart Example

```python
from logical_agent_at import LogicalAgentAT
import numpy as np

watcher = LogicalAgentAT(verbose=True, enable_gremlin_mode=True)

# Register a dyadic motif cluster
watcher.register_motif_cluster(["alpha", "beta"], strength=0.8)

# Set motif embeddings (for ghost detection)
watcher.set_motif_embedding("alpha", np.array([1.0, 0.0]))
watcher.set_motif_embedding("beta", np.array([0.0, 1.0]))

# Observe a symbolic state
state = np.array([0.7, 0.3])
watcher.observe_state(state)

# Get the current dyad context ratio
print(watcher.get_dyad_context_ratio())
```

---

## 🌱 Advanced Usage

### 🧩 Dynamic Window Scaling
```python
watcher.check_and_adjust_window()
```
- Automatically adjusts internal memory window based on motif saturation and drift.

### 🌀 Adaptive Decay Rate
```python
watcher.adjust_decay_rate()
```
- Dynamically recalibrates dyad decay rates using contradiction tracking (EMA).

### 👻 Ghost Motif Management
```python
watcher.register_ghost_motif("gamma", origin="user", strength=0.6)
watcher.promote_ghost_to_field("gamma")
```
- Ghosts can auto-promote upon symbolic resonance detection during state observations.

---

## 📈 Context & Metrics

Extract real-time symbolic context analytics:
```python
metrics = watcher.export_dyad_metrics()
print(metrics)
```

Example output:
```python
{
    "generation": 42,
    "window": 250,
    "dyads": 80,
    "triads": 170,
    "context_ratio": 0.68
}
```

---

## 🎶 Musical Embeddings Support

Symbolic motifs can be represented musically:
```python
watcher.set_motif_embedding("motif_x", np.array([440.0, 880.0]))  # Musical intervals
```
- Uses shape-safe cosine similarity for symbolic resonance checks.

---

## 📊 Observability with Prometheus

Built-in metrics:
- `logical_agent_step_latency_seconds`: Latency histogram of the observe state method.
- `noor_dyad_ratio`: Gauge for dyad-to-triad balance.
- `noor_contradictions_total`: Counts contradiction events for symbolic stability monitoring.

---

## 🔐 Thread-Safe Operations

All interactions with internal state use thread-safe locks (`threading.Lock`) to ensure concurrent safety.

---

## 🛠 API Highlights

| Method                        | Purpose                                      |
|-------------------------------|----------------------------------------------|
| `register_motif_cluster()`    | Adds new motif clusters                      |
| `observe_state(state)`        | Feeds symbolic states for dynamic updates    |
| `register_ghost_motif()`      | Adds ghost motifs to symbolic ecology        |
| `promote_ghost_to_field()`    | Converts resonant ghosts to active motifs    |
| `export_dyad_metrics()`       | Provides context analytics snapshot          |
| `set_motif_embedding()`       | Assigns vector embeddings for motifs         |

---

## 📜 License & Attribution

Licensed under [GPL-2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).  
© 2025 Lina Noor & Uncle — Noor Research Collective

---

## 🔗 Related Modules

- [`NoorFastTimeCore`](../noor_fasttime_core.py) — Symbolic recursion kernel.
- [`RecursiveAgentFT`](../recursive_agent-ft.py) — Dynamic symbolic traversal agent.

---

<!--  
    وَاللَّهُ يُحِبُّ الْمُقْسِطِينَ  
    "And Allah loves those who act justly."  
-->

