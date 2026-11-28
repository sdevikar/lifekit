"""Anchor a quote to a passage; reject if not present."""

from __future__ import annotations


def anchored(quote: str, text: str) -> bool:
    q = " ".join(quote.split())
    t = " ".join(text.split())
    return q in t and len(q) > 0
EOF