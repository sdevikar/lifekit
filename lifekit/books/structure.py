"""Structure stage: turn a book file into sections and passages."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

import fitz  # PyMuPDF




def _load_kinds():
    import tomllib
    p = Path(__file__).with_name("section_kinds.toml")
    with p.open("rb") as f:
        data = tomllib.load(f)
    mapping = {}
    for kind, info in data.items():
        for t in info.get("titles", []):
            mapping[t.lower()] = kind
    return mapping


_KINDS = _load_kinds()


def _classify(title: str) -> str:
    low = title.strip().lower()
    for key, kind in _KINDS.items():
        if key in low:
            return kind
    return "body"


def _book_id(path: Path, override: str | None = None) -> str:
    if override:
        return override
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return h[:16]


def _toc_sections(doc) -> list[dict]:
    toc = doc.get_toc()  # [level, title, page]
    # Build parent tracking by level stack.
    stack: list[int] = []  # indices into sections
    sections = []
    for level, title, page in toc:
        while len(stack) >= level:
            stack.pop()
        parent = stack[-1] if stack else None
        parent_idx = sections[parent]["idx"] if parent is not None else None
        # depth = level-1
        sec = {
            "title": title,
            "page_start": page,
            "depth": level - 1,
            "parent_idx": parent_idx,
        }
        sections.append(sec)
        stack.append(len(sections) - 1)
    # assign idx (reading order) and page_end
    for i, s in enumerate(sections):
        s["idx"] = i
        # page_end = next section's page_start - 1 (or last page)
        if i + 1 < len(sections):
            s["page_end"] = max(s["page_start"], sections[i + 1]["page_start"] - 1)
        else:
            s["page_end"] = doc.page_count
    return sections


def _section_text(doc, page_start, page_end) -> str:
    parts = []
    for pno in range(max(1, page_start), min(doc.page_count, page_end) + 1):
        try:
            parts.append(doc[pno - 1].get_text())
        except Exception:
            pass
    return "\n".join(parts)


def _passages(text: str) -> list[str]:
    # Split into paragraphs; drop short/header-like lines.
    paras = [p.strip() for p in re.split(r"\n\s*\n", text)]
    out = []
    for p in paras:
        if len(p) < 40:
            continue
        # drop lines that look like page numbers / headers
        if re.fullmatch(r"\d+", p):
            continue
        out.append(p)
    return out


def ingest(db_path, file_path, book_id_override=None) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF/EPUB not found: {path}")
    book_id = _book_id(path, book_id_override)
    doc = fitz.open(str(path))
    fmt = path.suffix.lstrip(".").lower() or "pdf"
    title = doc.metadata.get("title") or path.stem
    author = doc.metadata.get("author")

    sections = _toc_sections(doc)
    # classify kind: top-level parent's kind for children
    top_kind = {}
    for s in sections:
        if s["parent_idx"] is None:
            top_kind[s["idx"]] = _classify(s["title"])
    for s in sections:
        if s["parent_idx"] is None:
            s["kind"] = _classify(s["title"])
        else:
            # find top-level ancestor
            # walk up
            cur = s
            while cur["parent_idx"] is not None:
                cur = sections[cur["parent_idx"]]
            s["kind"] = top_kind.get(cur["idx"], _classify(s["title"]))

    # apply overrides
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        # ensure schema
        from lifekit.db.schema import init_db
        init_db(db_path)
        # upsert book
        conn.execute(
            """INSERT INTO books (id, title, author, file_path, format, content_hash)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET title=excluded.title, author=excluded.author,
               file_path=excluded.file_path, format=excluded.format, content_hash=excluded.content_hash""",
            (book_id, title, author, str(path), fmt,
             hashlib.sha256(path.read_bytes()).hexdigest()),
        )
        # overrides
        overrides = {r[0]: r[1] for r in conn.execute(
            "SELECT section_idx, kind FROM section_kind_overrides WHERE book_id = ?",
            (book_id,),
        ).fetchall()}
        # remove old sections/passages for this book
        conn.execute("DELETE FROM passages WHERE book_id = ?", (book_id,))
        conn.execute("DELETE FROM sections WHERE book_id = ?", (book_id,))
        for s in sections:
            idx = s["idx"]
            kind = overrides.get(idx, s["kind"])
            conn.execute(
                """INSERT INTO sections (book_id, idx, parent_idx, depth, title, page_start, page_end, kind)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (book_id, idx, s["parent_idx"], s["depth"], s["title"],
                 s["page_start"], s["page_end"], kind),
            )
            text = _section_text(doc, s["page_start"], s["page_end"])
            paras = _passages(text)
            for n, p in enumerate(paras):
                pid = f"{book_id}:{idx}:{n}"
                conn.execute(
                    """INSERT INTO passages (id, book_id, section_idx, n, text, char_start, char_end)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (pid, book_id, idx, n, p, None, None),
                )
        conn.commit()
    finally:
        conn.close()
    doc.close()

    from lifekit.runs import record_run
    record_run(db_path, book_id, "structure", status="ok",
              counts={"sections": len(sections)})
    return book_id