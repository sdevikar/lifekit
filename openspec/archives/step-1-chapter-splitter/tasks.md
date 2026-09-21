# Step 1: Chapter splitter — tasks ✅ COMPLETED (2026-09-15)

- [x] 1.1 Add `PyMuPDF` to `pyproject.toml` dependencies
- [x] 1.2 Implement TOC-based splitting via `doc.get_toc()` → `(title, page_start, page_end)` ranges
- [x] 1.3 Implement heading-heuristic fallback (font-size detection) for PDFs with missing/empty TOC
- [x] 1.4 Implement fixed-size section fallback when neither TOC nor headings are usable
- [x] 1.5 Refuse image-only PDFs with a clear error (`EmptyPDFError`)
- [x] 1.6 Add `chapters` table migration to `../../../lifekit/db/schema.py` (idempotent)
- [x] 1.7 Add CLI `python -m lifekit.store.split --pdf <path>` printing detected chapters
- [x] 1.8 py_compile clean on all new/changed files
- [x] 1.9 Done-criterion test: run on 2–3 real self-help PDFs, record boundary accuracy vs. actual TOCs (incl. one heuristic-fallback case + one image-only refusal) below

## Test results (2026-09-15)

`tests/test_chapter_splitter.py` — **6/6 passed** (`pytest tests/test_chapter_splitter.py`).

- **Designing Your Life PDF (real, 199 pp, embedded TOC):** 17 chapters detected; all 11 numbered chapters + Introduction + Conclusion boundaries match the embedded TOC exactly (e.g. ch.1 pp.24–42, ch.11 pp.166–177). Image-only front-matter pages (1–2) correctly skipped. Every chapter carries >200 chars of text.
- **As a Man Thinketh (Gutenberg text → PDF with embedded TOC):** 7 chapters, boundaries match the TOC; zero-length Foreword entry (shared page 1) correctly dropped.
- **Heading-heuristic fallback (synthetic, no TOC):** 2 chapters detected from 24pt headings. ✅ exercised.
- **Fixed-size fallback (synthetic, no TOC/headings):** 20 pages → 2 sections of 15 pages. ✅ exercised.
- **Image-only PDF:** refused with `EmptyPDFError`. ✅
- **DB persistence:** `chapters` rows written and re-readable. ✅

New files: `../../../lifekit/store/chapter_splitter.py`, `../../../lifekit/store/split.py`, `tests/test_chapter_splitter.py`.
Changed: `../../../lifekit/db/schema.py` (+`chapters` table), `pyproject.toml` (+PyMuPDF).
