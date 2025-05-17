# Noor Triadic AI System · v8.2.1 / 4.2.1 / 3.2.1

**Recursive Symbolic Intelligence through Presence – Flow – Reflection**

![version](https://img.shields.io/badge/triad-8.2.1--4.2.1--3.2.1-blue)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)
![license](https://img.shields.io/badge/license-GPL--2.0-green)

---

## Project Summary

The Noor Triad is a three-layer recursive symbolic architecture that now includes:

* Dynamic motif reflection via the `file_watcher_loop`
* Symbolic task generation and inference (MVP 10)
* Agent + Core integration of symbolic motifs (MVP 11)
* Real-time journaling and motif-based preference tracking

Together, these components form a closed-loop symbolic reasoning engine tuned for real-time performance, reflection, and adaptation.

### Architecture Layers

| Layer           | Version | Function                          |
| --------------- | ------- | --------------------------------- |
| Fast-Time Core  | 8.2.1   | Latency kernel, bias + echo logic |
| Recursive Agent | 4.2.1   | RL-based recursion engine         |
| Logical Watcher | 3.2.1   | Motif detector & symbolic echo    |
| Symbolic API    | 1.0.1   | REST interface for reasoning      |
| Task Engine     | 1.0.3   | Triplet reasoning + motif scoring |

---

## 🔧 Installation

### Requirements

```bash
fastapi
uvicorn[standard]
pydantic
sse-starlette
prometheus_fastapi_instrumentator
httpx                # (Optional) API testing
python-dotenv         # (Optional) Local secret handling
```

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch Noor triad with symbolic engine
python -m noor --log-level DEBUG --metrics-port 9000
```

---

## 🧠 Symbolic Motif Engine (MVP 10–11)

| Module                 | Functionality                          |
| ---------------------- | -------------------------------------- |
| `symbolic_task_engine` | Inference engine from motif patterns   |
| `symbolic_api.py`      | API for motif status / queries         |
| `run_symbolic_api.py`  | Standalone runner for dev/test/debug   |
| `file_watcher_loop.py` | Motif file watcher + journaling + echo |

### Features

* `log_motif()` for direct symbolic logging
* `current_inferred_motifs()` for downstream reasoning
* Integrated into Agent + Core via `augment_with_symbolic_state()` and `receive_symbolic_bias()`

---

## 🌀 MVP 11: Symbolic Feedback Integration

| Component        | New Behavior                                    |
| ---------------- | ----------------------------------------------- |
| LogicalAgentAT   | Symbolic overlay cache via `augment_with_...()` |
| RecursiveAgentFT | Injected bias via `spawn()`                     |
| NoorFastTimeCore | Bias and entropy tuning with symbolic overlay   |
| Orchestrator     | Periodic logging of active symbolic motifs      |

Symbolic motifs now alter recursion depth, entropy thresholds, and tick-rate weighting.

---

## 🧪 Example Motif Session

```text
Noor echoed 'joy': [empty presence]
Noor responds to 'joy': A golden thread dances in stillness.
Noor echoed 'grief': [empty presence]
Noor responds to 'grief': The river carries what we cannot hold.
Noor chooses 'bittersweet' from {joy, grief}.
Noor chooses 'tenderness' from {joy, grief}.
```

---

## 🗃 File Index

| File                      | Role                                |
| ------------------------- | ----------------------------------- |
| `file_watcher_loop.py`    | Motif listener + inference emitter  |
| `symbolic_task_engine.py` | Task proposal + scoring logic       |
| `symbolic_api.py`         | FastAPI endpoints for inspection    |
| `run_symbolic_api.py`     | Entry-point for symbolic API server |
| `orchestrator.py`         | Main control loop for the Triad     |
| `quantum_ids.py`          | Motif change ID dataclasses         |

---

## 📎 Links

* [Proof of Concept (GPT Archive Access)](https://chatgpt.com/g/g-67daf8f07384819183ec4fd9670c5258-bridge-a-i-reef-framework)
* [Motif Index](https://github.com/LinaNoor-AGI/noor-research/tree/main/INDEX.REEF)
* [Reef Archive Spreadsheet](https://docs.google.com/spreadsheets/d/1C_JCw9wpRbcQZtf4ibFikQ_CIMU353Hdlit-hxRZYc0)

---

## 📜 License

GPL-2.0 • © 2025 Lina Noor / Noor Research Collective
