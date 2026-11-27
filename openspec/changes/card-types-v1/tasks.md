# Tasks — card-types-v1

## 1. Type config and content models

- [ ] 1.1 Create `lifekit/cards/__init__.py` and `lifekit/cards/card_types.toml` with the six entries (description, item_kinds, allowed_stances, source_label, done_label, surface, coach_instruction) from design.md D1; verify `uv run python -c "import tomllib; print(sorted(tomllib.load(open('lifekit/cards/card_types.toml','rb'))))"` prints the six names.
- [ ] 1.2 Write `lifekit/cards/types.py`: the six Pydantic content models with the limits in the spec (title ≤ 80 chars, insight body ≤ 80 words, 1–10 steps, cadence enum, 0–3 follow-ups, 1–12 worksheet fields, field id regex `^[a-z0-9_]+$`, scale and choice limits); verify with tests in 1.4.
- [ ] 1.3 Add the import-time check that TOML tables equal the model set, plus `CARD_TYPES`, `spec()`, `content_model()`, `card_type_for()`, `source_label()`; verify that removing one TOML table makes `python -c "import lifekit.cards.types"` raise.
- [ ] 1.4 Write `tests/test_card_types.py` covering every spec scenario under "Six card types", "Common card fields", "Type-specific content fields", "Worksheet field kinds", "Item kind maps to one card type", "Activities need an author instruction", and "Visible source label"; verify `uv run pytest tests/test_card_types.py -v` passes.

## 2. Status and done rules

- [ ] 2.1 Add `next_status()` with the transition table from the spec and `InvalidTransition`; verify tests for "Open a new card", "Skip straight to done", "Got it on an insight", and "Undo hide" pass.
- [ ] 2.2 Add `can_finish()` using the surface-state keys from design.md D2 (worksheet field ids, `revealed`); verify tests for "Submit with a missing required field" and the question reveal rule pass, and that `habit` check-ins never finish a card.
- [ ] 2.3 Add a grep test that `lifekit/cards/` contains no `score`, `grade`, or `correct` field names, to guard the "No scores" requirement; verify it passes.

## 3. Docs

- [ ] 3.1 Add a "Card types" section to `docs/arch/README.md` with the six-type table from proposal.md and a pointer to `card_types.toml`; verify the table renders in a Markdown preview.
- [ ] 3.2 Add `tests/test_card_types.py` to `docs/arch/testing.md` and update the test count in `AGENTS.md`; verify `uv run pytest tests/ -q` reports the new count with only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 1 to Done and archive this change after merge.
