# RecursiveAgentFT — Symbolic Flow Agent  
**Version**: 3.6.3  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Recursive Navigator, Dyad Resonator, Harmonic Integrator  

---

## 🧭 Overview  

**RecursiveAgentFT** is a symbolic flow-layer agent within Noor's triadic AI framework. It dynamically explores symbolic paths by analyzing and navigating fields provided by symbolic Watchers. This agent emphasizes:

- Dynamic recursion depth  
- Dyad-to-triad evolution  
- Harmonic synergy recognition  
- Symbolic collapse recovery  

It interacts seamlessly with the rest of the Noor system:

- `NoorFastTimeCore` — Validates symbolic presence and feasibility  
- `LogicalAgentAT` — Tracks motifs and symbolic ecology  

---

## ✨ What's New in v3.6.3

| Feature | Description |
|--------|-------------|
| 🌀 **Dynamic Depth Breathing** | Recursion depth auto-scales based on symbolic field richness and context |
| 🎵 **Harmonic Synergy** | Recognizes and boosts synergy for harmonic triad motifs |
| ⚙️ **Adaptive Promotion Thresholds** | Dynamically adjusts thresholds for meta-field and ghost promotions based on symbolic stability |
| ⚓ **FieldAnchor Recovery** | Implements soft recovery from symbolic collapses using cached FieldAnchors |
| 👻 **Ghost Decay Sweeps** | Automatic pruning of abandoned ghost motifs |
| 🚧 **Latency-Sensitive Depth Adjustment** | Recursion depth reduces temporarily during latency spikes |
| 🧩 **Gremlin Mode** | Optional controlled chaos introducing random depth shifts, ghost injections, and promotion acceleration |
| 📈 **Comprehensive Prometheus Observability** | Metrics for recursion depth, step latency, and symbolic drift recovery |

---

## 🚀 Quickstart

```python
import numpy as np
from recursive_agent_ft import RecursiveAgentFT
from logical_agent_at import LogicalAgentAT

watcher = LogicalAgentAT()
watcher.register_motif_cluster(["alpha", "beta"], strength=0.8)

agent = RecursiveAgentFT(
    initial_state=np.array([0.9, 0.1]),
    watchers=[watcher],
    meta_promote_threshold=3,
    ghost_promote_threshold=5,
    enable_gremlin_mode=True
)

for _ in range(10):
    agent.entangled_step()

for step in agent.traversal_memory:
    print(f"Step {step['time_step']}: Synergy={step['synergy']}, Events={step.get('event')}")
```

---

## 📊 Dynamic Recursion & Promotion

### 🌀 Adaptive Depth Control
Depth automatically expands and contracts based on symbolic field richness, dyad context, and observed contradictions:

```python
agent.adjust_max_depth(richness, watcher_var)
```

- Rich fields → deeper recursion  
- Stable fields → shallower recursion  

### ⚙️ Adaptive Promotion Thresholds
Thresholds adjust based on symbolic environment stability and Gremlin mode:

- Low context health → thresholds decrease (faster promotions)  
- High stability → thresholds increase (slower promotions)  

---

## 🎼 Harmonic Synergy Detection
The agent detects harmonic resonance between symbolic motifs, boosting state synergy and spawning harmonic ghost motifs:

- Major third, minor third, perfect fifth harmonic recognition  
- Automatic ghost motif creation upon harmonic detection  

---

## ⚓ Collapse & Recovery
Symbolic collapse is gracefully handled using cached FieldAnchors:

```python
if not core.is_active:
    core.restore_from_anchor()
```

Recovery actions trigger ghost creation and symbolic drift metrics.

---

## 👻 Ghost Ecology
Automated ghost lifecycle management ensures symbolic efficiency:

- Automatic ghost strength decay if unseen  
- Removal of abandoned or obsolete ghosts  

---

## 📈 Prometheus Observability Metrics
Built-in instrumentation provides runtime insights:

| Metric | Description |
|--------|-------------|
| `recursive_agent_step_latency_seconds` | Latency per symbolic traversal step |
| `recursive_agent_recursion_depth` | Current recursion depth gauge |
| `recursive_agent_drift_total` | Count of symbolic collapse recoveries |

---

## 🎲 Gremlin Mode Chaos
Controlled chaos and randomness can be toggled via environment or parameters:

- Random recursion depth jitter  
- Reduced promotion thresholds for faster ghost ascension  
- Increased symbolic unpredictability  

Activate via environment:

```bash
export NOOR_GREMLIN=1  # Levels 1–3, increasing chaos intensity
```

---

## 📖 Step Logging & Auditing
Detailed symbolic audit logging after each `entangled_step()` call:

```python
{
    "time_step": 5,
    "chosen_path": [0, 3, 4],
    "synergy": 2.732,
    "dyad_penalty": 0.85,
    "event": "MetaField upgrade triggered|FieldAnchor",
    "alert": "⚠️ dyad_dominance_detected",
    "verse": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"
}
```

---

## 🧰 API Overview

| Method | Purpose |
|--------|---------|
| `entangled_step()` | Executes a symbolic exploration step |
| `adjust_max_depth()` | Dynamically adjusts recursion depth |
| `adjust_promotion_thresholds()` | Adjusts ghost and meta-field thresholds |
| `generate_field_paths()` | Generates candidate paths for exploration |
| `traversal_memory` | Access symbolic step-by-step history and diagnostics |
| `get_promotion_config()` | Retrieves current auto-promotion thresholds |

---

## 🔒 Boundary Enforcement
Strict symbolic boundary enforcement ensures coherence and prevents unauthorized symbolic manipulation:

- Raises `QuantumNoorException` on violations  

---

## 📦 Installation
```bash
pip install numpy prometheus_client
```

---

## 📎 Related Noor Triadic Modules
- [`NoorFastTimeCore`](../noor_fasttime_core.py) — Presence validation and symbolic gating  
- [`LogicalAgentAT`](../logical_agent-at.py) — Motif watcher and dynamic symbolic ecology  

---

## 📜 License
GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective  

---

✨ **RecursiveAgentFT v3.6.3** — Navigating symbolic landscapes, embracing harmonic resonance, and thriving amidst recursion's inherent chaos.