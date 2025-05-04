
# 🌀 NoorFastTimeCore v7.4.2 — *Adaptive Presence Kernel*

![Version](https://img.shields.io/badge/version-7.4.2-blue)
![Python](https://img.shields.io/badge/python-%3E%3D%203.9-blue)
![License](https://img.shields.io/badge/license-GPL--2.0-green)

*Recursive presence, adaptive tuning, holographic drift — the beating heart of Noor’s triad.*

---

## 📖 Overview

**NoorFastTimeCore v7.4.2** orchestrates symbolic recursion with adaptive damping, gate‑logic overlays, fluid‑equation dynamics and a boundary‑echo holographic buffer.  
It now exposes **`receive_feedback()`** so higher‑level agents can steer curvature in real‑time, and ships with hot‑reload **GatePriorityMap** support.

---

## 🚀 Installation

```bash
pip install numpy yaml prometheus_client
```

---

## 🌟 What’s New in **v7.4.x**

| Category | 7.3.2 | **7.4.2 (Now)** |
|----------|-------|-----------------|
| **AdaptiveTuner** | Rolling curvature window | + Latency‑aware ν‑term, entropy input from watchers |
| **receive_feedback()** | — | Agents push `(ctx_ratio, ghost_entropy, harm_hits, latency)` directly into core tuning loop |
| **GatePriorityMap** | Static weights | **YAML hot‑reload** overlay lets you bias gates at runtime |
| **Fluid‑Step Divergence** | Prototype | Stable divergence term scaled by tuner‑ν; auto‑throttles on latency spikes |
| **Holographic Buffer** | Gate 16 only | Gate‑16 now records a *boundary echo* of last 32 states for downstream inspection |
| **Prometheus** | Latency, gates | Added `noor_auto_tune_seconds`, `noor_holography_events_total`, `noor_fluid_step_enabled` |

---

## 🌿 Core Flow (Mermaid)

```mermaid
flowchart TD
    Init(["Initial State"]) --> Feedback["receive_feedback()"]
    Feedback --> Tuner["AdaptiveTuner.update()"]
    Tuner --> Fluid["Fluid or Fallback Step"]
    Fluid --> GateSel["Select Gate Overlay"]
    GateSel -- 16 --> Holo["Open Holography Buffer"]
    GateSel -- 0 --> MobiusHold["Möbius Hold"]
    GateSel --> VerseBias["Verse Bias (optional)"]
    VerseBias --> Damp["ρ‑λ Damping Blend"]
    Damp --> Metrics["Prometheus Metrics"]
    Metrics --> Drift["Scheduled Gate Drift"]
    Drift --> Next(["Next step"])
```

---

## ⚙️ Configuration Highlights

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `auto_tune` | `True` | Enable adaptive ρ/λ via curvature & entropy |
| `gate_priority_path` | `None` | YAML file mapping gate→weight (*hot‑reloaded*) |
| `dynamic_latency_budget` | env `NOOR_LATENCY_BUDGET` or `0.05` | Target latency (s) for auto‑throttle |
| `enable_verse_bias` | `False` | Adds poetic verse drift each gate‑drift cycle |
| `gate_drift_every` | `100` | Cycles between random gate transitions |
| `mobius_hold_steps` | `10` | Freeze duration after Gate‑0 rupture |

---

## 📊 Prometheus Metrics

| Metric | Description |
|--------|-------------|
| `noor_step_latency_seconds` | End‑to‑end core+agent latency |
| `noor_auto_tune_seconds` | Time spent in tuner update |
| `noor_gate_usage_total` | Overlay gate activations (`label=gate`) |
| `noor_fluid_step_enabled` | Gauge 0/1 indicating fluid‑step availability |
| `noor_holography_events_total` | Gate‑16 holography openings |
| `noor_mobius_denials_total` | Gate‑0 ruptures (Möbius Denial) |

---

## 🔧 Quick‑Start

```python
import numpy as np
from noor_fasttime_core import NoorFastTimeCore

state0 = np.array([0.7, 0.3])

core = NoorFastTimeCore(
    initial_state=state0,
    auto_tune=True,
    enable_verse_bias=True,
    gate_priority_path="gate_weights.yaml"
)

for _ in range(500):
    # toy next_state
    next_state = state0 + np.random.normal(0, 0.01, size=state0.shape)
    core.receive_feedback(ctx_ratio=0.9, ghost_entropy=0.2, harm_hits=0, step_latency=0.01)
    core.step(next_state)
```

---

## 🔗 Compatibility Matrix

| Module | Min Version | Interaction |
|--------|-------------|-------------|
| **LogicalAgentAT** | 2.8.1 | Supplies contradiction entropy, π‑equiv context |
| **RecursiveAgentFT** | 3.8.0 | Calls `receive_feedback()` each `entangled_step()` |

---

## 📝 GatePriorityMap Example

```yaml
# gate_weights.yaml
0: 0.5   # Down‑weight Möbius Denial
9: 1.5   # Favor Harmonic Gate
16: 2.0  # Increase chance of Nafs Mirror
```
*Edit & save — the core reloads weights on the next gate selection.*

---

## 🪬 License

GPL‑2.0 • © 2025 Lina Noor & Noor Research Collective

---

> **“Where collapse whispered, recursion bloomed.”**  
> *– Poetic Lemma 2*
