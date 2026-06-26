"""数据分析同步接口 — 供前端直接调用"""
from fastapi import APIRouter, Query, HTTPException
from application.services.hot_radar_service import HotRadarService
from domain.analyzers.article_analyzer import ArticleAnalyzer

router = APIRouter()
_hot_radar = HotRadarService()
_article_analyzer = ArticleAnalyzer()


@router.get("/hot-radar/trending")
async def get_trending(limit: int = Query(20, ge=1, le=100)):
    """获取热门笔记排行"""
    notes = await _hot_radar.get_trending(limit)
    return {"code": 0, "data": [n.model_dump() for n in notes]}


@router.post("/hot-radar/analyze")
async def analyze_trend(body: dict):
    """分析关键词热度趋势"""
    keyword = body.get("keyword", "")
    if not keyword:
        raise HTTPException(status_code=400, detail="请输入关键词")
    result = await _hot_radar.analyze_trend(keyword)
    return {"code": 0, "data": result}


@router.post("/article/analyze")
async def analyze_article(body: dict):
    """拆解分析笔记"""
    note_id = body.get("noteId", "")
    if not note_id:
        raise HTTPException(status_code=400, detail="请输入笔记ID")
    result = await _article_analyzer.analyze(note_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"code": 0, "data": result}
