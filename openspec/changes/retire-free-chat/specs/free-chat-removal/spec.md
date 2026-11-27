# Spec — free-chat-removal

## Purpose

Remove the free chat, the sidebar, and the journal placeholder, so the feed is
the only screen and a card comment is the only way to talk to the coach.

## ADDED Requirements

### Requirement: Old pages redirect to the feed

The paths `/chat`, `/chat/<id>`, `/c/<id>`, and `/journal` SHALL redirect to
`/feed` with a temporary redirect.

#### Scenario: Old chat link
- **WHEN** the browser opens `/chat/3f2a`
- **THEN** it lands on `/feed`

#### Scenario: Old journal link
- **WHEN** the browser opens `/journal`
- **THEN** it lands on `/feed`

### Requirement: No sidebar

The app layout SHALL render the page with no sidebar, tab bar, or
recent-conversations list.

#### Scenario: Feed has no sidebar
- **WHEN** the feed loads on a desktop browser
- **THEN** the page shows only the feed column and its header

### Requirement: Free-chat API removed

The routes under `/api/conversations` SHALL be removed. A request to any of
them MUST return HTTP 404.

#### Scenario: Old API route
- **WHEN** the client sends `GET /api/conversations`
- **THEN** the server returns HTTP 404

### Requirement: Card threads kept

The `conversations` and `messages` tables and their rows SHALL stay. Card
threads MUST keep working.

#### Scenario: Card threads kept
- **WHEN** a card has a thread with 4 messages before the change
- **THEN** the feed shows "View all 4 comments" under that card after the change
