"""运营全链路 — 工作流触发路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from workflow.executor import WorkflowExecutor

router = APIRouter()
_executor = WorkflowExecutor()


class PipelineRequest(BaseModel):
    flow_type: str = "report"
    keyword: str = ""
    params: dict = {}


@router.post("/run")
async def run_pipeline(req: PipelineRequest):
    """执行工作流"""
    if req.flow_type not in ["publish", "trend", "report", "review", "collect"]:
        raise HTTPException(status_code=400, detail=f"不支持的流程类型: {req.flow_type}")

    context = {
        "keyword": req.keyword,
        "flow_type": req.flow_type,
        **req.params,
    }

    result = await _executor.run(req.flow_type, context)

    # 清理中间状态
    result.pop("_node", None)
    result.pop("_progress", None)
    result.pop("notes", None)

    return {"code": 0, "data": result}


@router.get("/flows")
async def list_flows():
    """列出所有可用工作流"""
    return {"code": 0, "data": [
        {"type": "collect", "name": "数据采集", "nodes": ["收集", "通知"]},
        {"type": "trend", "name": "热点发现", "nodes": ["收集", "分析", "生成报告", "通知"]},
        {"type": "report", "name": "日报生成", "nodes": ["收集", "分析", "生成", "审核", "通知"]},
        {"type": "review", "name": "批量审核", "nodes": ["分析", "审核", "通知"]},
        {"type": "publish", "name": "发布流程", "nodes": ["收集", "分析", "审核", "通知"]},
    ]}
