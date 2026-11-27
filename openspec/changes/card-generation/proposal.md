# Proposal — card-generation

## Why

The feed needs stored cards. Each card must render through OpenUI, because
everything LifeKit shows goes through one OpenUI renderer (ROADMAP D6). Today
OpenUI renders only chat replies (`frontend/src/lib/openui.tsx`: `Card`,
`TextContent`, four charts), and the feed cards are fixed React components
(`ExerciseCard.tsx`, `ResurfacedIdeaCard.tsx`).

In v1, **code** writes each card's OpenUI program from the card's content. In
v3, the model will write it. Storing the program now means v3 changes only who
writes it, not the table, the API, or the renderer. Code-built programs in v1
avoid invalid model output, about 200–250 model calls per book, and a
validation and rejection path at ingest (ROADMAP D6, ASSUMPTIONS A27).

Nothing is generated while the user scrolls. intent.md: "Generated UI is
checked before anyone sees it."

## What Changes

- Add a `cards` pipeline stage after `items`. For every `kept` item it makes
  one card. For each body chapter it also derives one `question` card from the
  highest-rated insight item (card-types-v1 D4).
- Build each card's `card_ui` (OpenUI Lang) in Python from a fixed layout per
  card type, using a new card library. No model writes card UI in v1.
- The only model calls in this stage write the question and the author's
  answer for each derived question card (about one per chapter). A question
  that still fails validation after two retries gets no card, and the stage
  records the failure in the run's stats. There is no template fallback.
- Give each card a **stable UUID**: UUIDv5 of book id, card type, and the
  normalized quote. Re-running the pipeline keeps the ids, so the user's
  comments and reactions stay attached. Cards that a re-run no longer produces
  are retired, not deleted.
- Reuse a stored question when its source item and prompt are unchanged, unless
  `--force` is given.
- Add a card library next to the chat library: `FeedCard` (root),
  `SourceLabel`, `TextContent`, `Quote`, `Steps`, and `AuthorAnswer`.
  `TextContent` and `Quote` move to a shared file, so coach replies can quote
  the book too.
- A test parses every layout's output with the real OpenUI parser, through a
  small Node script. Node is needed only for tests, not at ingest.

## Capabilities

### New Capabilities

- `card-generation`: how kept items become stored cards with code-built
  `card_ui`, derived question cards, stable ids, retirement, and reuse.
- `card-library`: the OpenUI components that card programs may use, and what
  each one shows.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New: `lifekit/cards/generate.py` (ids, positions, question choice),
  `lifekit/cards/render.py` (layouts per type), `lifekit/cards/stage.py`,
  `lifekit/cards/prompts.py` (question prompt),
  `lifekit/cards/openui_card_schema.json` (generated),
  `frontend/src/lib/openuiShared.tsx`, `frontend/src/lib/cardLibrary.tsx`,
  `frontend/scripts/validate_openui.mjs`, table `cards`.
- Changed: `frontend/src/lib/openui.tsx` (shared parts move out; chat library
  gains `Quote`), `frontend/scripts/gen_openui_prompt.ts` (also writes the card
  schema), `lifekit/ingest.py` (register `CardsStage`), `lifekit/db/schema.py`,
  and `frontend/package.json` only if the installed `@openuidev/react-lang`
  lacks `createParser`.
- Depends on: card-types-v1, item-extraction-v2.
- Model cost for `dyl`: about 17 calls (one per body chapter), run on the home
  workstation.
- Supersedes `openui-exercise-surfaces/`.
