# Spec — feed-only-ui

## Purpose

Make the feed the only screen. Remove the sidebar, the free chat, and the
journal placeholder, so that later slices build on a feed-only layout.

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

### Requirement: No chat buttons on the feed

The feed MUST NOT show a control that opens a chat page.

#### Scenario: No chat buttons
- **WHEN** the feed shows today's exercise, the resurfaced idea, and the fading ideas
- **THEN** no card shows a "Talk about" button

### Requirement: Free-chat API removed

The routes under `/api/conversations` SHALL be removed. A request to any of
them MUST return HTTP 404.

#### Scenario: Old API route
- **WHEN** the client sends `GET /api/conversations`
- **THEN** the server returns HTTP 404

### Requirement: Tables kept

The `conversations` and `messages` tables and their rows SHALL stay.

#### Scenario: Tables kept
- **WHEN** a database has 12 rows in `conversations` and 80 rows in `messages` before the change
- **THEN** it has the same rows after the server starts and runs `init_db()`
