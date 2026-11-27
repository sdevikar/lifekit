# Spec — item-extraction

## Purpose

Turn the body text of a book into a small set of typed items. Each item is
grounded in a verbatim quote, anchored to a passage, free of duplicates, and
judged useful before it can become a card.

## ADDED Requirements

### Requirement: Body sections only

The items stage SHALL read only sections of kind `body`. Sections of kind
`front` or `back` MUST produce no items and no model calls.

#### Scenario: Notes are skipped
- **WHEN** a book has a back-matter section "Notes" with 12 pages of text
- **THEN** the items stage makes no model call for "Notes" and stores no item from it

### Requirement: Windowed reading with overlap

The stage SHALL read each top-level body section, including its child sections,
in windows that start and end on passage boundaries, hold at most the configured
number of characters, and repeat the last passage of the previous window. A
single passage longer than the limit MUST form its own window.

#### Scenario: Exercise across a window edge
- **WHEN** an exercise's instructions start in the last passage of window 1
- **THEN** that passage is also the first passage of window 2, so the model sees the whole exercise in one window

### Requirement: Typed items

Each extracted item SHALL have a kind (`idea`, `rule`, `pitfall`, `term`,
`exercise`, `habit`, `prompt`, or `template`), a stance (`author_instructs` or
`author_states`), a title, a verbatim quote of at most 300 characters, and the
content fields of the card type that its kind maps to. An item whose content
fails the card type's validation MUST be stored with status `rejected_invalid`.

#### Scenario: Habit with cadence
- **WHEN** the text says "Every evening, write down the activities that energized you"
- **THEN** one item of kind `habit` with cadence `daily` and stance `author_instructs` is stored

#### Scenario: Exercise without steps
- **WHEN** the model returns an `exercise` item with an empty steps list
- **THEN** the item is stored with status `rejected_invalid` and the reason "steps: 1 to 10 items"

### Requirement: No activities from stories

The stage SHALL instruct the model to extract kinds `exercise`, `habit`,
`prompt`, and `template` only when the author tells the reader to do something.
An activity item with stance `author_states` MUST be stored with status
`rejected_invalid`.

#### Scenario: Anecdote is not an exercise
- **WHEN** the text tells how one person read poetry each week, with no instruction to the reader
- **THEN** no `exercise` or `habit` item with status `kept` comes from that passage

### Requirement: Quote grounding and passage anchor

Each item's quote SHALL be checked against its window text after whitespace and
punctuation normalization. A quote that is not found MUST give status
`rejected_ungrounded`. A found quote MUST be anchored to the id of the passage
where the quote starts.

#### Scenario: Quote across two passages
- **WHEN** a quote starts at the end of passage `dyl:4:7` and ends in `dyl:4:8`
- **THEN** the item is grounded and anchored to `dyl:4:7`

#### Scenario: Invented quote
- **WHEN** the model returns a quote that does not appear in the window
- **THEN** the item has status `rejected_ungrounded` and never becomes a card

### Requirement: Duplicate consolidation

After all windows of a top-level section are read, the stage SHALL ask the
model to group grounded items that describe the same thing. Then it SHALL do
the same once per card type across the whole book. A group MUST hold items of
one card type only. One item per group stays `kept`; the others get status
`merged` and point to the kept item. Invalid groups from the model MUST be
ignored.

#### Scenario: Repeated exercise in one chapter
- **WHEN** three windows of one chapter each return an "Odyssey Plans" exercise
- **THEN** one item is `kept` and two are `merged` into it

#### Scenario: Same topic, different type
- **WHEN** the model groups an `exercise` item with an `idea` item
- **THEN** the group is ignored and both items stay `kept`

#### Scenario: Recap in the conclusion
- **WHEN** the conclusion repeats the "Good Time Journal" habit from chapter 2
- **THEN** the book-level pass merges the two items and one stays `kept`

### Requirement: Usefulness judgement

Every `kept` item SHALL be judged against the usefulness rubric and get a
rating from 1 to 5, a one-sentence reason, and zero or more fail codes
(`generic`, `meta`, `story`, `fragment`). Items rated below the configured
threshold (default 4) MUST get status `rejected_not_useful`. These ratings are
internal pipeline data and MUST never reach the user interface.

#### Scenario: Meta statement rejected
- **WHEN** an item says "In this chapter we will look at how to get unstuck"
- **THEN** it gets fail code `meta`, a rating below 4, and status `rejected_not_useful`

#### Scenario: Specific rule kept
- **WHEN** an item says "If a problem is not actionable, it is a gravity problem: accept it and reframe"
- **THEN** it keeps status `kept`

### Requirement: Item records

Every item SHALL be stored with its book, the run that produced it, its section,
its passage anchor (if grounded), its kind and card type, stance, title, quote,
content, status, the reason for a rejection, and a key derived from the book,
card type, and normalized quote. A new items run MUST replace the book's earlier
items.

#### Scenario: Re-run replaces items
- **WHEN** the items stage runs twice for the same book
- **THEN** only the second run's items remain, and both runs stay in the run records

#### Scenario: Stable item key
- **WHEN** the same quote is extracted as the same card type in two runs
- **THEN** both items have the same key

### Requirement: Stage summary

The items stage SHALL report counts per status and per card type, and the number
of model calls, in its run record and in the ingest output.

#### Scenario: Summary line
- **WHEN** the items stage finishes
- **THEN** the output shows counts such as "kept 212 · merged 160 · not useful 95 · ungrounded 4 · invalid 7" and counts per card type
