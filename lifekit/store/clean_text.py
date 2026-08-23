"""lifekit.store.clean_text — Advanced text cleaning for PDF extraction output.

Adopted from book-to-skill's clean_pdftotext pattern (book_to_skill/parsers/pdf.py).
Applies page-level boilerplate stripping and hyphenated-word rejoining before
chunking, so your SQLite store receives far cleaner content.

Usage:
    from lifekit.store.clean_text import clean_pdf_output
    
    text = extract_pypdf_pages(pdf_path)  # <- raw pypdf output with form-feeds
    cleaned = clean_pdf_output(text)       # <- boilerplate stripped, hyphens rejoined
"""
from __future__ import annotations

import re
from collections import Counter


# Bare page number (Arabic digits or Roman numerals for front matter).
_ROMAN_1_99 = r"(?=[ivxl])(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})"
_PAGE_NUM_PATTERN = re.compile(
    rf"^\s*(?:\d{{1,4}}|{_ROMAN_1_99})\s*$",
    re.IGNORECASE,
)

# Hyphen-at-line-end joined to the next line's start.
_HYPHEN_WRAP = re.compile(r"(\w)-\n(\w)")


def clean_pdf_output(raw_text: str) -> str:
    """Strip running headers/footers and join hyphenated lines from PDF extraction.

    Args:
        raw_text: Output from a PDF extractor (pypdf, pdftotext), ideally with
                  form-feed ('\\f') page delimiters.

    Returns:
        Cleaned text with boilerplate edge-lines removed and hyphen-wrapped words
        rejoined.
    """
    # Split into pages if form-feed present; otherwise treat as single "page".
    if "\f" in raw_text:
        pages = raw_text.split("\f")
    else:
        pages = [raw_text]

    if len(pages) >= 3:
        # --- Edge-line boilerplate detection ---
        edge: Counter[str] = Counter()
        for p in pages:
            nb = [ln.strip() for ln in p.splitlines() if ln.strip()]
            if nb:
                edge[nb[0]] += 1  # top edge line
                if len(nb) > 1:
                    edge[nb[-1]] += 1  # bottom edge line (if multi-line page)

        # Anything repeating on more than half the pages is boilerplate.
        boiler = {ln for ln, c in edge.items() if c > len(pages) / 2}

        kept: list[str] = []
        for p in pages:
            lines = p.splitlines()
            nb_idx = [i for i, ln in enumerate(lines) if ln.strip()]
            first_edge = nb_idx[0] if nb_idx else None
            last_edge = nb_idx[-1] if nb_idx else None

            for i, ln in enumerate(lines):
                if i in (first_edge, last_edge):
                    s = ln.strip()
                    # Strip boilerplate or bare page numbers only at the very edge.
                    if s in boiler or _PAGE_NUM_PATTERN.match(s):
                        continue
                kept.append(ln)

        text = "\n".join(kept)
    else:
        # Fewer than 3 pages — just replace form-feeds with newlines (no stripping).
        text = raw_text.replace("\f", "\n")

    # --- Hyphenated word rejoining ---
    # Joins well-\nknown → wellknown on every line. Fine-grained dictionaries
    # are future work; for now this fixes most PDF extraction artefacts.
    text = _HYPHEN_WRAP.sub(r"\1\2", text)

    return text


# ---------------------------------------------------------------------------
# Lightweight sanitization: remove invisible/control characters that corrupt
# FTS5 indexing and search matching.
# ---------------------------------------------------------------------------

_BIDI_RE = re.compile(
    r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]"  # BIDI controls
)


def sanitize(content: str) -> str:
    """Remove zero-width / bidi characters and normalise whitespace.

    Does NOT strip punctuation or modify semantics — only cleans invisible noise
    that corrupts SQLite FTS5 indexes and search matching.
    """
    content = _BIDI_RE.sub("", content)
    # Normalise vertical whitespace: collapse runs of blank lines to one.
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content


def clean_and_sanitize(text: str) -> str:
    """Run both cleaning and sanitization in one pass."""
    text = clean_pdf_output(text)
    text = sanitize(text)
    return text
