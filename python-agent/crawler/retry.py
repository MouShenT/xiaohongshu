"""重试机制 — 指数退避重试"""
import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def async_retry(max_retries: int = 3, base_delay: float = 1.0, backoff: float = 2.0):
    """异步函数重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (backoff ** (attempt - 1))
                        logger.warning("重试 %s/%s: %s, 等待 %.1fs", attempt, max_retries, e, delay)
                        await asyncio.sleep(delay)
                    else:
                        logger.error("重试耗尽 %s/%s: %s", attempt, max_retries, e)
            raise last_exception
        return wrapper
    return decorator


class RetryHandler:
    """可配置的重试处理器"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute(self, func, *args, **kwargs):
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
        raise last_exception
