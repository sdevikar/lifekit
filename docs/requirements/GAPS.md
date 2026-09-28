# LifeKit — Gaps Identified & Recommended Actions

## Critical Gaps (block progress)

| # | Gap | Impact | Recommended Action |
|---|-----|--------|-------------------|
| G1 | **Dogfood exit criterion undefined** | Stage 5 cannot be gated; program layer is in limbo | Draft `docs/product/DOGFOOD-EXIT.md` with 3-5 measurable criteria; get human approval |
| G2 | **Book model is still a draft** | The proprietary layer (the moat) has no finalized schema | Finalize `docs/backend/BOOK_MODEL.md` open questions (items table vs per-type, relation set, key-idea typing) |
| G3 | **No formal requirements document** | User stories exist but no SRS for non-functional requirements | This document becomes the SRS; get human approval to make it binding |

## Documentation Gaps (correct and extend)

| # | Gap | Impact | Recommended Action |
|---|-----|--------|-------------------|
| G4 | **No API specification** | Feed API endpoints are documented across STATUS.md and test files, but no single API reference | Create `docs/backend/API.md` with request/response schemas |
| G5 | **No ADR (Architecture Decision Records)** | Decisions are scattered across PHILOSOPHY.md, BORROW-REPORT, and code comments | Create `docs/arch/adrs/` for each significant decision |
| G6 | **No data dictionary** | Schema is in code (`db/schema.py`) but not documented for humans | Create `docs/backend/DATA-DICTIONARY.md` |
| G7 | **No deployment runbook** | Deployment is documented in STATUS.md fragments; no single ops guide | Create `docs/ops/RUNBOOK.md` |
| G8 | **No testing strategy document** | Testing principles are in STATUS.md; no standalone strategy | Create `docs/backend/TESTING.md` |
| G9 | **No onboarding flow for new users** | User stories exist but no first-run experience design | Design onboarding when Stage 4 exit is proven |
| G10 | **No backup/restore documentation** | Data backup is mentioned but no procedure | Add to `docs/ops/RUNBOOK.md` |

## Code Gaps (known issues)

| # | Gap | Impact | Recommended Action |
|---|-----|--------|-------------------|
| G11 | **D3: Cross-chapter merged quotes can never validate** | Medium | Add `merged_chapter_title` to `dedupe_log`; validate extra quotes against origin chapter |
| G12 | **D4: No overlapping sections in extraction** | Low/Medium | Implement manual overlap (500-char sliding window) or accept contiguous |
| G13 | **D5: `search_exercises` crashes on empty book-id list** | Low | Return `[]` early; add regression test |
| G14 | **D6: `review_exercise` on nonexistent exercise creates orphans** | Low | Verify exercise exists or enable FK pragma |
| G15 | **D7: Step 3 proposal promised `page_start`/`page_end`** | Low | Add columns or record drift in ASSUMPTIONS.md |
| G16 | **P2: `test_split_dyl_pdf` hardcodes VM path** | Medium | Skip when PDF absent or read from env var |
| G17 | **P3: Dead no-op loop in chapter splitter** | Low | Delete (trivial cleanup) |
| G18 | **P4: Two `EmptyPDFError` classes** | Low | Consolidate to one shared exception |
| G19 | **P5: `book_id_for` hashes raw path** | Low | `Path.resolve()` before hashing |
| G20 | **P6: LIKE wildcards unescaped** | Low | Escape wildcards in query |

## Recommended Priority Order

1. **G1** — Define dogfood exit criterion (unblocks everything)
2. **G2** — Finalize book model (the moat)
3. **G3** — Approve this document as the SRS
4. **G4-G8** — Write missing docs (API, ADRs, data dictionary, runbook, testing)
5. **G11-G20** — Fix known code issues (batch into a "harden" commit)
