"""Spider_XHS 桥接 — 小红书数据 Provider"""
from providers.data.base import IDataProvider
from models.schemas import Note, Comment


class XiaoHongShuProvider(IDataProvider):

    async def search_notes(self, keyword: str, limit: int = 20) -> list[Note]:
        # TODO: 调用 Spider_XHS 搜索接口
        return []

    async def get_note_detail(self, note_id: str) -> Note:
        # TODO: 调用 Spider_XHS 获取笔记详情
        ...

    async def get_comments(self, note_id: str, limit: int = 50) -> list[Comment]:
        # TODO: 调用 Spider_XHS 获取评论
        return []

    async def get_user_notes(self, user_id: str, limit: int = 20) -> list[Note]:
        return []

    async def publish_note(self, title: str, content: str, images: list[str]) -> str:
        # TODO: 调用 Spider_XHS 发布笔记
        return ""
