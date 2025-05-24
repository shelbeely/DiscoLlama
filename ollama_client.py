import aiohttp
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

HEADERS = {}
if OLLAMA_API_KEY:
    HEADERS["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

async def list_models():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{OLLAMA_HOST}/api/tags") as resp:
            data = await resp.json()
            return [model["name"] for model in data.get("models", [])]

async def start_model(model: str):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(f"{OLLAMA_HOST}/api/pull", json={"name": model}) as resp:
            if resp.status == 200:
                return True
            data = await resp.json()
            return data.get("status", "failed")

async def generate_response(model: str, prompt: str):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        async with session.post(f"{OLLAMA_HOST}/api/generate", json=payload) as resp:
            data = await resp.json()
            return data.get("response", "No response received.")
