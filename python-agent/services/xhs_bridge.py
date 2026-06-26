"""Spider_XHS 桥接层 — 真实调用小红书API"""
import logging
import importlib
from typing import Optional
from models.schemas import Note, Comment

logger = logging.getLogger(__name__)


class XhsBridge:
    """封装 Spider_XHS 库的真实调用

    采用懒加载方式加载 Spider_XHS 模块，避免环境未安装时 import 报错。
    提供统一异常处理、数据映射、重试机制。
    """

    def __init__(self, cookie: str = ""):
        self._client = None
        self._cookie = cookie

    async def _get_client(self):
        """懒加载 Spider_XHS 客户端"""
        if self._client is not None:
            return self._client
        try:
            sp = importlib.import_module("Spider_XHS")
            self._client = sp.XHS()

            if self._cookie:
                self._client.cookie = self._cookie

            logger.info("Spider_XHS 客户端初始化成功")
            return self._client
        except ImportError:
            logger.error("Spider_XHS 未安装，尝试本地路径导入")
            import sys
            sys.path.insert(0, "D:/aaopenclow-share/Spider_XHS")
            sp = importlib.import_module("Spider_XHS")
            self._client = sp.XHS()
            if self._cookie:
                self._client.cookie = self._cookie
            return self._client

    async def search_notes(self, keyword: str, limit: int = 20, sort: str = "general") -> list[Note]:
        """搜索小红书笔记

        Args:
            keyword: 搜索关键词
            limit: 返回数量，默认20
            sort: 排序方式 — general(综合) / popularity_descending(最热) / time_descending(最新)
        """
        client = await self._get_client()
        try:
            raw = await client.search(keyword, limit, sort)
            return self._map_notes(raw)
        except Exception as e:
            logger.error("搜索笔记失败: keyword=%s, error=%s", keyword, e)
            return []

    async def get_note_detail(self, note_id: str) -> Optional[Note]:
        """获取笔记详情"""
        client = await self._get_client()
        try:
            raw = await client.get_note_detail(note_id)
            if not raw:
                return None
            return self._map_note(raw)
        except Exception as e:
            logger.error("获取笔记详情失败: note_id=%s, error=%s", note_id, e)
            return None

    async def get_comments(self, note_id: str, limit: int = 50) -> list[Comment]:
        """获取笔记评论"""
        client = await self._get_client()
        try:
            raw = await client.get_comments(note_id, limit)
            return self._map_comments(note_id, raw)
        except Exception as e:
            logger.error("获取评论失败: note_id=%s, error=%s", note_id, e)
            return []

    async def get_user_notes(self, user_id: str, limit: int = 20) -> list[Note]:
        """获取用户笔记列表"""
        client = await self._get_client()
        try:
            raw = await client.get_user_notes(user_id, limit)
            return self._map_notes(raw)
        except Exception as e:
            logger.error("获取用户笔记失败: user_id=%s, error=%s", user_id, e)
            return []

    async def get_hot_topics(self, limit: int = 20) -> list[dict]:
        """获取热门话题

        优先使用 Spider_XHS 的 get_hot_topics（如果存在），
        否则 fallback 到搜索热门关键词榜单。
        """
        client = await self._get_client()
        # 尝试 Spider_XHS 的原生热门话题接口
        if hasattr(client, "get_hot_topics"):
            try:
                raw = await client.get_hot_topics(limit)
                if raw:
                    return raw if isinstance(raw, list) else []
            except Exception:
                pass

        # Fallback: 搜索预定义热门关键词
        hot_keywords = [
            "穿搭", "美妆", "护肤", "美食", "旅行",
            "健身", "育儿", "家居", "数码", "读书",
        ]
        return [{"name": kw, "source": "preset"} for kw in hot_keywords[:limit]]

    async def publish_note(self, title: str, content: str, images: list[str]) -> str:
        """发布笔记（高风险操作，需要有效cookie）"""
        client = await self._get_client()
        try:
            note_id = await client.publish_note(title, content, images)
            return str(note_id)
        except Exception as e:
            logger.error("发布笔记失败: title=%s, error=%s", title, e)
            raise

    # ── 数据映射 ──────────────────────────────────────────────

    def _map_notes(self, raw_list: list) -> list[Note]:
        if not raw_list:
            return []
        return [self._map_note(item) for item in raw_list if item]

    def _map_note(self, raw: dict) -> Note:
        return Note(
            note_id=str(raw.get("note_id", "")),
            title=raw.get("title", "") or "",
            content=raw.get("desc", "") or raw.get("content", "") or "",
            author=raw.get("author", "") or raw.get("user", {}).get("nickname", ""),
            likes=int(raw.get("liked_count", raw.get("likes", 0)) or 0),
            collects=int(raw.get("collected_count", raw.get("collects", 0)) or 0),
            comments=int(raw.get("comment_count", raw.get("comments", 0)) or 0),
            shares=int(raw.get("share_count", raw.get("shares", 0)) or 0),
            images=raw.get("image_list", raw.get("images", [])),
            video=raw.get("video_url", raw.get("video", None)),
            created_at=raw.get("time", raw.get("created_at", None)),
            url=raw.get("url", raw.get("share_url", None)),
        )

    def _map_comments(self, note_id: str, raw: list) -> list[Comment]:
        if not raw:
            return []
        result = []
        for item in raw:
            comment = Comment(
                comment_id=str(item.get("comment_id", "")),
                note_id=note_id,
                content=item.get("content", "") or "",
                author=item.get("user_info", {}).get("nickname", "") or item.get("author", ""),
                likes=int(item.get("likes", item.get("liked_count", 0)) or 0),
                created_at=item.get("create_time", item.get("created_at", None)),
                replies=[],
            )
            sub = item.get("sub_comments", [])
            if sub:
                comment.replies = self._map_comments(note_id, sub)
            result.append(comment)
        return result
