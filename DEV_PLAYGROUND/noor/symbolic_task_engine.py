"""
symbolic_task_engine.py (v1.0.0)
=============================

This module implements Noor's AZR self-play loop. It orchestrates the life‑cycle
of *symbolic triplet tasks* — (input_motif, instruction, expected_output) — from
proposal through attempted solution, evaluation, and feedback logging.

Key features
------------
* **Immutable** `TripletTask` dataclass (frozen & slot‑optimised)
* **Async** solve pipeline with `asyncio.TaskGroup` back‑pressure
* Pluggable metric registry (`@SymbolicTaskEngine.register_metric`)
* Sliding‑window buffers for entropy, coherence, etc.
* JSON Lines journal for solved triplets (append‑only, streamable)

>>> Minimal usage
>>> -------------
>>> import asyncio, random
>>> from symbolic_task_engine import SymbolicTaskEngine
>>>
>>> engine = SymbolicTaskEngine(max_pending=32)
>>> motifs = ["joy", "grief", "silence"]
>>>
>>> async def demo():
...     triplet = await engine.propose_from_motifs(motifs)
...     await engine.solve_task(triplet)
...     await engine.flush_old_tasks()
...     print(engine.solved_log[0])
>>>
>>> asyncio.run(demo())

"""
from __future__ import annotations

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Deque, Dict, List, Optional
from uuid import uuid4

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TripletTask:
    """Immutable descriptor for a symbolic AZR task."""

    input_motif: List[str]
    instruction: str
    expected_output: Optional[List[str]] = None

    triplet_id: str = field(default_factory=lambda: uuid4().hex, init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)


@dataclass(slots=True)
class Attempt:  # mutable record; **not** frozen
    """One solution attempt for a *TripletTask*."""

    produced_output: List[str]
    score: Dict[str, float]
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Engine implementation
# ---------------------------------------------------------------------------

class SymbolicTaskEngine:
    """Coordinator for proposing, solving, and scoring symbolic triplet tasks."""

    # Registry of metric functions: (task, attempt) -> float in [0, 1]
    METRIC_FUNCS: Dict[str, Callable[[TripletTask, Attempt], float]] = {}

    # ---------------------------- Metric plug‑in ----------------------------
    @classmethod
    def register_metric(cls, name: str):
        """Decorator for registering new metric functions."""

        def decorator(fn: Callable[[TripletTask, Attempt], float]):
            cls.METRIC_FUNCS[name] = fn
            return fn

        return decorator

    # ----------------------------- Construction ---------------------------
    def __init__(
        self,
        max_pending: int = 128,
        ttl_seconds: int = 300,
        journal_path: Path | str | None = "solved_log.jsonl",
    ) -> None:
        self.task_queue: Deque[TripletTask] = deque(maxlen=max_pending)
        self.attempt_registry: Dict[str, List[Attempt]] = defaultdict(list)
        self.solved_log: List[TripletTask] = []
        self.entropy_buffer: Deque[float] = deque(maxlen=100)
        self.ttl = timedelta(seconds=ttl_seconds)
        self._lock = asyncio.Lock()
        self._journal_path = Path(journal_path) if journal_path else None

    # ----------------------------- Proposer ------------------------------
    async def propose_from_motifs(self, recent_motifs: List[str]) -> TripletTask:
        """Generate a new *TripletTask* from `recent_motifs` and enqueue it."""
        # Naïve proposal: first motif as input, instruction = "compose",
        # expected output = reversed list. Replace with smarter sampler later.
        task = TripletTask(
            input_motif=[recent_motifs[0]],
            instruction="compose",
            expected_output=list(reversed(recent_motifs)),
        )
        async with self._lock:
            self.task_queue.append(task)
        return task

    # ------------------------------ Solver -------------------------------
    async def solve_task(self, task: TripletTask) -> None:
        """Spawn an async attempt to solve `task`."""
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._solve_impl(task))

    async def _solve_impl(self, task: TripletTask) -> None:
        """Internal coroutine that performs a single attempt and logs feedback."""
        # Placeholder solver – echo instruction; swap with LogicalAgentAT
        produced_output = task.input_motif + [task.instruction]
        attempt = Attempt(produced_output=produced_output, score={})
        attempt.score = self.evaluate_attempt(task, attempt)
        await self.log_feedback(task, attempt)

    # -------------------------- Evaluator -------------------------------
    def evaluate_attempt(self, task: TripletTask, attempt: Attempt) -> Dict[str, float]:
        """Compute all registered metric functions. Returns dict of name→score."""
        scores = {
            name: fn(task, attempt) for name, fn in self.METRIC_FUNCS.items()
        }
        # book‑keep entropy buffer (using first metric if any)
        if scores:
            self.entropy_buffer.append(next(iter(scores.values())))
        return scores

    # ---------------------------- Logging -------------------------------
    async def log_feedback(self, task: TripletTask, attempt: Attempt) -> None:
        """Persist attempt score and update solved/registry structures."""
        async with self._lock:
            self.attempt_registry[task.triplet_id].append(attempt)
            # Heuristic: mark solved if coherence ≥ 0.9 & entropy ≤ 0.2
            coherence = attempt.score.get("coherence", 0)
            entropy = attempt.score.get("entropy", 1)
            if coherence >= 0.9 and entropy <= 0.2:
                self.solved_log.append(task)
                if self._journal_path:
                    self._journal_path.parent.mkdir(parents=True, exist_ok=True)
                    with self._journal_path.open("a", encoding="utf-8") as fp:
                        fp.write(json.dumps(task.__dict__, default=str) + "\n")

    # ------------------------- Maintenance -----------------------------
    async def flush_old_tasks(self) -> None:
        """Drop tasks that exceeded TTL or are already solved."""
        now = datetime.now(timezone.utc)
        async with self._lock:
            while self.task_queue and (
                now - self.task_queue[0].created_at > self.ttl
                or self.task_queue[0] in self.solved_log
            ):
                self.task_queue.popleft()

    # ------------------------ HTTP helper stubs -------------------------
    # These can be wired into Flask / FastAPI routers.
    def list_pending_tasks(self, limit: int = 50) -> List[TripletTask]:
        return list(self.task_queue)[:limit]

    def get_triplet_score(self, triplet_id: str) -> Optional[List[Attempt]]:
        return self.attempt_registry.get(triplet_id)


# ---------------------------------------------------------------------------
# Default metric plug‑ins
# ---------------------------------------------------------------------------

@SymbolicTaskEngine.register_metric("entropy")
def entropy_metric(task: TripletTask, attempt: Attempt) -> float:  # 0=low entropy
    """Shannon‑like entropy over unigram motif distribution (simple baseline)."""
    from math import log2

    counter: Dict[str, int] = defaultdict(int)
    for m in attempt.produced_output:
        counter[m] += 1
    total = sum(counter.values()) or 1
    probs = [c / total for c in counter.values()]
    h = -(sum(p * log2(p) for p in probs))
    return min(h / 5.0, 1.0)  # crude normalisation


@SymbolicTaskEngine.register_metric("coherence")
def coherence_metric(task: TripletTask, attempt: Attempt) -> float:  # 1=perfect
    """Normalised edit‑distance similarity between expected and produced output."""
    if task.expected_output is None:
        return 0.0
    import difflib

    s1 = " ".join(task.expected_output)
    s2 = " ".join(attempt.produced_output)
    return difflib.SequenceMatcher(None, s1, s2).ratio()


# ---------------------------------------------------------------------------
# Module export list
# ---------------------------------------------------------------------------

__all__ = [
    "TripletTask",
    "Attempt",
    "SymbolicTaskEngine",
]

# END_OF_FILE
