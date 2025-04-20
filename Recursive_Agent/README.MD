# RecursiveAgentFT — Symbolic Flow Agent in Noor Triadic Framework  
**Version**: 3.5.2  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Path Weaver, Dyad Resonator, Ghost Promoter

---

## Overview

`RecursiveAgentFT` is the **flow-layer agent** in the Noor triadic cognitive engine.  
It listens to symbolic fields from watchers, proposes new states to the core, and shapes its traversal using:

- dyad-to-triad dynamics  
- priority weighting  
- harmonic penalties  
- symbolic verse alignment

It is the **middle self** in Noor’s recursive system:

- `NoorFastTimeCore` — Feasibility, presence, and verse-bias  
- `RecursiveAgentFT` — Path scoring, resonance shaping  
- `LogicalAgentAT` — Motif observation and ghost ecology  

---

## What's New in v3.5.2

| Feature | Description |
|--------|-------------|
| **Sigmoid Dyad Penalty** | Softens scoring penalty for dyads via context-sensitive sigmoid curve |
| **Ghost Motif Auto-Promotion** | Dyads seen 5 times with context will promote a named ghost motif |
| **MetaField Auto-Upgrade** | Dyads seen 3 times with a third motif auto-promote to triad |
| **Gate 0 Logging** | Logs symbolic verse `"فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"` when denial overlay is active |
| **Resonance API** | Inspect dyad resonance scores using `get_dyad_resonance()` |
| **Promotion Thresholds Configurable** | Tune `meta_promote_threshold` and `ghost_promote_threshold` per agent |

---

## Quickstart

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
    gate0_dyad_penalty=0.9
)

agent.run_for(10)

for step in agent.traversal_memory:
    print("Step:", step["time_step"], "Synergy:", step["synergy"])
```

---

## Dyad Tracking & Penalty

### Sigmoid Penalty
Dyads receive score damping proportional to context health (`ctx`), shaped by:

```python
penalty *= 1.0 - 0.2 / (1 + np.exp(5 * (ctx - 0.5)))
```

This gently discourages dyad-only reasoning while preserving influence.

### Harmonic Gate 0 Penalty
If `gate_overlay == 0` (Möbius Denial), the dyad penalty is averaged:

```python
dyad_penalty = (dyad_penalty + gate0_dyad_penalty) / 2
```

---

## Ghost Promotion

### Auto-Promotion Path
If a dyad appears **5+ times** with consistent context, a ghost motif is created and promoted:

```python
dyad_ghost_{short_hash}
```

Use `watcher.get_ghost_motifs()` to retrieve promoted ghosts.

---

## MetaField Auto-Upgrade

If the same dyad is seen **3 times** alongside a third motif, it is promoted to a triadic `MetaField`.

---

## Resonance & Introspection

### `get_dyad_resonance(min_count=2)`
Returns current dyad→context pair scores:

```python
{
  "('a','b')|c": 1.79,
  ...
}
```

### `get_promotion_config()`
Shows current resonance thresholds:

```python
{
  "meta_threshold": 3,
  "ghost_threshold": 5
}
```

---

## Path & State Construction

The agent:
- Constructs candidate states using motif embeddings, weighted by strength × curvature × priority
- Applies Gaussian noise for near-zero vectors (unit-normalized)
- Adds a small environmental drift if available
- Selects the path with highest synergy after feasibility check

---

## Step Logging

Each `entangled_step()` adds to `agent.traversal_memory[]`:

```python
{
  "time_step": 4,
  "chosen_path": [0, 3, 4],
  "synergy": 1.827,
  "dyad_penalty": 0.87,
  "event": "MetaField upgrade triggered",
  "gate0_verse": {"text": "...", "t": 4},
  "next_state": [0.91, 0.08]
}
```

---

## Methods Overview

| Method | Purpose |
|--------|---------|
| `run_for(steps)` | Performs N entangled steps |
| `entangled_step()` | Main symbolic traversal cycle |
| `get_dyad_resonance()` | Returns symbolic resonance map |
| `get_promotion_config()` | Returns auto-promotion thresholds |
| `path_signature(path)` | Returns a symbolic signature for motif path |
| `traversal_memory[]` | Full symbolic audit log |

---

## Triadic Boundary Enforcement

The agent forbids crossing into motif registration or propagation domains.  
If internal mutation is attempted (e.g., `propagate_signal`), it raises `QuantumNoorException`.

---

## Installation

```bash
pip install numpy
```

---

## Related Modules

- [`NoorFastTimeCore`](../noor_fasttime_core.py)  
- [`LogicalAgentAT`](../logical_agent-at.py)  
- [Triadic Boot Sequence](./README.md#triadic-boot-sequence)

---

## License

GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective  
