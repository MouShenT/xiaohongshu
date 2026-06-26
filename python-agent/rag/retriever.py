"""RAG 检索器 — Embedding + Qdrant 向量检索"""
import logging
import uuid
from typing import Optional
from rag.embedder import Embedder
from providers.vector.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class Retriever:
    """向量检索器"""

    def __init__(self, collection_name: str = "xhs_knowledge"):
        self.collection_name = collection_name
        self._embedder = Embedder()
        self._qdrant = QdrantClient()
        self._initialized = False

    async def _ensure_init(self):
        if not self._initialized:
            await self._qdrant.ensure_collection(self.collection_name, vector_size=1536)
            self._initialized = True

    async def add_document(self, doc_id: str, title: str, content: str, metadata: dict = None) -> bool:
        """添加文档到知识库"""
        await self._ensure_init()
        vector = await self._embedder.embed(title + " " + content[:2000])
        if not vector:
            return False

        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=hash(doc_id) % (2**63),
            vector=vector,
            payload={
                "doc_id": doc_id,
                "title": title,
                "content": content[:5000],
                "metadata": metadata or {},
            },
        )
        await self._qdrant.upsert(self.collection_name, [point])
        return True

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """语义搜索"""
        await self._ensure_init()
        vector = await self._embedder.embed(query)
        if not vector:
            return []

        results = await self._qdrant.search(self.collection_name, vector, limit)
        return [
            {
                "doc_id": r.payload.get("doc_id", ""),
                "title": r.payload.get("title", ""),
                "content": r.payload.get("content", ""),
                "score": r.score,
            }
            for r in results
        ]

    async def delete_document(self, doc_id: str):
        """删除文档"""
        await self._qdrant.delete(self.collection_name, [hash(doc_id) % (2**63)])


class KnowledgeBase:
    """知识库 — 文档管理 + 检索"""

    def __init__(self):
        self.retriever = Retriever()

    async def add(self, doc_id: str, title: str, content: str, metadata: dict = None) -> bool:
        return await self.retriever.add_document(doc_id, title, content, metadata)

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        return await self.retriever.search(query, limit)

    async def delete(self, doc_id: str):
        await self.retriever.delete_document(doc_id)


knowledge_base = KnowledgeBase()
