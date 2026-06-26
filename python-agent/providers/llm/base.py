"""LLM Provider 接口"""
from abc import ABC, abstractmethod


class ILLMProvider(ABC):

    @abstractmethod
    async def chat(self, messages: list[dict], model: str = None) -> str:
        ...

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        ...
