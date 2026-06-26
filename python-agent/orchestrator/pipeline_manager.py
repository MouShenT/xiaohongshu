"""AI Orchestrator — Pipeline 生命周期管理"""
from workflow.executor import WorkflowExecutor


class PipelineManager:
    """管理 LangGraph Workflow 生命周期"""

    def __init__(self):
        self.executor = WorkflowExecutor()

    async def execute(self, pipeline_id: str, flow_type: str):
        workflow = self.executor.create_workflow(flow_type)
        result = await workflow.run()
        return result
