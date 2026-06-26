"""LLM Provider 工厂 — 统一获取 Provider 实例"""
import logging
from typing import Optional
from providers.llm.base import ILLMProvider

logger = logging.getLogger(__name__)

_providers: dict[str, ILLMProvider] = {}


def get_llm_provider(provider_type: str = "openai") -> ILLMProvider:
    """获取 LLM Provider 实例 (单例)"""
    if provider_type in _providers:
        return _providers[provider_type]

    from config import settings

    if provider_type == "openai":
        from providers.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o",
        )
    elif provider_type == "deepseek":
        from providers.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            api_key=settings.deepseek_api_key or settings.openai_api_key,
            base_url="https://api.deepseek.com/v1",
            default_model="deepseek-chat",
        )
    elif provider_type == "qwen":
        from providers.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            api_key=settings.qwen_api_key or settings.openai_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            default_model="qwen-plus",
        )
    elif provider_type == "claude":
        from providers.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url="https://api.anthropic.com/v1",
            default_model="claude-3-5-sonnet-20241022",
        )
    else:
        raise ValueError(f"未知 Provider 类型: {provider_type}")

    _providers[provider_type] = provider
    return provider


def list_available_providers() -> list[str]:
    return ["openai", "deepseek", "qwen", "claude"]
