"""lifekit.store.epub_ingester -- EPUB ingestion pipeline for LifeKit knowledge store.

Extracts book metadata + full text from an EPUB file, applies the same cleaning
boilerplate stripping / sanitization as PDF ingestion, chunks by sentence-boundary,
and stores into the same SQLite tables (books + book_chunks).

Supports:
- ebooklib library (preferred) for spine-ordered reading sequence
- stdlib zipfile fallback for environments without external deps

Usage:
    from lifekit.store.epub_ingester import ingest_epub
    
    result = ingest_epub("path/to/book.epub")
    # => {"book_id": "...", "title": "...", "chunk_count": 42}
"""
from __future__ import annotations

import hashlib
import posixpath
import re
import sqlite3
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Optional

# Try ebooklib first; fall back to stdlib-only parsing below.
try:
    from html.parser import HTMLParser
except ImportError:
    # Fallback for rare embedded Python — should never happen in practice.
    raise ImportError("html.parser is required (stdlib)") from None


# ---------------------------------------------------------------------------
# Shared sanitization (same as pdf_ingester via clean_text)
# ---------------------------------------------------------------------------
from lifekit.store.clean_text import clean_and_sanitize


CHUNK_SIZE = 2000
OVERLAP_CHARS = 200


class EmptyEPUBError(Exception):
    """Raised when the EPUB yields zero extractable text."""


class DuplicateIngestError(Exception):
    """Raised when attempting to ingest a duplicate file_path into books table."""


# ---------------------------------------------------------------------------
# EPUB text extraction: ebooklib path (preferred)
# ---------------------------------------------------------------------------

try:
    import ebooklib  # type: ignore
    from ebooklib import epub as epub_lib
    from bs4 import BeautifulSoup  # type: ignore

    HAS_EBOOKLIB = True
except ImportError:
    HAS_EBOOKLIB = False


def extract_epub_with_ebooklib(epub_path: str) -> tuple[dict[str, str], list[tuple[int, str]]]:
    """Extract metadata + spine-ordered text from EPUB via ebooklib.

    Args:
        epub_path: Path to the .epub file.

    Returns:
        (metadata_dict, chapters_list) where chapters_list is [(chapter_num, text)].
    """
    book = epub_lib.read_epub(epub_path)
    meta: dict[str, str] = {}

    # Try to pull Dublin Core metadata from the book's metadata dict.
    for dc_key in ("title", "creator", "contributor", "publisher", "language"):
        values = list(book.get_metadata("DC", dc_key, default=[]))
        if values:
            meta[dc_key] = "; ".join(v[0] for v in values)

    # Collect reading order from the spine.
    parts: list[str] = []
    seen_href: set[str] = set()

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        href = item.get_name()
        if href in seen_href:
            continue
        seen_href.add(href)
        soup = BeautifulSoup(item.get_content(), "html.parser")

        # Remove navigation elements that don't contribute to the book text.
        for tag in soup(["nav", "sidebar", "aside"]):
            tag.decompose()
        parts.append(soup.get_text(separator="\n"))

    return meta, list(enumerate(parts, 1))


# ---------------------------------------------------------------------------
# EPUB text extraction: stdlib-only zipfile fallback
# ---------------------------------------------------------------------------

_HTML_RE = re.compile(r"\.(html?|xhtml)$", re.IGNORECASE)


def _find_opf_path(zf: zipfile.ZipFile) -> Optional[str]:
    """Locate the OPF package document inside an EPUB archive."""
    try:
        container_xml = zf.read("META-INF/container.xml").decode("utf-8", errors="replace")
        m = re.search(r'full-path=["\']([^"\']+\.opf)["\']', container_xml)
        if m:
            return m.group(1)
    except (KeyError, Exception):
        pass

    opf_files = [n for n in zf.namelist() if n.endswith(".opf")]
    return opf_files[0] if opf_files else None


