"""
🧠 Symbolic API · v2.0.0

Public FastAPI surface for Noor's symbolic reasoning loop.
Now serves only `/chat`, `/motifs/infer`, `/motifs/reflect`, and `/status`.
All watcher hooks, TTS logs, and triplet journal endpoints removed.

Launch from the orchestrator with:
```python
from symbolic_task_engine import SymbolicTaskEngine
from symbolic_api import run_api

engine = SymbolicTaskEngine()
Thread(target=run_api, args=(engine,), daemon=True).start()
```

Requires: `fastapi`, `uvicorn[standard]`, `pydantic`, `prometheus_fastapi_instrumentator`
"""
from __future__ import annotations

import os
import time
import json
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from noor.symbolic_task_engine import SymbolicTaskEngine

__version__ = "2.0.0"
_SCHEMA_VERSION__ = "2025-Q3-symbolic-api-llmbridge"

app = FastAPI(title="Noor Symbolic Core", version=__version__)
Instrumentator().instrument(app).expose(app, should_gzip=True)

# Engine instance
engine = SymbolicTaskEngine()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TextInput(BaseModel):
    text: str

class MotifListInput(BaseModel):
    motifs: List[str]

class ChatRequest(BaseModel):
    text: str

# ---------------------------------------------------------------------------
# HMAC Auth (Optional)
# ---------------------------------------------------------------------------
_HMAC_HEADER = "X-Signature"
_TS_HEADER = "X-Timestamp"
_DRIFT_SEC = int(os.getenv("SYMBOLIC_TS_DRIFT", "30"))


def _get_secret() -> Optional[str]:
    return os.getenv("SYMBOLIC_API_SECRET")


def _verify_hmac(request: Request, secret: str) -> None:
    sig = request.headers.get(_HMAC_HEADER)
    ts = request.headers.get(_TS_HEADER)
    if not sig or not ts:
        raise HTTPException(401, detail="auth headers missing")
    try:
        ts_int = int(ts)
    except ValueError:
        raise HTTPException(401, detail="bad timestamp")
    if abs(time.time() - ts_int) > _DRIFT_SEC:
        raise HTTPException(401, detail="timestamp drift")

    body = (request.scope.get("body") or b"") if "body" in request.scope else b""
    payload = f"{request.method}|{request.url.path}|{body.decode()}|{ts}".encode()
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(401, detail="bad signature")


@app.middleware("http")
async def hmac_middleware(request: Request, call_next):
    secret = _get_secret()
    if secret and request.url.path != "/status":
        _verify_hmac(request, secret)
    return await call_next(request)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/status")
async def get_status():
    return {"status": "ok", "version": __version__}


@app.post("/chat")
async def chat(payload: ChatRequest):
    motifs = engine._infer_motifs(payload.text)
    task = await engine.propose_from_motifs(motifs)
    await engine.solve(task)
    rendered = engine._render_motifs(task.expected_output or [])
    return {"reply": rendered}


@app.post("/motifs/infer")
async def infer(payload: TextInput):
    return {"motifs": engine._infer_motifs(payload.text)}


@app.post("/motifs/reflect")
async def reflect(payload: MotifListInput):
    return {"text": engine._render_motifs(payload.motifs)}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_api(engine: SymbolicTaskEngine, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run("symbolic_api:app", host=host, port=port, log_level="info")

# End of File
