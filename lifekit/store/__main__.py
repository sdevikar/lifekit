"""CLI entry for book ingestion (PDF + EPUB).

Usage:
    python -m lifekit.store --pdf <path/to/book.pdf>      # PDF input
    python -m lifekit.store --epub <path/to/book.epub>     # EPUB input
    python -m lifekit.store --check                        # Verify extractors available
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.db.schema import init_db
from lifekit.store.pdf_ingester import ingest_pdf, EmptyPDFError, DuplicateIngestError as PDFDuplicate
from lifekit.store.epub_ingester import ingest_epub, EmptyEPUBError, DuplicateIngestError as EPUBDuplicate


def _check_extractors():
    """Print extractor availability for each supported format (used by --check)."""
    available = {}
    try:
        from pypdf import PdfReader
        available["PDF (pypdf)"] = "✓"
    except ImportError:
        try:
            from PyPDF2 import PdfReader
            available["PDF (PyPDF2)"] = "✓"
        except ImportError:
            available["PDF"] = "✗ Install: pip install pypdf"

    if HAS_EBOOKLIB_AVAILABLE:
        available["EPUB (ebooklib)"] = "✓"
    else:
        available["EPUB (ebooklib)"] = "⚠ Not installed — stdlib fallback active"

    # Check ebooklib specifically
    try:
        import ebooklib
        from bs4 import BeautifulSoup
        eutil = "ebooklib + BeautifulSoup"
    except ImportError:
        eutil = "stdlib zipfile (limited)"
    available["EPUB backend"] = eutil

    print("Extractor availability:")
    for fmt, status in available.items():
        print(f"  {fmt}: {status}")


# Early detection of ebooklib for --check output.
try:
    import ebooklib as _tmp_ebooklib  # noqa: F401

    HAS_EBOOKLIB_AVAILABLE = True
except ImportError:
    HAS_EBOOKLIB_AVAILABLE = False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest a PDF or EPUB book into the LifeKit knowledge store.",
    )
    parser.add_argument("path", nargs="?", help="Path to a .pdf or .epub file (positional)")
    parser.add_argument("--pdf", dest="pdf_path", help="Alternative: path to a PDF file")
    parser.add_argument("--epub", dest="epub_path", help="Alternative: path to an EPUB file")
    parser.add_argument(
        "--db-path", default=None, help="Path to SQLite database (default: ~/.lifekit/lifekit.db)"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check extractor availability and exit"
    )
    args = parser.parse_args()

    # --check mode
    if args.check:
        _check_extractors()
        return

    # Determine target file
    pdf_target = args.pdf_path or (args.path if args.path and str(args.path).lower().endswith(".pdf") else None)
    epub_target = args.epub_path or (args.path if args.path and str(args.path).lower().endswith(".epub") else None)

    if not pdf_target and not epub_target:
        parser.print_help(file=sys.stderr)
        print("\nError: Provide a .pdf or .epub file via positional arg, --pdf, or --epub", file=sys.stderr)
        sys.exit(1)

    try:
        init_db(args.db_path)  # ensure tables exist

        if epub_target:
            result = ingest_epub(epub_target, db_path=args.db_path)
            print(
                f"Ingested {result['title']} by {result.get('author', 'Unknown')}: "
                f"{result['chunk_count']} chunks (book_id={result['book_id']})"
            )
        else:
            result = ingest_pdf(pdf_target, db_path=args.db_path)
            print(
                f"Ingested {result['title']}: {result['chunk_count']} chunks "
                f"(book_id={result['book_id']})"
            )
    except FileNotFoundError as e:
        print(f"Error: File not found — {e}", file=sys.stderr)
        sys.exit(1)
    except (EmptyPDFError, EmptyEPUBError) as e:
        print(f"Error: No extractable text — {e}", file=sys.stderr)
        sys.exit(1)
    except PDFDuplicate as e:
        print(f"Warning: Already ingested — {e}")
        sys.exit(0)
    except EPUBDuplicate as e:
        print(f"Warning: Already ingested — {e}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e!s}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
