"""lifekit.store -- Knowledge store ingestion for LifeKit.

Exports all public interfaces so callers import from lifekit.store only.
Supported formats: PDF (pypdf), EPUB (ebooklib fallback zipfile).

Usage (library):
    from lifekit.store import ingest_book, SupportedFormat
    
    result = ingest_book("/path/to/book.pdf")      # auto-detect
    result = ingest_epub("/path/to/book.epub")

Usage (CLI):
    python -m lifekit.store --pdf book.pdf
    python -m lifekit.store --epub book.epub
"""
from __future__ import annotations

from lifekit.store.clean_text import clean_and_sanitize, sanitize
from lifekit.store.epub_ingester import ingest_epub, EmptyEPUBError, DuplicateIngestError as EPUBDuplicateIngestError
from lifekit.store.pdf_ingester import (
    ingest_pdf,
    EmptyPDFError,
    DuplicateIngestError as PDFDuplicateIngestError,
)


class DuplicateIngestError(Exception):
    """Unified duplicate error raised when trying to ingest a file already in the store."""


def ingest_book(file_path: str | None = None, epub_path: str | None = None, **kwargs):
    """Auto-detect and ingest a book by filename suffix.

    Args:
        file_path: Path to a PDF file (passed as positional or keyword).
        epub_path: Path to an EPUB file (passed as named kwarg).
        **kwargs: Extra args forwarded to the underlying ingestor (e.g. db_path).

    Returns:
        dict with book_id, title, chunk_count (+ author for EPUBs).
    """
    if epub_path is not None:
        return ingest_epub(epub_path, **kwargs)

    target = file_path or kwargs.pop("path", None)
    if target and str(target).lower().endswith((".pdf",)):
        return ingest_pdf(target, **kwargs)
    elif target and str(target).lower().endswith((".epub",)):
        return ingest_epub(target, **kwargs)
    else:
        raise ValueError(
            "Provide 'file_path' for a PDF or 'epub_path' for an EPUB. "
            "Auto-detection failed — no file path matched .pdf or .epub."
        )


__all__ = [
    "ingest_book",
    "ingest_pdf",
    "ingest_epub",
    "clean_and_sanitize",
    "sanitize",
    "EmptyPDFError",
    "EmptyEPUBError",
    "DuplicateIngestError",
]
