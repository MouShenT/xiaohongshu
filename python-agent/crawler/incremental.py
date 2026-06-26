"""增量采集 — 基于时间戳的去重"""
from datetime import datetime
from typing import Optional


class IncrementalCollector:
    """增量采集控制器，避免重复采集"""

    def __init__(self):
        self._last_collected: dict[str, datetime] = {}

    def should_collect(self, key: str, max_interval_hours: float = 24) -> bool:
        """检查是否需要重新采集"""
        last = self._last_collected.get(key)
        if last is None:
            return True
        elapsed = (datetime.now() - last).total_seconds() / 3600
        return elapsed > max_interval_hours

    def mark_collected(self, key: str):
        self._last_collected[key] = datetime.now()

    def get_last_time(self, key: str) -> Optional[datetime]:
        return self._last_collected.get(key)
