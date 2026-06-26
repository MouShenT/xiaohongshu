"""AI 创作路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.services.content_writer_service import ContentWriterService

router = APIRouter()
_writer = ContentWriterService()


class TitleRequest(BaseModel):
    topic: str
    count: int = 5


class ContentRequest(BaseModel):
    topic: str
    style: str = "教程"
    keywords: list[str] = []


class DraftRequest(BaseModel):
    title: str
    outline: str


@router.post("/titles")
async def generate_titles(req: TitleRequest):
    """生成标题"""
    titles = await _writer.generate_titles(req.topic, req.count)
    return {"code": 0, "data": titles}


@router.post("/content")
async def generate_content(req: ContentRequest):
    """生成正文"""
    content = await _writer.generate_content(req.topic, req.style, req.keywords)
    return {"code": 0, "data": content}


@router.post("/tags")
async def generate_tags(body: dict):
    """生成标签"""
    tags = await _writer.generate_tags(body.get("topic", ""), body.get("content", ""))
    return {"code": 0, "data": tags}


@router.post("/draft")
async def complete_draft(req: DraftRequest):
    """完成整篇草稿"""
    result = await _writer.complete_draft(req.title, req.outline)
    return {"code": 0, "data": result}
