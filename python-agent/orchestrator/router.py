"""AI Orchestrator — 任务路由器"""
from orchestrator.task_dispatcher import TaskDispatcher


class TaskRouter:
    """根据 task.type 路由到对应 Handler"""

    def __init__(self, dispatcher: TaskDispatcher):
        self.dispatcher = dispatcher

    async def route(self, task_type: str, task_data: dict):
        handlers = {
            "HOT_RADAR": self.dispatcher.dispatch_hot_radar,
            "ARTICLE_ANALYSIS": self.dispatcher.dispatch_article_analysis,
            "COMMENT_INSIGHT": self.dispatcher.dispatch_comment_insight,
            "CONTENT_WRITE": self.dispatcher.dispatch_content_write,
            "PIPELINE": self.dispatcher.dispatch_pipeline,
            "DATA_CLEAN": self.dispatcher.dispatch_data_clean,
        }

        handler = handlers.get(task_type)
        if handler:
            return await handler(task_data)
        raise ValueError(f"Unknown task type: {task_type}")
