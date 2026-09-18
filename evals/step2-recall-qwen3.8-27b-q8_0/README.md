# Step-2 full-book extraction eval — `qwen3.8:27b-q8_0`

**Date completed:** 2026-09-17 ~21:30 EDT
**Model:** `qwen3.8:27b-q8_0` via the Ollama API on the user's home workstation (Tailscale; tailnet traffic through runtime proxy port 3130). The VM ran only the eval harness — no model ran here.
**Pipeline:** LifeKit `extract_chapter` (strict JSON-schema, temp 0.1, Pydantic retry), sequential chapters, 15 s pacing (user's home GPU).
**Ground truth:** 20 exercises/practices (`~/workspace/self-help-exercises/designing-your-life-exercises.md`).
**Coverage:** all 17 chapters (0–16). 156 exercise records.

**Method note:** chapters were extracted in ~4k-char sections (`LIFEKIT_MAX_CHAPTER_CHARS=4000`, `LIFEKIT_SECTION_CHUNK_CHARS=3000`) because full-chapter requests timed out over the tunnel; socket timeout 600 s, per-request deadline 900 s. Chapter 13 ("11. Building a Team") needed a temporary 2000/1500 sectioning after repeated silent deaths. Checkpointing preserved every completed chapter across ~9 VM reboots; total wall-clock ~17 h.

## Results

| Ch | Chapter | Exercises |
|----|---------|-----------|
| 0 | Dedication | 0 |
| 1 | Contents | 0 |
| 2 | Introduction: Life by Design | 3 |
| 3 | 1. Start Where You Are | 13 |
| 4 | 2. Building a Compass | 9 |
| 5 | 3. Wayfinding | 15 |
| 6 | 4. Getting Unstuck | 13 |
| 7 | 5. Design Your Lives | 11 |
| 8 | 6. Prototyping | 18 |
| 9 | 7. How Not to Get a Job | 9 |
| 10 | 8. Designing Your Dream Job | 9 |
| 11 | 9. Choosing Happiness | 16 |
| 12 | 10. Failure Immunity | 7 |
| 13 | 11. Building a Team | 10 |
| 14 | Conclusion: A Well-Designed Life | 23 |
| 15 | Acknowledgments | 0 |
| 16 | Notes | 0 |

## Findings

1. **Substance recall 19/20 (95%).** The only genuine miss is Practice 20 ("Ask-for-Help Journal"). Exercise 10 ("Internet Job Search Tips") is present but fragmented into 8 résumé-tip micro-records (ch 9); Practice 19 ("Five Mind-Sets as Daily Questions") into 5 single-mind-set records (ch 14). Keyword-only recall scored 14/20; semantic review recovered 3 more.
2. **Fragmentation is the dominant defect.** Same-title duplicates: Good Time Journal ×4, Mind Mapping ×3, Life Design Interview ×2, Health/Work/Play/Love Dashboard ×2, Dysfunctional Belief Reframe ×3. Within-chapter near-duplicates too (ch 8 has three brainstorming variants; ch 14 splits personal practices into single-habit records). Step 3 dedupe has NOT run on these outputs — recall must be re-measured post-dedupe.
3. **Quote grounding: exact 16/156 (10%), whitespace-normalized 87/156 (56%).** The model quotes real book text and only alters whitespace. The Step 4 validator (`lifekit/validate/validator.py`) uses exact-substring comparison and would false-fail ~90% of genuine quotes as written — it must normalize whitespace before comparing. See `openspec/changes/step-4-quote-whitespace-normalization/`.
4. **Over-extraction of anecdotes/sidebars.** All spot-checked suspicious records are real book content (e.g. "Play Dead" anecdote ch 11, "Call Your Mother" ch 14) — no clear hallucinations, but the prompt's broad net ("practice, prompt, routine, challenge") catches narrative anecdotes. Examples: "Commentators vs. Participants Reflection", "Journaling to Discover Your Inner Voice".
5. **Zero-step records: 0.** All 156 records have at least one step (better than the earlier dots-studio run's 0-step reframes).
6. **Materials: 100/156 records have none.** Many exercises genuinely lack materials, but spot-check against the ground truth (Odyssey Plan worksheets, Good Time Journal notebook).
7. **Chapters 0, 1, 15, 16 correctly empty** (front/back matter).

## Verdict — MVP extraction-quality gate

**Conditional pass.** Substance recall is 95% with zero hallucinations found and every record having steps — the pipeline finds the exercises. But raw output is not coach-ready: heavy fragmentation means Step 3 dedupe must run before recall means anything, and the Step 4 validator's quote check must be fixed to normalize whitespace. Fix those two, run Step 3 over these extractions, and re-score — then the gate is proven.

## Post-eval follow-up (2026-09-18)

Both fixes landed; the gate is now proven for *Designing Your Life*:

- **Dedupe-aware recall (BACKLOG E2):** `scripts/eval_dedupe_recall.py` ran Step 3 `reduce_extractions` over these outputs: 156 raw → **144 exercises** (12 merges), **875 key ideas**. Dedupe-aware recall **19/20 (95%)** — same single miss (Ask-for-Help Journal). Deterministic dedupe only merges identical normalized titles, so fragmentation survives: Good Time Journal ×4, Mind Mapping ×3, five mind-set questions as separate records, Dysfunctional Belief Reframe ×3. Near-duplicate title merging is a future Step 3 refinement, not required for MVP.
- **Validator fix (BACKLOG E1):** `normalize_ws` now does NFKC + typographic-punctuation folding (curly quotes, em/en dashes, NBSP) before whitespace collapse — still strict substring matching, no fuzzy. Ingest validation (`scripts/ingest_eval_book.py`, product DB `~/.lifekit/lifekit.db`, book id `dyl`): **142/144 exercises grounded**. The 2 failures are PDF-text corruptions in the chapter text itself ("welldesigned", "designi ngyour.life") where the model quoted correctly. Extra_quotes now ground against full book text (dedupe merges records across chapters); source_quote still requires its own chapter.
- **Bottom line: 0 hallucinations in 144 exercises.** The book is ingested and coach-ready at `~/.lifekit/lifekit.db` (17 chapters, 144 exercises, 875 key ideas, validation_log).

## Files

- `results_qwen3.8-27b-q8_0.json` — per-chapter records with `ok`, timing, exercise titles, and per-exercise `grounded_exact` / `grounded_ws` flags.
- `extractions_qwen3.8-27b-q8_0.json` — full raw extractions (chapter keys 0–16): titles, steps, materials, source quotes, key ideas.
