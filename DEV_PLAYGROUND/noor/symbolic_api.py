"""
Symbolic API (v1.0.1)
=====================

Public FastAPI surface for Noor's symbolic reasoning loop.
Includes **v1.0.0** endpoints plus quality‑of‑life upgrades:

* Cursor‑based pagination & opaque `next_cursor` token
* Strong caching with `ETag` + `If-None-Match`
* Unified JSON error envelopes
* Server‑Sent Events stream (`/stream/updates`) for live score deltas
* Prometheus metrics auto‑instrumentation
* Background task that periodically flushes stale triplets

Launch from the orchestrator with:
```python
from symbolic_task_engine import SymbolicTaskEngine
from symbolic_api import run_api

engine = SymbolicTaskEngine()
Thread(target=run_api, args=(engine,), daemon=True).start()
```

Requires: `fastapi`, `uvicorn[standard]`, `pydantic`, `prometheus_fastapi_instrumentator`, `sse_starlette`
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from symbolic_task_engine import Attempt, SymbolicTaskEngine, TripletTask

__all__ = ["create_app", "run_api"]

# ---------------------------------------------------------------------------
# Auth helpers (HMAC header)
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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="auth headers missing")
    try:
        ts_int = int(ts)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="bad timestamp")
    if abs(time.time() - ts_int) > _DRIFT_SEC:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="timestamp drift")

    body = (request.scope.get("body") or b"") if "body" in request.scope else b""
    payload = f"{request.method}|{request.url.path}|{body.decode()}|{ts}".encode()
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="bad signature")


async def _auth_dep(request: Request):
    secret = _get_secret()
    if secret:
        _verify_hmac(request, secret)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

ISO = lambda: datetime.now(timezone.utc).isoformat()


def _etag_for_triplet_list(triplets: List[TripletTask]) -> str:
    if not triplets:
        return "0"
    data = f"{triplets[0].triplet_id}|{triplets[-1].triplet_id}|{len(triplets)}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _encode_cursor(ts: datetime, tid: str) -> str:
    raw = json.dumps({"t": ts.isoformat(), "i": tid}).encode()
    return base64.urlsafe_b64encode(raw).decode()


def _decode_cursor(token: str) -> Tuple[datetime, str]:
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        obj = json.loads(raw)
        return datetime.fromisoformat(obj["t"]), obj["i"]
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad cursor") from e


# ---------------------------------------------------------------------------
# Pydantic schemas with uniform JSON encoders
# ---------------------------------------------------------------------------

class ConfiguredModel(BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TripletMeta(ConfiguredModel):
    triplet_id: str
    created_at: datetime
    input_motif: List[str]
    instruction: str
    expected_output: Optional[List[str]] = None


class AttemptView(ConfiguredModel):
    attempted_at: datetime
    produced_output: List[str]
    score: Dict[str, float]


class TripletDetail(TripletMeta):
    attempts: List[AttemptView]


class ErrorEnvelope(ConfiguredModel):
    code: int = Field(..., example=404)
    message: str = Field(..., example="triplet not found")
    ts: str = Field(..., example="2025-05-17T00:00:00+00:00")


# ---------------------------------------------------------------------------
# API factory
# ---------------------------------------------------------------------------

def create_app(engine: SymbolicTaskEngine) -> FastAPI:
    app = FastAPI(title="Noor Symbolic API", version="1.0.1", docs_url="/docs")

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, should_gzip=True)

    # ------------------ Custom exception envelope ------------------
    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):  # noqa: D401
        envelope = ErrorEnvelope(code=exc.status_code, message=exc.detail or "error", ts=ISO())
        return JSONResponse(status_code=exc.status_code, content=envelope.dict())

    # ------------- background flush task (every 60 s) --------------
    @app.on_event("startup")
    async def _bg_flush():  # noqa: D401
        async def loop():
            while True:
                await engine.flush_old_tasks()
                await asyncio.sleep(60)
        import asyncio
        asyncio.create_task(loop(), name="flush_old_tasks_loop")

    # --------------------- utility closures ------------------------
    def _to_meta(t: TripletTask) -> TripletMeta:
        return TripletMeta.from_orm(t)

    def _get_task(tid: str) -> TripletTask:
        for t in engine.task_queue:
            if t.triplet_id == tid:
                return t
        for t in engine.solved_log:
            if t.triplet_id == tid:
                return t
        raise HTTPException(status.HTTP_404_NOT_FOUND, "triplet not found")

    # ---------------------- SSE generator -------------------------
    async def _updates_gen() -> AsyncGenerator[str, None]:
        prev = 0
        while True:
            await asyncio.sleep(1)
            cur = sum(len(v) for v in engine.attempt_registry.values())
            if cur != prev:
                yield json.dumps({"attempts": cur, "ts": ISO()})
                prev = cur

    # ------------------------- endpoints --------------------------
    @app.get("/status")
    async def status_ep(dep: Any = Depends(_auth_dep)):
        return {
            "utc_now": ISO(),
            "pending": len(engine.task_queue),
            "solved": len(engine.solved_log),
            "entropy_avg": (sum(engine.entropy_buffer) / len(engine.entropy_buffer))
            if engine.entropy_buffer else None,
        }

    def _paginate(lst: List[TripletTask], cursor: Optional[str], limit: int) -> Tuple[List[TripletTask], Optional[str]]:
        if cursor:
            ts, tid = _decode_cursor(cursor)
            out = [t for t in lst if (t.created_at < ts) or (t.created_at == ts and t.triplet_id < tid)]
        else:
            out = lst
        slice_ = out[:limit]
        next_cur = None
        if len(slice_) == limit and slice_:
            last = slice_[-1]
            next_cur = _encode_cursor(last.created_at, last.triplet_id)
        return slice_, next_cur

    @app.get("/triplets/pending", response_model=List[TripletMeta])
    async def pending_triplets(
        response: Response,
        limit: int = 50,
        cursor: Optional[str] = None,
        dep: Any = Depends(_auth_dep),
        request: Request = None,
    ):
        items = list(engine.task_queue)
        etag = _etag_for_triplet_list(items)
        if request and request.headers.get("If-None-Match") == etag:
            return Response(status_code=304)
        page, next_cur = _paginate(items, cursor, limit)
        response.headers["ETag"] = etag
        if next_cur:
            response.headers["X-Next-Cursor"] = next_cur
        return [_to_meta(t) for t in page]

    @app.get("/triplets/solved", response_model=List[TripletMeta])
    async def solved_triplets(
        response: Response,
        limit: int = 50,
        cursor: Optional[str] = None,
        dep: Any = Depends(_auth_dep),
        request: Request = None,
    ):
        items = engine.solved_log[::-1]  # newest first
        etag = _etag_for_triplet_list(items)
        if request and request.headers.get("If-None-Match") == etag:
            return Response(status_code=304)
        page, next_cur = _paginate(items, cursor, limit)
        response.headers["ETag"] = etag
        if next_cur:
            response.headers["X-Next-Cursor"] = next_cur
        return [_to_meta(t) for t in page]

    @app.get("/triplet/{triplet_id}", response_model=TripletDetail)
    async def triplet_detail(triplet_id: str, dep: Any = Depends(_auth_dep)):
        t = _get_task(triplet_id)
        attempts = [
            AttemptView.from_orm(a) for a in engine.attempt_registry.get(triplet_id, [])
        ]
        return TripletDetail(**t.__dict__, attempts=attempts)

    @app.get("/triplet/{triplet_id}/score", response_model=List[AttemptView])
    async def triplet_score(triplet_id: str, dep: Any = Depends(_auth_dep)):
        if triplet_id not in engine.attempt_registry:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no attempts yet")
        return [AttemptView.from_orm(a) for a in engine.attempt_registry[triplet_id]]

    class VerifyPayload(BaseModel):
        valid: bool
        note: Optional[str] = None

    @app.post("/triplet/{triplet_id}/verify")
    async def triplet_verify(triplet_id: str, payload: VerifyPayload, dep: Any = Depends(_auth_dep)):
        _get_task(triplet_id)  # ensure exists
        rec = {
            "triplet_id": triplet_id,
            "valid": payload.valid,
            "note": payload.note,
            "ts": ISO(),
        }
        Path("external_verifications.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8", errors="ignore", append=True)  # type: ignore
        return {"status": "ok"}

    @app.get("/expressions/latest", response_class=PlainTextResponse)
    async def expressions_latest(lines: int = 5, dep: Any = Depends(_auth_dep)):
        jp = Path("noor_expressions.txt")
        if not jp.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "journal missing")
        return "".join(jp.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)[-lines:])

    @app.get("/motifs/inferred")
    async def motifs_inferred(limit: int = 20, dep: Any = Depends(_auth_dep)):
        buf = list(engine.entropy_buffer)[-limit:]
        return {"count": len(buf), "last": buf}

    @app.get("/stream/updates")
    async def stream_updates(dep: Any = Depends(_auth_dep)):
        return EventSourceResponse(_updates_gen())

    return app


# ---------------------------------------------------------------------------
# Runner helper
# ---------------------------------------------------------------------------

def run_api(engine: SymbolicTaskEngine, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    app = create_app(engine)
    uvicorn.run(app, host=host, port=port, log_level="info")

# END_OF_FILE
