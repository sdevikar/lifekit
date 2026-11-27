# Tasks — card-types-v1

## 1. Type config and content models

- [ ] 1.1 Create `lifekit/cards/__init__.py` and `lifekit/cards/card_types.toml` with the five entries (description, item_kinds, allowed_stances, source_label, comment_hint, coach_instruction) from design.md D1; verify `uv run python -c "import tomllib; print(sorted(tomllib.load(open('lifekit/cards/card_types.toml','rb'))))"` prints the five names.
- [ ] 1.2 Write `lifekit/cards/types.py`: the five Pydantic content models with the limits in the spec (title ≤ 80 chars, insight body ≤ 80 words, 1–12 steps, cadence enum, 0–3 follow-ups); verify with tests in 1.4.
- [ ] 1.3 Add the import-time check that TOML tables equal the model set, plus `CARD_TYPES`, `spec()`, `content_model()`, `card_type_for()`, `validate_card()`, `source_label()`; verify that removing one TOML table makes `python -c "import lifekit.cards.types"` raise.
- [ ] 1.4 Write `tests/test_card_types.py` covering every spec scenario; verify `uv run pytest tests/test_card_types.py -v` passes.
- [ ] 1.5 Add a grep test that `lifekit/cards/` contains no `score`, `grade`, or `correct` field names, to guard the "No scores" requirement; verify it passes.

## 2. Docs

- [ ] 2.1 Add a "Card types" section to `docs/arch/README.md` with the five-type table from proposal.md and a pointer to `card_types.toml`; verify the table renders in a Markdown preview.
- [ ] 2.2 Add `tests/test_card_types.py` to `docs/arch/testing.md` and update the test count in `AGENTS.md`; verify `uv run pytest tests/ -q` reports the new count with only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 1 to Done and archive this change after merge.
