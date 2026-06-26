"""账号管理器 — 多账号池 + Cookie 同步"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Account:
    def __init__(self, account_id: int, cookie_str: str, proxy: str = None):
        self.account_id = account_id
        self.cookie_str = cookie_str
        self.proxy = proxy
        self.is_valid = True
        self.error_count = 0
        self.last_used = None


class AccountManager:
    """管理多个小红书账号的 Cookie 和状态"""

    def __init__(self):
        self._accounts: dict[int, Account] = {}

    def add_account(self, account_id: int, cookie_str: str, proxy: str = None):
        self._accounts[account_id] = Account(account_id, cookie_str, proxy)
        logger.info("账号已添加: account_id=%s", account_id)

    def remove_account(self, account_id: int):
        self._accounts.pop(account_id, None)

    def get_available(self) -> Optional[Account]:
        """轮询获取可用账号"""
        for acc in self._accounts.values():
            if acc.is_valid:
                return acc
        return None

    def mark_error(self, account_id: int):
        acc = self._accounts.get(account_id)
        if acc:
            acc.error_count += 1
            if acc.error_count >= 5:
                acc.is_valid = False
                logger.warning("账号已标记失效: account_id=%s", account_id)

    def mark_valid(self, account_id: int):
        acc = self._accounts.get(account_id)
        if acc:
            acc.error_count = 0
            acc.is_valid = True

    def count_valid(self) -> int:
        return sum(1 for acc in self._accounts.values() if acc.is_valid)
