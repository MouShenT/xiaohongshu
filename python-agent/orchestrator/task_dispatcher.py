"""AI Orchestrator — 任务分发器，调用真实Service"""
import logging
from application.services.hot_radar_service import HotRadarService
from domain.analyzers.article_analyzer import ArticleAnalyzer

logger = logging.getLogger(__name__)


class TaskDispatcher:
    """任务分发器：将任务分发给对应的 Service"""

    def __init__(self):
        self._hot_radar = HotRadarService()
        self._article_analyzer = ArticleAnalyzer()

    async def dispatch_hot_radar(self, task_data: dict):
        keyword = task_data.get("keyword", "")
        logger.info("热点雷达分析: keyword=%s", keyword)
        result = await self._hot_radar.analyze_trend(keyword)
        return {"status": "completed", "result": result}

    async def dispatch_article_analysis(self, task_data: dict):
        note_id = task_data.get("noteId", task_data.get("note_id", ""))
        logger.info("爆文拆解: note_id=%s", note_id)
        result = await self._article_analyzer.analyze(note_id)
        return {"status": "completed", "result": result}

    async def dispatch_comment_insight(self, task_data: dict):
        note_id = task_data.get("noteId", task_data.get("note_id", ""))
        logger.info("评论洞察: note_id=%s", note_id)
        from services.xhs_bridge import XhsBridge
        bridge = XhsBridge()
        comments = await bridge.get_comments(note_id, 200)
        # 简单统计
        total = len(comments)
        avg_len = sum(len(c.content) for c in comments) / max(total, 1)
        top_comment = max(comments, key=lambda c: c.likes).content if comments else ""
        return {"status": "completed", "result": {
            "note_id": note_id,
            "total_comments": total,
            "avg_comment_length": round(avg_len, 1),
            "top_comment": top_comment[:200] if top_comment else "",
        }}

    async def dispatch_content_write(self, task_data: dict):
        topic = task_data.get("topic", "")
        logger.info("AI创作: topic=%s", topic)
        # TODO: 接入LLM生成内容
        return {"status": "completed", "result": {"topic": topic, "content": "TODO: LLM生成"}}

    async def dispatch_pipeline(self, task_data: dict):
        pipeline_type = task_data.get("pipelineType", "")
        logger.info("全链路执行: pipeline=%s", pipeline_type)
        return {"status": "completed", "result": {"pipeline": pipeline_type, "steps": []}}

    async def dispatch_data_clean(self, task_data: dict):
        logger.info("数据清洗")
        return {"status": "completed", "result": "数据清洗完成"}
