"""数据源 Provider 接口"""
from abc import ABC, abstractmethod
from models.schemas import Note, Comment


class IDataProvider(ABC):

    @abstractmethod
    async def search_notes(self, keyword: str, limit: int = 20) -> list[Note]:
        ...

    @abstractmethod
    async def get_note_detail(self, note_id: str) -> Note:
        ...

    @abstractmethod
    async def get_comments(self, note_id: str, limit: int = 50) -> list[Comment]:
        ...

    @abstractmethod
    async def get_user_notes(self, user_id: str, limit: int = 20) -> list[Note]:
        ...

    @abstractmethod
    async def publish_note(self, title: str, content: str, images: list[str]) -> str:
        ...
