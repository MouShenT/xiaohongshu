"""小红书数据代理路由 — 对外暴露XHS数据查询API"""
from fastapi import APIRouter, Query, HTTPException
from services.xhs_bridge import XhsBridge

router = APIRouter()
_bridge: XhsBridge | None = None


def get_bridge() -> XhsBridge:
    global _bridge
    if _bridge is None:
        _bridge = XhsBridge()
    return _bridge


@router.get("/search")
async def search_notes(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    sort: str = Query("general", description="排序: general/popularity_descending/time_descending"),
):
    """搜索小红书笔记"""
    bridge = get_bridge()
    notes = await bridge.search_notes(keyword, limit, sort)
    return {"code": 0, "data": [n.model_dump() for n in notes], "total": len(notes)}


@router.get("/note/{note_id}")
async def get_note_detail(note_id: str):
    """获取笔记详情"""
    bridge = get_bridge()
    note = await bridge.get_note_detail(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return {"code": 0, "data": note.model_dump()}


@router.get("/note/{note_id}/comments")
async def get_comments(
    note_id: str,
    limit: int = Query(50, ge=1, le=200, description="返回评论数量"),
):
    """获取笔记评论"""
    bridge = get_bridge()
    comments = await bridge.get_comments(note_id, limit)
    return {"code": 0, "data": [c.model_dump() for c in comments], "total": len(comments)}


@router.get("/user/{user_id}/notes")
async def get_user_notes(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
):
    """获取用户笔记列表"""
    bridge = get_bridge()
    notes = await bridge.get_user_notes(user_id, limit)
    return {"code": 0, "data": [n.model_dump() for n in notes], "total": len(notes)}


@router.get("/hot-topics")
async def get_hot_topics(limit: int = Query(20, ge=1, le=50)):
    """获取热门话题"""
    bridge = get_bridge()
    topics = await bridge.get_hot_topics(limit)
    return {"code": 0, "data": topics}
