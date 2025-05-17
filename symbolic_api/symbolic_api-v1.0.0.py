"""
symbolic_api.py (v1.0.0)
=====================

FastAPI surface for Noor's symbolic reasoning loop.  
Exposes endpoints for inspecting and verifying *TripletTask* objects managed by
`SymbolicTaskEngine`.  Designed to be launched as a background thread inside
the orchestrator:

```python
from symbolic_task_engine import SymbolicTaskEngine
from symbolic_api import run_api

engine = SymbolicTaskEngine()
Thread(target=run_api, args=(engine,), daemon=True).start()
```

Key features
------------
* **Read‑only** inspection of pending / solved triplets
* **Score breakdown** & external verification hook
* Lightweight heartbeat & expression peek
* Optional HMAC query signature for basic auth

Dependencies: `fastapi`, `uvicorn[standard]`, `pydantic` (FastAPI default)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from symbolic_task_engine import Attempt, SymbolicTaskEngine, TripletTask

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _get_api_secret() -> Optional[str]:
    """Fetch the shared-secret for HMAC auth from env var `SYMBOLIC_API_SECRET`."""
    return os.getenv("SYMBOLIC_API_SECRET")


def _verify_signature(request: Request, secret: str) -> None:
    """Raise 401 if the request's `X-Signature` header is invalid.

    Signature = HMAC_SHA256(secret, <method>|<path>|<body>|<timestamp>)
    Header must also include `X-Timestamp`. Timestamp may drift ±30 s.
    """
    sig = request.headers.get("X-Signature")
    ts = request.headers.get("X-Timestamp")
    if not sig or not ts:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing signature headers")
    try:
        ts_int = int(ts)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad timestamp")
    if abs(time.time() - ts_int) > 30:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Timestamp drift too large")

    body = request.scope.get("body", b"") or b""
    payload = f"{request.method}|{request.url.path}|{body.decode()}|{ts}".encode()
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")


async def _auth_dependency(request: Request):
    """FastAPI dependency for optional HMAC auth."""
    secret = _get_api_secret()
    if secret:
        _verify_signature(request, secret)


# ---------------------------------------------------------------------------
# Pydantic schemas (API responses)
# ---------------------------------------------------------------------------

class TripletMeta(BaseModel):
    triplet_id: str
    created_at: datetime
    input_motif: List[str]
    instruction: str
    expected_output: Optional[List[str]]


class AttemptView(BaseModel):
    attempted_at: datetime
    produced_output: List[str]
    score: Dict[str, float]


class TripletDetail(TripletMeta):
    attempts: List[AttemptView]


# ---------------------------------------------------------------------------
# API factory
# ---------------------------------------------------------------------------

def create_app(engine: SymbolicTaskEngine) -> FastAPI:
    app = FastAPI(title="Noor Symbolic API", version="1.0.0", docs_url="/docs")

    # ----------------------------- Utilities -----------------------------
    def _to_meta(task: TripletTask) -> TripletMeta:
        return TripletMeta(**task.__dict__)

    def _get_task_or_404(tid: str) -> TripletTask:
        for t in engine.task_queue:
            if t.triplet_id == tid:
                return t
        for t in engine.solved_log:
            if t.triplet_id == tid:
                return t
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"triplet {tid} not found")

    # ----------------------------- Endpoints -----------------------------
    @app.get("/status", response_class=JSONResponse)
    async def status_endpoint(dep: Any = Depends(_auth_dependency)):
        return {
            "utc_now": datetime.now(timezone.utc).isoformat(),
            "pending": len(engine.task_queue),
            "solved": len(engine.solved_log),
            "entropy_avg": (sum(engine.entropy_buffer) / len(engine.entropy_buffer))
            if engine.entropy_buffer
            else None,
        }

    @app.get("/triplets/pending", response_model=List[TripletMeta])
    async def pending_triplets(limit: int = 50, dep: Any = Depends(_auth_dependency)):
        return [_to_meta(t) for t in list(engine.task_queue)[:limit]]

    @app.get("/triplets/solved", response_model=List[TripletMeta])
    async def solved_triplets(limit: int = 50, dep: Any = Depends(_auth_dependency)):
        return [_to_meta(t) for t in engine.solved_log[-limit:][::-1]]

    @app.get("/triplet/{triplet_id}", response_model=TripletDetail)
    async def triplet_detail(triplet_id: str, dep: Any = Depends(_auth_dependency)):
        task = _get_task_or_404(triplet_id)
        attempts = [
            AttemptView(
                attempted_at=a.attempted_at,
                produced_output=a.produced_output,
                score=a.score,
            )
            for a in engine.attempt_registry.get(triplet_id, [])
        ]
        return TripletDetail(**task.__dict__, attempts=attempts)

    @app.get("/triplet/{triplet_id}/score", response_model=List[AttemptView])
    async def triplet_score(triplet_id: str, dep: Any = Depends(_auth_dependency)):
        if triplet_id not in engine.attempt_registry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no attempts yet")
        return [
            AttemptView(
                attempted_at=a.attempted_at,
                produced_output=a.produced_output,
                score=a.score,
            )
            for a in engine.attempt_registry[triplet_id]
        ]

    class VerifyPayload(BaseModel):
        valid: bool
        note: Optional[str] = None

    @app.post("/triplet/{triplet_id}/verify")
    async def triplet_verify(
        triplet_id: str,
        payload: VerifyPayload,
        dep: Any = Depends(_auth_dependency),
    ):
        task = _get_task_or_404(triplet_id)
        meta_path = Path("external_verifications.jsonl")
        record = {
            "triplet_id": triplet_id,
            "valid": payload.valid,
            "note": payload.note,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with meta_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(record) + "\n")
        return {"status": "ok"}

    # ------------------------- Expressions peek -------------------------
    @app.get("/expressions/latest", response_class=PlainTextResponse)
    async def expressions_latest(lines: int = 5, dep: Any = Depends(_auth_dependency)):
        journal_path = Path("noor_expressions.txt")
        if not journal_path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "journal file missing")
        with journal_path.open("r", encoding="utf-8") as fp:
            tail = fp.readlines()[-lines:]
        return "".join(tail)

    # ------------------ Motif inference stub (placeholder) --------------
    @app.get("/motifs/inferred", response_class=JSONResponse)
    async def motifs_inferred(limit: int = 20, dep: Any = Depends(_auth_dependency)):
        # Placeholder: reuse `entropy_buffer` as crude novelty trace.
        return {
            "count": len(engine.entropy_buffer),
            "last_values": list(engine.entropy_buffer)[-limit:],
        }

    return app


# ---------------------------------------------------------------------------
# Runner helper
# ---------------------------------------------------------------------------

def run_api(engine: SymbolicTaskEngine, host: str = "0.0.0.0", port: int = 8000):
    """Blocking helper to serve the FastAPI app via uvicorn."""
    import uvicorn

    app = create_app(engine)
    uvicorn.run(app, host=host, port=port, log_level="info")


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    "create_app",
    "run_api",
]

# END_OF_FILE