def extract_epub_with_zipfile(epub_path: str) -> tuple[dict[str, str], list[tuple[int, str]]]:
    """Extract metadata + spine-ordered text from EPUB using stdlib only.

    Returns (metadata_dict, chapters_list). On failure, metadata may be partial
    and chapters empty — the caller will raise EmptyEPUBError.
    """
    meta: dict[str, str] = {}

    with zipfile.ZipFile(epub_path) as zf:
        opf_path = _find_opf_path(zf)
        opf_dir = posixpath.dirname(opf_path or "") or ""

        manifest: dict[str, str] = {}  # id -> resolved href
        spine_order: list[str] = []    # order of hrefs to read

        try:
            opf_text = zf.read(opf_path).decode("utf-8", errors="replace")

            # Parse <item> entries (manifest)
            for tag in re.findall(r"<item\b[^>]*?/?>", opf_text):
                id_m = re.search(r'\bid=["\']([^"\']+)["\']', tag)
                href_m = re.search(r"\bhref=['\"]([^'\"]+)['\"]", tag)
                if id_m and href_m:
                    href = href_m.group(1)
                    manifest[id_m.group(1)] = (
                        posixpath.normpath(posixpath.join(opf_dir, href))
                        if opf_dir else href
                    )

            # Parse <itemref> entries (spine = reading order)
            for idref in re.findall(r"<itemref\b[^>]*?\bidref=['\"]([^'\"]+)['\"]", opf_text):
                href = manifest.get(idref)
                if href and href not in set(spine_order):
                    spine_order.append(href)

            # Safety net: append remaining HTML files not in spine.
            for href in manifest.values():
                if _HTML_RE.search(href) and href not in spine_order:
                    spine_order.append(href)
        except Exception:
            pass

        if not spine_order:
            spine_order = sorted(
                n for n in zf.namelist() if _HTML_RE.search(n)
            )

        # Read all HTML content.
        parts: list[str] = []
        for name in spine_order:
            try:
                raw = zf.read(name).decode("utf-8", errors="replace")
                if HAS_EBOOKLIB:
                    soup = BeautifulSoup(raw, "html.parser")
                    for tag in soup(["nav", "sidebar", "aside"]):
                        tag.decompose()
                    parts.append(soup.get_text(separator="\n"))
                else:
                    # Minimal fallback stripping HTML tags.
                    clean = re.sub(r"<[^>]+>", "", raw)
                    clean = re.sub(r"&[a-z]+;", " ", clean, flags=re.IGNORECASE)
                    parts.append(clean)
            except Exception:
                continue

    return meta, list(enumerate(parts, 1))


def _count_epub_chapters(epub_path: str) -> int:
    """Count spine items (approximate chapter count) without reading content."""
    try:
        with zipfile.ZipFile(epub_path) as zf:
            opf_path = _find_opf_path(zf)
            if not opf_path:
                return 0
            opf_text = zf.read(opf_path).decode("utf-8", errors="replace")
            return len(re.findall(r"<itemref\b", opf_text))
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Chunking (same as pdf_ingester)
# ---------------------------------------------------------------------------

