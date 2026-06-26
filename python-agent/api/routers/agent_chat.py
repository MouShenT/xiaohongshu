"""AI 智能体对话路由 — SSE 流式响应"""
import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.xhs_bridge import XhsBridge

logger = logging.getLogger(__name__)
router = APIRouter()
_bridge = XhsBridge()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    history: list[dict] = []


# 简单关键词路由 — 模拟 Agent 意图识别
INTENT_MAP = [
    ("搜索", ["搜索", "查找", "找笔记", "搜", "search", "find"]),
    ("分析", ["分析", "拆解", "解读", "analyze", "拆"]),
    ("热度", ["热度", "趋势", "热点", "热", "trend", "火爆"]),
    ("评论", ["评论", "留言", "评价", "comment", "吐槽"]),
    ("创作", ["创作", "写笔记", "生成", "写一篇", "write", "generate"]),
    ("帮助", ["帮助", "功能", "你能", "可以", "help", "support"]),
]


@router.post("/chat")
async def chat(req: ChatRequest):
    intent = detect_intent(req.message)

    async def event_stream():
        yield f"data: {json.dumps({'type': 'intent', 'content': intent})}\n\n"
        await asyncio.sleep(0.1)

        if intent == "搜索":
            async for chunk in handle_search(req.message):
                yield chunk
        elif intent == "分析":
            async for chunk in handle_analyze(req.message):
                yield chunk
        elif intent == "热度":
            async for chunk in handle_trend(req.message):
                yield chunk
        elif intent == "评论":
            async for chunk in handle_comment(req.message):
                yield chunk
        elif intent == "创作":
            async for chunk in handle_write(req.message):
                yield chunk
        else:
            yield f"data: {json.dumps({'type': 'text', 'content': handle_help()})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def detect_intent(message: str) -> str:
    for intent, keywords in INTENT_MAP:
        for kw in keywords:
            if kw in message.lower():
                return intent
    return "帮助"


async def handle_search(message: str) -> list[str]:
    yield f"data: {json.dumps({'type': 'text', 'content': '正在搜索小红书笔记...'})}\n\n"
    await asyncio.sleep(0.5)

    keyword = message.replace("搜索", "").replace("查找", "").replace("找笔记", "").strip()
    if not keyword:
        keyword = message.strip()

    notes = await _bridge.search_notes(keyword, limit=5)
    if not notes:
        yield f"data: {json.dumps({'type': 'text', 'content': f'未找到「{keyword}」相关笔记，建议换个关键词试试。'})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'text', 'content': f'找到 {len(notes)} 篇相关笔记:'})}\n\n"
    for n in notes:
        yield f"data: {json.dumps({
            'type': 'note',
            'content': {
                'note_id': n.note_id,
                'title': n.title,
                'author': n.author,
                'likes': n.likes,
                'collects': n.collects,
                'comments': n.comments,
            }
        })}\n\n"
        await asyncio.sleep(0.1)


async def handle_analyze(message: str) -> list[str]:
    yield f"data: {json.dumps({'type': 'text', 'content': '笔记分析功能正在准备中...'})}\n\n"
    await asyncio.sleep(0.3)
    yield f"data: {json.dumps({'type': 'text', 'content': '请提供笔记ID，例如: 拆解 123456789'})}\n\n"


async def handle_trend(message: str) -> list[str]:
    yield f"data: {json.dumps({'type': 'text', 'content': '正在获取热点趋势...'})}\n\n"
    await asyncio.sleep(0.5)

    keyword = message.replace("热度", "").replace("趋势", "").replace("热点", "").strip()
    if keyword:
        from application.services.hot_radar_service import HotRadarService
        svc = HotRadarService()
        result = await svc.analyze_trend(keyword)
        yield f"data: {json.dumps({'type': 'text', 'content': (
            f'## {keyword} 热度分析\n'
            + f'- 热度分: {result["score"]}\n'
            + f'- 趋势: {result["trend"]}\n'
            + f'- 相关笔记: {result["total_notes"]}\n'
            + f'- 平均点赞: {result["avg_likes"]}\n'
        )})}\n\n"
    else:
        yield f"data: {json.dumps({'type': 'text', 'content': '请指定要分析的关键词，例如: 热度 美妆'})}\n\n"


async def handle_comment(message: str) -> list[str]:
    yield f"data: {json.dumps({'type': 'text', 'content': '评论洞察功能正在准备中...'})}\n\n"
    await asyncio.sleep(0.3)
    yield f"data: {json.dumps({'type': 'text', 'content': '请提供笔记ID，例如: 评论 123456789'})}\n\n"


async def handle_write(message: str) -> list[str]:
    yield f"data: {json.dumps({'type': 'text', 'content': 'AI创作功能正在开发中，即将上线...'})}\n\n"
    await asyncio.sleep(0.3)
    yield f"data: {json.dumps({'type': 'text', 'content': '敬请期待!'})}\n\n"


def handle_help() -> str:
    return (
        "## 小红书 AI 运营助手\n\n"
        "我可以帮你做这些事:\n\n"
        "1. **搜索笔记** — 输入 `搜索 关键词`\n"
        "2. **热度分析** — 输入 `热度 关键词`\n"
        "3. **笔记拆解** — 输入 `拆解 笔记ID`\n"
        "4. **评论洞察** — 输入 `评论 笔记ID`\n"
        "5. **AI 创作** — 输入 `写笔记 主题`\n\n"
        "试试输入 `搜索 美妆` 或 `热度 穿搭`"
    )
