# Proposal — card-generation

## Why

The user wants each card to be generative UI: the model writes the card in
OpenUI Lang, and the card has a button that opens its activity in the side
drawer. Today OpenUI renders only chat replies (`frontend/src/lib/openui.tsx`:
`Card`, `TextContent`, four charts), and the feed cards are fixed React
components (`ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`).

Generating UI while the user scrolls would be slow on a local 27B model and
could fail in front of the user. intent.md says "Generated UI is validated
before it is stored." So the cards and their surfaces are generated once, at
ingest time, checked by the OpenUI parser, and stored.

## What Changes

- Add a `cards` pipeline stage after `items`. For every `kept` item it makes
  one card. For each body chapter it also derives one `question` card from the
  highest-rated insight item (card-types-v1 D4).
- For each card, one model call writes two programs in OpenUI Lang: `card_ui`
  (the feed card) and `surface_ui` (the drawer surface). Content fields come
  from the item, so code owns the facts and the model owns the layout and
  wording.
- Validate both programs with the real OpenUI parser in a small Node script.
  Also check type rules, for example "the feed card has exactly one Open
  button" and "a worksheet surface has one input per worksheet field". On
  failure, retry twice with the errors in the prompt. After that the card is
  rejected and logged. There is no template fallback.
- Give each card a **stable UUID**: UUIDv5 of book id, card type, and the
  normalized quote. Re-running the pipeline keeps the ids, so the user's work
  stays attached. Cards that a re-run no longer produces are retired, not
  deleted.
- Skip the model call when the item content and the prompt are unchanged since
  the last run, unless `--force` is given.
- Add OpenUI components and actions for cards and surfaces in two new
  libraries next to the chat library:
  - Card library: `FeedCard` (root), `TextContent`, `Quote`, `SourceLabel`,
    `OpenButton` with the custom action `@OpenActivity()`.
  - Surface library: `Surface` (root), `TextContent`, `Quote`, `Checklist`,
    `TextArea`, `Scale`, `Choice`, `CheckIn`, `Reveal`, `AskCoach`, `DoneButton`
    with the custom actions `@MarkDone()` and `@CheckIn()`.
- Extend `frontend/scripts/gen_openui_prompt.ts` to write the card and surface
  prompts to Python, as it does today for chat.

## Capabilities

### New Capabilities

- `card-generation`: how kept items become stored cards with validated
  `card_ui` and `surface_ui`, stable ids, retirement, rejections, and reuse.
- `card-ui-library`: the OpenUI components and custom actions that cards and
  surfaces may use, and the state keys they write.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New: `lifekit/cards/generate.py`, `lifekit/cards/stage.py`,
  `lifekit/cards/prompts.py`, `lifekit/cards/validate.py`,
  `lifekit/cards/openui_prompts.py` and `lifekit/cards/openui_schemas.json`
  (both generated), `frontend/src/lib/openuiShared.tsx`,
  `frontend/src/lib/cardLibrary.tsx`, `frontend/src/lib/surfaceLibrary.tsx`,
  `frontend/scripts/validate_openui.mjs`, tables `cards` and `card_rejects`.
- Changed: `frontend/src/lib/openui.tsx` (shared parts move out),
  `frontend/scripts/gen_openui_prompt.ts`, `lifekit/ingest.py` (register
  `CardsStage`), `lifekit/db/schema.py`, `frontend/package.json` (raise
  `@openuidev/react-lang` from ^1.1.1 to ^1.2.0 if the installed version lacks
  `defineAction`; 1.2.0 exports it).
- Node is needed at ingest time to run the validator. The validator is plain
  JavaScript, so it needs no build step (design D2).
- Depends on: card-types-v1, item-extraction-v2.
- Model cost for `dyl`: one call per card (about 200–250 calls), run on the home
  workstation.
- Supersedes `openui-exercise-surfaces/`.
