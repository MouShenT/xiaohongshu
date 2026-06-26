"""热点雷达 — 服务层，调用 XhsBridge + TrendAnalyzer"""
import logging
from models.schemas import Note
from services.xhs_bridge import XhsBridge
from domain.analyzers.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)


class HotRadarService:
    """热点雷达服务：趋势分析、热点检测"""

    def __init__(self):
        self._bridge: XhsBridge | None = None
        self._analyzer = TrendAnalyzer()

    def _get_bridge(self) -> XhsBridge:
        if self._bridge is None:
            self._bridge = XhsBridge()
        return self._bridge

    async def get_trending(self, limit: int = 20) -> list[Note]:
        """获取当前热门笔记"""
        bridge = self._get_bridge()
        topics = await bridge.get_hot_topics(limit)
        logger.info("获取到 %d 个热门话题", len(topics))

        # 从热门话题中搜索具体笔记
        all_notes = []
        for topic in topics[:5]:
            keyword = topic.get("name", "") if isinstance(topic, dict) else str(topic)
            if keyword:
                notes = await bridge.search_notes(keyword, limit=10, sort="popularity_descending")
                all_notes.extend(notes)

        # 去重并按热度排序
        seen = set()
        unique = []
        for n in all_notes:
            if n.note_id and n.note_id not in seen:
                seen.add(n.note_id)
                unique.append(n)

        unique.sort(key=lambda x: x.likes + x.collects * 2 + x.comments * 3, reverse=True)
        return unique[:limit]

    async def analyze_trend(self, keyword: str) -> dict:
        """分析关键词热度趋势"""
        bridge = self._get_bridge()
        notes = await bridge.search_notes(keyword, limit=50, sort="popularity_descending")

        if not notes:
            return {
                "keyword": keyword,
                "score": 0,
                "trend": "unknown",
                "total_notes": 0,
                "avg_likes": 0,
                "related_topics": [],
                "suggestions": ["未找到相关笔记，尝试更换关键词"],
            }

        # 计算热度指标
        scores = [self._analyzer.calculate_hot_score(n.model_dump()) for n in notes]
        avg_score = sum(scores) / len(scores) if scores else 0

        trend = self._analyzer.detect_trend(avg_score, [avg_score * 0.8])

        return {
            "keyword": keyword,
            "score": round(avg_score, 2),
            "trend": trend,
            "total_notes": len(notes),
            "avg_likes": round(sum(n.likes for n in notes) / len(notes), 1),
            "avg_collects": round(sum(n.collects for n in notes) / len(notes), 1),
            "avg_comments": round(sum(n.comments for n in notes) / len(notes), 1),
            "related_topics": await self._extract_topics(notes),
            "suggestions": self._generate_suggestions(notes, avg_score),
        }

    async def _extract_topics(self, notes: list[Note]) -> list[str]:
        """从笔记标题中提取高频词作为相关话题"""
        words = {}
        for n in notes:
            if n.title:
                for w in n.title.split():
                    if len(w) > 1:
                        words[w] = words.get(w, 0) + 1
        sorted_words = sorted(words.items(), key=lambda x: -x[1])
        return [w for w, c in sorted_words[:10] if c >= 2]

    def _generate_suggestions(self, notes: list[Note], avg_score: float) -> list[str]:
        """生成运营建议"""
        suggestions = []
        if avg_score > 100:
            suggestions.append("该关键词竞争激烈，建议差异化切入")
        elif avg_score > 50:
            suggestions.append("中等热度，适合布局内容")
        else:
            suggestions.append("低竞争长尾词，建议抢占先机")

        high_engagement = sum(1 for n in notes if n.comments > 50)
        if high_engagement > len(notes) * 0.3:
            suggestions.append("互动率高，建议重点投入评论引导")

        return suggestions
