# Spec — card-types

## Purpose

Define the fixed set of card types that LifeKit shows in the feed, what content
each type carries, which surface it opens, how it is marked done, and how
extracted book items map to it.

## ADDED Requirements

### Requirement: Six card types

The system SHALL support exactly six card types: `insight`, `practice`,
`habit`, `reflect`, `worksheet`, and `question`. Any other type value MUST be
rejected when a card is created or loaded.

#### Scenario: Known type is accepted
- **WHEN** a card with type `habit` is validated
- **THEN** validation passes

#### Scenario: Unknown type is rejected
- **WHEN** a card with type `quiz` is validated
- **THEN** validation fails with an error that names the six allowed types

### Requirement: Common card fields

Every card SHALL carry a title of at most 80 characters, a verbatim quote from
the book, a reference to the passage that holds the quote, and a stance. The
stance MUST be one of `author_instructs`, `author_states`, or `inferred`.

#### Scenario: Card without a quote is rejected
- **WHEN** an `insight` card with an empty quote is validated
- **THEN** validation fails with a "quote required" error

#### Scenario: Long title is rejected
- **WHEN** a card title has 81 characters
- **THEN** validation fails with a "title too long" error

### Requirement: Type-specific content fields

Each type SHALL require its own content fields:
- `insight`: body (at most 80 words), why_it_matters (one sentence), 2–3 suggested coach questions.
- `practice`: purpose, 1–10 steps.
- `habit`: behavior, cadence (`daily` or `weekly`), how_to_start.
- `reflect`: prompt, 0–3 follow-up prompts.
- `worksheet`: instructions, 1–12 fields.
- `question`: question, author_answer.

#### Scenario: Practice with no steps is rejected
- **WHEN** a `practice` card has an empty steps list
- **THEN** validation fails with a "steps: 1 to 10 items" error

#### Scenario: Habit with an unknown cadence is rejected
- **WHEN** a `habit` card has cadence `hourly`
- **THEN** validation fails

### Requirement: Worksheet field kinds

A worksheet field SHALL have a stable id (lowercase letters, digits, and
underscores), a label, a `required` flag, and a kind of `text`, `scale`, or
`choice`. A `scale` field MUST have integer min < max and at most 11 steps. A
`choice` field MUST have 2–8 options.

#### Scenario: Scale with min equal to max is rejected
- **WHEN** a worksheet field has kind `scale`, min 5, and max 5
- **THEN** validation fails

#### Scenario: Duplicate field ids are rejected
- **WHEN** two worksheet fields share the id `health`
- **THEN** validation fails with a "duplicate field id" error

### Requirement: Item kind maps to one card type

The system SHALL map item kinds to card types as follows: `idea`, `rule`,
`pitfall`, and `term` → `insight`; `exercise` → `practice`; `habit` → `habit`;
`prompt` → `reflect`; `template` → `worksheet`. A `question` card SHALL be
derived from an `insight`-mapped item and never extracted directly.

#### Scenario: Pitfall becomes an insight
- **WHEN** the mapping receives item kind `pitfall`
- **THEN** it returns card type `insight`

#### Scenario: Unknown item kind has no card type
- **WHEN** the mapping receives item kind `story`
- **THEN** it returns no card type, and the item produces no card

### Requirement: Activities need an author instruction

Card types `practice`, `habit`, `reflect`, and `worksheet` SHALL require stance
`author_instructs`. A `question` card SHALL have stance `inferred`. An
`insight` card SHALL have stance `author_states` or `author_instructs`.

#### Scenario: Inferred practice is rejected
- **WHEN** a `practice` card has stance `inferred`
- **THEN** validation fails with an "activities need an author instruction" error

#### Scenario: Question is always inferred
- **WHEN** a `question` card has stance `author_states`
- **THEN** validation fails

### Requirement: Visible source label

Every card type SHALL define a source label shown on the card. Cards with stance
`author_instructs` or `author_states` MUST show "From the book". Cards with
stance `inferred` MUST show "LifeKit question".

#### Scenario: Label for a derived question
- **WHEN** the label for a `question` card is requested
- **THEN** the system returns "LifeKit question"

### Requirement: Card status model

A card SHALL have one status: `new`, `opened`, `in_progress`, `done`, or
`hidden`. Allowed transitions are new → opened, opened → in_progress, opened →
done, in_progress → done, any status → hidden, and hidden → the status before
hiding. Every other transition MUST be rejected. The user sets `done` and `hidden`; the system never sets them.

#### Scenario: Open a new card
- **WHEN** a `new` card moves to `opened`
- **THEN** the transition is allowed

#### Scenario: Skip straight to done
- **WHEN** a `new` card moves to `done`
- **THEN** the transition is rejected, because a card is done only after the user opens it

#### Scenario: Got it on an insight
- **WHEN** an `opened` insight card moves to `done`
- **THEN** the transition is allowed

#### Scenario: Undo hide
- **WHEN** a card that was `in_progress` is hidden and then unhidden
- **THEN** its status is `in_progress` again

### Requirement: Done action per type

Each type SHALL define one done action with a fixed label: `insight` "Got it",
`practice` "Done", `habit` "Stop tracking", `reflect` "Save and finish",
`worksheet` "Submit", `question` "Done". The `worksheet` done action MUST be
refused while a required field is empty. The `question` done action MUST be
refused until the author's answer is revealed.

#### Scenario: Submit with a missing required field
- **WHEN** the user submits a worksheet whose required field `health` is empty
- **THEN** the card stays `in_progress` and the response names the field `health`

#### Scenario: Habit check-ins do not finish the card
- **WHEN** the user checks in on a `habit` card five times
- **THEN** the card stays `in_progress`

### Requirement: No scores

No card type SHALL compute, store, or show a score, grade, percentage, or
correctness mark. A `question` card MUST show the user's answer next to the
author's answer without judging it.

#### Scenario: Answer revealed without a judgement
- **WHEN** the user reveals the author's answer on a `question` card
- **THEN** the drawer shows both answers and the quote, and no "correct" or "wrong" mark

### Requirement: Single source of truth for types

All card type definitions SHALL come from one configuration file. Extraction,
card generation, the feed API, and the coach prompt MUST read the type list from
that file, so that adding a type later changes one file plus its tests.

#### Scenario: Coach instruction comes from the type config
- **WHEN** the coach prompt for a `reflect` card is built
- **THEN** it contains the `reflect` coach instruction text from the type config
