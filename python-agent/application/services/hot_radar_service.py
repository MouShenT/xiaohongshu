"""热点雷达 — 服务层"""
from models.schemas import Note


class HotRadarService:
    """热点雷达服务：趋势分析、热点检测"""

    async def get_trending(self, limit: int = 20) -> list[Note]:
        # TODO: 调用 Spider_XHS 获取热门笔记
        return []

    async def analyze_trend(self, keyword: str) -> dict:
        """分析关键词热度趋势"""
        return {
            "keyword": keyword,
            "score": 85,
            "trend": "rising",
            "related_topics": [],
            "suggestions": [],
        }
