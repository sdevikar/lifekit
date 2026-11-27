# Spec — card-comments

## Purpose

Keep a thread of comments under each card, reply to every comment with a
grounded coach reply, never lose what the user wrote, and let the user react
to coach replies.

## ADDED Requirements

### Requirement: One thread per card

Each card SHALL have at most one thread. The thread MUST be made on the first
comment and tied to the card by `conversations.card_id`, with the card's
`book_id`.

#### Scenario: Two quick posts on a new card
- **WHEN** two comments on a card with no thread arrive at the same time
- **THEN** both land in one thread

### Requirement: Comment saved first

The server SHALL store the user's comment and mark the card responded before
it calls the model. The first event of the stream MUST carry the stored
comment with its id.

#### Scenario: Comment saved first
- **WHEN** the user posts "Did step 2 today." on a practice card
- **THEN** the thread holds that comment before the first model chunk is sent, and `card_state.responded_at` is set

### Requirement: The user's words are never lost

A failed model call SHALL NOT delete or hide the user's comment. The stream
MUST end with an error event, and the thread MUST offer Retry. Retry SHALL
reply to the last user comment that has no reply.

#### Scenario: Comment kept on failure
- **WHEN** the provider raises an error during the reply
- **THEN** the comment stays in the thread, and the UI shows "The coach could not reply." with a Retry button

#### Scenario: Retry
- **WHEN** the user taps Retry after a failure and the provider works
- **THEN** one coach reply is stored after the comment, and the comment is not stored again

#### Scenario: Nothing to retry
- **WHEN** retry is called and every user comment has a reply
- **THEN** the endpoint returns HTTP 409

### Requirement: Comment limits

Comment text SHALL be trimmed. Empty text MUST return HTTP 400. Text longer
than 8,000 characters MUST return HTTP 413. An unknown card MUST return HTTP
404.

#### Scenario: Empty comment
- **WHEN** the client posts `{"text": "   "}`
- **THEN** the endpoint returns HTTP 400 and stores nothing

#### Scenario: Too long
- **WHEN** the client posts 8,001 characters
- **THEN** the endpoint returns HTTP 413 and stores nothing

### Requirement: Coach replies to every comment

Every stored comment SHALL get one coach reply request. The prompt MUST hold
the coach rules and the card type's `coach_instruction`. The rules MUST ask for
a reply that fits the comment and MUST forbid grading the user.

#### Scenario: Type instruction in the prompt
- **WHEN** the prompt for a comment on a `reflect` card is built
- **THEN** the system message contains the `reflect` coach instruction from the type config

### Requirement: Grounding

The prompt SHALL use the card's own book. It MUST hold the card's content and
quote, the card's passage and its neighbors, and up to 3 `passages_fts` hits
for the comment. The context block MUST stay within 6,000 characters.

#### Scenario: Grounded in the card's book
- **WHEN** the server runs with a pinned book `dyl` and the user comments on a card from book `atomic`
- **THEN** every passage in the prompt comes from `atomic`

#### Scenario: Neighbor passages
- **WHEN** the card's passage has `ord` 7 in its section
- **THEN** the prompt holds the passages with `ord` 6, 7, and 8 of that section

#### Scenario: Missing passage
- **WHEN** the card's `passage_id` no longer exists
- **THEN** the prompt holds the card's quote, and the request succeeds

### Requirement: Thread history once

The prompt SHALL hold the thread oldest first, read after the comment is
stored. No message MUST appear twice.

#### Scenario: No duplicate message
- **WHEN** the prompt for the comment "Why does this matter?" is built
- **THEN** that text appears exactly once among the prompt's messages

### Requirement: Reactions on coach replies

`PUT /api/messages/<id>/reaction` SHALL set `like`, `dislike`, or null on a
coach reply. A user comment MUST return HTTP 400. An unknown id MUST return
HTTP 404.

#### Scenario: React to a reply
- **WHEN** the user dislikes a coach reply
- **THEN** `messages.reaction` is `dislike` for that reply, and the dislike button shows pressed

#### Scenario: No reaction on own comment
- **WHEN** the client sends a reaction for a user comment
- **THEN** the endpoint returns HTTP 400

### Requirement: Thread under the card

Under each feed card the page SHALL show the last 2 messages and, when there
are more, "View all N comments", which expands in place. The feed entry MUST
carry `comment_count`, `recent`, and `answered`.

#### Scenario: Feed shows recent comments
- **WHEN** a card's thread holds 5 messages
- **THEN** the entry has `comment_count` = 5 and `recent` holds the last 2, oldest first, and the page shows "View all 5 comments"

### Requirement: Comment box

The comment box SHALL be a growing plain text box with the card type's
`comment_hint` as placeholder. Ctrl/Cmd+Enter MUST post. The text MUST stay in
the box until the server confirms the stored comment.

#### Scenario: Post fails before storing
- **WHEN** the network drops before the server confirms the comment
- **THEN** the text is still in the box

### Requirement: Rendering

User comments SHALL render as markdown. Coach replies SHALL render through the
OpenUI renderer and the chat library. A reply in progress MUST show "Coach is
writing…" until its first chunk, and exactly one coach bubble per reply.

#### Scenario: Markdown in a comment
- **WHEN** the user posts "**Done** with:\n- step 1\n- step 2"
- **THEN** the comment shows bold text and a two-item list

#### Scenario: One bubble per reply
- **WHEN** a reply streams in 40 chunks
- **THEN** the thread shows one coach bubble during and after the stream

### Requirement: Author's answer after the first comment

A question card SHALL show the author's answer once its thread holds a user
comment. It MUST open without a page reload and MUST NOT mark the user's answer
right or wrong.

#### Scenario: Author's answer after the first comment
- **WHEN** the user posts an answer on a question card
- **THEN** the card shows the author's answer and the quote, with no score or mark

### Requirement: Old grounding removed

`_retrieve_passages`, `_search_chapters`, and the `python -m lifekit.store`
ingest path SHALL be removed. Coach grounding MUST read only `passages` and
`passages_fts`.

#### Scenario: No old search
- **WHEN** the code base is searched for `_search_chapters`
- **THEN** no match is found
