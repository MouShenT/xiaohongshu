"""爆文拆解 — 服务层"""
import logging
from services.xhs_bridge import XhsBridge
from models.schemas import Note

logger = logging.getLogger(__name__)


class ArticleAnalyzer:
    """爆文拆解服务"""

    def __init__(self):
        self._bridge: XhsBridge | None = None

    def _get_bridge(self) -> XhsBridge:
        if self._bridge is None:
            self._bridge = XhsBridge()
        return self._bridge

    async def analyze(self, note_id: str) -> dict:
        """分析单篇笔记，返回拆解报告"""
        bridge = self._get_bridge()
        note = await bridge.get_note_detail(note_id)
        if not note:
            return {"error": "笔记不存在", "note_id": note_id}

        comments = await bridge.get_comments(note_id, limit=100)

        return {
            "note_id": note.note_id,
            "title": note.title,
            "author": note.author,

            "engagement": {
                "likes": note.likes,
                "collects": note.collects,
                "comments": note.comments,
                "shares": note.shares,
                "interaction_rate": self._calc_interaction_rate(note),
            },

            "title_analysis": self._analyze_title(note.title),

            "content_analysis": {
                "length": len(note.content or ""),
                "image_count": len(note.images),
                "has_video": note.video is not None,
            },

            "comment_summary": self._summarize_comments(comments),

            "scores": {
                "overall": self._score(note),
                "title_score": self._score_title(note.title),
                "engagement_score": min(100, int((note.likes + note.collects * 2) / 10)),
            },
        }

    def _analyze_title(self, title: str) -> dict:
        """标题分析"""
        if not title:
            return {"length": 0, "has_number": False, "has_question": False, "has_emoji": False}

        import re
        return {
            "length": len(title),
            "has_number": bool(re.search(r"\d+", title)),
            "has_question": "?" in title or "？" in title or "如何" in title or "怎么" in title,
            "has_emoji": bool(re.search(r"[\U0001F300-\U0001F9FF]", title)),
        }

    def _summarize_comments(self, comments: list) -> dict:
        """评论摘要"""
        if not comments:
            return {"total": 0, "top_comment": "", "sentiment": "unknown"}

        top = max(comments, key=lambda c: c.likes)
        positive = sum(1 for c in comments if len(c.content) > 10)
        return {
            "total": len(comments),
            "top_comment": top.content[:100] if top.content else "",
            "top_comment_likes": top.likes,
            "positive_ratio": round(positive / len(comments), 2),
        }

    def _score(self, note: Note) -> int:
        return min(100, int((note.likes + note.collects * 2 + note.comments * 3) / 50))

    def _score_title(self, title: str) -> int:
        if not title:
            return 0
        score = 60
        a = self._analyze_title(title)
        if a["has_number"]:
            score += 10
        if a["has_question"]:
            score += 15
        if a["has_emoji"]:
            score += 5
        if 15 <= a["length"] <= 30:
            score += 10
        return min(100, score)

    def _calc_interaction_rate(self, note: Note) -> float:
        base = note.likes + note.collects + note.comments + note.shares
        return round(base / max(1, len(note.content or "")) * 100, 2)
