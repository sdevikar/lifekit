# Spec — card-types

## Purpose

Define the fixed set of card types that LifeKit shows in the feed, what content
each type carries, what a comment on it means, and how extracted book items map
to it.

## ADDED Requirements

### Requirement: Five card types

The system SHALL support exactly five card types: `insight`, `practice`,
`habit`, `reflect`, and `question`. Any other type value MUST be rejected when a
card is created or loaded.

#### Scenario: Known type is accepted
- **WHEN** a card with type `habit` is validated
- **THEN** validation passes

#### Scenario: Unknown type is rejected
- **WHEN** a card with type `worksheet` is validated
- **THEN** validation fails with an error that names the five allowed types

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
- `insight`: body (at most 80 words), why_it_matters (one sentence).
- `practice`: purpose, 1–12 steps.
- `habit`: behavior, cadence (`daily` or `weekly`), how_to_start.
- `reflect`: prompt, 0–3 follow-up prompts.
- `question`: question, author_answer.

#### Scenario: Practice with no steps is rejected
- **WHEN** a `practice` card has an empty steps list
- **THEN** validation fails with a "steps: 1 to 12 items" error

#### Scenario: Habit with an unknown cadence is rejected
- **WHEN** a `habit` card has cadence `hourly`
- **THEN** validation fails

### Requirement: Item kind maps to one card type

The system SHALL map item kinds to card types as follows: `idea`, `rule`,
`pitfall`, and `term` → `insight`; `exercise` and `template` → `practice`;
`habit` → `habit`; `prompt` → `reflect`. A `question` card SHALL be derived
from an `insight`-mapped item and never extracted directly.

#### Scenario: Pitfall becomes an insight
- **WHEN** the mapping receives item kind `pitfall`
- **THEN** it returns card type `insight`

#### Scenario: Template becomes a practice card
- **WHEN** the mapping receives item kind `template`
- **THEN** it returns card type `practice`

#### Scenario: Unknown item kind has no card type
- **WHEN** the mapping receives item kind `story`
- **THEN** it returns no card type, and the item produces no card

### Requirement: Activities need an author instruction

Card types `practice`, `habit`, and `reflect` SHALL require stance
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

### Requirement: Comment hint and coach instruction per type

Every card type SHALL define a comment box hint and a coach instruction. The
coach prompt for a card's comments MUST hold that type's coach instruction.

#### Scenario: Coach instruction comes from the type config
- **WHEN** the coach prompt for a comment on a `reflect` card is built
- **THEN** it contains the `reflect` coach instruction text from the type config

#### Scenario: Hint for a habit
- **WHEN** the comment hint for a `habit` card is requested
- **THEN** the system returns the `habit` hint from the type config, such as "How did it go today?"

### Requirement: No scores

No card type SHALL compute, store, or show a score, grade, percentage, or
correctness mark. A `question` card MUST show the author's answer without
judging the user's answer.

#### Scenario: Question config has no scoring fields
- **WHEN** the `question` content model is inspected
- **THEN** it has only the fields `question` and `author_answer`

### Requirement: Single source of truth for types

All card type definitions SHALL come from one configuration file. Extraction,
card generation, the feed API, and the coach prompt MUST read the type list from
that file, so that adding a type later changes one file plus its tests.

#### Scenario: Types listed from config
- **WHEN** `CARD_TYPES` is read
- **THEN** it equals the table names in `card_types.toml`, in file order
