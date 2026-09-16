"""lifekit.llm.openrouter_provider -- OpenRouter backend for the provider protocol.

Uses the OpenAI-compatible chat-completions endpoint
``POST https://openrouter.ai/api/v1/chat/completions`` (verified against the
OpenRouter API docs) with ``Authorization: Bearer $OPENROUTER_API_KEY``,
``response_format`` json_schema, and attribution headers. Stdlib urllib only —
no new dependencies.

Structured output follows OpenAI's json_schema response_format shape:
``{"type": "json_schema", "json_schema": {"name": …, "strict": true,
"schema": …}}``.
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any

from lifekit.llm.base import LLMProvider

BASE_URL = "https://openrouter.ai/api/v1"
CHAT_COMPLETIONS_PATH = "/chat/completions"
APP_NAME = "LifeKit"
APP_URL = "https://github.com/sdevikar/lifekit"


class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str | None = None):
        if not api_key:
            raise ValueError(
                "OpenRouterProvider needs an API key: set OPENROUTER_API_KEY "
                "in the environment (https://openrouter.ai/keys)."
            )
        self._api_key = api_key
        self._model = model

    def chat_json_schema(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        json_schema: dict[str, Any],
        temperature: float,
    ) -> str:
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "lifekit_extraction",
                    "strict": True,
                    "schema": json_schema,
                },
            },
        }
        req = urllib.request.Request(
            BASE_URL + CHAT_COMPLETIONS_PATH,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": APP_URL,
                "X-Title": APP_NAME,
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"]
