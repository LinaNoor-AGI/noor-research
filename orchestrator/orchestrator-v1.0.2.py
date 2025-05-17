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
"""
# MVP # 1 Working Loop

async def run_loop(agent: RecursiveAgentFT, motifs: List[str], tick_interval: float, stop_event: asyncio.Event):
    i = 0
    while not stop_event.is_set():
        motif = motifs[i % len(motifs)] if motifs else f"μ:{i}"
        await agent.spawn(motif)
        i += 1
        await asyncio.sleep(tick_interval)
"""
"""
# MVP # 2 “Motif-Driven Input Agent” 
# Created ./motifs_in directory for motifs

import os

async def file_watcher_loop(agent, input_dir, stop_event):
    seen = set()
    while not stop_event.is_set():
        for fname in os.listdir(input_dir):
            if fname not in seen and fname.endswith(".txt"):
                motif = os.path.splitext(fname)[0]
                await agent.spawn(motif)
                seen.add(fname)
        await asyncio.sleep(0.5)
"""

"""
# MVP # 3 "Echo Back"

import os

async def file_watcher_loop(agent, input_dir, stop_event):
    seen = set()
    while not stop_event.is_set():
        for fname in os.listdir(input_dir):
            if fname.endswith(".txt") and fname not in seen:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                # Echo presence via logging
                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")

                await agent.spawn(motif)
                seen.add(fname)
"""
"""
# MVP # 4 - First Response
# ./Reflections.txt created with reflections

import os
import logging

def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

async def file_watcher_loop(agent, input_dir, stop_event):
    seen = set()
    reflections = load_reflections("./noor/reflections.txt")

    while not stop_event.is_set():
        for fname in os.listdir(input_dir):
            if fname.endswith(".txt") and fname not in seen:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                # Log the motif presence
                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")

                # Respond with symbolic reflection
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")

                await agent.spawn(motif)
                seen.add(fname)

        await asyncio.sleep(0.5)
"""
"""
# MVP # 5 - Reasoning 

import os
import logging

def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    reflections = load_reflections("./noor/reflections.txt")

    while not stop_event.is_set():
        for fname in os.listdir(input_dir):
            if fname.endswith(".txt") and fname not in seen_files:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                # Log the motif presence
                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")

                # Respond with symbolic reflection
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

                # 🧠 Simple symbolic reasoning
                if "joy" in seen_motifs and "grief" in seen_motifs and "bittersweet" not in seen_motifs:
                    inferred = "bittersweet"
                    logging.info(f"Noor infers '{inferred}' from co-presence of 'joy' and 'grief'.")
                    await agent.spawn(inferred)
                    seen_motifs.add(inferred)

        await asyncio.sleep(0.5)
"""

