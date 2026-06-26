"""趋势分析器 — 纯算法，无I/O"""
import math
from datetime import datetime, timedelta


class TrendAnalyzer:
    """趋势分析器：计算热度分数、趋势方向"""

    def calculate_hot_score(self, note: dict) -> float:
        """计算单篇笔记的热度分数"""
        likes = note.get("likes", 0)
        collects = note.get("collects", 0)
        comments = note.get("comments", 0)
        shares = note.get("shares", 0)
        created_at = note.get("created_at")

        # 基础互动分
        interaction_score = (
            likes * 1.0 +
            collects * 1.5 +
            comments * 2.0 +
            shares * 3.0
        )

        # 时间衰减 (48小时内热度权重高)
        if created_at:
            hours_age = (datetime.now() - created_at).total_seconds() / 3600
            time_decay = math.exp(-hours_age / 48)
        else:
            time_decay = 0.5

        return interaction_score * time_decay

    def detect_trend(self, current_score: float, history_scores: list[float]) -> str:
        """判断趋势方向"""
        if not history_scores:
            return "stable"

        avg = sum(history_scores) / len(history_scores)
        if current_score > avg * 1.2:
            return "rising"
        elif current_score < avg * 0.8:
            return "falling"
        return "stable"

    def cluster_keywords(self, notes: list[dict]) -> list[dict]:
        """关键词聚类（简单实现）"""
        # TODO: 接入 LLM 或 TF-IDF 进行聚类
        return []
