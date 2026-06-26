# FastAPI 小红书 AI 运营平台 — 微服务
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, xhs_api, agent_chat, agent_pipeline, rag, data_clean
from core.config import settings

app = FastAPI(
    title="小红书 AI 运营平台",
    description="Python AI 微服务 — 热点雷达、爆文拆解、评论洞察、AI创作、RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(xhs_api.router, prefix="/api/v1/xhs", tags=["小红书数据"])
app.include_router(agent_chat.router, prefix="/api/v1/agent", tags=["AI 智能体"])
app.include_router(agent_pipeline.router, prefix="/api/v1/pipeline", tags=["运营全链路"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG 知识库"])
app.include_router(data_clean.router, prefix="/api/v1/data", tags=["数据清洗"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "xhs-ai-service"}
