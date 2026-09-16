"""lifekit.llm -- configurable model backends.

Usage:
    from lifekit.llm import get_provider, resolve_config

    provider = get_provider()  # resolves CLI/env/file/defaults
    text = provider.chat_json_schema(
        model=cfg.model, messages=[...], json_schema={...}, temperature=0.1)
"""
from lifekit.llm.base import LLMProvider
from lifekit.llm.config import LLMConfig, resolve_config
from lifekit.llm.ollama_provider import OllamaProvider
from lifekit.llm.openrouter_provider import OpenRouterProvider

__all__ = [
    "LLMProvider",
    "LLMConfig",
    "resolve_config",
    "get_provider",
    "OllamaProvider",
    "OpenRouterProvider",
]


def get_provider(config: LLMConfig | None = None) -> LLMProvider:
    """Build the configured provider."""
    config = config or resolve_config()
    if config.provider == "ollama":
        return OllamaProvider()
    if config.provider == "openrouter":
        return OpenRouterProvider(api_key=config.api_key, model=config.model)
    raise ValueError(f"Unknown provider {config.provider!r}")