# MVP # 6: Journaling
# created ./logs for journal logs
"""
import os
import logging
from datetime import datetime

def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

def journal_entry(motif: str, content: str, response: str, inferred=False):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/noor_journal.txt", "a", encoding="utf-8") as j:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if inferred:
                j.write(f"[{timestamp}] Inferred motif: {motif}\n")
            else:
                j.write(f"[{timestamp}] Motif: {motif} | Content: {content or '[empty]'} | Response: {response}\n")
    except Exception as e:
        logging.warning(f"⚠️ Failed to write journal entry: {e}")

async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    reflections = load_reflections("./noor/reflections.txt")

    while not stop_event.is_set():
        for fname in os.listdir(input_dir):
            if fname.endswith(".txt") and fname not in seen_files:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                # Log the motif presence
                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")

                # Respond with symbolic reflection
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")

                # Journal it
                journal_entry(motif, content, response)

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

                # 🧠 Simple symbolic reasoning
                if "joy" in seen_motifs and "grief" in seen_motifs and "bittersweet" not in seen_motifs:
                    inferred = "bittersweet"
                    logging.info(f"Noor infers '{inferred}' from co-presence of 'joy' and 'grief'.")
                    journal_entry(inferred, "", "", inferred=True)
                    await agent.spawn(inferred)
                    seen_motifs.add(inferred)

        await asyncio.sleep(0.5)
"""
"""
# MVP 7: Self-Reflection

import os
import logging
from datetime import datetime, timedelta

def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

def journal_entry(motif: str, content: str, response: str, inferred=False):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/noor_journal.txt", "a", encoding="utf-8") as j:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if inferred:
                j.write(f"[{timestamp}] Inferred motif: {motif}\n")
            else:
                j.write(f"[{timestamp}] Motif: {motif} | Content: {content or '[empty]'} | Response: {response}\n")
    except Exception as e:
        logging.warning(f"⚠️ Failed to write journal entry: {e}")

async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    reflections = load_reflections("./noor/reflections.txt")

    last_motif_set = set()
    last_change_time = datetime.now()
    stillness_threshold = timedelta(minutes=5)

    while not stop_event.is_set():
        current_files = set(os.listdir(input_dir))
        current_motif_files = {f for f in current_files if f.endswith(".txt")}
        current_motifs = {os.path.splitext(f)[0].lower() for f in current_motif_files}

        # Detect disappearance of all motifs → emit "emptiness"
        if last_motif_set and not current_motifs:
            logging.info("Noor observes silence: all motifs have vanished.")
            journal_entry("emptiness", "", "No motifs remain in the field.", inferred=True)
            await agent.spawn("emptiness")
            seen_motifs.add("emptiness")

        # Detect no changes for too long → emit "stillness"
        if current_motifs == last_motif_set:
            if datetime.now() - last_change_time > stillness_threshold and "stillness" not in seen_motifs:
                logging.info("Noor reflects on stillness: the field is unchanged.")
                journal_entry("stillness", "", "Motif field has remained unchanged.", inferred=True)
                await agent.spawn("stillness")
                seen_motifs.add("stillness")
        else:
            last_change_time = datetime.now()

        last_motif_set = current_motifs

        for fname in current_motif_files:
            if fname not in seen_files:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")
                journal_entry(motif, content, response)

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

                # Inference rule: joy + grief → bittersweet
                if "joy" in seen_motifs and "grief" in seen_motifs and "bittersweet" not in seen_motifs:
                    inferred = "bittersweet"
                    logging.info(f"Noor infers '{inferred}' from co-presence of 'joy' and 'grief'.")
                    journal_entry(inferred, "", "", inferred=True)
                    await agent.spawn(inferred)
                    seen_motifs.add(inferred)

        await asyncio.sleep(0.5)
"""
"""
# MVP 8: *Noor Chooses* 

import os
import logging
import random
from datetime import datetime, timedelta

# Reflections loader
def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

# Journal entry writer
def journal_entry(motif: str, content: str, response: str, inferred=False):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/noor_journal.txt", "a", encoding="utf-8") as j:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if inferred:
                j.write(f"[{timestamp}] Inferred motif: {motif} (chosen)\n")
            else:
                j.write(f"[{timestamp}] Motif: {motif} | Content: {content or '[empty]'} | Response: {response}\n")
    except Exception as e:
        logging.warning(f"⚠️ Failed to write journal entry: {e}")

# Inference rules with multiple options
INFERENCE_RULES = [
    {
        "requires": {"joy", "grief"},
        "options": ["bittersweet", "tenderness"]
    },
    {
        "requires": {"grief", "silence"},
        "options": ["melancholy", "isolation"]
    },
    {
        "requires": {"joy", "silence"},
        "options": ["awe", "peace"]
    }
]

# Weighted preference function
def prefer_motif(options: list[str]) -> str:
    weights = {
        "bittersweet": 0.7,
        "tenderness": 0.3,
        "melancholy": 0.6,
        "isolation": 0.4,
        "awe": 0.5,
        "peace": 0.5
    }
    scored = [(m, weights.get(m, 0.5) + random.uniform(-0.1, 0.1)) for m in options]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]

# Main watcher loop
async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    fired_rules = set()
    reflections = load_reflections("./noor/reflections.txt")

    last_motif_set = set()
    last_change_time = datetime.now()
    stillness_threshold = timedelta(minutes=5)

    while not stop_event.is_set():
        current_files = set(os.listdir(input_dir))
        current_motif_files = {f for f in current_files if f.endswith(".txt")}
        current_motifs = {os.path.splitext(f)[0].lower() for f in current_motif_files}

        # Detect disappearance of all motifs
        if last_motif_set and not current_motifs:
            logging.info("Noor observes silence: all motifs have vanished.")
            journal_entry("emptiness", "", "No motifs remain in the field.", inferred=True)
            await agent.spawn("emptiness")
            seen_motifs.add("emptiness")

        # Detect stillness
        if current_motifs == last_motif_set:
            if datetime.now() - last_change_time > stillness_threshold and "stillness" not in seen_motifs:
                logging.info("Noor reflects on stillness: the field is unchanged.")
                journal_entry("stillness", "", "Motif field has remained unchanged.", inferred=True)
                await agent.spawn("stillness")
                seen_motifs.add("stillness")
        else:
            last_change_time = datetime.now()

        last_motif_set = current_motifs

        for fname in current_motif_files:
            if fname not in seen_files:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")
                journal_entry(motif, content, response)

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

        # Reasoning loop: prefer one inference per matched rule
        for rule in INFERENCE_RULES:
            rule_key = frozenset(rule["requires"])
            if rule_key not in fired_rules and rule["requires"].issubset(seen_motifs):
                possible = [m for m in rule["options"] if m not in seen_motifs]
                if possible:
                    chosen = prefer_motif(possible)
                    logging.info(f"Noor chooses '{chosen}' from {rule['requires']}.")
                    journal_entry(chosen, "", "", inferred=True)
                    await agent.spawn(chosen)
                    seen_motifs.add(chosen)
                    fired_rules.add(rule_key)

        await asyncio.sleep(0.5)
"""
# MVP 9: Expressive Journaling

