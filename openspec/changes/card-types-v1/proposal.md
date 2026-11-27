# Proposal — card-types-v1

## Why

A card is the unit the user sees in the feed. Today the feed has two hard-coded
shapes, "exercise" and "idea" (`lifekit/serve/server.py`: `_exercise_dict`,
`_resurfaced_idea`). A journal prompt, a daily habit, and a self-check question
need different content on the card, a different hint in the comment box, and a
different coach behavior.

The other v1 slices (extraction, card generation, feed, comments) all need one
agreed list of card types. This change defines that list. It is the contract
the other slices build on, so it comes first.

In v1 the only way to act on a card is a comment (ROADMAP D2). So a card type
defines what the card shows and what a comment on it means. It does not define
a surface, a done action, or a status.

## What Changes

- Define five card types. Each type has a purpose, content fields, a comment box
  hint, and a coach instruction.

  | Type | What it is | Example (Designing Your Life) | What a comment is | Comment box hint |
  |------|------------|-------------------------------|-------------------|------------------|
  | `insight` | An idea, rule of thumb, pitfall, or term worth keeping | "Gravity problems: you can't solve a problem you can't act on — accept it and reframe." | A thought or a question | "What do you make of this?" |
  | `practice` | A one-off exercise, or a form the author gives, as steps | "Write your Workview in about 250 words." | Notes or results | "How did it go?" |
  | `habit` | A recurring behavior the author tells the reader to repeat | "Each evening, log your activities in the Good Time Journal." | A check-in | "How did it go today?" |
  | `reflect` | A journal prompt | "What gives you energy at work, and what drains it?" | The journal entry | "Write your entry…" |
  | `question` | A self-check question about an idea | "Why does the book call some problems 'gravity problems'?" | The user's answer | "Your answer…" |

- Map extracted item kinds to card types. A book "template" (a form or
  self-assessment) becomes a `practice` card whose steps are the form's fields
  (ROADMAP D7). The `worksheet` type waits for v2.
- Define stance labels that stay visible on every card: "From the book" for
  things the author says or instructs, and "LifeKit question" for derived
  question cards. Activities (`practice`, `habit`, `reflect`) come only from
  passages where the author instructs the reader. This removes anecdote-based
  exercises such as "Weekly Poetry Reading in the Body".
- Questions are allowed but never marked. The question card shows the author's
  answer after the user's first comment (ROADMAP D8).
- Store the type list in one config file, `lifekit/cards/card_types.toml`, and
  load it through one Python module. Extraction, generation, the feed API, and
  the coach prompt read it from there.

## After this slice

What you will see in the app: nothing new. The app looks the same as after
slice 0.

What exists after this slice:
- `lifekit/cards/card_types.toml` lists the five card types, with the comment
  hint and the coach instruction for each type.
- One Python module loads that file. Tests check it.

What is not there yet (expected, not a bug):
- Nothing in the app reads the card types yet. Extraction (slice 3), card
  generation (slice 4), the feed (slice 5), and the coach (slice 6) use them.

## Capabilities

### New Capabilities

- `card-types`: the set of card types, their content fields, comment box hints,
  coach instructions, stance labels, and the item-kind → card-type mapping.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet.

## Impact

- New: `lifekit/cards/__init__.py`, `lifekit/cards/types.py`,
  `lifekit/cards/card_types.toml`, `tests/test_card_types.py`.
- No database, API, or UI change in this slice. Later slices consume it.
- Supersedes `exercise-type-system/` and the five `exercise-surface-*`
  proposals (recorded in `docs/product/KANBAN.md`).
- Intent alignment: no scores (questions are unscored), grounded in the book
  (every type carries a quote), simple beats complete (no status model).
