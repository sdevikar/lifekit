# Tasks — card-generation

## 1. OpenUI version and libraries

- [ ] 1.1 Run `npm ls @openuidev/react-lang` in `frontend/`; if the version lacks `defineAction`, raise the range to `^1.2.0` and run `npm install`; verify `node -e "import('@openuidev/react-lang').then(m => console.log(typeof m.defineAction))"` prints `function` from `frontend/`.
- [ ] 1.2 Move `TextContent` into `frontend/src/lib/openuiShared.tsx`, add `Quote`, and keep the chat library working; verify `npx next build` passes and a chat reply still renders (ask the human to look).
- [ ] 1.3 Write `frontend/src/lib/cardLibrary.tsx` (`FeedCard`, `SourceLabel`, `OpenButton`, action `OpenActivity`) with `--lk-*` tokens only; verify `npx eslint src/lib` passes and the colour-literal grep from the spec finds nothing.
- [ ] 1.4 Write `frontend/src/lib/surfaceLibrary.tsx` (`Surface`, `Checklist`, `TextArea`, `Scale`, `Choice`, `CheckIn`, `Reveal`, `AskCoach`, `DoneButton`, actions `MarkDone` and `CheckIn`) using `useStateField`; verify `npx next build` passes.
- [ ] 1.5 Add a dev-only page `frontend/src/app/dev/surfaces/page.tsx` that renders one hand-written program per card type with `onStateUpdate` printing state; verify by hand the scenarios "Checklist state", "Restore state", "Reveal blocked until the user answers", and "Reveal sets state" (ask the human to look), then delete the page before the commit.

## 2. Generated artifacts and validator

- [ ] 2.1 Extend `frontend/scripts/gen_openui_prompt.ts` to write `lifekit/cards/openui_prompts.py` and `lifekit/cards/openui_schemas.json` with a source-hash header (D5); find the command that runs it today and add it to `AGENTS.md`; verify the three artifacts regenerate and the test "Card prompt lists only card components" passes.
- [ ] 2.2 Write `frontend/scripts/validate_openui.mjs` (D2); verify `echo '{"id":"1","library":"card","program":"root = FeedCard([OpenButton(\"Try it\", @OpenActivity())])"}' | node frontend/scripts/validate_openui.mjs` prints a line with `"errors":[]` and the actual program syntax follows the generated prompt.
- [ ] 2.3 Write `lifekit/cards/validate.py` (Node process plus type rules); verify tests for "Unknown component retried" (errors surfaced), "Two Open buttons", "Worksheet missing a field", and one valid program per card type pass in `tests/test_card_validate.py` (tests skip when `node` is absent).
- [ ] 2.4 Add the staleness test for the generated artifacts; verify it fails after touching a library file without regenerating and passes after regenerating.

## 3. Cards stage

- [ ] 3.1 Add `cards` and `card_rejects` tables (D4) to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy.
- [ ] 3.2 Write `lifekit/cards/generate.py`: ids (D3), positions, question-source choice, content hash, and the prompt in `lifekit/cards/prompts.py` (D1); verify tests for "Kept practice item", "Rejected item", "Question for a chapter", "Re-run keeps ids", and "Feed order" pass with a stub provider.
- [ ] 3.3 Write `CardsStage` in `lifekit/cards/stage.py` with retries, rejection records, reuse, retire and un-retire, `--force`, and the summary, and register it in `lifekit/ingest.py`; verify tests for "Steps match the content", "Rejected after three tries", "Item merged away", "Second run without changes", and "Summary line" pass.
- [ ] 3.4 Run `lifekit ingest --book dyl --from cards` on the workstation against a dogfood copy; verify the run is `ok`, rejections are at most 10% of cards, and paste the summary line into the change's handoff.

## 4. Docs

- [ ] 4.1 Add the D6 diagram, the two libraries with their components, and the validator to `docs/arch/README.md`; add the new tests to `docs/arch/testing.md` and update the test count; verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## Workflow follow-up

- Move the KANBAN row for slice 4 to Done and archive this change after merge.