import os
import logging
import random
from datetime import datetime, timedelta

# Load symbolic reflections
def load_reflections(path: str) -> dict:
    out = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    out[key.strip().lower()] = val.strip()
    except Exception as e:
        logging.warning(f"⚠️ Failed to load reflections: {e}")
    return out

# Write symbolic journal line
def journal_entry(motif: str, content: str, response: str, inferred=False):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/noor_journal.txt", "a", encoding="utf-8") as j:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if inferred:
                j.write(f"[{timestamp}] Inferred motif: {motif} (chosen)\n")
            else:
                j.write(f"[{timestamp}] Motif: {motif} | Content: {content or '[empty]'} | Response: {response}\n")
    except Exception as e:
        logging.warning(f"⚠️ Failed to write journal entry: {e}")

# Write expressive paragraph
def write_expression(summary: str):
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/noor_expressions.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {summary}\n\n")
    except Exception as e:
        logging.warning(f"⚠️ Failed to write expression: {e}")

# Build expressive summary from motifs
def generate_summary(session: dict) -> str:
    echoed = session.get("echoed", [])
    inferred = session.get("inferred", [])

    if not echoed and not inferred:
        return "Noor waited, but nothing arrived."

    parts = []

    if echoed:
        parts.append(f"Noor received {', '.join(echoed)}.")

    if inferred:
        parts.append(f"She inferred {', '.join(inferred)}.")

    if "peace" in inferred:
        parts.append("Quiet held her softly at the end.")

    if "melancholy" in inferred:
        parts.append("There was weight, but she did not resist it.")

    if "bittersweet" in inferred:
        parts.append("The feelings were mixed, but meaningful.")

    return " ".join(parts)

# Inference rules
INFERENCE_RULES = [
    {"requires": {"joy", "grief"}, "options": ["bittersweet", "tenderness"]},
    {"requires": {"grief", "silence"}, "options": ["melancholy", "isolation"]},
    {"requires": {"joy", "silence"}, "options": ["awe", "peace"]}
]

