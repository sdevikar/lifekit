"""lifekit.utils.clean_text -- Text-cleaning primitives for ingested documents.

Adapted from book-to-skill's ``book_to_skill.parsers.pdf`` (see commit history of
that project for provenance). Core idea: a page extracted via pypdf, pdfminer or
pdftotext is *joined with form-feed separators* so that per-page running headers
and footers become candidates for "edge frequency" analysis. A line appearing in
more than half the pages is almost certainly boilerplate and gets stripped.

Exports:
    clean_pdftotext(text): strip boilerplate + dehyphenate wrapped words
    extract_text_with_cleaning(pdf_path, source="pypdf"): end-to-end extractor
      that returns cleaned full text from a PDF.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections import Counter

# --- Page-number pattern --------------------------------------------------------
# A bare (or mostly-bare) number on its own line. The roman-numeral branch spells
# out the SHAPE of a canonical numeral instead of listing permitted letters one by
# one, so accidental matches on words like "MIX", "CIVIL" or "VIVID" don't blow a
# front-matter page title out of history.
_ROMAN_1_99 = r"(?=[ivxl])(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})"
_PDF_PAGE_NUM_RE = re.compile(rf"^\s*(?:\d{{1,4}}|{_ROMAN_1_99})\s*$", re.IGNORECASE)

# Hyphen-wrapped word break: a letter at end of line joined with one at start of
# next line via a hyphen. Naive; if it joins genuinely-hyphenated compounds
# ("well-known") that's caught downstream by tokenization, not this cleaning pass.
_HYPHEN_WRAP_RE = re.compile(r"(\w)-\n(\w)")


def clean_pdftotext(text: str) -> str:
    """Apply the standard pdftotext-style cleanup to a form-feed delimited PDF dump.

    The three passes are (applied in order):
        1. Running header/footer rejection via edge-frequency counting across pages.
           Only lines at the *edge* of a page (first/last non-blank) participate
           in detection -- mid-page headings are preserved verbatim because they
           appear as running headers too, and stripping them everywhere would erase
           genuine section titles that happen to match header text.
        2. Bare-page-number removal on edge lines is additive to #1 for the common
           case of a book with only a page number (no title) at the top/bottom.
        3. Naive dehyphenation of word wraps across line ends.

    Parameters
        text: Form-feed delimited text (one section per ``\\f``). If fewer than three
              form feeds are present, treat everything as a single logical page and
              only run the hyphen-wrapped-words pass.

    Returns
        Cleaned ``str`` with boilerplate edges stripped where detectable.
    """
    pages = text.split("\f")
    if len(pages) >= 3:
        # Count how many pages each *edge line* (first or last non-blank) shows up
        # on across the whole book. Anything in > half is boilerplate. A single-line
        # page contributes its "last" only via ``nb[-1]`` once so one-part divider
        # appearing twice on four pages doesn't cast 4/4 votes by double-counting
        # the same bare divider line as both first and last.
        edge_count: Counter[str] = Counter()
        for page in pages:
            nonblank = [ln.strip() for ln in page.splitlines() if ln.strip()]
            if not nonblank:
                continue
            edge_count[nonblank[0]] += 1  # top edge of this page (often empty)
            if len(nonblank) > 1:
                # bottom edge -- skip when there's only one non-blank line to avoid
                # giving the lone visible content line a "last-line" vote.
                edge_count[nonblank[-1]] += 1

        boiler_set = {ln for ln, c in edge_count.items() if c > len(pages) / 2}

        kept_lines: list[str] = []
        for page in pages:
            lines = page.splitlines()
            nonblank_indices = [i for i, ln in enumerate(lines) if ln.strip()]
            # First and last *non-blank* edge of the page; these are where running
            # headers/footers/page-numbers ever show up.
            first_nb = nonblank_indices[0] if nonblank_indices else None
            last_nb = nonblank_indices[-1] if nonblank_indices else None

            for i, line in enumerate(lines):
                if i not in (first_nb, last_nb):
                    kept_lines.append(line)
                    continue
                stripped = line.strip()
                # Drop the line entirely if it matches either the boiler set or is a
                # bare page number. Mid-page text never passes this; only edge lines
                # ever touch it.
                if stripped in boiler_set:
                    continue
                if _PDF_PAGE_NUM_RE.match(stripped):
                    continue
                kept_lines.append(line)

        text = "\n".join(kept_lines)
    else:
        # Fewer than three "pages" -- probably a single-page extract. Don't try to
        # detect boilerplate (would over-strip on one-shot extractions), just swap
        # form feeds for newlines so downstream chunking sees natural breaks.
        text = text.replace("\f", "\n")

    return _HYPHEN_WRAP_RE.sub(r"\1\2", text)


# --------------------------------------------------------------------------- public extractor helpers ------------------------------
def extract_with_pypdf(pdf_path: str) -> str | None:
    """page-by-page extraction via pypdf, then run clean_pdftotext over it all.

    Pages are joined with form-feed separators so that per-page running headers /
    footers participate in the edge-frequency analysis and can be stripped as a
    class; without form feeds, each page is treated independently.
    """
    try:
        import pypdf  # type: ignore[import-untyped]

        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            parts = []
            for i in range(len(reader.pages)):
                page_text = ""
                try:
                    page_text = reader.pages[i].extract_text() or ""
                except Exception:
                    pass  # keep going -- some pages are image-only
                parts.append(page_text)
        return clean_pdftotext("\f".join(parts))
    except ImportError as exc:
        raise RuntimeError(
            "pypdf required for PDF extraction. Install with `pip install pypdf`."
        ) from exc


def extract_with_pdfminer(pdf_path: str) -> str | None:
    """pdfminer high-level text extraction (layout-aware), then clean."""
    try:
        from pdfminer.high_level import extract_text  # type: ignore[import-untyped]

        raw = extract_text(pdf_path) or ""
    except ImportError:
        return None
    except Exception as e:
        print(
            f"  [warn] clean_text.extract_with_pdfminer failed: {type(e).__name__}: {e}",
            file=__import__("sys").stderr,
        )
        return None

    if not raw.strip():
        return None
    # pdfminer emits form-feed boundaries between pages -- perfect for cleaning.
    return clean_pdftotext(raw)


def extract_with_pdftotext(pdf_path: str) -> str | None:
    """Best-effort subprocess wrapper around the ``pdftotext -layout`` tool."""
    if not shutil.which("pdftotext"):
        return None
    try:
        pdf_path = os.path.abspath(pdf_path)
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0 and result.stdout.strip():
            return clean_pdftotext(result.stdout)
    except Exception as e:
        print(
            f"  [warn] extract_with_pdftotext failed: {type(e).__name__}: {e}",
            file=__import__("sys").stderr,
        )
    return None


def extract_text_with_cleaning(pdf_path: str) -> str | None:
    """Best-effort PDF → cleaned full text, trying multiple backends.

    Order of preference (mirrors book-to-skill): pdftotext (tool, fastest) >
    pdfminer (python package, layout-aware) > pypdf (widest availability). Each
    backend is best-effort: if one fails the next is attempted and on full
    exhaustion ``None`` is returned.
    """
    for extractor in (extract_with_pdftotext, extract_with_pdfminer, extract_with_pypdf):
        text = extractor(pdf_path)
        if text and len(text.strip()) > 10:
            return text  # type: ignore[return-value]
    return None
