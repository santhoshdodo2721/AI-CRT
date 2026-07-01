import json
import logging
import httpx
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger("ai_engine.llm_client")

async def ask(prompt: str, system_prompt: str = "", temperature: float = 0.2, max_tokens: int = 2048) -> str:
    """Call NVIDIA NIM API if key exists, else fallback to local Ollama."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    if settings.NVIDIA_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta/llama-3.1-8b-instruct",
                        "messages": messages,
                        "temperature": temperature,
                        "top_p": 0.7,
                        "max_tokens": max_tokens,
                        "stream": False
                    },
                )
                r.raise_for_status()
                data = r.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"NVIDIA NIM API Error: {e}. Falling back to Ollama...")

    # Fallback to local Ollama
    try:
        ollama_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL, 
                    "prompt": ollama_prompt, 
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
            )
            r.raise_for_status()
            return r.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama API Error: {e}")
        return f"[AI offline - run Ollama locally or configure NVIDIA NIM] Error: {e}"

async def ask_json(prompt: str, system_prompt: str = "", temperature: float = 0.1) -> Optional[Dict[str, Any]]:
    """Forces JSON output and parses it."""
    sys_prompt = system_prompt + "\n\nCRITICAL: You MUST respond ONLY with valid JSON. Do not include any markdown formatting like ```json or ```. Return exactly the JSON object."
    
    response_text = await ask(prompt, sys_prompt, temperature=temperature)
    
    # Try to clean up markdown if the LLM ignored instructions
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON output. Error: {e}. Raw output: {response_text}")
        return None
