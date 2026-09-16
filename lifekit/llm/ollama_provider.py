"""lifekit.llm.ollama_provider -- Ollama backend for the provider protocol."""
from __future__ import annotations

from typing import Any

from lifekit.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Wraps ``ollama.Client`` behind the provider protocol.

    Behavior is byte-identical to the pre-abstraction call sites:
    schema-constrained chat via ``format=<json schema>`` with
    ``options={"temperature": …}``.
    """

    def __init__(self, client: Any | None = None):
        if client is None:
            import ollama

            client = ollama.Client()
        self._client = client

    def chat_json_schema(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        json_schema: dict[str, Any],
        temperature: float,
    ) -> str:
        resp = self._client.chat(
            model=model,
            messages=messages,
            format=json_schema,
            options={"temperature": temperature},
        )
        return resp["message"]["content"]
