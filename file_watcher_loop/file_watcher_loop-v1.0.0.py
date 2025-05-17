# file_watcher_loop.py (v1.0.0)

import os
import logging
import asyncio
from datetime import datetime, timedelta
from noor.symbolic_task_engine import SymbolicTaskEngine

async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    reflections = SymbolicTaskEngine.INSTANCE.reflections

    while not stop_event.is_set():
        current_files = set(os.listdir(input_dir))
        current_motif_files = {f for f in current_files if f.endswith(".txt")}
        current_motifs = {os.path.splitext(f)[0].lower() for f in current_motif_files}

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

                SymbolicTaskEngine.INSTANCE.log_motif(motif, content, response)
                SymbolicTaskEngine.INSTANCE.attempt_inference()

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

        await asyncio.sleep(0.5)
