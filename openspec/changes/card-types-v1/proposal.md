# Proposal — card-types-v1

## Why

A card is the unit the user sees in the feed. Today the feed has two hard-coded
shapes: "exercise" and "idea". Every exercise gets the same chat surface, and
every idea gets the same "remembered?" signal. A journal prompt, a daily habit,
and a self-assessment form need different surfaces, so the feed cannot help the
user do them.

The other five v1 slices (extraction, card generation, feed, drawer) all need
one agreed list of card types. This change defines that list. It is the
contract the other slices build on, so it comes first.

## What Changes

- Define six card types. Each type has a purpose, content fields, a surface in
  the drawer, a "done" action, and a coach instruction.

  | Type | What it is | Example (Designing Your Life) | Surface in the drawer | Done action |
  |------|------------|-------------------------------|-----------------------|-------------|
  | `insight` | An idea, rule of thumb, pitfall, or term worth keeping | "Gravity problems: you can't solve a problem you can't act on — accept it and reframe." | The quote, a short explanation, 2–3 suggested questions for the coach | "Got it" |
  | `practice` | A one-off exercise the author tells the reader to do | "Write your Workview in about 250 words." | Step checklist, notes box | "Done" |
  | `habit` | A recurring behavior the author tells the reader to repeat | "Each evening, log your activities in the Good Time Journal." | Check-in button with an optional note, plain check-in count | "Stop tracking" |
  | `reflect` | A journal prompt | "What gives you energy at work, and what drains it?" | Autosaved text editor, 0–3 follow-up prompts | "Save and finish" |
  | `worksheet` | A structured template or self-assessment | "Rate Health, Work, Play, Love from 0 to full." | Form with text, scale, and choice fields | "Submit" |
  | `question` | A self-check question about an idea | "Why does the book call some problems 'gravity problems'?" | Answer box, then "Show the author's answer" reveals answer and quote | "Done" (after reveal) |

- Define which extracted item kinds map to which card type (see the spec).
- Define stance labels that stay visible on every card: "From the book" for
  things the author says or instructs, and "LifeKit question" for derived
  question cards. Activities (`practice`, `habit`, `reflect`, `worksheet`)
  come only from passages where the author instructs the reader. This removes
  anecdote-based exercises such as "Weekly Poetry Reading in the Body".
- Define card status: `new` → `opened` → `in_progress` → `done`, plus `hidden`
  ("Not useful"). Statuses are self-declared. There are no scores.
- Questions are allowed, but never marked. This replaces the old ban on "quiz
  framing" with the rule in intent.md: "Questions are self-checks."
- Store the type list in one config file, `lifekit/cards/card_types.toml`, and
  load it through one Python module. Extraction, generation, the API, and the
  coach prompt read it from there.

## Capabilities

### New Capabilities

- `card-types`: the set of card types, their content fields, surfaces, done
  actions, status model, stance labels, and the item-kind → card-type mapping.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New: `lifekit/cards/__init__.py`, `lifekit/cards/types.py`,
  `lifekit/cards/card_types.toml`, `tests/test_card_types.py`.
- No database, API, or UI change in this slice. Later slices consume it.
- Supersedes `exercise-type-system/` and the five `exercise-surface-*`
  proposals (recorded in `docs/product/KANBAN.md`).
- Intent alignment: no scores (questions are unscored), grounded in the book
  (every type carries a quote), deterministic runtime (status rules live in
  code, not in the model).
