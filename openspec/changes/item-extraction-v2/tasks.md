# Tasks — item-extraction-v2

## 1. Table, config, and fixtures

- [ ] 1.1 Add the `items` table and index from design.md D8 to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a copy of `dogfood/lifekit.db` without error.
- [ ] 1.2 Add `lifekit/items/__init__.py` and `lifekit/items/items.toml` with the values in design.md D2, plus a loader; verify a test reads `window_chars == 6000`.
- [ ] 1.3 Add a stub provider in `tests/test_items.py` that returns canned JSON per call (same pattern as existing stubbed tests, no new mock library) and a fixture book built with the book-model-v1 test helper; verify the fixture has body, front, and back sections.

## 2. Windows, extraction, validation, anchoring

- [ ] 2.1 Write `lifekit/items/extract.py` window building (D4); verify tests for "Exercise across a window edge" and the single-long-passage rule pass.
- [ ] 2.2 Write the prompt and flat schema in `lifekit/items/prompts.py` (D3) and the window call with the 3-attempt retry; verify a stubbed call returns parsed candidates and that `prompt_hash` is stable across two imports.
- [ ] 2.3 Add per-type content validation and the activity-stance rule; verify tests for "Habit with cadence", "Exercise without steps", and "Anecdote is not an exercise" (stub returns an `author_states` exercise) pass.
- [ ] 2.4 Write `lifekit/items/anchor.py` (D5) with `normalize_ws`; verify tests for "Quote across two passages" and "Invented quote" pass.
- [ ] 2.5 Verify "Notes are skipped": a test asserts the stub provider receives no call containing back-matter text.

## 3. Consolidation and judge

- [ ] 3.1 Write `lifekit/items/consolidate.py` with the chapter and book passes and the group rules (D6); verify tests for "Repeated exercise in one chapter", "Same topic, different type", "Recap in the conclusion", and an unknown-number group pass.
- [ ] 3.2 Write `lifekit/items/judge.py` with the rubric prompt, batches of 10, and the single retry (D7); verify tests for "Meta statement rejected", "Specific rule kept", and a malformed batch entry pass.
- [ ] 3.3 Add a test that no API route in `lifekit/serve/` returns `useful_rating` or `fail_codes`; verify it passes.

## 4. Stage and records

- [ ] 4.1 Write `ItemsStage` in `lifekit/items/stage.py` with item keys, positions, the replace-in-one-transaction rule, pacing, and the stats summary (D8, D10), and register it in `lifekit/ingest.py`; verify tests for "Re-run replaces items", "Stable item key", and "Summary line" pass.
- [ ] 4.2 Run `lifekit ingest --book dyl --from items` on the home workstation's Ollama (`qwen3.8:27b-q8_0`) against a copy of the dogfood DB; verify the run record is `ok` and paste the summary line into the change's handoff.

## 5. Usefulness eval

- [ ] 5.1 Write `lifekit/evals/usefulness.py` with sampling (D9), the labelling loop, and resume; verify tests for "Label and quit", "The label screen hides the judge verdict", "Resume labelling", and "Labels after re-extraction" pass, driving input through a list instead of a terminal.
- [ ] 5.2 Add the report and gate with exit codes; verify tests for "Precision computed", "Too few labels", and "Gate fails" pass.
- [ ] 5.3 Add `eval usefulness label|report` to `lifekit/__main__.py`; verify `lifekit eval usefulness --help` lists both commands.
- [ ] 5.4 The human labels at least 60 `dyl` items and runs the report; verify `evals/usefulness/dyl/report.md` exists and record PASS or FAIL in KANBAN.

## 6. Docs

- [ ] 6.1 Add the D1 diagram and the item statuses to `docs/arch/README.md`, the eval commands to `AGENTS.md`, mark D4 fixed in KANBAN, add the new tests to `docs/arch/testing.md`, and update the test count; verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 3 to Done and archive this change after merge.
