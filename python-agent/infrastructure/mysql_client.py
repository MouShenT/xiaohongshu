"""MySQL 数据操作层"""
import json
from typing import Optional


class MySQLClient:
    """异步 MySQL 客户端 — 导入 aiomysql 放在方法内避免启动报错"""

    def __init__(self):
        self.pool: Optional = None

    async def connect(self):
        import aiomysql
        from config import settings
        self.pool = await aiomysql.create_pool(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database,
            charset="utf8mb4",
            autocommit=True,
        )

    async def update_task_result(self, task_id: int, status: str, result: dict = None,
                                  progress: int = 100, error_message: str = None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """UPDATE task SET status=%s, result=%s, progress=%s,
                         error_message=%s, finished_at=NOW()
                         WHERE id=%s"""
                await cur.execute(sql, (
                    status,
                    json.dumps(result, ensure_ascii=False) if result else None,
                    progress,
                    error_message,
                    task_id,
                ))

    async def insert_note(self, user_id: int, note: dict) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql = """INSERT INTO note (user_id, note_id, title, content, author, author_id,
                         likes, collects, comments_cnt, shares, images, video, tags, url, collected_at)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                         ON DUPLICATE KEY UPDATE likes=VALUES(likes), collects=VALUES(collects),
                         comments_cnt=VALUES(comments_cnt), shares=VALUES(shares)"""
                await cur.execute(sql, (
                    user_id,
                    note.get("note_id"),
                    note.get("title"),
                    note.get("content"),
                    note.get("author"),
                    note.get("author_id"),
                    note.get("likes", 0),
                    note.get("collects", 0),
                    note.get("comments_cnt", 0),
                    note.get("shares", 0),
                    json.dumps(note.get("images", []), ensure_ascii=False),
                    note.get("video"),
                    json.dumps(note.get("tags", []), ensure_ascii=False),
                    note.get("url"),
                ))
                return cur.lastrowid

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
