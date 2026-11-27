# Spec — card-generation

## Purpose

Turn every kept item of a book into a stored card whose OpenUI program is built
by code, derive one self-check question card per chapter, and keep cards under
a stable id across pipeline runs.

## ADDED Requirements

### Requirement: One card per kept item

The cards stage SHALL make one card for each item with status `kept`, using the
item's card type, title, quote, passage anchor, stance, and content. Items with
any other status MUST produce no card.

#### Scenario: Kept practice item
- **WHEN** the book has a `kept` item of kind `exercise`
- **THEN** one `practice` card with that item's title, quote, and steps is stored

#### Scenario: Rejected item
- **WHEN** an item has status `rejected_not_useful`
- **THEN** no card is made for it

### Requirement: Card program built by code

The stage SHALL build each card's `card_ui` in OpenUI Lang from a fixed layout
for the card's type, using only the card library. No model call SHALL write any
part of a card program. Facts in the program (title, quote, steps, author's
answer) MUST come from the card's content.

#### Scenario: Steps match the content
- **WHEN** a practice card has 4 steps in its content
- **THEN** its program has one `Steps` component with those 4 steps in order

### Requirement: Programs parse

Every program a layout can produce SHALL parse with the OpenUI parser against
the card library with no errors and with `FeedCard` as the root, including text
that holds quotes, backslashes, newlines, and non-ASCII characters.

#### Scenario: Quote with escapes
- **WHEN** an insight card's quote holds a double quote, a backslash, and an em dash
- **THEN** its program parses with no errors and shows the quote unchanged

### Requirement: Derived question cards

For each top-level body section that has at least one kept insight item, the
stage SHALL make one `question` card from the highest-rated such item. The
model MUST write only the question and the author's answer. The card MUST have
stance `inferred` and the quote of its source item.

#### Scenario: Question for a chapter
- **WHEN** chapter 3 has kept insight items rated 5, 4, and 4
- **THEN** one question card is made from the item rated 5, labelled "LifeKit question"

### Requirement: Question failure without fallback

A question whose content still fails validation after two retries SHALL produce
no card. The stage MUST record the item key and the last errors in the run's
stats and MUST NOT store a template-made question in its place.

#### Scenario: Question fails three times
- **WHEN** all three attempts for chapter 5's question fail validation
- **THEN** chapter 5 has no question card, and the run stats list the item key with the errors

### Requirement: Stable card id

A card's id SHALL be the UUIDv5 of the book id, the card type, and the
normalized quote. Running the stage again on the same items MUST give the same
ids, and existing user state for those ids MUST be kept.

#### Scenario: Re-run keeps ids
- **WHEN** the cards stage runs twice on the same items
- **THEN** every card has the same id in both runs

### Requirement: Retire missing cards

When a run no longer produces a card id that exists from an earlier run, the
stage SHALL mark that card retired instead of deleting it. A retired card that a
later run produces again MUST become active again with its user state.

#### Scenario: Item merged away
- **WHEN** a re-run merges the item behind card X into another item
- **THEN** card X is retired, and its reactions and comments stay in the database

### Requirement: Reuse unchanged questions

The stage SHALL skip the model call for a question card whose source content
hash and prompt hash equal those of its stored version, unless forced. A forced
run MUST regenerate every question.

#### Scenario: Second run without changes
- **WHEN** the cards stage runs twice with no item or prompt change
- **THEN** the second run makes no model calls and reports every question as reused

### Requirement: Reading-order position

Each card SHALL have a position that sorts cards in the book's reading order.
A derived question card MUST sort after the last other card of its chapter.

#### Scenario: Feed order
- **WHEN** cards from chapters 1 and 2 are sorted by position
- **THEN** every chapter 1 card comes before every chapter 2 card, and the chapter 1 question card is the last chapter 1 card

### Requirement: Stage summary

The cards stage SHALL report counts of cards made, retired, and collided,
counts per card type, questions made, reused, and failed, and the number of
model calls, in its run record and in the ingest output.

#### Scenario: Summary line
- **WHEN** the cards stage finishes
- **THEN** the output shows a line such as "cards 196 · retired 3 · questions 16 (reused 0, failed 1) · model calls 19"
