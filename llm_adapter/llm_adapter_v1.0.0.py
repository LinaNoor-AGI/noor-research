# llm_adapter.py · Noor LLM Integration (Phi-2 via Ollama)
import aiohttp
import asyncio
import logging

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "phi"

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

# Test stub
if __name__ == "__main__":
    prompt = "Give a gentle symbolic reflection on the motif 'light'."
    result = asyncio.run(query_phi(prompt))
    print("→", result)
