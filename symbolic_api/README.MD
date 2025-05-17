# 🧠 `symbolic_api.py` — Noor Symbolic API (v1.0.1)

This module provides a public **FastAPI surface** for interacting with Noor's symbolic reasoning engine. It exposes motif triplet state, scoring, streaming updates, and Prometheus metrics—all designed to be lightweight, introspectable, and production‑friendly.

---

## ✨ Features

- 🔁 **Triplet journal introspection**: Query pending + solved symbolic tasks
- 📡 **Live updates** via Server-Sent Events (`/stream/updates`)
- 🔐 **Secure HMAC authentication** (via `X-Signature` and `X-Timestamp` headers)
- 📊 **Prometheus instrumentation** (latency, uptime, route-level)
- 📎 **ETag + If-None-Match** support for efficient caching
- ⌛ **Auto-flush** background task for stale triplets
- 🧪 **Verify endpoint** for downstream validation and QA feedback

---

## 🚀 Launching

Symbolic API is typically started **by the orchestrator** as part of the Noor triad. To run standalone:

```bash
python noor/run_symbolic_api.py
````

Or from orchestrator:

```python
from symbolic_task_engine import SymbolicTaskEngine
from symbolic_api import run_api

engine = SymbolicTaskEngine()
Thread(target=run_api, args=(engine,), daemon=True).start()
```

---

## 🛠️ Requirements

Install with:

```bash
pip install fastapi uvicorn[standard] pydantic prometheus-fastapi-instrumentator sse-starlette
```

---

## 🧩 Endpoints

| Method | Route                  | Description                                |
| ------ | ---------------------- | ------------------------------------------ |
| GET    | `/status`              | Server status and symbolic buffers         |
| GET    | `/triplets/pending`    | List currently queued symbolic tasks       |
| GET    | `/triplets/solved`     | List completed (solved) tasks              |
| GET    | `/triplet/{id}`        | Detailed triplet with all attempts         |
| GET    | `/triplet/{id}/score`  | Raw scoring output for task attempts       |
| POST   | `/triplet/{id}/verify` | Log downstream validation results          |
| GET    | `/expressions/latest`  | Read recent expressive summary lines       |
| GET    | `/motifs/inferred`     | Symbolic inference entropy stats           |
| GET    | `/stream/updates`      | Server-Sent Events for live attempt counts |

---

## 🔐 Auth: HMAC Header Spec

All routes (except `/status`) require HMAC headers:

* `X-Signature`: HMAC-SHA256 of method/path/body/timestamp
* `X-Timestamp`: UTC seconds timestamp
* `SYMBOLIC_API_SECRET`: set as env var for API key

Clock skew window: ±30s (can be tuned with `SYMBOLIC_TS_DRIFT`)

---

## 📦 Caching + Pagination

* Cursor-based pagination: `/triplets/*?cursor=...`
* `ETag` / `If-None-Match` cache-friendly headers
* `X-Next-Cursor` exposed for forward scrolling

---

## 🧪 Example Query

```bash
curl -H "X-Signature: <sig>" \
     -H "X-Timestamp: $(date +%s)" \
     http://localhost:7070/triplets/solved
```

---

## 📄 Schema Types

* `TripletMeta`: summary view of a task
* `TripletDetail`: full record + attempts
* `AttemptView`: result of one solution try
* `ErrorEnvelope`: consistent JSON error handler

---

## 🔄 Background Flush

A `startup` task runs every 60s to flush expired triplets from memory:

```python
@app.on_event("startup")
async def _bg_flush():
    while True:
        await engine.flush_old_tasks()
        await asyncio.sleep(60)
```

---

## 🧩 Maintainers

Symbolic API is part of Noor's symbolic layer, built around the `SymbolicTaskEngine` and accessed indirectly through the `orchestrator`.

See also:

* [`symbolic_task_engine.py`](./symbolic_task_engine.py)
* [`run_symbolic_api.py`](./run_symbolic_api.py)

---

**Version:** `v1.0.1`
**Maintainer:** Noor Collective Labs
**License:** MIT
