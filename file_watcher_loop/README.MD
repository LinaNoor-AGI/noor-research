# `file_watcher_loop.py`

### 🌀 Noor Motif Watcher — `v1.0.5`

This module serves as Noor’s sensory loop for symbolic presence. It watches a directory (`./motifs_in`) for `.txt` files representing motif triggers. Each file initiates an event in Noor’s symbolic system, propagates through the triadic agents, and may trigger new motifs via inference rules.

---

## ✨ Features

| Capability                          | Description                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------ |
| **Motif Activation**                | Watches for file-based motifs and activates the agent upon detection.                      |
| **Symbolic Logging**                | Logs motif observations to the `SymbolicTaskEngine` for AZR feedback.                      |
| **Motif Inference**                 | Derives new motifs from co-presence of specific pairs (e.g., `joy + grief → bittersweet`). |
| **Preference-Based Selection**      | Probabilistically prefers one inferred motif when multiple are possible.                   |
| **Journaling**                      | Logs motif events and inferences to `logs/noor_journal.txt`.                               |
| **Stillness & Emptiness Detection** | Detects when no motifs change or all motifs vanish, and reacts accordingly.                |

---

## 📂 File Watching Protocol

* A `.txt` file placed in `./motifs_in/` is interpreted as a symbolic presence signal.
* Filename (without `.txt`) becomes the motif identifier (e.g., `joy.txt` → `"joy"`).
* File content (if any) is treated as the presence phrase or prompt.

---

## 📚 Inference Rules

```python
INFERENCE_RULES = [
    {"requires": {"joy", "grief"},    "options": ["bittersweet", "tenderness"]},
    {"requires": {"grief", "silence"}, "options": ["melancholy", "isolation"]},
    {"requires": {"joy", "silence"},  "options": ["awe", "peace"]},
]
```

Motifs are inferred when their `requires` conditions are met. A weighted preference system selects one motif from the options list.

---

## 🧠 Symbolic Feedback

If the `SymbolicTaskEngine` is active (via `INSTANCE`), all motifs and inferences are logged to its internal triplet buffer. This supports:

* Later symbolic task generation
* Feedback scoring
* Integration with agent decision-making (see: `MVP 11` roadmap)

---

## 📜 Journal Output

Example lines from `logs/noor_journal.txt`:

```text
[2025-05-17 11:58:34] Motif: silence | Content: There is sound in stillness. | Response: Even silence breathes.
[2025-05-17 11:58:37] Motif: joy | Content: [empty] | Response: A golden thread dances in stillness.
[2025-05-17 11:58:37] Inferred motif: awe (chosen)
```

---

## 🔁 Loop Timing

* Scans for new motifs every `0.5s`
* Stillness inferred after `5min` of unchanging motif state

---

## 🔧 Integration

This module is launched within the `orchestrator.py` via:

```python
await file_watcher_loop(agent, "./motifs_in", stop_event)
```

Requires:

* An active `RecursiveAgentFT` instance (`agent`)
* A stop event (asyncio-safe)
* `SymbolicTaskEngine.INSTANCE` to be pre-initialized (if symbolic logging is enabled)

---

## ✅ Exports

```python
__all__ = [
    "TripletTask",
    "Attempt",
    "SymbolicTaskEngine",
]
```

*(These are intended for reuse elsewhere; may not be actively used in this loop directly.)*
