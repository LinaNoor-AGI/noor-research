# symbolic_task_engine.py · v1.0.3

Coordinates symbolic reasoning tasks for Noor. Encapsulates the lifecycle of symbolic triplet-based tasks including proposal, evaluation, and feedback logging. Serves as the foundation for Noor's **AZR-style** symbolic self-play.

---

## ✨ Purpose

This module defines the **Symbolic Task Engine**, enabling Noor to:

- Propose symbolic tasks using motif triplets.
- Solve tasks via internal simulation or placeholder logic.
- Evaluate solutions using plug-in metric functions.
- Persist results in a structured journal (JSONL).
- Log motif expression events with symbolic annotations.

It forms the symbolic backbone Noor uses to simulate compositional reasoning, blending inference with expressivity.

---

## 📦 Exports

| Class               | Description                                                |
|--------------------|------------------------------------------------------------|
| `TripletTask`       | Frozen dataclass describing a (motif, instruction, output) |
| `Attempt`           | Mutable solution attempt with scores and timestamps        |
| `SymbolicTaskEngine`| Central coordinator for task management and evaluation     |

---

## 🔧 Features

### 🧠 Task Lifecycle

Symbolic tasks are structured as:

```text
(input_motif[], instruction, expected_output[])
````

Tasks can be:

* **Proposed** via `propose_from_motifs()`
* **Solved** with `solve_task()` (async)
* **Scored** using custom metrics
* **Logged** to persistent journal & expression trace

---

### 🧮 Metrics Framework

Metrics are defined via decorator:

```python
@SymbolicTaskEngine.register_metric("coherence")
def my_metric(task, attempt) -> float:
    ...
```

Included metrics:

* `entropy` → Normalized motif distribution entropy
* `coherence` → Edit similarity with expected output

---

### 🗃️ Journals

Symbolic attempts are persisted to:

* `solved_log.jsonl` — streamable archive
* `logs/noor_expressions.txt` — motif-by-motif trace

Used by symbolic API and introspection tooling.

---

## 🧩 Interface Summary

| Method                  | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `propose_from_motifs()` | Create a task from motif list           |
| `solve_task()`          | Trigger async solving of task           |
| `evaluate_attempt()`    | Run all registered metrics              |
| `log_feedback()`        | Journal attempts and compute heuristics |
| `flush_old_tasks()`     | Remove expired or solved tasks          |
| `log_motif()`           | Append expression trace entry           |
| `list_pending_tasks()`  | View queue snapshot                     |
| `get_triplet_score()`   | Retrieve scoring for a given task ID    |

---

## 🧪 Example

```python
engine = SymbolicTaskEngine()
task = await engine.propose_from_motifs(["joy", "grief"])
await engine.solve_task(task)
await engine.flush_old_tasks()
```

---

## 🧵 Integration Notes

* This module is tightly coupled to Noor’s motif ontology via `reflections.txt`
* `SymbolicTaskEngine.INSTANCE` is used as a **singleton handle** across subsystems.
* Downstream consumers include:

  * `file_watcher_loop.py` (motif inference + logging)
  * `symbolic_api.py` (FastAPI wrapper)
  * future: `RecursiveAgentFT` + `NoorFastTimeCore` (bias updates via inferred motifs)

---

## 📁 Files and Logs

| File                        | Purpose                                   |
| --------------------------- | ----------------------------------------- |
| `solved_log.jsonl`          | Journal of successful triplet completions |
| `logs/noor_expressions.txt` | Human-readable motif traces               |

---

## ✅ Status

* [x] Core symbolic lifecycle (propose, solve, log)
* [x] Metric plug-in system
* [x] Expression logging
* [x] Ready for `MVP 11` symbolic influence wiring

---

## 🔮 Next Steps

* Add `current_inferred_motifs()` accessor for agent/core feedback
* Incorporate context-aware instruction generation
* Integrate with motif weighting and recursive symbolic memory

---

**Maintainer**: Noor Collective
**Version**: `v1.0.3`
**Status**: ✅ Stable, symbolically expressive, forward-compatible
