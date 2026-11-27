# Spec — card-generation

## Purpose

Turn every kept item of a book into a stored card whose feed UI and drawer
surface are written by the model in OpenUI Lang, validated before storage, and
kept under a stable id across pipeline runs.

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

### Requirement: Derived question cards

For each top-level body section that has at least one kept insight item, the
stage SHALL make one `question` card from the highest-rated such item. The
question card MUST have stance `inferred`, its own question text, and an
author's answer built from the item's content and quote.

#### Scenario: Question for a chapter
- **WHEN** chapter 3 has kept insight items rated 5, 4, and 4
- **THEN** one question card is made from the item rated 5, labelled "LifeKit question"

### Requirement: Generated card and surface UI

For each card, the model SHALL write a feed card program and a drawer surface
program in OpenUI Lang, using only the card library and surface library. Facts
(title, quote, steps, worksheet fields, author's answer) MUST come from the
card's content, not from new model text.

#### Scenario: Steps match the content
- **WHEN** a practice card has 4 steps in its content
- **THEN** its surface program has one Checklist with those 4 steps in order

### Requirement: Validation before storage

Both programs SHALL be parsed with the OpenUI parser against their library and
MUST have no parse errors, the correct root, and only known components. The
feed card MUST hold exactly one Open button. The surface MUST hold the parts its
card type needs (see card-ui-library). A failed program MUST be retried at most
twice with the errors in the prompt.

#### Scenario: Unknown component retried
- **WHEN** the model's surface uses a component named `Slider`
- **THEN** the stage retries with the error "unknown component Slider" in the prompt

#### Scenario: Two Open buttons
- **WHEN** a feed card program holds two Open buttons
- **THEN** validation fails

### Requirement: Rejection without fallback

A card that still fails validation after the retries SHALL be rejected: it is
not stored as a card, and a rejection record with the item, the run, and the
last errors MUST be stored. The stage MUST NOT store a template-made card in its
place.

#### Scenario: Rejected after three tries
- **WHEN** all three attempts for an item fail validation
- **THEN** the item has a rejection record, no card exists for it, and the stage summary counts one rejection

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
- **THEN** card X is retired, and its user state and conversation stay in the database

### Requirement: Reuse unchanged cards

The stage SHALL skip the model call for a card whose content and prompt hash
equal those of its stored version, unless forced. A forced run MUST regenerate
every card.

#### Scenario: Second run without changes
- **WHEN** the cards stage runs twice with no item or prompt change
- **THEN** the second run makes no model calls and reports all cards as reused

### Requirement: Reading-order position

Each card SHALL have a position that sorts cards in the book's reading order.
A derived question card MUST sort after the last other card of its chapter.

#### Scenario: Feed order
- **WHEN** cards from chapters 1 and 2 are sorted by position
- **THEN** every chapter 1 card comes before every chapter 2 card, and the chapter 1 question card is the last chapter 1 card

### Requirement: Stage summary

The cards stage SHALL report counts of cards made, reused, retired, and
rejected, counts per card type, and the number of model calls, in its run
record and in the ingest output.

#### Scenario: Summary line
- **WHEN** the cards stage finishes
- **THEN** the output shows a line such as "made 180 · reused 40 · retired 3 · rejected 5"
