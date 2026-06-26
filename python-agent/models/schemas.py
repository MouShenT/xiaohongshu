"""Pydantic 模型定义"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Note(BaseModel):
    """小红书笔记"""
    note_id: str
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    likes: Optional[int] = 0
    collects: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    images: list[str] = []
    video: Optional[str] = None
    created_at: Optional[datetime] = None
    url: Optional[str] = None


class Comment(BaseModel):
    """小红书评论"""
    comment_id: str
    note_id: str
    content: str
    author: Optional[str] = None
    likes: Optional[int] = 0
    created_at: Optional[datetime] = None
    replies: list["Comment"] = []


class Task(BaseModel):
    """异步任务"""
    id: int
    user_id: int
    type: str
    status: str = "PENDING"
    params: Optional[dict] = None
    result: Optional[dict] = None
    progress: int = 0
    error_message: Optional[str] = None


class AnalysisResult(BaseModel):
    """分析结果"""
    summary: str
    score: float
    details: dict = {}
    suggestions: list[str] = []
