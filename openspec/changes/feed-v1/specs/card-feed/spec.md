# Spec — card-feed

## Purpose

Show every active card of one book in reading order, let the user hide cards
that are not useful, and open a card's activity in the side drawer.

## ADDED Requirements

### Requirement: Feed contents

The feed SHALL list the book's cards that are not retired and whose status is
not `hidden` or `done`, sorted by position. A card with no state row MUST count
as status `new`.

#### Scenario: Done and hidden cards left out
- **WHEN** a book has cards A, B, C, and D, B is `done`, and C is `hidden`
- **THEN** the feed lists A and D in position order

#### Scenario: Retired card left out
- **WHEN** a card has `retired_at` set
- **THEN** the feed does not list it

### Requirement: Paging

The feed endpoint SHALL return at most 20 cards per page and a `next_cursor`
that is the last card's position, or null on the last page. A request with a
cursor MUST return only cards with a greater position.

#### Scenario: Second page
- **WHEN** a book has 45 active cards and the client requests with the cursor from the first page
- **THEN** the response holds cards 21–40 and a non-null `next_cursor`

### Requirement: Default book

With no `book_id`, the feed SHALL use the book whose cards were most recently
generated. With no book that has cards, the response MUST hold an empty list
and `book` = null.

#### Scenario: No cards yet
- **WHEN** the database has no cards
- **THEN** the feed page shows "No cards yet. Run `lifekit ingest <file>`."

#### Scenario: Unknown book
- **WHEN** the client requests `book_id=nope`
- **THEN** the endpoint returns HTTP 404

### Requirement: Card response fields

Each feed entry SHALL hold `id`, `type`, `title`, `card_ui`, `status`, and
`position`. It MUST NOT hold `surface_ui`, which the drawer loads only when it
opens.

#### Scenario: Entry shape
- **WHEN** the client reads a feed entry
- **THEN** it has exactly the keys id, type, title, card_ui, status, and position

### Requirement: Generated card rendering

The feed page SHALL render each entry's `card_ui` with the OpenUI renderer and
the card library. The `OpenActivity` action MUST open the drawer for that card.

#### Scenario: Open from the feed
- **WHEN** the user taps the Open button on a practice card
- **THEN** the drawer opens and shows that card's surface

### Requirement: Drawer surface

The drawer SHALL load the card's `surface_ui` and render it with the surface
library. On screens narrower than 768 px, the drawer MUST fill the screen and
show a back button that closes it.

#### Scenario: Phone view
- **WHEN** the user opens a card on a 390 px wide screen
- **THEN** the surface fills the screen and the back button returns to the same scroll position in the feed

### Requirement: Not useful

Every feed card SHALL have a "Not useful" control that the code draws, outside
the generated program. Using it MUST set the card's status to `hidden`, log a
`not_useful` event, remove the card from the feed, and show an Undo toast for 6
seconds. Undo MUST restore the previous status and log a `not_useful_undone`
event.

#### Scenario: Hide and undo
- **WHEN** the user taps "Not useful" on an `opened` card and then taps Undo
- **THEN** the card is back in the feed with status `opened`, and the event log holds `not_useful` then `not_useful_undone`

#### Scenario: Hidden card stays hidden after re-ingest
- **WHEN** the user hides card X and the cards stage runs again and produces X
- **THEN** X is still hidden

### Requirement: Header count

The feed header SHALL show the book title and the plain count of active cards,
such as "142 cards". It MUST NOT show streaks, scores, or progress bars.

#### Scenario: Header after a hide
- **WHEN** the feed shows "142 cards" and the user hides one card
- **THEN** the header shows "141 cards"

### Requirement: Old briefing removed

The endpoints `/api/briefing/today`, `/api/completions`, and `/api/idea-signals`
SHALL no longer exist.

#### Scenario: Old endpoint
- **WHEN** a client requests `/api/briefing/today`
- **THEN** the server returns HTTP 404
