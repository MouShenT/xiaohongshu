"""LangGraph 工作流引擎 — MVP 实现"""
import asyncio
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class WorkflowNode:
    """工作流节点基类"""

    async def execute(self, context: dict) -> dict:
        raise NotImplementedError


class CollectNode(WorkflowNode):
    """采集节点：拉取数据"""

    async def execute(self, context: dict) -> dict:
        keyword = context.get("keyword", "")
        logger.info("[CollectNode] 采集: keyword=%s", keyword)
        from services.xhs_bridge import XhsBridge
        bridge = XhsBridge()
        notes = await bridge.search_notes(keyword, limit=20, sort="popularity_descending")
        context["notes"] = [n.model_dump() for n in notes]
        context["collect_count"] = len(notes)
        return context


class AnalyzeNode(WorkflowNode):
    """分析节点：热点/情绪分析"""

    async def execute(self, context: dict) -> dict:
        logger.info("[AnalyzeNode] 开始分析")
        notes = context.get("notes", [])
        if not notes:
            context["analysis"] = {"error": "无数据可分析"}
            return context

        from domain.analyzers.trend_analyzer import TrendAnalyzer
        analyzer = TrendAnalyzer()
        scores = [analyzer.calculate_hot_score(n) for n in notes]
        avg_score = sum(scores) / len(scores) if scores else 0
        trend = analyzer.detect_trend(avg_score, [avg_score * 0.8])

        context["analysis"] = {
            "avg_score": round(avg_score, 2),
            "trend": trend,
            "total_notes": len(notes),
            "avg_likes": round(sum(n.get("likes", 0) for n in notes) / len(notes), 1),
            "avg_comments": round(sum(n.get("comments", 0) for n in notes) / len(notes), 1),
        }
        return context


class GenerateNode(WorkflowNode):
    """生成节点：生成报告/内容"""

    async def execute(self, context: dict) -> dict:
        logger.info("[GenerateNode] 生成报告")
        analysis = context.get("analysis", {})
        keyword = context.get("keyword", "")
        context["report"] = {
            "title": f"{keyword} 热点分析报告",
            "generated_at": datetime.now().isoformat(),
            "summary": f"共分析 {analysis.get('total_notes', 0)} 篇笔记，"
                       f"平均热度分 {analysis.get('avg_score', 0)}，"
                       f"趋势: {analysis.get('trend', 'unknown')}",
            "details": analysis,
            "suggestions": [
                "建议结合热门话题创作内容",
                "关注高互动率的笔记类型",
                "定期跟踪趋势变化",
            ],
        }
        return context


class ReviewNode(WorkflowNode):
    """审核节点：检查结果"""

    async def execute(self, context: dict) -> dict:
        logger.info("[ReviewNode] 审核")
        report = context.get("report", {})
        report["reviewed"] = True
        report["reviewed_at"] = datetime.now().isoformat()
        return context


class NotifyNode(WorkflowNode):
    """通知节点：推送结果"""

    async def execute(self, context: dict) -> dict:
        logger.info("[NotifyNode] 通知完成")
        context["status"] = "completed"
        context["finished_at"] = datetime.now().isoformat()
        return context


class WorkflowExecutor:
    """工作流执行器 — 按序执行节点链"""

    def __init__(self):
        self._nodes: dict[str, list[WorkflowNode]] = {
            "publish": [
                CollectNode(),
                AnalyzeNode(),
                ReviewNode(),
                NotifyNode(),
            ],
            "trend": [
                CollectNode(),
                AnalyzeNode(),
                GenerateNode(),
                NotifyNode(),
            ],
            "report": [
                CollectNode(),
                AnalyzeNode(),
                GenerateNode(),
                ReviewNode(),
                NotifyNode(),
            ],
            "review": [
                AnalyzeNode(),
                ReviewNode(),
                NotifyNode(),
            ],
            "collect": [
                CollectNode(),
                NotifyNode(),
            ],
        }

    def create_workflow(self, flow_type: str) -> list[WorkflowNode]:
        return self._nodes.get(flow_type, self._nodes["report"])

    async def run(self, flow_type: str, context: dict) -> dict:
        nodes = self.create_workflow(flow_type)
        logger.info("[Workflow] 启动 flow=%s, nodes=%d", flow_type, len(nodes))

        for i, node in enumerate(nodes):
            node_name = node.__class__.__name__
            logger.info("[Workflow] 执行节点 %d/%d: %s", i + 1, len(nodes), node_name)
            context["_node"] = node_name
            context["_progress"] = int((i + 1) / len(nodes) * 100)
            try:
                context = await node.execute(context)
            except Exception as e:
                logger.error("[Workflow] 节点失败: %s, error=%s", node_name, e)
                context["status"] = "failed"
                context["error"] = str(e)
                return context
            await asyncio.sleep(0.2)

        context["status"] = "completed"
        context["_progress"] = 100
        return context
