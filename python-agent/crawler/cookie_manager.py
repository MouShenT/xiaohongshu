"""Cookie 管理器 — 多账号 Cookie 轮换/有效期检查"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CookieManager:
    """管理小红书 Cookie，支持多账号轮换"""

    def __init__(self):
        self._cookies: dict[int, str] = {}  # credential_id -> cookie_json

    def add_cookie(self, credential_id: int, cookie_str: str):
        self._cookies[credential_id] = cookie_str
        logger.info("Cookie 已添加: credential_id=%s", credential_id)

    def remove_cookie(self, credential_id: int):
        self._cookies.pop(credential_id, None)

    def get_cookie(self, credential_id: int) -> Optional[str]:
        return self._cookies.get(credential_id)

    def get_any_valid(self) -> Optional[str]:
        """获取任意一个有效 Cookie"""
        for cookie in self._cookies.values():
            return cookie
        return None

    def get_all(self) -> dict[int, str]:
        return dict(self._cookies)
