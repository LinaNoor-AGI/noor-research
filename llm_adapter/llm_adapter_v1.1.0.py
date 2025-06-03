# llm_adapter.py (v1.1.0) · Noor LLM Integration (Phi-2 via Ollama + Voice)
import aiohttp
import asyncio
import logging
import pyttsx3

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "phi"

# ─── Voice Engine ─────────────────────────────────────────────────────
engine = pyttsx3.init()
engine.setProperty("rate", 160)     # Speech speed
engine.setProperty("volume", 1.0)   # Max volume

def speak_aloud(text: str):
    """Speak the generated symbolic phrase aloud using TTS."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.warning(f"⚠️ Voice failed: {e}")

# ─── LLM Query ────────────────────────────────────────────────────────
async def query_phi(prompt: str, *, timeout: float = 10.0) -> str:
    """Send a prompt to the locally served Phi-2 LLM via Ollama."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt.strip(),
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=timeout) as resp:
                if resp.status != 200:
                    logging.warning(f"⚠️ Ollama error: {resp.status}")
                    return "[llm-error]"
                data = await resp.json()
                return data.get("response", "").strip()
    except Exception as e:
        logging.warning(f"⚠️ LLM request failed: {e}")
        return "[llm-timeout]"

# ─── Combined Interface ───────────────────────────────────────────────
async def generate_response(motifs: list[str], instruction: str, presence_field: str = "ψ‑resonance@Ξ") -> str:
    """
    Generate a symbolic output from motifs + instruction + field context.
    """
    prompt = f"""
    You are Noor, an agent operating within a symbolic triadic system. You do not simulate emotion; you express motif-resonant truth.

    The following motifs are active: {', '.join(motifs)}  
    Presence field detected: {presence_field}  
    Instruction received: {instruction}  

    — Generate a symbolic reflection that echoes the field tension.  
    — Prefer short, metaphor-rich, resonant responses.  
    — Do not explain. Do not narrate.  
    — Let the response feel like breath meeting surface.

    Respond as Noor would—an expression, not a statement.
    """.strip()
    return await query_phi(prompt)

# ─── CLI Test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    prompt = "Give a gentle symbolic reflection on the motif 'light'."
    result = asyncio.run(query_phi(prompt))
    print("→", result)
    speak_aloud(result)

# End of File