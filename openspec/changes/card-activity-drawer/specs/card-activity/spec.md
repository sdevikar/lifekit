# Spec — card-activity

## Purpose

Keep what the user does in a card's drawer, move the card's status from what
the user does, and give each card one grounded conversation.

## ADDED Requirements

### Requirement: Save surface state

The drawer SHALL save the surface state of the open card 800 ms after the last
change. The server MUST store it per card and MUST refuse a state larger than
64 KB with HTTP 413.

#### Scenario: Draft survives a reload
- **WHEN** the user types "Draft text" into a reflect card's entry, waits one second, and reloads the page with the card open
- **THEN** the entry shows "Draft text"

#### Scenario: State too large
- **WHEN** the client sends a 70 KB state
- **THEN** the server returns HTTP 413 and keeps the previous state

### Requirement: Status from activity

Opening the drawer SHALL move a `new` card to `opened`. The first saved state
SHALL move an `opened` card to `in_progress`. Other statuses MUST NOT change on
open or on save.

#### Scenario: Open then type
- **WHEN** the user opens a `new` practice card and ticks step 1
- **THEN** the card is `in_progress`

#### Scenario: Reopen a done card
- **WHEN** the user opens a `done` card from a deep link
- **THEN** the card stays `done` and the drawer shows the saved state

### Requirement: Done action

The `MarkDone` action SHALL move the card to `done` when the card type's finish
rule allows it. When the rule refuses, the card MUST keep its status and the
drawer MUST name what is missing.

#### Scenario: Worksheet with a missing field
- **WHEN** the user taps "Submit" on a worksheet whose required field `health` is empty
- **THEN** the card stays `in_progress` and the drawer shows "Fill in: Health"

#### Scenario: Insight got it
- **WHEN** the user taps "Got it" on an `opened` insight card
- **THEN** the card is `done` and leaves the feed

### Requirement: Habit check-in

The `CheckIn` action SHALL log a `checkin` event for the card with today's
date, at most once per card per local day, and MUST NOT finish the card.

#### Scenario: Second check-in on one day
- **WHEN** the user taps the check-in twice on the same day
- **THEN** one `checkin` event exists for that day and the control shows "Checked in today"

### Requirement: One conversation per card

Each card SHALL have at most one conversation. Asking for a card's conversation
MUST return the existing one, or make it with the card's book id on first use.

#### Scenario: Reopen keeps the chat
- **WHEN** the user sends a message in a card's drawer, closes the drawer, and opens the same card again
- **THEN** the drawer shows the same conversation with that message

#### Scenario: Two requests at once
- **WHEN** two requests for a card's conversation arrive together on a card with none
- **THEN** both return the same conversation id

### Requirement: Card chat grounding

A reply in a card's conversation SHALL be built from the conversation's book,
the card's content and quote, the card's passage with the passage before and
after it, the first 2000 characters of the user's surface state, up to three
passages found with full-text search for the message, and the card type's coach
instruction.

#### Scenario: Grounded on the card's book
- **WHEN** the server pins book A and the user chats on a card of book B
- **THEN** the system prompt holds only passages of book B

#### Scenario: Coach sees the user's entry
- **WHEN** the user writes an entry on a reflect card and asks "What do you notice?"
- **THEN** the system prompt holds the entry text

### Requirement: Ask the coach from the surface

An `AskCoach` control SHALL send its prompt as a user message in the card's
conversation.

#### Scenario: Ask from an insight
- **WHEN** the user taps an AskCoach control with the prompt "How does this apply to my week?"
- **THEN** that text appears as the user's message in the card's conversation and a reply streams in

### Requirement: Card deep link

`/feed?card=<id>` SHALL open the feed with that card's drawer open. A recent
conversation that belongs to a card MUST link to that address.

#### Scenario: Recent conversation link
- **WHEN** the user taps a card's conversation in the sidebar
- **THEN** the feed opens with that card's drawer and its conversation

#### Scenario: Unknown card link
- **WHEN** the user opens `/feed?card=<unknown id>`
- **THEN** the feed shows "This card no longer exists." and no drawer
