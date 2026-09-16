"""Tests for the `lifekit config` CLI (in-process, isolated config path)."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lifekit.config.__main__ as config_cli


@pytest.fixture()
def isolated(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(config_cli, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("lifekit.llm.config.CONFIG_PATH", tmp_path / "config.json")
    for var in ("LIFEKIT_PROVIDER", "LIFEKIT_MODEL", "OLLAMA_MODEL", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path, capsys


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["lifekit.config", *argv])
    config_cli.main()


def test_set_and_view_roundtrip(isolated, monkeypatch):
    tmp_path, capsys = isolated
    _run(monkeypatch, "set", "provider", "ollama")
    _run(monkeypatch, "set", "model", "my-model:1")
    _run(monkeypatch, "view")
    out = capsys.readouterr().out
    assert "provider : ollama" in out
    assert "my-model:1" in out
    assert "config file" in out


def test_set_refuses_key_like_names(isolated, monkeypatch):
    _, capsys = isolated
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "set", "api_key", "sk-or-secret")
    assert exc.value.code == 2
    assert "never in the config file" in capsys.readouterr().err


def test_view_never_prints_key_value(isolated, monkeypatch):
    tmp_path, capsys = isolated
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-should-not-appear")
    _run(monkeypatch, "view")
    out = capsys.readouterr().out
    assert "sk-or-should-not-appear" not in out
    assert "OPENROUTER_API_KEY: set" in out


def test_unset_removes_value(isolated, monkeypatch):
    tmp_path, capsys = isolated
    _run(monkeypatch, "set", "model", "x")
    _run(monkeypatch, "unset", "model")
    stored = json.loads((tmp_path / "config.json").read_text())
    assert "model" not in stored


def test_set_unknown_provider_rejected(isolated, monkeypatch):
    _, capsys = isolated
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "set", "provider", "notareal")
    assert exc.value.code == 2
