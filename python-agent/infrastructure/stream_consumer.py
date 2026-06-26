"""Redis Stream 消费者 — 异步任务处理"""
import asyncio
import json
import logging
from typing import Optional

from config import settings
from orchestrator.router import TaskRouter
from orchestrator.task_dispatcher import TaskDispatcher

logger = logging.getLogger(__name__)


class StreamConsumer:
    """消费 xhs:task:queue，路由到 Orchestrator"""

    def __init__(self):
        self.redis = None
        self.stream_key = "xhs:task:queue"
        self.group_name = "xhs-workers"
        self.consumer_name = "worker-1"
        self.router = TaskRouter(TaskDispatcher())

    async def connect(self):
        import redis.asynced as aioredis
        self.redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
        )
        try:
            await self.redis.xgroup_create(self.stream_key, self.group_name, id="0", mkstream=True)
        except Exception:
            pass

    async def consume(self):
        await self.connect()
        logger.info("StreamConsumer 启动，监听: %s", self.stream_key)

        while True:
            try:
                results = await self.redis.xreadgroup(
                    self.group_name, self.consumer_name,
                    {self.stream_key: ">"}, count=1, block=5000
                )
                if not results:
                    await asyncio.sleep(0.1)
                    continue

                for stream_name, messages in results:
                    for msg_id, msg_data in messages:
                        await self._process_message(msg_id, msg_data)

            except Exception as e:
                logger.error("消费异常: %s", e)
                await asyncio.sleep(1)

    async def _process_message(self, msg_id: str, msg_data: dict):
        try:
            payload = json.loads(msg_data.get("payload", "{}"))
            task_type = payload.get("type", "")
            logger.info("处理任务: type=%s, id=%s", task_type, payload.get("taskId"))

            result = await self.router.route(task_type, payload)

            logger.info("任务完成: type=%s, result=%s", task_type, result)
            await self.redis.xack(self.stream_key, self.group_name, msg_id)

        except Exception as e:
            logger.error("任务处理失败: %s", e)
            await self.redis.xack(self.stream_key, self.group_name, msg_id)
