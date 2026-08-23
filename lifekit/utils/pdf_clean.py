"""lifekit.utils.pdf_clean -- advanced PDF raw-text cleaning.

Picks up exactly the boilerplate-stripping logic from book-to-skill's pdf parser
and makes it available to the ingestors with zero extra dependencies beyond the
standard library and pypdf (which the PDF ingester already pulls in).

Key capabilities:
    - Form-feed delimited page parsing that automatically strips repeated edge
      lines (typical running headers / footers / bare leaf-page numbers).
    - Hyphenated word rejoining across line breaks.
    - End-to-end extractor ``extract_with_cleaning`` that tries pdftotext >
      pdfminer > pypdf, falling back until one returns real text.

Both PDF ingestors (the original and the new) use this module so extracted
text quality is identical regardless of which extraction backend actually runs.
"""
from __future__ import annotations

import os as _os
import re as _re
import subprocess as _subprocess
from collections import Counter


# --- page-number regex ---------------------------------------------------------
# Roman numerals are spelled out by their *shape* rather than as a set of allowed
# letters so short real words ("MIX", "CIVIL") can't be mistaken for front-matter
# pages. The range is 1-99, which covers what a book's front matter ever prints.
_ROMAN_1_99 = r"(?=[ivxl])(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})"
_PDFTOTEXT_PAGE_RE = _re.compile(rf"^\s*(?:\d{{1,4}}|{_ROMAN_1_99})\s*$", _re.IGNORECASE)

# Hyphen-wrapped word break: letter at end of line + one at start of next.
_PDFTOTEXT_HYPHEN_WRAP = _re.compile(r"(\w)-\n(\w)")


def clean_pdftotext(text: str) -> str:
    """Clean pdftotext-style output (pages split on form feeds): strip repeated
    running headers/footers and edge page numbers, rejoin hyphen-wrap word-breaks."""

    # Form-feed delimited pages. Anything fewer than three pages can't be used to
    # detect boilerplate -- one-shot extractions would over-strike.
    if text.count("\f") < 2:
        # Single logical page or already-clean extract; just swap form feeds for
        # newlines so the chunker sees proper line breaks below.
        cleaned = text.replace("\f", "\n")
    else:
        pages = text.split("\f")

        # Edge-frequency analysis across all pages -- boilerplate lives at a page's
        # first or last non-blank line in every pass of the document. Anything in
        # more than half the pages is dropped *only from edges* so a genuine mid-
        # page "Chapter 3" heading that happens to match an even-occurrence footer
        # survives as text below it.
        edge_counter = Counter()
        for page in pages:
            nonblank_lines = [ln.strip() for ln in page.splitlines() if ln.strip()]
            if not nonblank_lines:
                continue
            # Top edge -- even a one-line non-blank page contributes one vote toward
            # "this title is part of boilerplate". If it only has ONE line (the lone
            # non-blank line), the next addition would give it two identical votes
            # from first AND last and let a single-part divider flip the threshold.
            edge_counter[nonblank_lines[0]] += 1
            if len(nonblank_lines) > 1:
                edge_counter[nonblank_lines[-1]] += 1

        boiler = {ln for ln, count in edge_counter.items() if count > len(pages) / 2}

        # Now walk every page again and drop the boiler lines -- but only at the
        # edges of each individual page. If a footer matched across 70% of pages
        # it's gone from all those pages' top/bottom; we are NOT erasing that same
        # string if it shows up in the middle of one page (a section header, for
        # instance).
        kept_lines = []
        for page in pages:
            lines = page.splitlines()
            first_index = next((i for i, ln in enumerate(lines) if ln.strip()), None)
            last_index = next(
                (i for i in reversed(range(len(lines))) if lines[i].strip()), None
            )
            for idx, raw_line in enumerate(lines):
                if idx not in (first_index, last_index):
                    kept_lines.append(raw_line)
                    continue
                stripped = _PDFTOTEXT_PAGE_RE.sub("", raw_line).strip()
                # Two independent deletion gates: full-line matches of either the
                # edge-set or a bare-page-number regex. The regex is checked even
                # before the set because some front-matter numerals don't appear
                # verbatim as boilerplate yet still get classified as page numbers.
                if stripped in boiler or _PDFTOTEXT_PAGE_RE.fullmatch(stripped):
                    continue
                kept_lines.append(raw_line)

        cleaned = "\n".join(kept_lines)

    # Naive dehyphenation across line boundaries -- the one operation that must
    # live at the end because it only ever operates on raw text, not page-delimited
    # form feeds. If a legitimately-hyphenated compound ("well-known") gets eaten
    # here then tokenization will recover; this function is loss-safe by design.
    return _PDFTOTEXT_HYPHEN_WRAP.sub(r"\1\2", cleaned)


