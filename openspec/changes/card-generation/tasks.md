# Tasks — card-generation

## 1. OpenUI libraries

- [ ] 1.1 Run `npm ls @openuidev/react-lang` in `frontend/`; if the version lacks `createParser`, raise the range to `^1.2.0` and run `npm install`; verify `node -e "import('@openuidev/react-lang').then(m => console.log(typeof m.createParser))"` prints `function` from `frontend/`.
- [ ] 1.2 Move `TextContent` into `frontend/src/lib/openuiShared.tsx`, add `Quote`, and add `Quote` to the chat library; verify `npx next build` passes and a chat reply still renders (ask the human to look).
- [ ] 1.3 Write `frontend/src/lib/cardLibrary.tsx` (`FeedCard`, `SourceLabel`, `Steps`, `AuthorAnswer`, `CardContext`) with `--lk-*` tokens only and the ROADMAP D15 rules; verify `npx eslint src/lib` passes and the colour-literal grep from the spec finds nothing.

## 2. Generated artifact and parse check

- [ ] 2.1 Extend `frontend/scripts/gen_openui_prompt.ts` to write `lifekit/cards/openui_card_schema.json` with a source-hash header (D4); find the command that runs it today and add it to `AGENTS.md`; verify both artifacts regenerate.
- [ ] 2.2 Add the hash-header test; verify it fails after touching a library file without regenerating and passes after regenerating.
- [ ] 2.3 Write `frontend/scripts/validate_openui.mjs` (D2); verify `echo '{"id":"1","program":"root = FeedCard(\"insight\", [])"}' | node frontend/scripts/validate_openui.mjs` prints a line with `"errors":[]`.

## 3. Cards stage

- [ ] 3.1 Add the `cards` table (D6) to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy.
- [ ] 3.2 Write `lifekit/cards/render.py` (D1) and `tests/test_card_render.py` (D2); verify every type's sample and the escaping samples parse with no errors, and the test skips cleanly with `PATH` stripped of `node`.
- [ ] 3.3 Write `lifekit/cards/generate.py`: ids (D3), positions, question-source choice, content hash, and the question prompt in `lifekit/cards/prompts.py` (D5); verify tests for "Kept practice item", "Rejected item", "Question for a chapter", "Re-run keeps ids", and "Feed order" pass with a stub provider.
- [ ] 3.4 Write `CardsStage` in `lifekit/cards/stage.py` with question retries, failure records, reuse, retire and un-retire, `--force`, and the summary, and register it in `lifekit/ingest.py`; verify tests for "Steps match the content", "Question fails three times", "Item merged away", "Second run without changes", and "Summary line" pass.
- [ ] 3.5 Run `lifekit ingest --book dyl --from cards` on the workstation against a dogfood copy; verify the run is `ok` and paste the summary line into the change's handoff.

## 4. Docs

- [ ] 4.1 Add the D7 diagram, the card library, and the parse check to `docs/arch/README.md`; add the new tests to `docs/arch/testing.md` and update the test count; verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 4 to Done and archive this change after merge.
