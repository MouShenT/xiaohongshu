"""获取评论工具"""
from tools import BaseTool
from services.xhs_bridge import XhsBridge


class GetCommentsTool(BaseTool):
    name = "get_comments"
    description = "获取小红书笔记的评论列表"

    def __init__(self):
        self._bridge = XhsBridge()

    async def execute(self, note_id: str, limit: int = 50) -> list[dict]:
        comments = await self._bridge.get_comments(note_id, limit)
        return [{
            "comment_id": c.comment_id,
            "content": c.content[:200],
            "author": c.author,
            "likes": c.likes,
        } for c in comments]

    def _parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "笔记ID"},
                "limit": {"type": "integer", "description": "返回评论数量"},
            },
            "required": ["note_id"],
        }


class AnalyzeSentimentTool(BaseTool):
    name = "analyze_sentiment"
    description = "分析笔记评论的情绪倾向（正面/中性/负面）"

    async def execute(self, note_id: str) -> dict:
        from services.xhs_bridge import XhsBridge
        bridge = XhsBridge()
        comments = await bridge.get_comments(note_id, 100)
        if not comments:
            return {"note_id": note_id, "total": 0, "sentiment": "unknown"}

        positive = sum(1 for c in comments if len(c.content) > 10)
        negative = sum(1 for c in comments if any(w in c.content for w in ["差", "垃圾", "不好", "失望", "骗"]))
        neutral = len(comments) - positive - negative

        return {
            "note_id": note_id,
            "total": len(comments),
            "positive": positive,
            "neutral": max(0, neutral),
            "negative": max(0, negative),
            "top_comment": max(comments, key=lambda c: c.likes).content[:200] if comments else "",
        }

    def _parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "笔记ID"},
            },
            "required": ["note_id"],
        }
