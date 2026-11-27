# Spec — card-feed

## Purpose

Show the active cards of one book in reading order, start where the user left
off, and let the user like or dislike each card.

## ADDED Requirements

### Requirement: Feed contents

The feed SHALL list the book's cards that are not retired and not disliked,
sorted by position. A card with no state row MUST count as no reaction and
never responded.

#### Scenario: Disliked and retired cards left out
- **WHEN** a book has cards A, B, C, and D, B is disliked, and C has `retired_at` set
- **THEN** the feed lists A and D in position order

### Requirement: Start where you left off

With no cursor, the feed SHALL start at the active card with the highest
position among the cards the user responded to. A response is a reaction or a
comment. With no responses, the feed MUST start at the first active card.

#### Scenario: Start where you left off
- **WHEN** the user responded to the cards at positions 3 and 12, and the client requests with no cursor
- **THEN** the first card in the response is the card at position 12

#### Scenario: Furthest, not latest
- **WHEN** the user responded to position 12, then later commented on position 3
- **THEN** the feed still starts at position 12

#### Scenario: No responses yet
- **WHEN** the user has no responses
- **THEN** the first card in the response is the card with the lowest active position

### Requirement: Paging both ways

The feed SHALL return at most 20 cards per page. `next_cursor` MUST be the last
returned position when more cards follow, else null. `prev_cursor` MUST be the
first returned position when active cards come before it, else null.

#### Scenario: Second page
- **WHEN** a book has 45 active cards, the user has no responses, and the client requests `after=20`
- **THEN** the response holds positions 21–40 and `next_cursor` = 40

#### Scenario: Earlier page
- **WHEN** the client requests `before=30`
- **THEN** the response holds positions 10–29 in ascending order and `prev_cursor` = 10

### Requirement: Default book

With no `book_id`, the feed SHALL use the book whose cards changed most
recently. With no book that has cards, the response MUST hold `book` = null and
an empty list. An unknown `book_id` MUST return HTTP 404.

#### Scenario: No cards yet
- **WHEN** the database has no cards
- **THEN** the feed page shows "No cards yet. Run `lifekit ingest <file>`."

#### Scenario: Unknown book
- **WHEN** the client requests `book_id=nope`
- **THEN** the endpoint returns HTTP 404

### Requirement: Entry shape

Each feed entry SHALL hold `id`, `type`, `title`, `card_ui`, `position`,
`reaction`, and `comment_hint`. The response SHALL hold `book` (`id`, `title`),
`total` (active cards), `cards`, `prev_cursor`, and `next_cursor`.

#### Scenario: Entry shape
- **WHEN** the feed returns a `habit` card with no reaction
- **THEN** the entry has `reaction` = null and the `habit` comment hint from the type config

### Requirement: Card reactions

`PUT /api/cards/<id>/reaction` SHALL accept `like`, `dislike`, or null. It MUST
store the value, mark the card responded if it was not, and append a row to
`card_events`. Any other value MUST return HTTP 400; an unknown card, HTTP 404.

#### Scenario: Dislike and undo
- **WHEN** the user dislikes a card, then taps Undo
- **THEN** the card shows "Marked not useful · Undo" after the first tap, the card returns after Undo, and `card_events` holds two rows for it

#### Scenario: Bad reaction value
- **WHEN** the client sends `{"value": "love"}`
- **THEN** the endpoint returns HTTP 400 and stores nothing

### Requirement: User state survives the pipeline

Reactions and the responded mark SHALL live outside the `cards` table, keyed by
card id. A pipeline run MUST NOT change them.

#### Scenario: Reaction survives re-ingest
- **WHEN** the user likes a card and the cards stage runs again and makes the same card id
- **THEN** the card still shows the like

### Requirement: Card rendering

The feed page SHALL render each card's `card_ui` with the OpenUI renderer and
the card library. Code SHALL draw the reaction buttons outside the program.
Pressed buttons MUST pair color with a filled icon and set `aria-pressed`.

#### Scenario: Reactions outside the program
- **WHEN** a card renders
- **THEN** the like and dislike buttons sit below the rendered program and are not part of `card_ui`

### Requirement: One column with a header

The feed page SHALL show one centered column at every screen width. The header
SHALL show the book title and the active card count. A "Show earlier cards"
button MUST appear at the top when `prev_cursor` is not null.

#### Scenario: Header count
- **WHEN** the book has 142 active cards
- **THEN** the header shows "142 cards"

#### Scenario: Show earlier cards
- **WHEN** the feed opens at position 12 and the user taps "Show earlier cards"
- **THEN** positions 1–11 appear above, and the card at position 12 stays where it was on screen

### Requirement: Briefing removed

The briefing endpoints and components SHALL be removed.

#### Scenario: Old endpoint
- **WHEN** the client requests `/api/briefing/today`
- **THEN** the server returns HTTP 404
