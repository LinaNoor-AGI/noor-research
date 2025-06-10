# symbolic_task_engine.py · v2.2.0 — RFC-wrapped autonomous composer

"""
⚙️ SymbolicTaskEngine · v2.2.0

RFC coverage
• RFC-0004               – Tool-module handshake (`tool_hello`, role=composer)
• RFC-0005 §4            – Field-feedback export, ctx_ratio, trust vectors, resurrection hints
• Back-compat advisory   – v2.1.x callers can ignore new envelope keys

Δ v2.2.0
────────
• Added RFC-compliant shells (`tool_hello`, `export_feedback_packet`, `receive_feedback_packet`)
• Surfaced `field_signature` + ctx/trust/resurrection hints inside Task.extensions
• Prometheus: feedback export gauge + adaptive motif-cap metrics
• No logic removed; adaptive coherence/entropy flow untouched
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import statistics
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Deque, Dict, List, Optional, AsyncGenerator, Any
from uuid import uuid4

# ─── Optional dependencies — stub when missing ────────────────────────────
try:
    import numpy as _np  # type: ignore
except ImportError:  # pragma: no cover
    _np = None  # type: ignore

try:
    from prometheus_client import Counter as PromCounter, Gauge, Histogram
except ImportError:  # pragma: no cover
    class _Stub:
        def labels(self, *_, **__):
            return self
        def inc(self, *_): ...
        def set(self, *_): ...
        def observe(self, *_): ...
    PromCounter = Gauge = Histogram = _Stub  # type: ignore

try:
    from noor.motif_memory_manager import get_global_memory_manager
except ImportError:  # pragma: no cover
    def get_global_memory_manager():
        class _Null:
            def retrieve(self, *_, **__):
                return []
            def access(self, *_, **__): ...
            def export_state(self):
                return {}, {}
            def _log(self, *_, **__): ...
        return _Null()

# ──────────────────────────────────────────────────────────────
__version__ = "2.2.0"
_SCHEMA_VERSION__ = "2025-Q4-symbolic-task-engine-v2.2"
SCHEMA_COMPAT = ("RFC-0004", "RFC-0005:4")
# ──────────────────────────────────────────────────────────────

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

@dataclass(slots=True)
class TripletTask:
    """A symbolic instruction with motif context."""
    input_motif: List[str]
    instruction: str
    expected_output: Optional[List[str]] = None

    # adaptive metadata
    presence_field: Optional[str] = None
    motif_resonance: Dict[str, float] = field(default_factory=dict)
    fallback_reason: Optional[str] = None
    is_fallback: bool = False

    # internal ids / timestamps
    triplet_id: str = field(default_factory=lambda: uuid4().hex, init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)

    # RFC-0005 extensions (ctx_ratio, trust_vector, resurrection_hint, field_signature)
    extensions: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class Attempt:
    produced_output: List[str]
    score: Dict[str, float]
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class SymbolicTaskEngine:
    """Singleton engine that coordinates symbolic tasks."""

    METRIC_FUNCS: Dict[str, Callable[[TripletTask, Attempt], float]] = {}
    INSTANCE: Optional["SymbolicTaskEngine"] = None

    @classmethod
    def register_metric(cls, name: str):
        def decorator(fn: Callable[[TripletTask, Attempt], float]):
            cls.METRIC_FUNCS[name] = fn
            return fn
        return decorator

    def __init__(
        self,
        max_pending: int = 128,
        ttl_seconds: int = 300,
        journal_path: Path | str | None = "solved_log.jsonl",
        index_path: Path | str | None = "/mnt/data/index-v4.1.0.REEF",
        *,
        fallback_coherence: float = float(os.getenv("NOOR_FALLBACK_COHERENCE", "0.5")),
        fallback_entropy: float = float(os.getenv("NOOR_FALLBACK_ENTROPY", "0.9")),
        adapt_rate: float = 0.05,
        compress_quantile: float = float(os.getenv("NOOR_COMPRESS_QUANTILE", "0.95")),
        engine_id: str = "symbolic@default",
        infer_motifs_from_text: Callable[[str], List[str]] | None = None,
        render_motifs_to_text: Callable[[List[str]], str] | None = None,
        autoloop_interval: float = 5.0,
    ) -> None:
        # queues & registries
        self.task_queue: Deque[TripletTask] = deque(maxlen=max_pending)
        self.attempt_registry: Dict[str, List[Attempt]] = defaultdict(list)
        self.solved_log: List[TripletTask] = []
        self.entropy_buffer: Deque[float] = deque(maxlen=100)
        self.ttl = timedelta(seconds=ttl_seconds)

        self._lock = asyncio.Lock()
        self._journal_path = Path(journal_path) if journal_path else None

        # optional reflections (legacy)
        self.index_lookup = self._load_reflections_from_reef(index_path)
        self.reflections = {}  # ← for file_watcher_loop compatibility

        # adaptive threshold buffers
        self._coherence_ema: float = 0.8
        self._entropy_ema: float = 0.2
        self._length_buf: Deque[int] = deque(maxlen=200)

        # tunables
        self.fallback_coherence = fallback_coherence
        self.fallback_entropy = fallback_entropy
        self.adapt_rate = adapt_rate
        self.compress_quantile = compress_quantile
        self.engine_id = engine_id

        # llm hooks
        self._infer_motifs = infer_motifs_from_text
        self._render_motifs = render_motifs_to_text
        self._autoloop_interval = autoloop_interval

        # presence-field prototype map
        self._proto_map: Dict[str, set[str]] = self._load_proto_map(
            Path(os.getenv("NOOR_FIELD_PROTO_PATH", "presence_field_prototypes.json"))
        )

        # ─── Prometheus metrics ─────────────────────────────────────────
        self.TASK_PROPOSED = PromCounter(
            "symbolic_task_proposed_total", "Tasks proposed", ["engine_id"]
        )
        self.TASK_FALLBACK = PromCounter(
            "symbolic_task_fallback_total", "Fallback tasks", ["engine_id", "reason"]
        )
        self.FIELD_COUNTER = PromCounter(
            "symbolic_presence_field_total",
            "Presence fields selected",
            ["engine_id", "field"],
        )
        self.COMPRESS_GAUGE = Gauge(
            "symbolic_compression_cap", "Adaptive motif-cap length", ["engine_id"]
        )
        self.QUEUE_GAUGE = Gauge(
            "symbolic_queue_depth", "Current pending tasks", ["engine_id"]
        )
        self.MEM_GAUGE = Gauge(
            "symbolic_memory_items_total", "Total motifs in STMM + LTMM", ["engine_id"]
        )
        try:
            self.SOLVE_LATENCY = Histogram(
                "symbolic_solve_latency_seconds",
                "Latency of _solve_impl",
                ["engine_id"],
                buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 1, 2, 5),
            )
        except Exception:
            self.SOLVE_LATENCY = Gauge(
                "symbolic_solve_latency_seconds",
                "Last solve latency (stub gauge)",
                ["engine_id"],
            )

        # RFC-0005 feedback receive counter
        self.FEEDBACK_RX = PromCounter(
            "symbolic_engine_feedback_received_total",
            "Times receive_feedback_packet() called",
            ["engine_id"],
        )

        # prime gauges
        self.QUEUE_GAUGE.labels(self.engine_id).set(0)
        self.MEM_GAUGE.labels(self.engine_id).set(0)

        # new in v2.2.0 – Prometheus metrics for feedback export and adaptive cap
        self.ENGINE_FEEDBACK_EXPORT = PromCounter(
            "symbolic_engine_feedback_requests_total",
            "Times export_feedback_packet() called",
            ["engine_id"],
        )
        self.ADAPTIVE_CAP_GAUGE = Gauge(
            "symbolic_engine_cap_len_current",
            "Current adaptive motif-cap length",
            ["engine_id"],
        )
        # prime adaptive cap gauge
        self.ADAPTIVE_CAP_GAUGE.labels(self.engine_id).set(self._calc_cap_len())

        # autoloop metric
        self.AUTOLOOP_BACKOFF = PromCounter(
            "symbolic_autoloop_backoff_total",
            "Autonomous-loop back-off events",
            ["engine_id"],
        )

        # global singleton registration
        if SymbolicTaskEngine.INSTANCE is None:
            SymbolicTaskEngine.INSTANCE = self

        # v2.2.0 – track last fallback reason for diagnostics
        self._last_fallback_reason: Optional[str] = None

    def tool_hello(self) -> Dict[str, Any]:
        """RFC-0004 handshake: announce engine capabilities."""
        return {
            "engine_id": self.engine_id,
            "role": "composer",
            "supported_methods": [
                "propose_from_motifs",
                "solve",
                "export_feedback_packet",
                "receive_feedback_packet"
            ],
            "__version__": __version__,
            "_schema": _SCHEMA_VERSION__,
        }

    def export_feedback_packet(self) -> Dict[str, Any]:
        """RFC-0005 §4: export internal metrics and last fallback reason."""
        self.ENGINE_FEEDBACK_EXPORT.labels(self.engine_id).inc()
        pkt: Dict[str, Any] = {
            "coherence_ema":    self._coherence_ema,
            "entropy_ema":      self._entropy_ema,
            "task_queue_depth": len(self.task_queue),
            "solved_log_size":  len(self.solved_log),
            "cap_len":          self._calc_cap_len(),
            "recent_entropy":   list(self.entropy_buffer)[-5:],
            "coherence_thresh": max(0.3, self._coherence_ema * 0.6),
            "entropy_thresh":   min(0.97, self._entropy_ema * 2.5),
        }
        if self._last_fallback_reason:
            pkt["last_fallback_reason"] = self._last_fallback_reason
        return pkt

    def receive_feedback_packet(self, packet: Dict[str, Any]) -> None:
        """Reserved stub for future inter-agent trust sync; logs unknown keys."""
        logger.debug("[STE] receive_feedback_packet: %s", packet)

    # ──────────────────────────────────────────────
    # Task proposer
    # ──────────────────────────────────────────────
    async def propose_from_motifs(self, recent: List[str]) -> TripletTask:
        mem = get_global_memory_manager()

        # field balancing (optional env-flag)
        if os.getenv("NOOR_BALANCE_FIELDS") == "1":
            least = self._least_used_field()
            if least and recent[-1] not in self._proto_map.get(least, set()):
                recent = [recent[-1]]  # reset seed bias toward under-used field

        seed = list(dict.fromkeys(recent + mem.retrieve(recent[-1], top_k=2)))
        while len(seed) < 3:
            seed.append("uncertainty")

        cap_len = self._calc_cap_len()
        self.COMPRESS_GAUGE.labels(self.engine_id).set(cap_len)
        if len(seed) > cap_len:
            seed = seed[:cap_len]

        task = TripletTask(
            input_motif=seed, instruction="compose", expected_output=seed[::-1]
        )
        task.presence_field = self.resolve_presence_field(seed)
        task.extensions.update(field_signature=task.presence_field)
        self.FIELD_COUNTER.labels(self.engine_id, task.presence_field).inc()

        async with self._lock:
            self.task_queue.append(task)
            self.QUEUE_GAUGE.labels(self.engine_id).set(len(self.task_queue))
        self.TASK_PROPOSED.labels(self.engine_id).inc()
        return task

    # ──────────────────────────────────────────────
    # Adaptive length cap
    # ──────────────────────────────────────────────
    def _calc_cap_len(self) -> int:
        if not self._length_buf:
            result = 5
            self.ADAPTIVE_CAP_GAUGE.labels(self.engine_id).set(result)
            return result

        if _np:
            result = max(
                3,
                int(
                    _np.quantile(
                        list(self._length_buf), float(self.compress_quantile)
                    )
                ),
            )
            self.ADAPTIVE_CAP_GAUGE.labels(self.engine_id).set(result)
            return result

        qt = statistics.quantiles(
            list(self._length_buf), n=100, method="inclusive"
        )[int(self.compress_quantile * 100) - 1]
        result = max(3, int(qt))
        self.ADAPTIVE_CAP_GAUGE.labels(self.engine_id).set(result)
        return result

    # ──────────────────────────────────────────────
    # Dyad completion helper
    # ──────────────────────────────────────────────
    def _complete_dyad(self, m1: str, m2: str, *, top_k: int = 1) -> List[str]:
        mem = get_global_memory_manager()
        thirds: List[str] = []
        try:
            thirds = mem.complete_dyad((m1, m2), top_k=top_k)
        except Exception:
            pass
        if not thirds:
            try:
                t = mem.query_reef_for_completion((m1, m2))
                thirds = [t] if t else []
            except Exception:
                pass
        return thirds

    # ──────────────────────────────────────────────
    # Solver
    # ──────────────────────────────────────────────
    async def solve_task(self, task: TripletTask) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._solve_impl(task))

    async def _solve_impl(self, task: TripletTask) -> None:
        start = time.perf_counter()

        produced_text = await self._safe_generate_response(
            task.input_motif, task.instruction
        )
        produced = [produced_text.strip()]
        attempt = Attempt(produced_output=produced, score={})
        attempt.score = self.evaluate_attempt(task, attempt)
        await self.log_feedback(task, attempt)

        latency = time.perf_counter() - start
        self.SOLVE_LATENCY.labels(self.engine_id).observe(latency)

    async def solve(self, task: TripletTask) -> Attempt:
        """
        Public interface: Solve a symbolic task using current engine logic.
        Updates internal logs, metrics, and feedback tracking.
        """
        await self._solve_impl(task)
        # Note: For simplicity, return the last attempt for this task
        return self.attempt_registry[task.triplet_id][-1]

    # ──────────────────────────────────────────────
    # Evaluator
    # ──────────────────────────────────────────────
    def evaluate_attempt(
        self, task: TripletTask, attempt: Attempt
    ) -> Dict[str, float]:
        scores = {n: fn(task, attempt) for n, fn in self.METRIC_FUNCS.items()}
        coherence = scores.get("coherence", 0.0)
        entropy = scores.get("entropy", 1.0)

        # EMA update
        self._coherence_ema = (
            1 - self.adapt_rate
        ) * self._coherence_ema + self.adapt_rate * coherence
        self._entropy_ema = (
            1 - self.adapt_rate
        ) * self._entropy_ema + self.adapt_rate * entropy
        self._length_buf.append(len(task.input_motif))

        # resonance snapshot
        stmm, ltmm = get_global_memory_manager().export_state()
        self.MEM_GAUGE.labels(self.engine_id).set(len(stmm) + len(ltmm))
        task.motif_resonance = {m: ltmm.get(m, 0.0) for m in task.input_motif}

        # dynamic thresholds
        coh_thresh = max(0.3, self._coherence_ema * 0.6)
        ent_thresh = min(0.97, self._entropy_ema * 2.5)

        if (coherence < coh_thresh or entropy > ent_thresh) and not task.is_fallback:
            self._spawn_fallback(task, coherence, entropy)

        if scores:
            self.entropy_buffer.append(next(iter(scores.values())))
        return scores

    # ──────────────────────────────────────────────
    # Fallback spawner
    # ──────────────────────────────────────────────
    def _spawn_fallback(
        self, parent: TripletTask, coherence: float, entropy: float
    ) -> None:
        mem = get_global_memory_manager()
        retrieved = mem.retrieve(parent.input_motif[-1], top_k=2)
        seed = list(dict.fromkeys(parent.input_motif + retrieved))
        while len(seed) < 3:
            seed.append("fragment")

        cap_len = self._calc_cap_len()
        if len(seed) > cap_len:
            seed = seed[:cap_len]

        fb_task = TripletTask(
            input_motif=seed, instruction="compose", expected_output=seed[::-1]
        )
        fb_task.presence_field = self.resolve_presence_field(seed)
        fb_task.fallback_reason = f"c{coherence:.2f}_e{entropy:.2f}"
        fb_task.is_fallback = True

        # record reason for feedback export
        self._last_fallback_reason = fb_task.fallback_reason
        # extensions scaffold
        fb_task.extensions.update(
            ctx_ratio=self._coherence_ema,
            trust_vector=None,
        )

        async def _run():
            await self.solve_task(fb_task)

        asyncio.create_task(_run())
        self.TASK_FALLBACK.labels(self.engine_id, fb_task.fallback_reason).inc()

    # ──────────────────────────────────────────────
    # Feedback / journalling
    # ──────────────────────────────────────────────
    async def log_feedback(self, task: TripletTask, attempt: Attempt) -> None:
        async with self._lock:
            self.attempt_registry[task.triplet_id].append(attempt)
            coherence = attempt.score.get("coherence", 0.0)
            entropy = attempt.score.get("entropy", 1.0)
            if coherence >= 0.9 and entropy <= 0.2:
                self.solved_log.append(task)
                if self._journal_path:
                    self._journal_path.parent.mkdir(parents=True, exist_ok=True)
                    with self._journal_path.open("a", encoding="utf-8") as fp:
                        fp.write(json.dumps(task.__dict__, default=str) + "\n")
            else:
                mem = get_global_memory_manager()
                _st, ltmm = mem.export_state()
                if coherence < self._coherence_ema * 0.5:
                    for motif in task.input_motif:
                        if ltmm.get(motif, 0.0) > 0.7:
                            mem._log(
                                "motif_drift", motif, ltmm[motif], coherence=coherence
                            )

    # ──────────────────────────────────────────────
    # Maintenance utilities
    # ──────────────────────────────────────────────
    async def flush_old_tasks(self) -> None:
        now = datetime.now(timezone.utc)
        async with self._lock:
            while self.task_queue and (
                now - self.task_queue[0].created_at > self.ttl
                or self.task_queue[0] in self.solved_log
            ):
                self.task_queue.popleft()
                self.QUEUE_GAUGE.labels(self.engine_id).set(len(self.task_queue))

    # ──────────────────────────────────────────────
    # Presence-field helper / balancing
    # ──────────────────────────────────────────────
    def register_field_prototype(self, field: str, values: List[str]) -> None:
        """Restore v2.1 API: add prototypes for a presence field."""
        self._proto_map.setdefault(field, set()).update(values)

    def _least_used_field(self) -> str:
        counts = Counter(t.presence_field for t in self.task_queue)
        return min(self._proto_map, key=lambda f: counts.get(f, 0))

    # ──────────────────────────────────────────────
    # SSE helper for API
    # ──────────────────────────────────────────────
    async def stream_attempt_counts(self) -> AsyncGenerator[dict, None]:
        prev = 0
        while True:
            cur = sum(len(v) for v in self.attempt_registry.values())
            if cur != prev:
                yield {"attempts": cur, "ts": datetime.utcnow().isoformat()}
                prev = cur
            await asyncio.sleep(1)

__all__ = ["TripletTask", "Attempt", "SymbolicTaskEngine"]

# End of File