# --------------------------------------------------- End-to-end extraction helpers --------------------------------

def extract_with_pypdf(pdf_path: str) -> str | None:
    """Page-by-page text via pypdf, joined with form feeds for clean_pdftotext."""
    try:
        import pypdf  # noqa: F401 -- keep the import in scope so pytest can stub it out

        with open(pdf_path, "rb") as fh:
            reader = pypdf.PdfReader(fh)
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    pass  # image-only pages are silently skipped; cleaning still runs on the rest.
        return clean_pdftotext("\f".join(parts)) if any(p.strip() for p in parts) else None

    except ImportError as exc:
        raise RuntimeError(
            "Cannot extract this PDF -- pypdf is required."
        ) from exc


def extract_with_pdfminer(pdf_path: str) -> str | None:
    """pdfminer-based text extraction; already form-feed delimited per page."""
    try:
        from pdfminer.high_level import extract_text  # type: ignore[import-untyped]

        raw = (extract_text(pdf_path) or "").strip()
    except ImportError as exc:
        raise RuntimeError(
            "Cannot extract this PDF -- python-pdfminer is required."
        ) from exc
    return clean_pdftotext(raw) if raw else None


def extract_with_pdftotext(pdf_path: str) -> str | None:
    """Fastest path when the ``pdftotext`` system tool is available."""
    import shutil  # noqa: F811 -- keep it local so a missing pdftotext skips this branch.

    if not shutil.which("pdftotext"):
        return None

    try:
        result = _subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0 and result.stdout.strip():
            return clean_pdftotext(result.stdout)

    except Exception as exc:
        print(  # noqa: T201 -- stderr output in a best-effort utility.
            f"[warn] extract_with_pdftotext failed: {type(exc).__name__}: {exc}",
            file=__import__("sys").stderr,
        )

    return None


def extract_text_with_cleaning(pdf_path: str) -> str | None:
    """Best-effort PDF → clean full-text. Tries backends in order of preference."""
    for extractor in (extract_with_pdftotext, extract_with_pdfminer, extract_with_pypdf):
        try:
            text = extractor(pdf_path)
        except Exception as exc:  # noqa: BLE001 -- one bad backend doesn't kill the whole pipeline.
            continue

        if not isinstance(text, str) or not text.strip():
            continue
        return text

    print(  # noqa: T201 -- fallback logger for the case every extractor failed.
        f"[warn] All PDF extractors failed on {pdf_path}",
        file=__import__("sys").stderr,
    )
    return None


# ----------------------------------------------------------------------- testing guard ---------------------------------------------------------------------------------
def is_pdf_text_empty(pdf_path: str) -> bool:  # pragma: no cover -- diagnostic only.
    """True iff *every* non-blank page of the PDF has fewer than 10 chars.

    Used before invoking the expensive extractor list on image-only scans so
    callers can fail fast without running every backend in turn.
    """
    count = extract_text_with_cleaning(pdf_path) or ""
    return not any(ln.strip() for ln in "\n".join(count.splitlines()) if len(ln) > 10)
