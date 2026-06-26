"""WebSocket 通知客户端"""
import asyncio
import json
import logging

import aiohttp

logger = logging.getLogger(__name__)


class WebSocketNotifier:
    """通过 HTTP 调用 SpringBoot Gateway 推送 WebSocket 消息"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    async def notify_task_progress(self, task_id: int, log_message: str):
        """通知 SpringBoot Gateway 推送任务日志"""
        url = f"{self.base_url}/api/internal/notify-task"
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={
                    "taskId": task_id,
                    "log": log_message,
                })
        except Exception as e:
            logger.warning("WebSocket 通知失败: %s", e)
