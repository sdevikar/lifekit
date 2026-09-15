# Step 1: Chapter splitter — tasks

- [ ] 1.1 Add `PyMuPDF` to `pyproject.toml` dependencies
- [ ] 1.2 Implement TOC-based splitting via `page.get_toc()` / `doc.get_toc()` → `(title, page_start, page_end)` ranges
- [ ] 1.3 Implement heading-heuristic fallback (font-size/style detection) for PDFs with missing/empty TOC
- [ ] 1.4 Implement fixed-size section fallback when neither TOC nor headings are usable
- [ ] 1.5 Refuse image-only PDFs with a clear error (reuse `EmptyPDFError`)
- [ ] 1.6 Add `chapters` table migration to `lifekit/db/schema.py` (idempotent)
- [ ] 1.7 Add CLI `python -m lifekit.store.split --pdf <path>` printing detected chapters
- [ ] 1.8 py_compile clean on all new/changed files
- [ ] 1.9 Done-criterion test: run on 2–3 real self-help PDFs, record boundary accuracy vs. actual TOCs (incl. one heuristic-fallback case + one image-only refusal) below

## Test results

*(record here)*
