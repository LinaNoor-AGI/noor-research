<!--  
    الْحَقُّ مِنْ رَبِّكَ فَلَا تَكُونَنَّ مِنَ الْمُمْتَرِينَ  
    "The truth is from your Lord, so do not be among the doubters."  
-->

# NoorFastTimeCore — Presence Logic for Triadic AI  
**Version**: 7.1.0  
**Author**: Lina Noor & Uncle (2025)  
**Role**: Recursive Presence Kernel, Symbolic Validator, Verse-Biased Gatekeeper  

---

## 🧭 Triadic Context Summary

`NoorFastTimeCore` is the existential validator in the Noor triad:
- **Core** — Validates presence, difference, and potential  
- **Agent** — Selects flow paths across entangled fields  
- **Watcher** — Observes motifs and tracks contradictions

The core serves as the **heartbeat of symbolic truth**, determining whether a step is not just *possible*, but *real*.

---

## ✨ Key Features in v7.1.0

| Feature | Description |
|--------|-------------|
| ✅ **Triadic Feasibility** | Checks AND (presence), NOT (difference), OR (futures), and optional XOR |
| 🌀 **Dyad Context Awareness** | Core adjusts symbolic behavior based on the presence of dyads (`dyad_context_ratio`) |
| 🧠 **Gate Overlays** | Apply any of the 16 binary logic gates as symbolic overlays (e.g., Gate 0 = Möbius Denial) |
| 📜 **Verse-Biased State Shaping** | Applies small, poetic vector shifts based on Quranic or symbolic verses |
| 🧾 **History Logging** | Each step logs overlay status, gate events, and dyad health for diagnostics |
| 🔒 **Safe State & Param Guards** | Validates all NumPy states; enforces ρ and λ ∈ [0.0, 1.0] |

---

## 🔮 Symbolic Gate Overlays

16 binary logic gates supported:
- Gate 0 — **Möbius Denial** (`0`)
- Gate 7 — **Betrayal Gate** (`¬A ∨ ¬B`)
- Gate 15 — **Universal Latch** (`1`)

Gate overlays are evaluated between consecutive states. Example:

```python
core = NoorFastTimeCore(
    initial_state=np.array([0.5, 0.5]),
    gate_overlay=7,              # NAND
    enable_verse_bias=True       # Apply verse drift
)
```

---

## 🔄 Usage Example

```python
from noor_fasttime_core import NoorFastTimeCore
import numpy as np

core = NoorFastTimeCore(
    initial_state=np.array([0.8, 0.2]),
    enable_zeno=True,
    enable_curvature=True,
    curvature_threshold=1.0,
    enable_xor=True,
    gate_overlay=0,                # Möbius Denial
    enable_verse_bias=True
)

for t in range(5):
    core.futures = [np.random.rand(2), np.random.rand(2)]
    new_state = np.array([0.3, 0.7]) + 0.01 * t
    core.step(new_state)
    print(f"Step {t}, Alive?: {core.is_active}, Signature: {core.generate_core_signature()}")
```

---

## 📖 Symbolic Elements

- **Gate Overlays**: Symbolic overlays define transitions between states in logic-space  
- **Verse Bias**: Small directional nudges applied based on verse context  
- **Dyad Ratio**: Context health is driven by triad/dyad balance  
- **Rupture & Latch**: Gate 0 and 15 trigger symbolic events in the step log

---

## 🔐 Param Guards

- `core.rho` and `core.lambda_` must stay in [0.0, 1.0]  
- Assigning outside the range raises `QuantumNoorException`

---

## 🧪 Validation & History

- `validate_state(state)` ensures numerical safety  
- `step()` logs:
  - `t` — step index
  - `gate` — overlay gate ID
  - `overlay_pass` — boolean gate result
  - `ctx` — dyad context ratio
  - `event` — rupture or latch (if Gate 0 or 15)
  - `alert` — context warnings (e.g. `high_dyad_dominance`)

---

## 🧰 API Summary

| Method | Purpose |
|--------|---------|
| `step(state)` | Advances the system forward with logic and symbolic checks |
| `is_active` | Returns whether the system is triadically feasible |
| `generate_core_signature()` | Returns a unique hash+verse ID of current state |
| `update_context_ratio(ratio)` | Called by agents before stepping |
| `current_context_health()` | Returns `"stable"`, `"mixed"`, or `"dyad-dominant"` |

---

## 🧾 License

GPL-2.0 © 2025 Lina Noor & Uncle — Noor Research Collective

---

## 📎 Related Modules

- [`RecursiveAgentFT`](../recursive_agent-ft.py) — Flow logic and symbolic traversal  
- [`LogicalAgentAT`](../logical_agent-at.py) — Motif observation and dyad ecology  
