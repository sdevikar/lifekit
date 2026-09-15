# Assumptions log

Living document. Every consequential assumption gets an ID, the step/change
that introduced it, a status, and a revisit trigger. Nothing here is silently
dropped — assumptions are retired explicitly when evidence or decisions change them.

Statuses: `locked` (Step 0 — not revisited during MVP), `active` (in force,
revisitable), `challenged` (evidence against it is being gathered),
`retired` (no longer in force; reason + date recorded).

## Step 0 — locked (2026-09-14)

Canonical text lives in `ROADMAP.md`. One-liners here for traceability.

| ID | Assumption | Status |
|----|------------|--------|
| A1 | PDF only. No EPUB, audio, YouTube. | locked |
| A2 | Text-layer PDFs only; scanned/image PDFs refused with a clear error, never silently ingested. | locked |
| A3 | PDFs are well-formed with an embedded TOC; splitter reads TOC first, heuristics only as fallback. Pathological PDFs out of scope. | locked |
| A4 | English-language self-help books. | locked |
| A5 | Single user, local machine, Ollama running (`qwen3.6:latest` or configured model). | locked |
| A6 | Books are chapter-detectable; fixed-size sections as fallback. | locked |
| A7 | Extraction need not be perfect — misses fine; systemic failures flagged, not silently shipped. | locked |
| A8 | No frontend (CLI + MCP tools only); no auth, no cloud, no sync. | locked |

## Step 1 — chapter splitter (`openspec/changes/step-1-chapter-splitter/`)

| ID | Assumption | Status | Revisit trigger |
|----|------------|--------|-----------------|
| A9 | Embedded TOC via PyMuPDF `get_toc()` is the primary chapter source; zero heuristics on this path. | active | If TOCs prove missing or unreliable across test books, reorder the strategy. |
| A10 | Heading/font heuristics are the fallback when TOC is missing or empty. | active | If boundary accuracy is too low in the done-criterion test, replace with a better detector. |
| A11 | Fixed-size sections are the final fallback when neither TOC nor headings work. | active | If Step 2 extraction quality suffers on section-split chapters, revisit granularity (e.g. Chonkie semantic chunking). |
| A12 | Image-only PDFs are refused with a clear error; no OCR in MVP. | active | If the user wants scanned books, add an OCR path. |
| A13 | PyMuPDF is added as a dependency for this path; pypdf remains for ingest. | active | Consolidate to one parser later if maintaining two proves annoying. |
| A14 | `chapters` table shape: `(id, book_id, idx, title, page_start, page_end, content)`. | active | If Steps 2–3 need finer/coarser units, migrate the schema. |
| A15 | Fixed-size fallback granularity: 15 pages per section (`FALLBACK_SECTION_PAGES`). | active | If Step 2 extraction quality suffers on section-split chapters, tune granularity. |
| A16 | `chapters.book_id` has no FK to `books` — the splitter stays decoupled from ingestion; book_id defaults to sha256(path)[:16]. | active | If referential integrity is needed later, add the FK + migration. |

## Step 2 — extraction map (`openspec/changes/step-2-extraction-map/`)

| ID | Assumption | Status | Revisit trigger |
|----|------------|--------|-----------------|
| A17 | Dev eval uses llama.cpp + Qwen3-4B-Q4_K_M GGUF via a dev-only Ollama-interface shim (Ollama binary not downloadable in this sandbox: registry TLS blocked). Product code stays Ollama-native (`ollama.Client`, `format=<json_schema>`, temp 0.1). Subset validation (ch.0,1) confirms pipeline correctness. The 4B cannot extract exercises from content chapters (systematic validation failures; plain-JSON mode worse); Qwen3-8B (5GB) OOMs on 7.9GB RAM. Full 15/20 recall DEFERRED to production Ollama + capable model. | active | When Ollama runs with a suitable model (qwen3.6 or larger), re-run the full-book recall eval through the product path. |
| A18 | Oversized chapters (>48k chars) split via Chonkie `RecursiveChunker` into per-section extractions, concatenated. Dev eval uses smaller thresholds (16k/12k) to fit 7GB RAM; product defaults unchanged. | active | If section-boundary exercises are missed/duplicated in recall, add overlap or raise thresholds. |
| A19 | `extract_chapter` backfills missing `chapter_title` from the known `Chapter.title` instead of failing/retriing when the model omits it (observed on front matter). Strict Pydantic schema unchanged for model output. | active | If backfill masks real model confusion, remove it and require the field. |
| A20 | Full-book extraction recall eval (20-exercise ground truth) deferred to the user's local dev setup with their own model (decision 2026-09-15). Not blocking Steps 3–7; pipeline validated via subset/proxy evals (A17). | active | When the user runs the eval locally, record results in `openspec/archives/step-2-extraction-map/tasks.md`. |
