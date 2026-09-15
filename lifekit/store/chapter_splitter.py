"""lifekit.store.chapter_splitter -- TOC-first PDF chapter splitting.

Strategy (in order):
  1. Embedded TOC via PyMuPDF (``doc.get_toc()``) — primary, zero heuristics.
  2. Heading/font-size heuristics when the TOC is missing or empty.
  3. Fixed-size page sections as the final fallback.
  4. Image-only PDFs are refused with a clear error (never silently empty).

Usage:
    from lifekit.store.chapter_splitter import split_chapters

    chapters = split_chapters("book.pdf")  # -> list[Chapter]
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from statistics import median

import fitz  # PyMuPDF

from lifekit.store.clean_text import clean_and_sanitize


class EmptyPDFError(Exception):
    """Raised when the PDF yields zero extractable text (e.g. image-only scans)."""


# Final-fallback granularity when neither TOC nor headings are usable.
FALLBACK_SECTION_PAGES = 15

# A heading must be at least this much larger than the page's median font size.
HEADING_SIZE_RATIO = 1.3


@dataclass
class Chapter:
    index: int
    title: str
    text: str
    page_start: int  # 1-based
    page_end: int    # 1-based, inclusive


def _page_texts(doc: "fitz.Document") -> list[str]:
    """Extract (lightly cleaned) text per page, 0-based list."""
    texts = []
    for page in doc:
        raw = page.get_text() or ""
        texts.append(clean_and_sanitize(raw).strip())
    return texts


def _check_text_layer(texts: list[str], pdf_path: Path) -> None:
    total = sum(len(t) for t in texts)
    if total < 200:
        raise EmptyPDFError(
            f"No extractable text in PDF (image-only scan?): {pdf_path}"
        )


def _chapters_from_toc(
    toc: list[tuple[int, str, int]], texts: list[str], page_count: int
) -> list[Chapter] | None:
    """Build chapters from the embedded TOC. Returns None if unusable."""
    entries = [(lvl, t.strip(), p) for lvl, t, p in toc if t and t.strip()]
    entries = [e for e in entries if 1 <= e[2] <= page_count]
    if len(entries) < 2:
        return None
    # Use the shallowest level present (parts > chapters).
    top_level = min(e[0] for e in entries)
    entries = [e for e in entries if e[0] == top_level]
    if len(entries) < 2:
        return None

    chapters: list[Chapter] = []
    for i, (_, title, start_1based) in enumerate(entries):
        end_1based = entries[i + 1][2] - 1 if i + 1 < len(entries) else page_count
        if end_1based < start_1based:
            continue
        text = "\n\n".join(texts[start_1based - 1 : end_1based]).strip()
        if not text:
            continue
        chapters.append(
            Chapter(
                index=len(chapters),
                title=title,
                text=text,
                page_start=start_1based,
                page_end=end_1based,
            )
        )
    return chapters or None


def _page_heading(page: "fitz.Page") -> str | None:
    """Return the page's heading candidate, or None.

    A heading is the first line whose font size is markedly larger than the
    page's median body size.
    """
    try:
        data = page.get_text("dict")
    except Exception:
        return None
    sizes: list[float] = []
    lines: list[tuple[float, str]] = []
    for block in data.get("blocks", []):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            line_text = "".join(s.get("text", "") for s in line.get("spans", []))
            line_text = line_text.strip()
            if not line_text:
                continue
            max_size = max((s.get("size", 0) for s in line.get("spans", [])), default=0)
            sizes.append(max_size)
            lines.append((max_size, line_text))
    if not sizes or not lines:
        return None
    body = median(sizes)
    if body <= 0:
        return None
    for size, text in lines:
        if size >= body * HEADING_SIZE_RATIO and len(text) <= 160:
            return text
    return None


def _chapters_from_headings(texts: list[str], doc: "fitz.Document") -> list[Chapter] | None:
    """Detect chapter boundaries from styled headings. None if unusable."""
    bounds: list[tuple[int, str]] = []  # (0-based page, title)
    for i, page in enumerate(doc):
        if not texts[i]:
            continue
        heading = _page_heading(page)
        if heading:
            bounds.append((i, heading))
    if len(bounds) < 2:
        return None

    chapters: list[Chapter] = []
    for j, (page_0, title) in enumerate(bounds):
        end_0 = bounds[j + 1][0] - 1 if j + 1 < len(bounds) else len(texts) - 1
        text = "\n\n".join(texts[page_0 : end_0 + 1]).strip()
        if not text:
            continue
        chapters.append(
            Chapter(
                index=len(chapters),
                title=title,
                text=text,
                page_start=page_0 + 1,
                page_end=end_0 + 1,
            )
        )
    return chapters or None


def _chapters_fixed_size(texts: list[str]) -> list[Chapter]:
    """Final fallback: fixed-size page sections."""
    chapters: list[Chapter] = []
    for start_0 in range(0, len(texts), FALLBACK_SECTION_PAGES):
        end_0 = min(start_0 + FALLBACK_SECTION_PAGES - 1, len(texts) - 1)
        text = "\n\n".join(texts[start_0 : end_0 + 1]).strip()
        if not text:
            continue
        n = len(chapters) + 1
        chapters.append(
            Chapter(
                index=len(chapters),
                title=f"Section {n}",
                text=text,
                page_start=start_0 + 1,
                page_end=end_0 + 1,
            )
        )
    return chapters


def _default_book_id(pdf_path: Path) -> str:
    return hashlib.sha256(str(pdf_path.resolve()).encode()).hexdigest()[:16]


def _persist(chapters: list[Chapter], db_path: str, book_id: str) -> None:
    from lifekit.db.schema import init_db

    conn = init_db(db_path)
    conn.executemany(
        "INSERT OR REPLACE INTO chapters "
        "(book_id, idx, title, page_start, page_end, content) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(book_id, c.index, c.title, c.page_start, c.page_end, c.text)
         for c in chapters],
    )
    conn.commit()


def split_chapters(
    pdf_path: str | Path,
    db_path: str | None = None,
    book_id: str | None = None,
) -> list[Chapter]:
    """Split a PDF into chapters (TOC-first, heading fallback, fixed-size last).

    Args:
        pdf_path: Path to the PDF.
        db_path: Optional SQLite path; when given, chapters are persisted.
        book_id: Book id for persisted rows; defaults to sha256(path)[:16].

    Raises:
        FileNotFoundError: PDF does not exist.
        EmptyPDFError: No extractable text (image-only scan).
    """
    p = Path(pdf_path)
    if not p.is_file():
        raise FileNotFoundError(f"PDF not found: {p}")

    doc = fitz.open(str(p))
    try:
        texts = _page_texts(doc)
        _check_text_layer(texts, p)

        chapters = _chapters_from_toc(doc.get_toc(), texts, doc.page_count)
        strategy = "toc"
        if chapters is None:
            chapters = _chapters_from_headings(texts, doc)
            strategy = "headings"
        if chapters is None:
            chapters = _chapters_fixed_size(texts)
            strategy = "fixed-size"
    finally:
        doc.close()

    if db_path:
        _persist(chapters, db_path, book_id or _default_book_id(p))

    for c in chapters:
        c.title = c.title  # no-op; titles already stripped
    return chapters
