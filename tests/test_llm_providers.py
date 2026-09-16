"""Tests for lifekit.llm providers — mocked transport, no network."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.llm import get_provider
from lifekit.llm.base import LLMProvider
from lifekit.llm.config import resolve_config
from lifekit.llm.ollama_provider import OllamaProvider
from lifekit.llm.openrouter_provider import OpenRouterProvider


class FakeOllamaClient:
    def __init__(self):
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        return {"message": {"content": '{"chapter_title": "X"}'}}


def test_ollama_provider_passes_schema_and_temperature():
    client = FakeOllamaClient()
    provider = OllamaProvider(client=client)
    schema = {"type": "object", "properties": {}}
    out = provider.chat_json_schema(
        model="qwen3.6:latest",
        messages=[{"role": "user", "content": "hi"}],
        json_schema=schema,
        temperature=0.1,
    )
    assert out == '{"chapter_title": "X"}'
    call = client.calls[0]
    assert call["format"] == schema
    assert call["options"] == {"temperature": 0.1}
    assert call["model"] == "qwen3.6:latest"


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _fake_urlopen(captured):
    def _inner(request, timeout=None):
        captured["request"] = request
        captured["body"] = json.loads(request.data.decode())
        return FakeResponse(
            {"choices": [{"message": {"content": '{"chapter_title": "Y"}'}}]}
        )

    return _inner


def test_openrouter_provider_request_shape():
    captured = {}
    provider = OpenRouterProvider(api_key="sk-or-secret", model="some/model")
    schema = {"type": "object", "properties": {}}
    with patch("urllib.request.urlopen", _fake_urlopen(captured)):
        out = provider.chat_json_schema(
            model="some/model",
            messages=[{"role": "user", "content": "hi"}],
            json_schema=schema,
            temperature=0.1,
        )
    assert out == '{"chapter_title": "Y"}'
    req = captured["request"]
    assert req.full_url == "https://openrouter.ai/api/v1/chat/completions"
    assert req.get_header("Authorization") == "Bearer sk-or-secret"
    assert req.get_header("Content-type") == "application/json"
    body = captured["body"]
    assert body["model"] == "some/model"
    assert body["messages"] == [{"role": "user", "content": "hi"}]
    assert body["temperature"] == 0.1
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["schema"] == schema


def test_openrouter_provider_without_key_raises():
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider(api_key=None, model="some/model")


def test_factory_returns_ollama_by_default(monkeypatch, tmp_path):
    for var in ("LIFEKIT_PROVIDER", "LIFEKIT_MODEL", "OLLAMA_MODEL", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("lifekit.llm.config.CONFIG_PATH", tmp_path / "config.json")

    class FakeOllamaModule:
        @staticmethod
        def Client():
            return FakeOllamaClient()

    monkeypatch.setitem(sys.modules, "ollama", FakeOllamaModule)
    provider = get_provider()
    assert isinstance(provider, OllamaProvider)


def test_factory_returns_openrouter(monkeypatch, tmp_path):
    for var in ("LIFEKIT_PROVIDER", "LIFEKIT_MODEL", "OLLAMA_MODEL"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setattr("lifekit.llm.config.CONFIG_PATH", tmp_path / "config.json")
    provider = get_provider(resolve_config(cli_provider="openrouter", cli_model="m/x"))
    assert isinstance(provider, OpenRouterProvider)


def test_providers_satisfy_protocol():
    assert isinstance(OllamaProvider(client=FakeOllamaClient()), LLMProvider)
    assert isinstance(OpenRouterProvider(api_key="sk-or-x", model="m/x"), LLMProvider)
