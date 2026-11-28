"""Load the card type definitions from card_types.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

_CONFIG = Path(__file__).with_name("card_types.toml")

CARD_TYPES = ("insight", "practice", "habit", "reflect", "question")


def load_card_types(path: Path | None = None) -> dict:
    with (path or _CONFIG).open("rb") as f:
        data = tomllib.load(f)
    # Validate expected types present.
    for t in CARD_TYPES:
        if t not in data:
            raise ValueError(f"missing card type: {t}")
    return data


def card_type_names() -> tuple[str, ...]:
    return CARD_TYPES


if __name__ == "__main__":
    print(load_card_types())