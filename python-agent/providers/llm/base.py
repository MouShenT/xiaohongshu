"""LLM Provider 接口"""
from abc import ABC, abstractmethod
from typing import Optional


class ILLMProvider(ABC):

    @abstractmethod
    async def chat(self, messages: list[dict], model: Optional[str] = None) -> str:
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[dict], model: Optional[str] = None):
        """SSE 流式聊天，yield str chunks"""
        ...

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        ...
