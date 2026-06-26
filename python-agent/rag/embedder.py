"""Embedding 生成器 — 调用 LLM Provider 生成向量"""
import logging
from typing import Optional
from providers.llm import get_llm_provider

logger = logging.getLogger(__name__)


class Embedder:
    """文本向量化"""

    def __init__(self, provider_type: str = "openai"):
        self._provider = get_llm_provider(provider_type)

    async def embed(self, text: str) -> list[float]:
        try:
            return await self._provider.generate_embedding(text)
        except Exception as e:
            logger.error("Embedding 生成失败: %s", e)
            return []

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        results = []
        for t in texts:
            vec = await self.embed(t)
            if vec:
                results.append(vec)
            else:
                results.append([])
        return results
