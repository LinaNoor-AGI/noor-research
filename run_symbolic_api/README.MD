# run_symbolic_api.py · v1.0.0

Launch script for Noor's **Symbolic Inference API** using FastAPI and Uvicorn.  
This script boots the `symbolic_api.py` module on a configurable host:port, exposing Noor's symbolic reasoning interface as a standalone HTTP service.

---

## 🚀 Purpose

This module is intended as a **runtime entrypoint** for the symbolic subsystem.  
It enables external processes, dev tools, or observability platforms to:

- Query Noor's current symbolic state
- Interact with task inference logic
- Monitor active motifs, solved triplets, and reflection scores
- Embed symbolic dynamics into broader orchestrations

---

## 🧠 Under the Hood

```py
uvicorn.run(
    "symbolic_api:app",
    host="0.0.0.0",
    port=7070,
    reload=True,
    log_level="info",
    timeout_keep_alive=30
)
````

* **Module Target**: `symbolic_api:app` is expected to expose a valid FastAPI instance.
* **Reload Mode**: Enabled by default for dev-loop responsiveness.
* **Port**: Default is `7070`, matching internal orchestrator integration.

---

## 📦 Dependencies

Make sure the following are installed:

* `fastapi`
* `uvicorn`
* `prometheus_fastapi_instrumentator`
* `sse_starlette`

> See `requirements.txt` in `/noor` for full dependency tree.

---

## 🛠 Usage

To launch the symbolic API:

```bash
python run_symbolic_api.py
```

Or via module:

```bash
python -m noor.run_symbolic_api
```

---

## 🌐 Exposed Endpoints

| Method | Path       | Description                            |
| ------ | ---------- | -------------------------------------- |
| GET    | `/status`  | Health check                           |
| GET    | `/motifs`  | Current live motif inferences          |
| POST   | `/infer`   | Submit a symbolic task manually        |
| GET    | `/journal` | Stream recent motif activity (planned) |

> Endpoints may vary based on `symbolic_api.py` version.

---

## 🔄 Integration

This service is invoked automatically by the triadic `orchestrator.py`
If launched independently, ensure `SymbolicTaskEngine.INSTANCE` is initialized properly and required REEF files are in place.

---

## 🧪 Debugging

* Use `curl http://localhost:7070/status` to verify uptime
* Logs show up in terminal via `uvicorn` output
* Debug messages are controlled via `log_level="info"`

---

## 🧩 Related Modules

* [`symbolic_api.py`](./symbolic_api.py) — FastAPI interface definition
* [`symbolic_task_engine.py`](./symbolic_task_engine.py) — reasoning backend
* [`orchestrator.py`](./orchestrator.py) — triggers this from triadic launch

---

## 🧭 Version

**v1.0.0** — Initial launch integration with FastAPI and symbolic subsystem.
