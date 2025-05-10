"""
orchestrator.py · production bootstrap for the Noor triad

Spin‑up order
─────────────
Logical Watcher → Fast‑Time Core → Recursive Agent

The orchestrator:
• parses CLI flags (no hidden env magic)
• starts a Prometheus HTTP endpoint (optional)
• runs the agent’s spawn loop at a configurable rate
• wires Core feedback automatically
• handles graceful shutdown on SIGINT/SIGTERM
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import random
import signal
import sys
from pathlib import Path
from typing import List

from prometheus_client import start_http_server

from noor.logical_agent_at import LogicalAgentAT
from noor.noor_fasttime_core import NoorFastTimeCore
from noor.recursive_agent_ft import RecursiveAgentFT

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
    return p


# ──────────────────────────────────────────────────────────────
# Bootstrap helpers
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
# Main async loop
# ──────────────────────────────────────────────────────────────
async def run_loop(agent: RecursiveAgentFT, motifs: List[str], tick_interval: float, stop_event: asyncio.Event):
    i = 0
    while not stop_event.is_set():
        motif = motifs[i % len(motifs)] if motifs else f"μ:{i}"
        await agent.spawn(motif)
        i += 1
        await asyncio.sleep(tick_interval)


async def main_async(args):
    watcher, core, agent = build_triad(args)

    # Prometheus endpoint
    if args.metrics_port > 0:
        start_http_server(addr="0.0.0.0", port=args.metrics_port)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    tick_interval = 1.0 / args.tick_rate
    logging.getLogger("orchestrator").info("Triad online ‑ %s ticks/sec", args.tick_rate)

    await asyncio.gather(run_loop(agent, args.motifs, tick_interval, stop_event), stop_event.wait())
    logging.getLogger("orchestrator").info("Shutdown complete.")


def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)
    init_logging(args.log_level)
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main(sys.argv[1:])

# END_OF_FILE
