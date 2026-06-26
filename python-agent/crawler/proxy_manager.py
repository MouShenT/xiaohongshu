"""代理管理器 — 代理 IP 轮换"""
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ProxyManager:
    """管理代理 IP 池"""

    def __init__(self):
        self._proxies: list[str] = []

    def add_proxy(self, proxy: str):
        if proxy not in self._proxies:
            self._proxies.append(proxy)

    def add_proxies(self, proxies: list[str]):
        for p in proxies:
            self.add_proxy(p)

    def get_random(self) -> Optional[str]:
        if not self._proxies:
            return None
        return random.choice(self._proxies)

    def remove_proxy(self, proxy: str):
        if proxy in self._proxies:
            self._proxies.remove(proxy)
            logger.info("代理已移除: %s", proxy)

    def count(self) -> int:
        return len(self._proxies)
