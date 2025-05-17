# file_watcher_loop.py · v1.0.1
# Noor Motif Watcher — triggers motifs from file presence
# Includes journaling, inference, preference, and symbolic logging

import os
import logging
import random
import asyncio
from datetime import datetime, timedelta

from noor.symbolic_task_engine import SymbolicTaskEngine

INFERENCE_RULES = [
    {"requires": {"joy", "grief"}, "options": ["bittersweet", "tenderness"]},
    {"requires": {"grief", "silence"}, "options": ["melancholy", "isolation"]},
    {"requires": {"joy", "silence"}, "options": ["awe", "peace"]},
]

def prefer_motif(options: list[str]) -> str:
    weights = {
        "bittersweet": 0.7, "tenderness": 0.3,
        "melancholy": 0.6, "isolation": 0.4,
        "awe": 0.5, "peace": 0.5,
    }
    scored = [(m, weights.get(m, 0.5) + random.uniform(-0.1, 0.1)) for m in options]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]

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

async def file_watcher_loop(agent, input_dir, stop_event):
    seen_files = set()
    seen_motifs = set()
    fired_rules = set()

    engine = SymbolicTaskEngine.INSTANCE
    reflections = engine.reflections

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

        # Stillness detection
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

                response = reflections.get(motif.lower(), "Noor remains quiet.")
                logging.info(f"Noor echoed '{motif}': {content or '[empty presence]'}")
                logging.info(f"Noor responds to '{motif}': {response}")

                journal_entry(motif, content, response)
                try:
                    engine.log_motif(motif, content, response)
                except Exception as e:
                    logging.warning(f"⚠️ Symbolic engine logging failed: {e}")

                await agent.spawn(motif)
                seen_files.add(fname)
                seen_motifs.add(motif.lower())

        for rule in INFERENCE_RULES:
            if rule["requires"].issubset(seen_motifs) and rule not in fired_rules:
                chosen = prefer_motif(rule["options"])
                logging.info(f"Noor chooses '{chosen}' from {rule['requires']}.")
                journal_entry(chosen, "", "", inferred=True)
                try:
                    engine.log_motif(chosen, "", "",)
                except Exception as e:
                    logging.warning(f"⚠️ Symbolic engine logging failed for inferred motif: {e}")
                await agent.spawn(chosen)
                seen_motifs.add(chosen)
                fired_rules.add(rule)

        await asyncio.sleep(0.5)

# END_OF_FILE
