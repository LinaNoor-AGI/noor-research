# symbolic_task_engine.py · v1.0.4b INDEX.REEF Motifs
# Coordinates symbolic task lifecycle (propose, solve, evaluate, journal)

from __future__ import annotations

import asyncio
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Deque, Dict, List, Optional
from uuid import uuid4

# ─────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class TripletTask:
    input_motif: List[str]
    instruction: str
    expected_output: Optional[List[str]] = None

    triplet_id: str = field(default_factory=lambda: uuid4().hex, init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)


@dataclass(slots=True)
class Attempt:
    produced_output: List[str]
    score: Dict[str, float]
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ─────────────────────────────────────────────────
# Symbolic Task Engine
# ─────────────────────────────────────────────────

class SymbolicTaskEngine:
    METRIC_FUNCS: Dict[str, Callable[[TripletTask, Attempt], float]] = {}
    INSTANCE: Optional[SymbolicTaskEngine] = None  # Singleton

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
    ) -> None:
        self.task_queue: Deque[TripletTask] = deque(maxlen=max_pending)
        self.attempt_registry: Dict[str, List[Attempt]] = defaultdict(list)
        self.solved_log: List[TripletTask] = []
        self.entropy_buffer: Deque[float] = deque(maxlen=100)
        self.ttl = timedelta(seconds=ttl_seconds)
        self._lock = asyncio.Lock()
        self._journal_path = Path(journal_path) if journal_path else None
        self._log_path = Path("logs/noor_expressions.txt")
        self.index_lookup = self._load_reflections_from_reef(index_path)

    def _load_reflections_from_reef(self, path: str) -> dict[str, str]:
        lookup = {}
        current_motif = None
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("motif_id"):
                        current_motif = stripped.split("=", 1)[1].strip().lower().replace("‑", "-").replace("–", "-")
                    elif stripped.startswith("expression") and current_motif:
                        expr = stripped.split("=", 1)[1].strip()
                        if current_motif not in lookup:
                            lookup[current_motif] = expr
                        current_motif = None
        except Exception as e:
            print(f"⚠️ Failed to load reflections from REEF: {e}")
        return lookup

    def resolve_expression_from_index(self, motif: str, content: str = "") -> str:
        motif = motif.lower().strip().replace("‑", "-").replace("–", "-")
        return self.index_lookup.get(motif, "Noor remains quiet.")

    def log_motif(self, motif: str, content: str, response: str | None = None, inferred: bool = False) -> None:
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resolved_response = response or self.resolve_expression_from_index(motif, content)
            with self._log_path.open("a", encoding="utf-8") as log:
                if inferred:
                    log.write(f"[{timestamp}] Inferred motif: {motif}\n")
                else:
                    log.write(f"[{timestamp}] Motif: {motif} | Content: {content or '[empty]'} | Response: {resolved_response}\n")
        except Exception as e:
            print(f"⚠️ Failed to log motif: {e}")

    def current_inferred_motifs(self) -> List[str]:
        return [task.input_motif[0] for task in self.solved_log[-5:] if task.instruction == "compose"]

    async def propose_from_motifs(self, recent_motifs: List[str]) -> TripletTask:
        task = TripletTask(
            input_motif=[recent_motifs[0]],
            instruction="compose",
            expected_output=list(reversed(recent_motifs)),
        )
        async with self._lock:
            self.task_queue.append(task)
        return task

    async def solve_task(self, task: TripletTask) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._solve_impl(task))

    async def _solve_impl(self, task: TripletTask) -> None:
        produced_output = task.input_motif + [task.instruction]
        attempt = Attempt(produced_output=produced_output, score={})
        attempt.score = self.evaluate_attempt(task, attempt)
        await self.log_feedback(task, attempt)

    def evaluate_attempt(self, task: TripletTask, attempt: Attempt) -> Dict[str, float]:
        scores = {
            name: fn(task, attempt) for name, fn in self.METRIC_FUNCS.items()
        }
        if scores:
            self.entropy_buffer.append(next(iter(scores.values())))
        return scores

    async def log_feedback(self, task: TripletTask, attempt: Attempt) -> None:
        async with self._lock:
            self.attempt_registry[task.triplet_id].append(attempt)
            coherence = attempt.score.get("coherence", 0)
            entropy = attempt.score.get("entropy", 1)
            if coherence >= 0.9 and entropy <= 0.2:
                self.solved_log.append(task)
                if self._journal_path:
                    self._journal_path.parent.mkdir(parents=True, exist_ok=True)
                    with self._journal_path.open("a", encoding="utf-8") as fp:
                        fp.write(json.dumps(task.__dict__, default=str) + "\n")

    async def flush_old_tasks(self) -> None:
        now = datetime.now(timezone.utc)
        async with self._lock:
            while self.task_queue and (
                now - self.task_queue[0].created_at > self.ttl
                or self.task_queue[0] in self.solved_log
            ):
                self.task_queue.popleft()

    def list_pending_tasks(self, limit: int = 50) -> List[TripletTask]:
        return list(self.task_queue)[:limit]

    def get_triplet_score(self, triplet_id: str) -> Optional[List[Attempt]]:
        return self.attempt_registry.get(triplet_id)


# ─────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────

@SymbolicTaskEngine.register_metric("entropy")
def entropy_metric(task: TripletTask, attempt: Attempt) -> float:
    from math import log2
    counter: Dict[str, int] = defaultdict(int)
    for m in attempt.produced_output:
        counter[m] += 1
    total = sum(counter.values()) or 1
    probs = [c / total for c in counter.values()]
    h = -(sum(p * log2(p) for p in probs))
    return min(h / 5.0, 1.0)


@SymbolicTaskEngine.register_metric("coherence")
def coherence_metric(task: TripletTask, attempt: Attempt) -> float:
    if task.expected_output is None:
        return 0.0
    import difflib
    s1 = " ".join(task.expected_output)
    s2 = " ".join(attempt.produced_output)
    return difflib.SequenceMatcher(None, s1, s2).ratio()


__all__ = [
    "TripletTask",
    "Attempt",
    "SymbolicTaskEngine",
]

# END_OF_FILE
