"""搜索笔记工具"""
from tools import BaseTool
from services.xhs_bridge import XhsBridge


class SearchNoteTool(BaseTool):
    name = "search_notes"
    description = "搜索小红书笔记，根据关键词返回笔记列表"

    def __init__(self):
        self._bridge = XhsBridge()

    async def execute(self, keyword: str, limit: int = 10) -> list[dict]:
        notes = await self._bridge.search_notes(keyword, limit)
        return [{
            "note_id": n.note_id,
            "title": n.title,
            "author": n.author,
            "likes": n.likes,
            "collects": n.collects,
            "comments": n.comments,
        } for n in notes]

    def _parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜索关键词"},
                "limit": {"type": "integer", "description": "返回数量，默认10"},
            },
            "required": ["keyword"],
        }
