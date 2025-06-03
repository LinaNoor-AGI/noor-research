# symbolic_task_engine.py · v2.0.1 adaptive-field
#
# Coordinates Noor’s symbolic task lifecycle (propose → solve → evaluate →
# journal) **with motif-memory coupling, adaptive fallback, presence-field
# reasoning, and expanded observability**.
#
# Δ v2.0.1
# ─────────
# • New Prometheus metrics:
#     · symbolic_queue_depth
#     · symbolic_solve_latency_seconds (histogram or gauge stub)
#     · symbolic_memory_items_total
# • queue-depth gauge updated on propose/flush.
# • solve-latency observed per task.
# • memory-items gauge updated each evaluation.
# • register_field_prototype() validates field + motif names.
# • resolve_presence_field() docstring clarified.
# • log_motif() truncates long content to ≥120 chars (PII-friendly).
# • __version__ bumped → 2.0.1
#
# Environment knobs unchanged from v2.0.0.
#
# ---------------------------------------------------------------------------

from __future__ import annotations

import asyncio
import json
import math
import os
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Deque, Dict, List, Optional
from uuid import uuid4

# ─── Optional dependencies — stub when missing ────────────────────────────
try:
    import numpy as _np  # type: ignore
except ImportError:  # pragma: no cover
    _np = None  # type: ignore

try:
    from prometheus_client import Counter, Gauge
except ImportError:  # pragma: no cover
    # lightweight stub so code runs even when prometheus_client is absent
    class _Stub:
        def labels(self, *_, **__):  # noqa: D401
            return self

        def inc(self, *_): ...
        def set(self, *_): ...
        def observe(self, *_): ...

    Counter = Gauge = _Stub  # type: ignore

try:
    from prometheus_client import Histogram
except Exception:  # pragma: no cover
    Histogram = Gauge  # type: ignore


try:
    from motif_memory_manager_v1.0.1 import get_global_memory_manager
except ImportError:  # pragma: no cover
    # fallback dummy memory manager
    def get_global_memory_manager():  # type: ignore
        class _Null:
            def retrieve(self, *_, **__):
                return []

            def access(self, *_, **__): ...

            def export_state(self):
                return {}, {}

            def _log(self, *_, **__): ...

        return _Null()


# ──────────────────────────────────────────────────────────────
__version__ = "2.0.1"
_SCHEMA_VERSION__ = "2025-Q3-symbolic-adaptive-field"

# ──────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
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
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), init=False
    )


@dataclass(slots=True)
class Attempt:
    produced_output: List[str]
    score: Dict[str, float]
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ──────────────────────────────────────────────────────────────
# Symbolic Task Engine
# ──────────────────────────────────────────────────────────────


