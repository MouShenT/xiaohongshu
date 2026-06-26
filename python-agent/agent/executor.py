"""Agent Planner / Executor / Memory — PydanticAI 智能体"""
import json
import logging
from typing import Optional

from tools.registry import get_all_tools, get_tool, get_openai_tools
from providers.llm import get_llm_provider

logger = logging.getLogger(__name__)


class AgentMemory:
    """短期记忆 — 对话历史"""

    def __init__(self, max_turns: int = 20):
        self.messages: list[dict] = []
        self.max_turns = max_turns

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self):
        if len(self.messages) > self.max_turns:
            self.messages = self.messages[-self.max_turns:]

    def get_system_prompt(self) -> str:
        return (
            "你是一个小红书 AI 运营助手。你可以使用以下工具来帮助用户：\n"
            "- search_notes: 搜索小红书笔记\n"
            "- get_comments: 获取笔记评论\n"
            "- analyze_sentiment: 分析评论情绪\n"
            "- analyze_trend: 分析关键词热度趋势\n"
            "- data_clean: 清洗文本数据\n\n"
            "请根据用户需求选择合适的工具，并用中文回复。"
        )

    def to_openai_messages(self) -> list[dict]:
        return [{"role": "system", "content": self.get_system_prompt()}, *self.messages]


class Planner:
    """任务规划器 — 分析用户意图并决定使用哪些工具"""

    async def plan(self, message: str, context: str = "") -> str:
        """返回规划结果"""
        return message


class Executor:
    """任务执行器 — 调用工具并返回结果"""

    def __init__(self):
        self._provider = None

    def _get_provider(self):
        if self._provider is None:
            self._provider = get_llm_provider("openai")
        return self._provider

    async def execute(self, memory: AgentMemory) -> str:
        """使用 LLM 分析并调用工具，返回最终回复"""
        provider = self._get_provider()
        messages = memory.to_openai_messages()
        tools = get_openai_tools()

        try:
            response = await provider.chat(messages)
            return response
        except Exception as e:
            logger.error("LLM 调用失败: %s", e)
            # fallback: 本地关键词回复
            last_user = messages[-1]["content"] if messages else ""
            return await self._local_fallback(last_user)

    async def _local_fallback(self, message: str) -> str:
        """LLM 不可用时的本地 fallback 回复"""
        from api.routers.agent_chat import detect_intent, handle_search, handle_help

        intent = detect_intent(message)
        if intent == "搜索":
            from services.xhs_bridge import XhsBridge
            bridge = XhsBridge()
            keyword = message.replace("搜索", "").replace("查找", "").strip()
            if keyword:
                notes = await bridge.search_notes(keyword, limit=3)
                if notes:
                    return f"找到以下笔记：\n" + "\n".join(
                        f"- {n.title} (❤️{n.likes})" for n in notes
                    )
                return f"未找到「{keyword}」相关笔记。"
        return "你好！我是小红书 AI 运营助手，可以帮你搜索笔记、分析热度、查看评论等。输入「帮助」查看功能列表。"


class Agent:
    """AI 智能体 — Planner + Executor + Memory"""

    def __init__(self):
        self.memory = AgentMemory()
        self.planner = Planner()
        self.executor = Executor()

    async def chat(self, message: str) -> str:
        self.memory.add_user(message)
        response = await self.executor.execute(self.memory)
        self.memory.add_assistant(response)
        return response