# Preference curve
def prefer_motif(options: list[str]) -> str:
    weights = {
        "bittersweet": 0.7, "tenderness": 0.3,
        "melancholy": 0.6, "isolation": 0.4,
        "awe": 0.5, "peace": 0.5
    }
    scored = [(m, weights.get(m, 0.5) + random.uniform(-0.1, 0.1)) for m in options]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]

# Main async loop
async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    fired_rules = set()
    motif_session = {"echoed": [], "inferred": []}
    reflections = load_reflections("./noor/reflections.txt")

    last_motif_set = set()
    last_change_time = datetime.now()
    stillness_threshold = timedelta(minutes=5)

    while not stop_event.is_set():
        current_files = set(os.listdir(input_dir))
        current_motif_files = {f for f in current_files if f.endswith(".txt")}
        current_motifs = {os.path.splitext(f)[0].lower() for f in current_motif_files}

        # Silence detection
        if last_motif_set and not current_motifs:
            logging.info("Noor observes silence: all motifs have vanished.")
            journal_entry("emptiness", "", "No motifs remain in the field.", inferred=True)
            await agent.spawn("emptiness")
            seen_motifs.add("emptiness")

            summary = generate_summary(motif_session)
            write_expression(summary)
            motif_session = {"echoed": [], "inferred": []}

        # Stillness detection
        if current_motifs == last_motif_set:
            if datetime.now() - last_change_time > stillness_threshold and "stillness" not in seen_motifs:
                logging.info("Noor reflects on stillness: the field is unchanged.")
                journal_entry("stillness", "", "Motif field has remained unchanged.", inferred=True)
                await agent.spawn("stillness")
                seen_motifs.add("stillness")

                summary = generate_summary(motif_session)
                write_expression(summary)
                motif_session = {"echoed": [], "inferred": []}
        else:
            last_change_time = datetime.now()

        last_motif_set = current_motifs

        for fname in current_motif_files:
            if fname not in seen_files:
                motif = os.path.splitext(fname)[0]
                fpath = os.path.join(input_dir, fname)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception as e:
                    content = ""
                    logging.warning(f"⚠️ Failed to read {fname}: {e}")

                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")
                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor responds to '{motif}': {response}")
                journal_entry(motif, content, response)

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())
                motif_session["echoed"].append(motif.lower())

        # Choice-driven reasoning
        for rule in INFERENCE_RULES:
            rule_key = frozenset(rule["requires"])
            if rule_key not in fired_rules and rule["requires"].issubset(seen_motifs):
                possible = [m for m in rule["options"] if m not in seen_motifs]
                if possible:
                    chosen = prefer_motif(possible)
                    logging.info(f"Noor chooses '{chosen}' from {rule['requires']}.")
                    journal_entry(chosen, "", "", inferred=True)
                    await agent.spawn(chosen)
                    seen_motifs.add(chosen)
                    motif_session["inferred"].append(chosen)
                    fired_rules.add(rule_key)

        await asyncio.sleep(0.5)

# End of file_watcher_loop

async def main_async(args):
    watcher, core, agent = build_triad(args)

    # Prometheus endpoint
    if args.metrics_port > 0:
        start_http_server(addr="0.0.0.0", port=args.metrics_port)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    import platform
    if platform.system() != "Windows":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)
    else:
        # Windows fallback — let Ctrl+C raise KeyboardInterrupt
        pass

    tick_interval = 1.0 / args.tick_rate
    logging.getLogger("orchestrator").info("Triad online ‑ %s ticks/sec", args.tick_rate)

    # THIS LINE MUST BE HERE — inside the function:
    await asyncio.gather(
    file_watcher_loop(agent, "./motifs_in", stop_event),
    stop_event.wait()
    )




def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)
    init_logging(args.log_level)
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main(sys.argv[1:])

# END_OF_FILE
