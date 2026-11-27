# Proposal — item-extraction-v2

## Why

The extractor finds things, but not useful things. Evidence from the dogfood DB
(`dogfood/lifekit.db`, book `dyl`):

- 875 key ideas and 144 exercises for one book. The user cannot act on 875 ideas.
- The same exercise appears many times: Odyssey Plans about 8 times (ids 46–56),
  Good Time Journal about 10 times (ids 24–36), the dashboard gauges about
  7 times (ids 4–13). Cause: sectioned extraction (ASSUMPTIONS A22) sends
  3000–4000-character pieces, each piece reports the exercise again, and the
  reducer merges only identical normalized titles
  (`lifekit/reduce/reducer.py:normalize_title`).
- Some exercises come from stories, not instructions. Exercise #138 "Weekly
  Poetry Reading in the Body" retells what one person did.
- Ideas are untyped strings. A rule of thumb, a pitfall, and a definition look
  the same, so nothing can choose the right card for them.
- The only quality gate is grounding (is the quote real?) and a 10% judge
  sample of grounding. Nothing checks whether an item is worth a card.

v1 needs a small set of typed, grounded, de-duplicated items, and a number
that says how many of them are useful.

## What Changes

- Extract **typed items** from body sections only (front and back matter are
  skipped, from book-model-v1). Item kinds: `idea`, `rule`, `pitfall`, `term`,
  `exercise`, `habit`, `prompt`, `template`. Each item has a stance
  (`author_instructs` or `author_states`), a title, a verbatim quote, and the
  content fields of its card type (from card-types-v1).
- Read each chapter in **windows cut at passage boundaries** with one passage
  of overlap. This keeps requests small enough for the home GPU over Tailscale
  (A22) and fixes the missing-overlap issue D4.
- **Anchor** every quote to the passage that contains it. Items with a quote
  that is not in the text are rejected, not stored as cards.
- **Consolidate duplicates with the model**, in two passes: once per chapter,
  then once per book for each card type. The model groups items that describe
  the same thing; code checks the groups and keeps one item per group.
- **Judge usefulness** of every remaining item against a written rubric, in
  batches. Only items that pass go on to card generation. Rejected items stay
  in the table with their reason, so the eval can see them.
- **Golden set**: `lifekit eval usefulness label <book_id>` shows a sample of
  items one by one and records the user's y/n verdict in
  `evals/usefulness/<book_id>/labels.jsonl`.
  `lifekit eval usefulness report <book_id>` writes precision and recall of the
  judge against those labels to `report.md`. Proposed v1 gate: precision ≥ 0.8.
- Register the `items` stage in `lifekit ingest`.
- The old tables `exercises` and `key_ideas` and the old
  extract/reduce/validate commands stay as they are, frozen. Nothing new reads
  or writes them.

## After this slice

What you will see in the app: nothing new. The app looks the same as after
slice 0.

What you can do on the command line:
- Run `lifekit ingest --book <book_id> --from items` on the home workstation. It
  extracts typed items from the body chapters, merges duplicates, and judges
  usefulness. This is a long model run.
- Run `lifekit eval usefulness label <book_id>` to mark a sample of items
  useful or not useful, one by one.
- Run `lifekit eval usefulness report <book_id>` to see how well the judge
  agrees with you (precision and recall).

Decide when you pick up this slice:
- The precision target. The draft says at least 0.8.

What is not there yet (expected, not a bug):
- Items are not cards yet, and the feed does not show them. Slices 4 and 5 do
  that.

## Capabilities

### New Capabilities

- `item-extraction`: how body sections become typed, grounded, consolidated,
  usefulness-judged items.
- `usefulness-eval`: the golden-set labelling command, the report, and the gate.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New: `lifekit/items/` (`extract.py`, `anchor.py`, `consolidate.py`,
  `judge.py`, `stage.py`, `prompts.py`, `items.toml`),
  `lifekit/evals/usefulness.py`, table `items`, `evals/usefulness/<book_id>/`.
- Changed: `lifekit/ingest.py` (register `ItemsStage`), `lifekit/__main__.py`
  (`eval usefulness` subcommands), `lifekit/db/schema.py`.
- Reused: `lifekit.llm` providers (`chat_json_schema`), `normalize_ws` from
  `lifekit/validate/validator.py`, card content models from card-types-v1.
- Depends on: card-types-v1 (content models, item-kind mapping), book-model-v1
  (sections, passages, runs, ingest command).
- Model runs go to the home workstation's Ollama (`qwen3.8:27b-q8_0`), per
  intent.md. Expected cost for `dyl`: about 100 window calls, about 25
  consolidation calls, and about 40 judge calls.
- Known issue D4 closes (overlap). D3 and H3 stay with the frozen old pipeline.
