"""Agent 工具基类"""
from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Agent 可调用的工具基类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        ...

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._parameters(),
            },
        }

    def _parameters(self) -> dict:
        return {"type": "object", "properties": {}, "required": []}
