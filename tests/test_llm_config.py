"""Tests for lifekit.llm.config — resolution order: CLI > env > config file > defaults."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.llm.config import (
    CONFIG_PATH,
    LLMConfig,
    resolve_config,
)


@pytest.fixture()
def clean_env(monkeypatch, tmp_path):
    for var in ("LIFEKIT_PROVIDER", "LIFEKIT_MODEL", "OLLAMA_MODEL", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("lifekit.llm.config.CONFIG_PATH", tmp_path / "config.json")
    return tmp_path


def _write_config(tmp_path, **kwargs):
    (tmp_path / "config.json").write_text(json.dumps(kwargs))


def test_defaults_ollama(clean_env):
    cfg = resolve_config()
    assert cfg.provider == "ollama"
    assert cfg.model == "qwen3.6:latest"
    assert cfg.provider_source == "default"
    assert cfg.model_source == "default"


def test_config_file_overrides_defaults(clean_env, tmp_path):
    _write_config(tmp_path, provider="openrouter", model="qwen/qwen3-72b-instruct")
    os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
    cfg = resolve_config()
    assert cfg.provider == "openrouter"
    assert cfg.provider_source == "config file"
    assert cfg.model_source == "config file"


def test_env_overrides_config_file(clean_env, tmp_path, monkeypatch):
    _write_config(tmp_path, provider="openrouter", model="file-model")
    monkeypatch.setenv("LIFEKIT_PROVIDER", "ollama")
    monkeypatch.setenv("LIFEKIT_MODEL", "env-model")
    cfg = resolve_config()
    assert cfg.provider == "ollama"
    assert cfg.provider_source == "env var LIFEKIT_PROVIDER"
    assert cfg.model == "env-model"
    assert cfg.model_source == "env var LIFEKIT_MODEL"


def test_legacy_ollama_model_env(clean_env, monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "legacy-model:1")
    cfg = resolve_config()
    assert cfg.model == "legacy-model:1"
    assert cfg.model_source == "env var OLLAMA_MODEL"


def test_cli_overrides_env(clean_env, monkeypatch):
    monkeypatch.setenv("LIFEKIT_PROVIDER", "ollama")
    monkeypatch.setenv("LIFEKIT_MODEL", "env-model")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    cfg = resolve_config(cli_provider="openrouter", cli_model="cli-model")
    assert cfg.provider == "openrouter"
    assert cfg.provider_source == "CLI flag"
    assert cfg.model == "cli-model"
    assert cfg.model_source == "CLI flag"


def test_openrouter_without_key_raises(clean_env):
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        resolve_config(cli_provider="openrouter", cli_model="some/model")


def test_openrouter_without_model_raises(clean_env, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    with pytest.raises(ValueError, match="[Mm]odel"):
        resolve_config(cli_provider="openrouter")


def test_unknown_provider_raises(clean_env):
    with pytest.raises(ValueError, match="Unknown provider"):
        resolve_config(cli_provider="notarealprovider")


def test_ollama_ignores_missing_openrouter_key(clean_env):
    cfg = resolve_config()
    assert cfg.provider == "ollama"
    assert cfg.api_key is None
