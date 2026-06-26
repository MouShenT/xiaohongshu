"""采集调度器 — 管理采集任务的调度执行"""
import asyncio
import logging
from datetime import datetime

from crawler.cookie_manager import CookieManager
from crawler.account_manager import AccountManager
from crawler.proxy_manager import ProxyManager
from crawler.limiter import RateLimiter
from crawler.retry import RetryHandler
from crawler.incremental import IncrementalCollector

logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """采集调度器 — 整合所有子模块"""

    def __init__(self):
        self.cookie_mgr = CookieManager()
        self.account_mgr = AccountManager()
        self.proxy_mgr = ProxyManager()
        self.limiter = RateLimiter()
        self.retry = RetryHandler()
        self.incremental = IncrementalCollector()

    async def execute_collect(self, task_data: dict) -> dict:
        """执行采集任务"""
        keyword = task_data.get("keyword", "")
        task_id = task_data.get("taskId", 0)

        if self.incremental.should_collect(f"keyword:{keyword}"):
            logger.info("开始采集: keyword=%s, taskId=%s", keyword, task_id)
            await self.limiter.wait_if_needed()

            account = self.account_mgr.get_available()
            if not account:
                return {"status": "FAILED", "error": "无可用账号"}

            # TODO: 实际调用 Spider_XHS
            result = {"status": "SUCCESS", "notes_count": 0}
            self.incremental.mark_collected(f"keyword:{keyword}")
            return result
        else:
            logger.info("跳过采集（仍在冷却期）: keyword=%s", keyword)
            return {"status": "SKIPPED", "reason": "cooling"}
