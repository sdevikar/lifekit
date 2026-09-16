"""lifekit.llm.base -- minimal provider protocol for model calls.

Every provider exposes one operation: send chat messages and get back a
content string constrained to a JSON schema. Transports (local Ollama,
OpenRouter, …) implement this; callers never touch provider specifics.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """A chat-completions backend with JSON-schema-constrained output."""

    def chat_json_schema(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        json_schema: dict[str, Any],
        temperature: float,
    ) -> str:
        """Return the assistant's content string for the given messages."""
        ...
