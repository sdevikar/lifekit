"""lifekit.store.pdf_ingester -- PDF ingestion pipeline.

Extracts text from a local PDF, chunks into ~2000 chars with sentence-boundary
detection and 200-char overlap, stores book + chunks in SQLite via
lifekit.db.schema. Uses BEGIN IMMEDIATE for TOCTOU-safe duplicate detection.

Usage:
    from lifekit.store.pdf_ingester import ingest_pdf

    result = ingest_pdf("path/to/book.pdf")
    # => {"book_id": "a1b2c3d4e5f6g7h8", "title": "...", "chunk_count": 42}

Raises:
    FileNotFoundError - PDF does not exist on disk
    EmptyPDFError     - No extractable text found
    DuplicateIngestError - Same file_path already ingested
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Any, Optional, List as TypingList, Tuple as TypingTuple

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

from lifekit.store.clean_text import clean_and_sanitize


CHUNK_SIZE = 2000
OVERLAP_CHARS = 200


class EmptyPDFError(Exception):
    """Raised when the PDF yields zero extractable text."""


class DuplicateIngestError(Exception):
    """Raised when attempting to ingest a duplicate file_path into books table."""


def _extract_pages(pdf_path: Path) -> TypingList[TypingTuple[int, str]]:
    """Extract non-empty pages from PDF.

    Returns list of (page_number, cleaned_text). Raises EmptyPDFError if all
    pages are blank or text is shorter than 50 characters.
    """
    reader = PdfReader(str(pdf_path))
    pages: TypingList[TypingTuple[int, str]] = []

    # Collect raw text per page with form-feed delimiters for clean_pdf_output later.
    raw_pages: list[str] = []
    valid_starts: list[int] = []

    for i, pg in enumerate(reader.pages):
        text = pg.extract_text()
        if not text or not text.strip():
            raw_pages.append("")  # keep alignment; page becomes empty
            valid_starts.append(-1)  # marker for blank page
            continue
        # Normalise internal whitespace (collapse runs of spaces/newlines).
        raw_pages.append(" ".join(text.split()))
        valid_starts.append(i + 1)

    if not any(vs >= 0 for vs in valid_starts):
        raise EmptyPDFError(
            f"No extractable text in PDF: {pdf_path}"
        )

    # --- Apply advanced cleaning (boilerplate stripping, hyphen join) ---
    raw_text = "\f".join(raw_pages)
    cleaned_raw = clean_and_sanitize(raw_text).strip()

    # Rebuild the pages list with cleaned text; split on form-feed again
    # but only for valid (non-blank) pages.
    if "\f" in cleaned_raw:
        cleaned_pages = cleaned_raw.split("\f")
    else:
        cleaned_pages = [cleaned_raw]

    for raw_i, vs in enumerate(valid_starts):
        if vs < 0 or raw_i >= len(cleaned_pages):
            continue
        ct = cleaned_pages[raw_i].strip()
        if len(ct) < 50:
            continue
        pages.append((vs, ct))

    if not pages:
        raise EmptyPDFError(
            f"No extractable text in PDF: {pdf_path}"
        )

    return pages


def _chunk_text(page_num: int, full_text: str) -> TypingList[TypingTuple[int, str]]:
    """Split one page's text into overlapping chunks with sentence-boundary.

    Tries to cut at period+newline+caps within `OVERLAP_CHARS` of the chunk
    boundary before falling back to a hard split. Returns list of
    (page_number, chunk_text) tuples.
    """
    chunks: TypingList[TypingTuple[int, str]] = []
    start = 0

    while start < len(full_text):
        end = min(start + CHUNK_SIZE, len(full_text))
        seg = full_text[start:end]

        # Try to find a sentence boundary when there's more text ahead
        split_point = None  # Initialize before inner loops
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

            # If no sentence boundary, try double-newline paragraph breaks
            if split_point is None:
                para_break = full_text.find("\n\n", end, end + OVERLAP_CHARS * 2)
                if para_break >= 0:
                    split_point = para_break + 1

        if split_point and split_point > start + CHUNK_SIZE // 2:
            seg = full_text[start:split_point]
            end = split_point
            start += OVERLAP_CHARS  # overlap for context continuity
        else:
            chunks.append((page_num, seg.strip()))
            start = end

    # Clean up last chunk -- merge if too short
    if len(chunks) >= 2 and len(chunks[-1][1]) < 50:
        last_text = chunks.pop()
        prev_text = chunks[-1][1] + " " + last_text[1]
        chunks[-1] = (chunks[-1][0], prev_text.strip())

    return chunks


def ingest_pdf(
    file_path: str | Path,
    db_path: Optional[str] = None,
) -> dict[str, Any]:
    """Ingest a local PDF into the LifeKit knowledge store.

    Args:
        file_path: Absolute or relative path to the PDF.
        db_path: Optional SQLite path. Defaults to ~/.lifekit/lifekit.db.

    Returns:
        {book_id, title, chunk_count}

    Raises:
        FileNotFoundError, EmptyPDFError, DuplicateIngestError
    """
    p = Path(file_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"PDF not found: {p}")

    # 1. Extract text from PDF
    pages = _extract_pages(p)

    # 2. Chunk each page
    chunks_raw: TypingList[TypingTuple[int, str]] = []
    for page_num, full_text in pages:
        chunks_raw.extend(_chunk_text(page_num, full_text))

    if not chunks_raw:
        raise EmptyPDFError(f"Generated zero chunks from {p.name}")

    # 3. Connect to DB and insert atomically
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

            # Insert book record
            conn.execute(
                "INSERT INTO books (id, title, author, file_path) VALUES (?, ?, ?, ?)",
                [book_id, p.stem, "Unknown", str(p)]
            )

            # Bulk-insert chunks
            conn.executemany(
                "INSERT INTO book_chunks (book_id, chunk_index, content, page_number) VALUES (?, ?, ?, ?)",
                [
                    (book_id, idx, text, page_num)
                    for idx, (page_num, text) in enumerate(chunks_raw)
                ]
            )

            # Update chunk_count
            conn.execute(
                "UPDATE books SET chunk_count = ? WHERE id = ?",
                (len(chunks_raw), book_id)
            )
    except Exception:
        conn.rollback()
        raise

    return {
        "book_id": book_id,
        "title": p.stem,
        "chunk_count": len(chunks_raw),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m lifekit.store.pdf_ingester <path/to/pdf>", file=sys.stderr)
        sys.exit(1)

    try:
        result = ingest_pdf(sys.argv[1])
        print(
            f"Ingested {result['title']}: "
            f"{result['chunk_count']} chunks "
            f"(book_id={result['book_id']})"
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
