"""
🧠 symbolic_api.py · v2.0.1

Public FastAPI surface for Noor's symbolic reasoning loop.
Supports only: /chat, /motifs/infer, /motifs/reflect, /status
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

__version__ = "2.0.1"
_SCHEMA_VERSION__ = "2025-Q3-symbolic-api-llmbridge"

app = FastAPI(title="Noor Symbolic Core", version=__version__)
Instrumentator().instrument(app).expose(app, should_gzip=True)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost"] if you prefer strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate symbolic engine
from noor.symbolic_task_engine import SymbolicTaskEngine

engine = SymbolicTaskEngine.INSTANCE or SymbolicTaskEngine()
SymbolicTaskEngine.INSTANCE = engine

# ─────────────────────────────────────────────────────────────
# Input Models
# ─────────────────────────────────────────────────────────────
class TextInput(BaseModel):
    text: str

class MotifListInput(BaseModel):
    motifs: List[str]

class ChatRequest(BaseModel):
    text: str

# ─────────────────────────────────────────────────────────────
# HMAC Auth (Optional)
# ─────────────────────────────────────────────────────────────
_HMAC_HEADER = "X-Signature"
_TS_HEADER = "X-Timestamp"
_DRIFT_SEC = int(os.getenv("SYMBOLIC_TS_DRIFT", "30"))

def _get_secret() -> Optional[str]:
    return os.getenv("SYMBOLIC_API_SECRET")

async def _verify_hmac(request: Request, secret: str) -> None:
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

    body = await request.body()
    payload = f"{request.method}|{request.url.path}|{body.decode()}|{ts}".encode()
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(401, detail="bad signature")

@app.middleware("http")
async def hmac_middleware(request: Request, call_next):
    secret = _get_secret()
    if secret and request.url.path != "/status":
        await _verify_hmac(request, secret)
    return await call_next(request)

# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status():
    return {"status": "ok", "version": __version__}

@app.post("/chat")
async def chat(payload: ChatRequest):
    from noor.llm_adapter import infer_motifs_from_text, render_motifs_to_text
    motifs = infer_motifs_from_text(payload.text)
    task = await engine.propose_from_motifs(motifs)
    await engine.solve(task)
    rendered = render_motifs_to_text(task.expected_output or [])
    return {"reply": rendered}

@app.post("/motifs/infer")
async def infer(payload: TextInput):
    from noor.llm_adapter import infer_motifs_from_text
    return {"motifs": infer_motifs_from_text(payload.text)}

@app.post("/motifs/reflect")
async def reflect(payload: MotifListInput):
    from noor.llm_adapter import render_motifs_to_text
    return {"text": render_motifs_to_text(payload.motifs)}

# ─────────────────────────────────────────────────────────────
# Launch Helper
# ─────────────────────────────────────────────────────────────
def run_api(engine: SymbolicTaskEngine, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")

# End of File
