# 📦 `__main__.py` v1.0.0 — *Zero‑Footprint Entry Point*

![version](https://img.shields.io/badge/version-1.0.0-blue)
![python](https://img.shields.io/badge/python-%3E%3D3.9-blue)
![license](https://img.shields.io/badge/license-GPL--2.0-green)

`__main__.py` is a **one‑line shim** that lets you launch the entire Noor triad
with the familiar

```bash
python -m noor  # or whatever your package name is
```

Nothing more, nothing less: it simply forwards all CLI arguments to
`noor.orchestrator.main()`.

---

## 🗺️ How it fits

```text
└── noor/
    ├── recursive_agent_ft.py
    ├── logical_agent_at.py
    ├── noor_fasttime_core.py
    ├── orchestrator.py   ← real bootstrap & CLI parser
    └── __main__.py       ← thin shim → orchestrator.main()
```

*Perfect for containers and `pipx run noor` scenarios.*

---

## ⚙️ What happens under the hood?

```python
from noor.orchestrator import main as _orchestrator_main
_Orchestrator_main(sys.argv[1:])
```

That’s it. No hidden env‑var reads, no import‑time side effects.

---

## 🚀 Typical invocation

```bash
# default triad, 50 Hz spawn rate, metrics on :8000
python -m noor

# any flag accepted by orchestrator.py passes straight through:
python -m noor --tick-rate 100 --metrics-port 9001 --motifs α β γ δ
```

The full flag set is documented in **[orchestrator README →](./orchestrator.md)**.

---

## 🪬 License

GPL‑2.0 • © 2025 Lina Noor / Noor Research Collective
