"""Agent 工具注册中心 — 统一管理所有 Tool 的创建与查找"""
from tools.search_note_tool import SearchNoteTool
from tools.get_comments_tool import GetCommentsTool, AnalyzeSentimentTool
from tools.analyze_trend_tool import AnalyzeTrendTool, DataCleanTool

_tool_registry: dict[str, type] = {
    "search_notes": SearchNoteTool,
    "get_comments": GetCommentsTool,
    "analyze_sentiment": AnalyzeSentimentTool,
    "analyze_trend": AnalyzeTrendTool,
    "data_clean": DataCleanTool,
}


def get_tool(name: str):
    cls = _tool_registry.get(name)
    if cls:
        return cls()
    raise ValueError(f"未知工具: {name}")


def list_tools() -> list[str]:
    return list(_tool_registry.keys())


def get_all_tools() -> list:
    return [cls() for cls in _tool_registry.values()]


def get_openai_tools() -> list[dict]:
    return [t.to_openai_tool() for t in get_all_tools()]
