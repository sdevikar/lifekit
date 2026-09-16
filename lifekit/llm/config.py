"""lifekit.llm.config -- layered configuration for the model backend.

Resolution order (highest precedence first):

1. CLI flags (``--provider`` / ``--model``)
2. Environment variables (``LIFEKIT_PROVIDER`` / ``LIFEKIT_MODEL``; legacy
   ``OLLAMA_MODEL`` still honored for the Ollama provider; ``OPENROUTER_API_KEY``
   for the OpenRouter provider)
3. Config file ``~/.lifekit/config.json`` (keys: ``provider``, ``model``).
   Never stores API keys.
4. Defaults: ``ollama`` / ``qwen3.6:latest``.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".lifekit" / "config.json"

SUPPORTED_PROVIDERS = ("ollama", "openrouter")

DEFAULT_PROVIDER = "ollama"
DEFAULT_OLLAMA_MODEL = "qwen3.6:latest"

KEY_LIKE_NAMES = ("key", "api_key", "apikey", "token", "secret", "password")


@dataclass
class LLMConfig:
    provider: str
    model: str
    provider_source: str = "default"
    model_source: str = "default"
    api_key: str | None = field(default=None, repr=False)


def _read_config_file() -> dict[str, Any]:
    try:
        return json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _provider_default_model(provider: str) -> str | None:
    if provider == "ollama":
        return DEFAULT_OLLAMA_MODEL
    return None  # openrouter: model must be explicit (no invented slug)


def resolve_config(
    cli_provider: str | None = None, cli_model: str | None = None
) -> LLMConfig:
    """Resolve provider/model per the precedence chain above."""
    file_cfg = _read_config_file()

    # --- provider ---
    if cli_provider:
        provider, provider_source = cli_provider, "CLI flag"
    elif os.environ.get("LIFEKIT_PROVIDER"):
        provider, provider_source = os.environ["LIFEKIT_PROVIDER"], "env var LIFEKIT_PROVIDER"
    elif file_cfg.get("provider"):
        provider, provider_source = file_cfg["provider"], "config file"
    else:
        provider, provider_source = DEFAULT_PROVIDER, "default"

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unknown provider {provider!r}. Supported: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    # --- model ---
    if cli_model:
        model, model_source = cli_model, "CLI flag"
    elif os.environ.get("LIFEKIT_MODEL"):
        model, model_source = os.environ["LIFEKIT_MODEL"], "env var LIFEKIT_MODEL"
    elif provider == "ollama" and os.environ.get("OLLAMA_MODEL"):
        model, model_source = os.environ["OLLAMA_MODEL"], "env var OLLAMA_MODEL"
    elif file_cfg.get("model"):
        model, model_source = file_cfg["model"], "config file"
    else:
        default = _provider_default_model(provider)
        if default is None:
            raise ValueError(
                f"Provider {provider!r} requires an explicit model: pass --model, "
                f"set LIFEKIT_MODEL, or run `lifekit config set model <model>`."
            )
        model, model_source = default, "default"

    # --- credentials (env only, never the config file) ---
    api_key = None
    if provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "Provider 'openrouter' needs OPENROUTER_API_KEY set in the "
                "environment. Get a key at https://openrouter.ai/keys and run: "
                "export OPENROUTER_API_KEY=sk-or-..."
            )

    return LLMConfig(
        provider=provider,
        model=model,
        provider_source=provider_source,
        model_source=model_source,
        api_key=api_key,
    )


def write_config_file(updates: dict[str, Any]) -> Path:
    """Merge updates into the config file; refuses key-like names."""
    for name in updates:
        if any(k in name.lower() for k in KEY_LIKE_NAMES):
            raise ValueError(
                f"Refusing to store {name!r}: API keys live in the environment, "
                "never in the config file."
            )
    cfg = _read_config_file()
    cfg.update(updates)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
    return CONFIG_PATH
