"""请求限流器 — 滑动窗口频率控制"""
import time
from collections import deque


class RateLimiter:
    """滑动窗口限流器"""

    def __init__(self, max_calls: int = 30, window: float = 60.0):
        self.max_calls = max_calls
        self.window = window
        self._calls: deque = deque()

    def acquire(self) -> float:
        """尝试获取许可，返回需要等待的秒数"""
        now = time.time()

        # 清除窗口外的记录
        while self._calls and now - self._calls[0] > self.window:
            self._calls.popleft()

        if len(self._calls) >= self.max_calls:
            # 需要等待
            wait = self._calls[0] + self.window - now
            return max(wait, 0)

        self._calls.append(now)
        return 0.0

    async def wait_if_needed(self):
        """如果超限则等待"""
        wait = self.acquire()
        if wait > 0:
            import asyncio
            await asyncio.sleep(wait)
