# Spec — card-library

## Purpose

Define the OpenUI components that card programs may use and what each one
shows, so that every card renders through the same renderer as coach replies.

## ADDED Requirements

### Requirement: Card library

The frontend SHALL define a card library with root `FeedCard` next to the
existing chat library. It MUST hold `FeedCard(type, children)`,
`SourceLabel(label, locator)`, `TextContent(text, size)`,
`Quote(text, locator)`, `Steps(items)`, and `AuthorAnswer(text, quote,
locator)`, and no actions or buttons.

#### Scenario: Schema lists only card components
- **WHEN** the card library schema is generated
- **THEN** it lists exactly FeedCard, SourceLabel, TextContent, Quote, Steps, and AuthorAnswer

### Requirement: Shared text components

`TextContent` and `Quote` SHALL live in one shared file used by both the card
library and the chat library, so a quote in a coach reply looks the same as a
quote on a card.

#### Scenario: Coach quotes the book
- **WHEN** a coach reply program holds `Quote("…", "p. 41")`
- **THEN** it renders with the same component as a card quote

### Requirement: Card frame owned by code

`FeedCard` SHALL draw the frame, padding, and a type badge for the given card
type. The badge text MUST come from the type, not from the program's children.

#### Scenario: Badge for a habit
- **WHEN** a program has root `FeedCard("habit", [...])`
- **THEN** the card shows the "Habit" badge

### Requirement: Author's answer after the user answers

`AuthorAnswer` SHALL hide the author's answer and quote while the host says the
user has not commented on the card, and show the hint "Post your answer to see
the author's answer." After the user's first comment it MUST show the answer
and the quote with no right or wrong mark.

#### Scenario: Before the first comment
- **WHEN** a question card renders and the user has no comment on it
- **THEN** the author's answer is hidden and the hint shows

#### Scenario: After the first comment
- **WHEN** the user posts a comment on the question card
- **THEN** the author's answer and the quote show, with no correctness mark

### Requirement: Theme tokens only

All new components SHALL use the existing `--lk-*` design tokens and no colour
literals, and MUST work in light and dark themes.

#### Scenario: No colour literals
- **WHEN** the new library files are searched for hex colours, `rgb(`, and `hsl(`
- **THEN** no match is found
