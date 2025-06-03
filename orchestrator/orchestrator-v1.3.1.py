# orchestrator.py · v1.3.1 — Noor Triad + Symbolic Engine Integration with Motif‑Memory Bootstrap

from __future__ import annotations

__version__ = "1.3.1"
_SCHEMA_VERSION__ = "2025-Q3-orchestrator-memory"

import argparse
import asyncio
import json
import logging
import os
import random
import signal
import sys
import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from typing import List

# Third‑party metrics server
from prometheus_client import start_http_server  # exposed elsewhere; may stub below

# ─── Prometheus safe‑import (falls back to no‑op stubs) ─────────────────────────
try:
    from prometheus_client import Counter, Gauge, Histogram
except ImportError:  # pragma: no cover
    class _Stub:  # noqa: D401
        def labels(self, *_, **__):
            return self

        def inc(self, *_):
            ...

        def set(self, *_):
            ...

        def observe(self, *_):
            ...

    Counter = Gauge = Histogram = _Stub  # type: ignore

# ─── Triad modules ──────────────────────────────────────────────────────────────
from noor.logical_agent_at import LogicalAgentAT
from noor.noor_fasttime_core import NoorFastTimeCore
from noor.recursive_agent_ft import RecursiveAgentFT
from noor.symbolic_task_engine import SymbolicTaskEngine
from noor.symbolic_api import app as symbolic_api_app

from noor.motif_memory_manager import get_global_memory_manager

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# ─── Seeding metrics ────────────────────────────────────────────────────────────
SEED_TOTAL = Gauge(
    "orchestrator_motif_seed_total",
    "Motifs seeded into STMM at boot",
    ["agent_id"],
)
SEED_LATENCY = Histogram(
    "orchestrator_seed_latency_seconds",
    "Latency of motif‑manifest load",
    ["agent_id"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 1, 2, 5),
)
SEED_FAILURES = Counter(
    "orchestrator_seed_failures_total",
    "Errors during motif‑manifest seeding",
    ["agent_id", "reason"],
)

# ─── Engine‑liveness metric ───────────────────────────────────────────
ENGINE_STATE = Gauge(
    "orchestrator_engine_state",
    "Symbolic engine state (0=dead,1=running)",
    ["agent_id"],
)

# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the Noor triadic core.")
    p.add_argument("--agent-id", default="agent@main")
    p.add_argument("--watcher-id", default="watcher@main")
    p.add_argument("--core-id", default="core@main")
    p.add_argument("--max-parallel", type=int, default=8)
    p.add_argument("--latency-budget", type=float, default=0.05)
    p.add_argument("--snapshot-cap", type=int, default=8, help="kB")
    p.add_argument("--tick-rate", type=float, default=50.0, help="ticks/sec")
    p.add_argument("--motifs", nargs="+", default=["α", "β", "γ"])
    p.add_argument("--metrics-port", type=int, default=8000)
    p.add_argument("--log-level", default="INFO")
    p.add_argument("--async-mode", action="store_true")
    p.add_argument("--low-latency-mode", action="store_true")
    p.add_argument("--symbolic-api-port", type=int, default=7070)
    p.add_argument("--api-host", default="127.0.0.1",
                   help="Bind address for the symbolic API (default: 127.0.0.1)")
    p.add_argument("--hmac-secret",
                   default=os.getenv("NOOR_HMAC_SECRET"),
                   help="Shared HMAC secret (env NOOR_HMAC_SECRET if omitted)")
    # motif‑memory bootstrap
    p.add_argument(
        "--motif-manifest",
        default="compiled/motif_ontology.json",
        help="Path to ontology manifest (JSON)",
    )
    p.add_argument(
        "--seed-boost",
        type=float,
        default=1.0,
        help="Boost applied per motif during memory seeding",
    )
    return p

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def init_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    )


