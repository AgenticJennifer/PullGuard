from __future__ import annotations
import os
from pullguard.llm.base import LLMClient
from pullguard.config import LLMConfig


def build_client(config: LLMConfig) -> LLMClient:
    provider = config.provider
    api_key = config.api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""

    if provider == "gemini":
        from pullguard.llm.gemini import GeminiClient
        return GeminiClient(
            model=config.model,
            api_key=api_key,
            temperature=config.temperature,
        )
    if provider == "anthropic":
        from pullguard.llm.anthropic import AnthropicClient
        return AnthropicClient(
            model=config.model,
            api_key=api_key,
            temperature=config.temperature,
        )

    raise ValueError(f"Unknown LLM provider: {provider}. Supported: gemini, anthropic")
