"""CLI: inspect and persist LifeKit's LLM provider configuration.

Usage:
    python -m lifekit.config view                 # resolved provider/model + source of each
    python -m lifekit.config set provider openrouter
    python -m lifekit.config set model <model-tag>
    python -m lifekit.config unset provider|model

Config lives in ~/.lifekit/config.json. API keys are never stored there —
only OPENROUTER_API_KEY in the environment is honored, and `view` only shows
whether it is set.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lifekit.llm.config import (
    CONFIG_PATH,
    KEY_LIKE_NAMES,
    SUPPORTED_PROVIDERS,
    _read_config_file,
    resolve_config,
    write_config_file,
)


def _view():
    cfg = resolve_config()
    file_cfg = _read_config_file()
    print(f"provider : {cfg.provider}  ({cfg.provider_source})")
    print(f"model    : {cfg.model}  ({cfg.model_source})")
    key_set = bool(os.environ.get("OPENROUTER_API_KEY"))
    print(f"OPENROUTER_API_KEY: {'set' if key_set else 'not set'}")
    print(f"config file: {CONFIG_PATH} ({'exists' if CONFIG_PATH.exists() else 'missing'})")
    if file_cfg:
        print("stored:", json.dumps(file_cfg))


def _set(name: str, value: str):
    if any(k in name.lower() for k in KEY_LIKE_NAMES):
        print(
            f"Refusing to store {name!r}: API keys live in the environment "
            "(OPENROUTER_API_KEY), never in the config file.",
            file=sys.stderr,
        )
        sys.exit(2)
    if name == "provider" and value not in SUPPORTED_PROVIDERS:
        print(
            f"Unknown provider {value!r}. Supported: {', '.join(SUPPORTED_PROVIDERS)}",
            file=sys.stderr,
        )
        sys.exit(2)
    if name not in ("provider", "model"):
        print("Can only set 'provider' or 'model'.", file=sys.stderr)
        sys.exit(2)
    path = write_config_file({name: value})
    print(f"Set {name}={value} in {path}")


def _unset(name: str):
    if name not in ("provider", "model"):
        print("Can only unset 'provider' or 'model'.", file=sys.stderr)
        sys.exit(2)
    cfg = _read_config_file()
    if name in cfg:
        del cfg[name]
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"Removed {name} from {CONFIG_PATH}")
    else:
        print(f"{name} was not set in {CONFIG_PATH}")


def main():
    parser = argparse.ArgumentParser(description="View/set LifeKit LLM provider config.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("view", help="Show resolved provider/model and their sources")
    p_set = sub.add_parser("set", help="Persist provider or model to the config file")
    p_set.add_argument("name", help="provider | model")
    p_set.add_argument("value", help="Value to store")
    p_unset = sub.add_parser("unset", help="Remove a stored value")
    p_unset.add_argument("name", help="provider | model")
    args = parser.parse_args()

    if args.cmd == "view":
        _view()
    elif args.cmd == "set":
        _set(args.name, args.value)
    elif args.cmd == "unset":
        _unset(args.name)


if __name__ == "__main__":
    main()
