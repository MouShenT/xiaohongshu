"""向量数据库客户端 — Qdrant 封装"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QdrantClient:
    """Qdrant 向量数据库客户端（懒加载）"""

    def __init__(self, host: str = "192.168.229.149", port: int = 6333):
        self.host = host
        self.port = port
        self._client = None

    async def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from qdrant_client import AsyncQdrantClient
            self._client = AsyncQdrantClient(host=self.host, port=self.port)
            logger.info("Qdrant 客户端初始化成功: %s:%s", self.host, self.port)
            return self._client
        except ImportError:
            logger.warning("qdrant_client 未安装，使用模拟模式")
            return None

    async def ensure_collection(self, collection_name: str, vector_size: int = 1536):
        client = await self._get_client()
        if client is None:
            return
        try:
            collections = await client.get_collections()
            existing = [c.name for c in collections.collections]
            if collection_name not in existing:
                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config={"size": vector_size, "distance": "Cosine"},
                )
                logger.info("创建 collection: %s (size=%d)", collection_name, vector_size)
        except Exception as e:
            logger.error("Qdrant 初始化失败: %s", e)

    async def upsert(self, collection_name: str, points: list):
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            logger.error("Qdrant upsert 失败: %s", e)

    async def search(self, collection_name: str, vector: list[float], limit: int = 10) -> list:
        client = await self._get_client()
        if client is None:
            return []
        try:
            results = await client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
            )
            return results
        except Exception as e:
            logger.error("Qdrant search 失败: %s", e)
            return []

    async def delete(self, collection_name: str, point_ids: list):
        client = await self._get_client()
        if client is None:
            return
        try:
            await client.delete(collection_name=collection_name, points_selector=point_ids)
        except Exception as e:
            logger.error("Qdrant delete 失败: %s", e)