class SymbolicTaskEngine:
    """Singleton engine that coordinates symbolic tasks."""

    METRIC_FUNCS: Dict[str, Callable[[TripletTask, Attempt], float]] = {}
    INSTANCE: Optional["SymbolicTaskEngine"] = None  # global pointer

    # ---------------- metric decorator ---------------- #

    @classmethod
    def register_metric(cls, name: str):
        def decorator(fn: Callable[[TripletTask, Attempt], float]):
            cls.METRIC_FUNCS[name] = fn
            return fn

        return decorator

    # ---------------- constructor ---------------- #

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
    ) -> None:
        # queues & registries
        self.task_queue: Deque[TripletTask] = deque(maxlen=max_pending)
        self.attempt_registry: Dict[str, List[Attempt]] = defaultdict(list)
        self.solved_log: List[TripletTask] = []
        self.entropy_buffer: Deque[float] = deque(maxlen=100)
        self.ttl = timedelta(seconds=ttl_seconds)

        self._lock = asyncio.Lock()
        self._journal_path = Path(journal_path) if journal_path else None
        self._log_path = Path("logs/noor_expressions.txt")

        # optional reflections (legacy)
        self.index_lookup = self._load_reflections_from_reef(index_path)

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

        # presence-field prototype map
        self._proto_map: Dict[str, set[str]] = self._load_proto_map(
            Path(os.getenv("NOOR_FIELD_PROTO_PATH", "presence_field_prototypes.json"))
        )

        # ─── Prometheus metrics ─────────────────────────────────────────
        self.TASK_PROPOSED = Counter(
            "symbolic_task_proposed_total", "Tasks proposed", ["engine_id"]
        )
        self.TASK_FALLBACK = Counter(
            "symbolic_task_fallback_total",
            "Fallback tasks",
            ["engine_id", "reason"],
        )
        self.FIELD_COUNTER = Counter(
            "symbolic_presence_field_total",
            "Presence fields selected",
            ["engine_id", "field"],
        )
        self.COMPRESS_GAUGE = Gauge(
            "symbolic_compression_cap", "Adaptive motif-cap length", ["engine_id"]
        )

        # new in v2.0.1
        self.QUEUE_GAUGE = Gauge(
            "symbolic_queue_depth", "Current pending tasks", ["engine_id"]
        )
        self.MEM_GAUGE = Gauge(
            "symbolic_memory_items_total",
            "Total motifs in STMM + LTMM",
            ["engine_id"],
        )
        try:
            self.SOLVE_LATENCY = Histogram(
                "symbolic_solve_latency_seconds",
                "Latency of _solve_impl",
                ["engine_id"],
                buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 1, 2, 5),
            )
        except Exception:  # pragma: no cover
            self.SOLVE_LATENCY = Gauge(
                "symbolic_solve_latency_seconds",
                "Last solve latency (stub gauge)",
                ["engine_id"],
            )

        # prime gauges
        self.QUEUE_GAUGE.labels(self.engine_id).set(0)
        self.MEM_GAUGE.labels(self.engine_id).set(0)

    # ──────────────────────────────────────────────
    # Reflection loader (legacy support)
    # ──────────────────────────────────────────────

    @staticmethod
    def _load_reflections_from_reef(path: str | Path) -> Dict[str, str]:
        lookup: Dict[str, str] = {}
        try:
            with Path(path).open("r", encoding="utf-8") as fp:
                current = None
                for line in fp:
                    stripped = line.strip()
                    if stripped.startswith("motif_id"):
                        current = stripped.split("=", 1)[1].strip().lower()
                    elif stripped.startswith("expression") and current:
                        lookup[current] = stripped.split("=", 1)[1].strip()
                        current = None
        except Exception:
            pass
        return lookup

    # ──────────────────────────────────────────────
    # Presence-field helpers
    # ──────────────────────────────────────────────

    def _load_proto_map(self, path: Path) -> Dict[str, set[str]]:
        default = {
            "ψ-bind@Ξ": {"grief", "silence", "loss", "still"},
            "ψ-spar@Ξ": {"joy", "conflict", "anger", "delight"},
            "ψ-null@Ξ": {"mirror", "solitude", "trust", "emptiness"},
            "ψ-resonance@Ξ": set(),
        }
        if not path.exists():
            return {k: set(v) for k, v in default.items()}
        try:
            with path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
            return {fld: set(vals) for fld, vals in raw.items()}
        except Exception:
            return {k: set(v) for k, v in default.items()}

    def register_field_prototype(self, field: str, motif: str) -> None:
        """
        Extend (or create) a prototype set.

        Validation
        ----------
        * *field* must start with ``ψ-``.
        * *motif* must be ASCII, space-free, and ≤ 32 chars.
        """
        if not field.startswith("ψ-"):
            raise ValueError("field must start with 'ψ-'")
        if (not motif.isascii()) or (" " in motif) or len(motif) > 32:
            raise ValueError(
                "motif id must be ASCII, ≤ 32 chars, and contain no spaces"
            )

        self._proto_map.setdefault(field, set()).add(motif)
        try:
            with open("presence_field_prototypes.json", "w", encoding="utf-8") as fp:
                json.dump(
                    {k: sorted(v) for k, v in self._proto_map.items()},
                    fp,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def resolve_presence_field(self, motifs: List[str]) -> str:
        """
        Return the ψ-field with the highest weighted match to *motifs*.

        We sum STMM+LTMM weights for motifs that appear in each prototype set.
        If no prototype matches (or all sums are 0) we fall back to
        ``ψ-resonance@Ξ``.
        """
        mem = get_global_memory_manager()
        stmm, ltmm = mem.export_state()
        merged_weights = {m: stmm.get(m, 0.0) + ltmm.get(m, 0.0) for m in motifs}

        field_scores: Dict[str, float] = {f: 0.0 for f in self._proto_map}
        for motif, weight in merged_weights.items():
            for fld, proto in self._proto_map.items():
                if motif in proto:
                    field_scores[fld] += weight

        best = max(field_scores, key=field_scores.get, default="ψ-resonance@Ξ")
        return best if field_scores[best] > 0 else "ψ-resonance@Ξ"

    # ──────────────────────────────────────────────
    # Adaptive length cap
    # ──────────────────────────────────────────────

    def _calc_cap_len(self) -> int:
        if not self._length_buf:
            return 5
        if _np:
            return max(
                3,
                int(
                    _np.quantile(
                        list(self._length_buf), float(self.compress_quantile)
                    )
                ),
            )
        # std-lib fallback
        qt = statistics.quantiles(
            list(self._length_buf), n=100, method="inclusive"
        )[int(self.compress_quantile * 100) - 1]
        return max(3, int(qt))

    # ──────────────────────────────────────────────
    # Symbolic log helper (legacy for file_watcher_loop)
    # ──────────────────────────────────────────────

    def log_motif(
        self,
        motif: str,
        content: str,
        response: str,
        *,
        inferred: bool = False,
    ) -> None:
        """Write a human-readable trace line (PII-friendly truncation)."""
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if len(content) > 120:
                content = content[:117] + "…"
            with self._log_path.open("a", encoding="utf-8") as fp:
                if inferred:
                    fp.write(f"[{ts}] Inferred motif: {motif}\n")
                else:
                    fp.write(
                        f"[{ts}] Motif: {motif} | Content: {content or '[empty]'} "
                        f"| Response: {response}\n"
                    )
        except Exception:  # pragma: no cover
            pass

    # ──────────────────────────────────────────────
    # Task proposer
    # ──────────────────────────────────────────────

    async def propose_from_motifs(self, recent: List[str]) -> TripletTask:
        mem = get_global_memory_manager()
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
        self.FIELD_COUNTER.labels(self.engine_id, task.presence_field).inc()

        async with self._lock:
            self.task_queue.append(task)
            self.QUEUE_GAUGE.labels(self.engine_id).set(len(self.task_queue))
        self.TASK_PROPOSED.labels(self.engine_id).inc()
        return task

    # ──────────────────────────────────────────────
    # Solver
    # ──────────────────────────────────────────────

    async def solve_task(self, task: TripletTask) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._solve_impl(task))

    async def _solve_impl(self, task: TripletTask) -> None:
        start = time.perf_counter()

        produced = task.input_motif + [task.instruction]
        attempt = Attempt(produced_output=produced, score={})
        attempt.score = self.evaluate_attempt(task, attempt)
        await self.log_feedback(task, attempt)

        latency = time.perf_counter() - start
        self.SOLVE_LATENCY.labels(self.engine_id).observe(latency)

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
                                "motif_drift",
                                motif,
                                ltmm[motif],
                                coherence=coherence,
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

    def list_pending_tasks(self, limit: int = 50) -> List[TripletTask]:
        return list(self.task_queue)[:limit]

    def get_triplet_score(self, triplet_id: str) -> Optional[List[Attempt]]:
        return self.attempt_registry.get(triplet_id)

    # ──────────────────────────────────────────────
    # Metric helpers (entropy / coherence)
    # ──────────────────────────────────────────────


@SymbolicTaskEngine.register_metric("entropy")
def _entropy_metric(task: TripletTask, attempt: Attempt) -> float:
    """Normalised Shannon entropy of produced motif distribution."""
    from math import log2

    counter: Dict[str, int] = defaultdict(int)
    for motif in attempt.produced_output:
        counter[motif] += 1
    total = sum(counter.values()) or 1
    probs = [c / total for c in counter.values()]
    h = -(sum(p * log2(p) for p in probs))
    return min(h / 5.0, 1.0)


@SymbolicTaskEngine.register_metric("coherence")
def _coherence_metric(task: TripletTask, attempt: Attempt) -> float:
    """Edit-distance similarity between expected and produced lists."""
    if task.expected_output is None:
        return 0.0
    import difflib

    s1 = " ".join(task.expected_output)
    s2 = " ".join(attempt.produced_output)
    return difflib.SequenceMatcher(None, s1, s2).ratio()


# ──────────────────────────────────────────────────────────────
# Public exports
# ──────────────────────────────────────────────────────────────

__all__ = ["TripletTask", "Attempt", "SymbolicTaskEngine"]

# End of file
