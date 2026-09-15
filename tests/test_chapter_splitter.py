"""Step 1 done-criterion tests: chapter splitter.

Covers all four strategies from the proposal:
  1. embedded TOC via PyMuPDF (primary)
  2. heading/font heuristics (fallback)
  3. fixed-size sections (last resort)
  4. image-only PDF refusal

Plus DB persistence. Run:  python -m pytest tests/test_chapter_splitter.py -v
"""
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.db.schema import init_db
from lifekit.store.chapter_splitter import split_chapters, EmptyPDFError

DYL_PDF = Path(
    "/home/hatch/workspace/user/files/Bill_Burnett_-_Designing_Your_Life__"
    "How_to_Build_a_Well-Lived__Joyful_Life__2016__Knopf_Doubleday_"
    "Publishing_Group__-_libgen.li.pdf"
)

KNOWN_DYL_CHAPTERS = [
    "Start Where You Are",
    "Building a Compass",
    "Wayfinding",
    "Getting Unstuck",
    "Design Your Lives",
    "Prototyping",
    "How Not to Get a Job",
    "Designing Your Dream Job",
    "Choosing Happiness",
    "Failure Immunity",
    "Building a Team",
]


def _make_pdf(path: Path, pages: list[str], toc=None, fontsize: float = 11.0):
    """Build a synthetic PDF with one text block per page."""
    import fitz

    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=fontsize)
    if toc:
        doc.set_toc(toc)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture()
def workdir(tmp_path):
    return tmp_path


def test_split_uses_embedded_toc(workdir):
    """Primary path: embedded TOC drives chapter boundaries."""
    pdf = _make_pdf(
        workdir / "toc.pdf",
        ["Chapter one body text. " * 40, "Chapter two body text. " * 40,
         "Chapter three body text. " * 40],
        toc=[[1, "One", 1], [1, "Two", 2], [1, "Three", 3]],
    )
    chapters = split_chapters(str(pdf))
    assert [c.title for c in chapters] == ["One", "Two", "Three"]
    assert chapters[0].page_start == 1 and chapters[0].page_end == 1
    assert chapters[1].page_start == 2
    assert "Chapter one body" in chapters[0].text
    assert "Chapter two body" in chapters[1].text


def test_split_dyl_pdf():
    """Done-criterion on the real book: DYL's 11 chapters detected via TOC."""
    chapters = split_chapters(str(DYL_PDF))
    titles = " || ".join(c.title for c in chapters)
    for known in KNOWN_DYL_CHAPTERS:
        assert known in titles, f"missing chapter: {known}"
    assert len(chapters) >= 11
    # every chapter carries real text
    for c in chapters:
        assert len(c.text.strip()) > 200, f"chapter too short: {c.title}"
    # page ranges are sane and ordered
    for c in chapters:
        assert 1 <= c.page_start <= c.page_end <= 199


def test_heading_heuristic_fallback(workdir):
    """No TOC: large styled headings are detected as chapter boundaries."""
    import fitz

    pdf = workdir / "headings.pdf"
    doc = fitz.open()
    sections = [("FIRST PART", "alpha body. " * 60),
                ("SECOND PART", "beta body. " * 60)]
    for heading, body in sections:
        page = doc.new_page()
        page.insert_text((72, 72), heading, fontsize=24)   # heading: big
        page.insert_text((72, 120), body, fontsize=11)     # body: small
    doc.save(str(pdf))
    doc.close()

    chapters = split_chapters(str(pdf))
    assert len(chapters) == 2, f"expected 2, got {[c.title for c in chapters]}"
    assert "FIRST PART" in chapters[0].title
    assert "SECOND PART" in chapters[1].title


def test_fixed_size_fallback(workdir):
    """No TOC, no headings: plain text falls back to fixed-size sections."""
    pdf = _make_pdf(
        workdir / "plain.pdf",
        [f"plain body text page {i}. " * 100 for i in range(20)],
        fontsize=11.0,
    )
    chapters = split_chapters(str(pdf))
    assert len(chapters) >= 2
    # each section bounded in size (fallback granularity)
    for c in chapters:
        assert len(c.text) <= 60000


def test_image_only_pdf_refused(workdir):
    """Image-only PDF is refused with a clear error, never silently empty."""
    import fitz

    pdf = workdir / "image.pdf"
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 100, 100))
    page.insert_image(page.rect, pixmap=pix)
    doc.save(str(pdf))
    doc.close()

    with pytest.raises(EmptyPDFError):
        split_chapters(str(pdf))


def test_chapters_persisted_to_db(workdir):
    """split_chapters writes rows to the chapters table."""
    db_path = str(workdir / "test.db")
    init_db(db_path)
    pdf = _make_pdf(
        workdir / "persist.pdf",
        ["Persisted one. " * 40, "Persisted two. " * 40],
        toc=[[1, "A", 1], [1, "B", 2]],
    )
    chapters = split_chapters(str(pdf), db_path=db_path, book_id="test-book")
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT idx, title, page_start, page_end FROM chapters "
        "WHERE book_id = 'test-book' ORDER BY idx"
    ).fetchall()
    assert len(rows) == len(chapters) == 2
    assert rows[0][1] == "A"
    content = conn.execute(
        "SELECT content FROM chapters WHERE book_id='test-book' AND idx=0"
    ).fetchone()[0]
    assert "Persisted one" in content