def _chunk_text(page_num: int, full_text: str):
    """Split text into overlapping chunks with sentence-boundary detection."""
    chunks = []
    start = 0
    while start < len(full_text):
        end = min(start + CHUNK_SIZE, len(full_text))
        seg = full_text[start:end]

        split_point = None
        if end < len(full_text):
            peek_len = min(OVERLAP_CHARS, len(full_text) - end)
            lookahead = full_text[end: end + peek_len]

            for j in range(len(lookahead)):
                ch = lookahead[j]
                if ch in (".", "!", "?"):
                    next_two = lookahead[j + 1: j + 3] if j + 1 < len(lookahead) else ""
                    if next_two and next_two.strip():
                        split_point = end + j + 1
                        break

            if split_point is None:
                para_break = full_text.find("\n\n", end, end + OVERLAP_CHARS * 2)
                if para_break >= 0:
                    split_point = para_break + 1

        if split_point and split_point > start + CHUNK_SIZE // 2:
            seg = full_text[start:split_point]
            end = split_point
            start += OVERLAP_CHARS
        else:
            chunks.append((page_num, seg.strip()))
            start = end

    # Merge trailing short chunk into the previous one.
    if len(chunks) >= 2 and len(chunks[-1][1]) < 50:
        last_text = chunks.pop()
        prev_text = chunks[-1][1] + " " + last_text[1]
        chunks[-1] = (chunks[-1][0], prev_text.strip())

    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_epub(
    file_path: str | Path,
    db_path: Optional[str] = None,
) -> dict[str, Any]:
    """Ingest a local EPUB book into the LifeKit knowledge store.

    Args:
        file_path: Absolute or relative path to the EPUB.
        db_path: Optional SQLite path. Defaults to ~/.lifekit/lifekit.db.

    Returns:
        {book_id, title, author, chunk_count}

    Raises:
        FileNotFoundError - EPUB does not exist on disk
        EmptyEPUBError     - No extractable text found
        DuplicateIngestError - Same file_path already ingested
    """
    p = Path(file_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"EPUB not found: {p}")

    # --- Extract metadata + text, choosing best available backend ---
    meta: dict[str, str] = {}
    raw_chapters: list[tuple[int, str]] = []

    if HAS_EBOOKLIB:
        meta, raw_chapters = extract_epub_with_ebooklib(str(p))
    else:
        meta, raw_chapters = extract_epub_with_zipfile(str(p))

    if not raw_chapters:
        raise EmptyEPUBError(f"No extractable text in EPUB: {p}")

    title = meta.get("title", p.stem)
    author = meta.get("creator", "Unknown")

    # Apply cleaning + sanitization per chapter, then chunk.
    chunks_raw: list[tuple[int, str]] = []
    for chap_no, text in raw_chapters:
        cleaned = clean_and_sanitize(text).strip()
        if len(cleaned) < 50:
            continue
        # Chapter-level "pages" — chunk further inside.
        page_chunks = _chunk_text(chap_no, cleaned)
        chunks_raw.extend(page_chunks)

    if not chunks_raw:
        raise EmptyEPUBError(f"Generated zero chunks from {p.name} (all too short after cleaning)")

    # --- Write to DB (same schema as pdf_ingester) ---
    db_path_to_use = Path(db_path) if db_path else Path.home() / ".lifekit" / "lifekit.db"
    db_path_to_use.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path_to_use))
    conn.execute("PRAGMA foreign_keys = ON")

    book_id = hashlib.sha256(str(p).encode()).hexdigest()[:16]

    try:
        with conn:
            # TOCTOU-safe duplicate check
            cur = conn.execute(
                "SELECT 1 FROM books WHERE file_path = ?",
                (str(p),)
            )
            if cur.fetchone():
                raise DuplicateIngestError(
                    f"Already ingested: {p} (book_id={book_id})"
                )

            # Insert book record with additional metadata columns.
            conn.execute(
                "INSERT INTO books (id, title, author, file_path) VALUES (?, ?, ?, ?)",
                [book_id, title, author, str(p)],
            )

            # Bulk-insert chunks (page_number now carries chapter number for EPUB).
            conn.executemany(
                "INSERT INTO book_chunks (book_id, chunk_index, content, page_number) VALUES (?, ?, ?, ?)",
                [
                    (book_id, idx, text, page_num)
                    for idx, (page_num, text) in enumerate(chunks_raw)
                ],
            )

            conn.execute(
                "UPDATE books SET chunk_count = ? WHERE id = ?",
                (len(chunks_raw), book_id),
            )
    except Exception:
        conn.rollback()
        raise

    return {
        "book_id": book_id,
        "title": title,
        "author": author,
        "chunk_count": len(chunks_raw),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m lifekit.store.epub_ingester <path/to/book.epub>", file=sys.stderr)
        sys.exit(1)

    try:
        result = ingest_epub(sys.argv[1])
        print(
            f"Ingested {result['title']} by {result['author']}: "
            f"{result['chunk_count']} chunks (book_id={result['book_id']})"
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
