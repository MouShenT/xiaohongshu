"""AI 创作服务 — 标题/正文/标签生成"""
import logging
from typing import Optional
from providers.llm import get_llm_provider
from prompt_center.prompt_service import prompt_center

logger = logging.getLogger(__name__)


class ContentWriterService:
    """AI 创作服务"""

    def __init__(self):
        self._provider = None

    def _get_provider(self):
        if self._provider is None:
            self._provider = get_llm_provider("openai")
        return self._provider

    async def generate_titles(self, topic: str, count: int = 5) -> list[str]:
        """根据主题生成标题"""
        prompt = (
            f"你是一个小红书爆款标题专家。请为主题「{topic}」生成 {count} 个吸引眼球的标题。\n\n"
            f"要求：\n"
            f"- 每个标题不超过20字\n"
            f"- 包含数字或疑问句\n"
            f"- 直接输出标题列表，每行一个，不要序号\n"
            f"- 风格要有小红书特色，可以用emoji"
        )
        provider = self._get_provider()
        try:
            result = await provider.chat([
                {"role": "user", "content": prompt}
            ], model="gpt-4o")
            titles = [t.strip().strip('"').strip("'") for t in result.split("\n") if t.strip()]
            return titles[:count]
        except Exception as e:
            logger.error("标题生成失败: %s", e)
            return [f"{topic}的5个惊人发现", f"原来{topic}可以这样", f"{topic}避坑指南"]

    async def generate_content(self, topic: str, style: str = "教程", keywords: list[str] = None) -> str:
        """根据主题生成正文"""
        kw = ", ".join(keywords or [])
        prompt = (
            f"你是一个小红书内容创作专家。请写一篇{style}类的笔记。\n\n"
            f"主题：{topic}\n"
            f"关键词：{kw}\n\n"
            f"要求：\n"
            f"- 300-500字\n"
            f"- 开头要吸引眼球\n"
            f"- 正文要干货满满\n"
            f"- 结尾要有互动引导\n"
            f"- 语言风格要像真人博主，不要官方腔"
        )
        provider = self._get_provider()
        try:
            return await provider.chat([
                {"role": "user", "content": prompt}
            ], model="gpt-4o")
        except Exception as e:
            logger.error("内容生成失败: %s", e)
            return f"关于{topic}的分享\n\n今天来和大家聊聊{topic}...（AI生成内容暂不可用）"

    async def generate_tags(self, topic: str, content: str = "") -> list[str]:
        """生成标签推荐"""
        text = content or topic
        prompt = (
            f"根据以下内容，推荐8-10个小红书标签：\n\n{text}\n\n"
            f"直接输出标签列表，每行一个，格式：#标签名"
        )
        provider = self._get_provider()
        try:
            result = await provider.chat([
                {"role": "user", "content": prompt}
            ], model="gpt-4o")
            tags = [t.strip() for t in result.split("\n") if t.strip().startswith("#")]
            return tags[:10]
        except Exception as e:
            logger.error("标签生成失败: %s", e)
            return [f"#{topic}", f"#{topic}教程", f"#{topic}干货"]

    async def complete_draft(self, title: str, outline: str) -> dict:
        """根据标题和大纲完成完整草稿"""
        prompt = (
            f"请根据以下标题和大纲，完成一篇小红书笔记。\n\n"
            f"标题：{title}\n"
            f"大纲：{outline}\n\n"
            f"要求：完整的正文内容，包含开头、正文、结尾，300-500字。"
        )
        provider = self._get_provider()
        try:
            content = await provider.chat([
                {"role": "user", "content": prompt}
            ], model="gpt-4o")
            tags = await self.generate_tags(title, content)
            return {"title": title, "content": content, "tags": tags}
        except Exception as e:
            logger.error("草稿生成失败: %s", e)
            return {"title": title, "content": "", "tags": []}
