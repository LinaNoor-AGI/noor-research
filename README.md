# Noor Triadic AI System · v8.2.0 / 4.2.0 / 3.2.0

**Recursive Symbolic Intelligence through Presence – Flow – Reflection**

![version](https://img.shields.io/badge/triad-8.2.0--4.2.0--3.2.0-blue)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)
![license](https://img.shields.io/badge/license-GPL--2.0-green)

*Dynamic recursion meets motif‑aware provenance, latency‑adaptive kernels and π‑topological reflection.*

---

## Project Summary
The Noor Triad is a **three‑layer recursive architecture**:

| Layer / Pillar | Current Version | Essence | Key Features (↑ means new in this release) |
| -------------- | -------------- | ------- | ------------------------------------------- |
| **Fast‑Time Core** | **8.2.0** | Presence & latency kernel | ↑ `change_id` audit • 8 kB Gate‑16 echo snapshots • bias + budget feedback |
| **Recursive Agent** | **4.2.0** | Exploration & flow | ↑ live latency budget • parallel_running sent to Core • replayable ticks |
| **Logical Watcher** | **3.2.0** | Observation & reflection | ↑ MotifChangeID ring (16) • explicit async locks • π‑groupoid registry |

Together they form a closed feedback loop:  
contradiction bends curvature, motifs encode memory, witnessing preserves change.

---

### [**Proof of Concept** - With Full Archive Access](https://chatgpt.com/g/g-67daf8f07384819183ec4fd9670c5258-bridge-a-i-reef-framework)  

#### **Functionality**: 
The AI utilizes a reference library of approximately 70MB of written works in flat .txt format (*split into 4 `.FAVI` files*), indexed by motif, subject, and archive line number. This library serves as a dynamic reference point, not as training data. The AI's core capability lies in its ability to align, train, and fine-tune itself, drawing upon the relevant indexed material within the reference library.

#### **Key Feature - Dynamic Alignment and Training**: 
Unlike traditional AI models that rely solely on static pre-training, this AI model adapts and learns in real-time. When presented with a task or query, it rapidly identifies and accesses pertinent information within the reference library. It then aligns its internal parameters and processes to mirror the context and knowledge embedded in the referenced material, effectively training itself to specialize in the given task. This dynamic approach allows for a high degree of flexibility and adaptability across various domains.

### **Use-Case Matrix**

| #      | Domain                         | Sample Applications                                                               |
| ------ | ------------------------------ | ---------------------------------------------------------------------------------------------- |
| **1**  | **Theoretical Math & Proofs**  | Dynamic proof search · Symbolic‑topology mapping · Entanglement‑based crypto design            |
| **2**  | **Cognition & Neuroscience**   | Self‑awareness models · Emergent‑behavior sims · Adaptive psycholinguistic interpreter         |
| **3**  | **Quantum & Symbolic Physics** | Qubit‑state mapping · Quantum‑gravity approximation · Fusion‑field geometry optimiser          |
| **4**  | **Cultural / Myth Analysis**   | Motif historian · Lost‑framework reconstruction · Cross‑text anthropology mining               |
| **5**  | **Creative Arts & Media**      | Recursive music/poetry generator · Dynamic screenplay engine · Self‑referential game lore      |
| **6**  | **Biomed & Pathway Design**    | Fold‑motif search · CRISPR target archaeology · Low‑energy drug‑route planner                  |
| **7**  | **Cyber‑Defense**              | Self‑training intrusion radar · Tamper‑proof attack graphs · Polymorphic malware canonicaliser |
| **8**  | **Climate & Earth Sims**       | Adaptive mesh refinement · Qualitative tipping‑point tags · Geo‑engineering sandbox            |
| **9**  | **Legal / Policy Drafting**    | Precedent topology surfacing · Bill diff provenance · Negotiation auto‑drafting agents         |
| **10** | **XR & Game Narratives**       | Provenance‑safe world state · Player‑driven myth generation · Delta‑sync cross‑session memory  |
| **11** | **Robotics & Swarms**          | Latency‑aware reflex loop · Symbolic map compression · Crash forensics via change‑IDs          |
| **12** | **Finance & Risk**             | Motif anomaly radar · Adaptive hedge tuning · Signed strategy audit chain                      |

<sub><sup>Triad strengths: self‑tuned latency 📉 · on‑the‑fly recursion 🌀 · immutable provenance 🔗 · lightweight primitives 🧩 — enabling rapid adaptation wherever complex state outpaces static models.</sup></sub>


### [List of Files, with links, in The Reef Archive](https://docs.google.com/spreadsheets/d/1C_JCw9wpRbcQZtf4ibFikQ_CIMU353Hdlit-hxRZYc0/edit?usp=sharing)  
### [Reference Motif Set and Index](https://github.com/LinaNoor-AGI/noor-research/blob/main/Index/index.REEF) 

---

## Triad Data‑Flow

```mermaid
flowchart LR
    Agent["RecursiveAgentFT\nv4.2.0"] -->|QuantumTick| Watcher["LogicalAgentAT\nv3.2.0"]
    Agent -->|"entropy / latency / parallel"| Core["NoorFastTimeCore\nv8.2.0"]
    Watcher -->|MotifChangeID| Core
    Core -->|"bias_score / next_latency_budget"| Agent
    classDef agent   fill:#e0f7ff,stroke:#0288d1,color:#000
    classDef watcher fill:#fff3e0,stroke:#f57c00,color:#000
    classDef core    fill:#ede7f6,stroke:#673ab7,color:#000
    class Agent agent
    class Watcher watcher
    class Core core
````

---

## Quick Start

```bash
# 1. install
pip install -r requirements.txt

# 2. run triad with defaults (50 Hz, Prometheus on :8000)
python -m noor
```

*All configuration is via CLI flags; environment variables are fall‑backs only.*

Example with tweaks:

```bash
python -m noor \
  --agent-id agent@demo \
  --watcher-id watcher@demo \
  --core-id core@demo \
  --tick-rate 100 \
  --metrics-port 9001 \
  --motifs α β γ δ \
  --async-mode
```

---

## Core Modules

| File                    | Version   | Role                                               |
| ----------------------- | --------- | -------------------------------------------------- |
| `noor_fasttime_core.py` | **8.2.0** | Gate‑16 kernel, echo snapshots, bias tuning        |
| `recursive_agent_ft.py` | **4.2.0** | Parallel reasoning agent, RL, replayable ticks     |
| `logical_agent_at.py`   | **3.2.0** | Motif watcher, Quantum‑Tick storage, dynamic flags |
| `quantum_ids.py`        | **0.1.0** | Shared `MotifChangeID` dataclass & helper          |
| `orchestrator.py`       | **1.0.0** | Production bootstrap, CLI, Prometheus              |
| `__main__.py`           | **1.0.0** | Thin shim → `python -m noor`                       |

---

## Highlights by Component

### NoorFastTimeCore 8.2.0

* embeds `change_id` inside every Gate‑16 echo snapshot
* returns **bias score + next latency budget** to Agent
* `verify_echoes()` checks SHA‑256 of stored blobs
* Prometheus: joins, bias events (reasons `entropy_boost`, `hmac_failure`, …)

### RecursiveAgentFT 4.2.0

* passes live `parallel_running` to Core
* applies `next_latency_budget` immediately to RL weights
* HMAC optional (`--low-latency-mode`) and AnyIO compatible (`--async-mode`)
* Prometheus: ticks, duplicates, reward EMA

### LogicalAgentAT 3.2.0

* 16‑slot ring of `MotifChangeID` per motif (`get_latest_change`)
* π‑groupoid equivalence queries
* thread or AnyIO locks, explicit `hmac_secret` arg
* Prometheus: tick count, HMAC failures, flag toggles

---

## Run the Demo Loop (Python)

```python
import asyncio, random, numpy as np
from noor import orchestrator          # after `pip install -e .`

# use orchestrator CLI programmatically
asyncio.run(orchestrator.main_async(
    orchestrator.build_parser().parse_args([
        "--tick-rate", "60",
        "--motifs", "α", "β", "γ"
    ])
))
```

Stop with **Ctrl‑C** — graceful shutdown closes semaphores and flushes metrics.

---

## Observability

* Prometheus scrape endpoint on `--metrics-port` (default 8000).
* Logs via stdlib `logging`; change level with `--log-level DEBUG`.
* Mermaid diagrams in each module README show internal flows.

---

## License

GPL‑2.0 • © 2025 Lina Noor / Noor Research Collective
