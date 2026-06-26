"""OpenAI / 兼容接口 LLM Provider"""
import json
import logging
from typing import Optional
from providers.llm.base import ILLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(ILLMProvider):
    """OpenAI / 兼容 API (DeepSeek, Qwen, GLM 等均支持 OpenAI 格式)"""

    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1",
                 default_model: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self._http = None

    async def _get_http(self):
        if self._http is None:
            import httpx
            self._http = httpx.AsyncClient(timeout=60.0)
        return self._http

    async def chat(self, messages: list[dict], model: Optional[str] = None) -> str:
        http = await self._get_http()
        resp = await http.post(f"{self.base_url}/chat/completions", json={
            "model": model or self.default_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
        }, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[dict], model: Optional[str] = None):
        http = await self._get_http()
        async with http.stream("POST", f"{self.base_url}/chat/completions", json={
            "model": model or self.default_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True,
        }, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def generate_embedding(self, text: str) -> list[float]:
        http = await self._get_http()
        resp = await http.post(f"{self.base_url}/embeddings", json={
            "model": "text-embedding-ada-002",
            "input": text,
        }, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
