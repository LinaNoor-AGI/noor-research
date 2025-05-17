# orchestrator.py · v1.2.0 — Noor Triad + Symbolic Engine Integration

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import random
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from typing import List

from prometheus_client import start_http_server

from noor.logical_agent_at import LogicalAgentAT
from noor.noor_fasttime_core import NoorFastTimeCore
from noor.recursive_agent_ft import RecursiveAgentFT
from noor.symbolic_task_engine import SymbolicTaskEngine
from noor.symbolic_api import app as symbolic_api_app

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
        hmac_secret=None,
        async_mode=args.async_mode,
        low_latency_mode=args.low_latency_mode,
    )
    agent = RecursiveAgentFT(
        initial_state=[0.0, 0.0, 0.0],
        watchers=[watcher],
        agent_id=args.agent_id,
        max_parallel=args.max_parallel,
        hmac_secret=None,
        core=core,
        latency_budget=args.latency_budget,
        async_mode=args.async_mode,
        low_latency_mode=args.low_latency_mode,
    )
    return watcher, core, agent

# ──────────────────────────────────────────────────────────────
# Symbolic API Launcher
# ──────────────────────────────────────────────────────────────
def run_symbolic_api(port: int):
    import uvicorn
    uvicorn.run(symbolic_api_app, host="0.0.0.0", port=port, log_level="info")

# ──────────────────────────────────────────────────────────────
# Main Loop
# ──────────────────────────────────────────────────────────────
async def main_async(args):
    watcher, core, agent = build_triad(args)

    # Init symbolic reasoning engine
    SymbolicTaskEngine.install()

    # Launch symbolic API
    Thread(target=run_symbolic_api, args=(args.symbolic_api_port,), daemon=True).start()

    # Prometheus metrics
    if args.metrics_port > 0:
        start_http_server(addr="0.0.0.0", port=args.metrics_port)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    import platform
    if platform.system() != "Windows":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
    else:
        pass  # Let Ctrl+C raise KeyboardInterrupt

    tick_interval = 1.0 / args.tick_rate
    logging.getLogger("orchestrator").info("Triad online ‑ %s ticks/sec", args.tick_rate)

    # Motif loop
    from noor.file_watcher_loop import file_watcher_loop
    await asyncio.gather(
        file_watcher_loop(agent, "./motifs_in", stop_event),
        stop_event.wait()
    )

# ──────────────────────────────────────────────────────────────
def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)
    init_logging(args.log_level)
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main(sys.argv[1:])

# END_OF_FILE
