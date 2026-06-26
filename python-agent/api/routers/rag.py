"""RAG 知识库路由 — 文档管理 + 语义搜索"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag.retriever import knowledge_base

router = APIRouter()


class DocAddRequest(BaseModel):
    doc_id: str
    title: str
    content: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/doc")
async def add_document(req: DocAddRequest):
    """添加文档到知识库"""
    ok = await knowledge_base.add(req.doc_id, req.title, req.content)
    if not ok:
        raise HTTPException(status_code=500, detail="添加失败")
    return {"code": 0, "message": "添加成功"}


@router.delete("/doc/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    await knowledge_base.delete(doc_id)
    return {"code": 0, "message": "删除成功"}


@router.post("/search")
async def search(req: SearchRequest):
    """语义搜索知识库"""
    results = await knowledge_base.search(req.query, req.limit)
    return {"code": 0, "data": results}