def build_triad(args) -> tuple[LogicalAgentAT, NoorFastTimeCore, RecursiveAgentFT]:
    watcher = LogicalAgentAT(
        agent_id=args.watcher_id,
        hmac_secret=None,
        async_mode=args.async_mode,
    )
    core = NoorFastTimeCore(
        agent_id=args.core_id,
        max_parallel=args.max_parallel,
        snapshot_cap_kb=args.snapshot_cap,
        latency_budget=args.latency_budget,
        hmac_secret=args.hmac_secret,
        async_mode=args.async_mode,
        low_latency_mode=args.low_latency_mode,
    )
    agent = RecursiveAgentFT(
        initial_state=[0.0, 0.0, 0.0],
        watchers=[watcher],
        agent_id=args.agent_id,
        max_parallel=args.max_parallel,
        hmac_secret=args.hmac_secret,
        core=core,
        latency_budget=args.latency_budget,
        async_mode=args.async_mode,
        low_latency_mode=args.low_latency_mode,
    )
    return watcher, core, agent

# ──────────────────────────────────────────────────────────────
# Motif‑memory bootstrapper
# ──────────────────────────────────────────────────────────────

def seed_motif_memory(args):
    """Load motif manifest and pre‑seed STMM. Safe‑no‑op on failure."""
    manifest_path = Path(args.motif_manifest)
    start = time.perf_counter()
    try:
        with manifest_path.open("r", encoding="utf-8") as fp:
            motifs = json.load(fp).get("motifs", [])
    except FileNotFoundError:
        logging.warning(
            "[orchestrator] %s not found — skipping memory seed", manifest_path
        )
        SEED_FAILURES.labels(args.agent_id, "file_missing").inc()
        return
    except Exception as exc:  # pragma: no cover
        logging.warning("[orchestrator] Unable to parse manifest: %s", exc)
        SEED_FAILURES.labels(args.agent_id, "json_error").inc()
        return

    memory = get_global_memory_manager()
    for motif_id in motifs:
        memory.access(motif_id, boost=args.seed_boost)

    latency = time.perf_counter() - start
    SEED_TOTAL.labels(args.agent_id).set(len(motifs))
    SEED_LATENCY.labels(args.agent_id).observe(latency)
    logging.info(
        "[orchestrator] Seeded STMM with %d motifs in %.3fs", len(motifs), latency
    )

# ──────────────────────────────────────────────────────────────
# Symbolic API Launcher
# ──────────────────────────────────────────────────────────────

def run_symbolic_api(port: int, host: str):
    import uvicorn

    uvicorn.run(symbolic_api_app, host=host, port=port, log_level="info")

# ──────────────────────────────────────────────────────────────
# Main Loop
# ──────────────────────────────────────────────────────────────


async def main_async(args):
    watcher, core, agent = build_triad(args)

    # Motif‑memory bootstrap (must precede any ticks)
    seed_motif_memory(args)

    # Init symbolic reasoning engine
    from noor.symbolic_task_engine import SymbolicTaskEngine
    symbolic_engine = SymbolicTaskEngine.INSTANCE or SymbolicTaskEngine()
    SymbolicTaskEngine.INSTANCE = symbolic_engine

    ENGINE_STATE.labels(args.agent_id).set(1)

    # Launch symbolic API (if enabled)
    if args.symbolic_api_port > 0:
        Thread(
            target=run_symbolic_api,
            args=(args.symbolic_api_port, args.api_host),
            daemon=True,
        ).start()

    # Prometheus metrics
    if args.metrics_port > 0:
        start_http_server(addr="0.0.0.0", port=args.metrics_port)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    import platform
    if platform.system() != "Windows":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

    tick_interval = 1.0 / args.tick_rate
    logging.getLogger("orchestrator").info("Triad online ‑ %s ticks/sec", args.tick_rate)

    await stop_event.wait()

# ──────────────────────────────────────────────────────────────

def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # ─── basic bounds check ───────────────────────────────────────────
    if not (0 < args.tick_rate <= 1_000):
        parser.error("--tick-rate must be > 0 and ≤ 1000")
    init_logging(args.log_level)
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main(sys.argv[1:])

# END_OF_FILE
