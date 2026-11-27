# Proposal — card-comments

## Why

In v1, a comment is the only way to act on a card (ROADMAP D2). A journal
entry, a habit check-in, a note on an exercise, and an answer to a question are
all comments. The coach replies to every comment (ROADMAP D4). After feed-v1,
the feed shows cards and reactions, but nothing the user writes is kept.

The old chat code had three problems that this slice must not carry over.
feed-only-ui (slice 0) deletes that code; it stays in git history:
- `post_message` deletes the user's message when the model call fails
  (`lifekit/serve/server.py`, `post_message` → `generate`). intent.md says the
  user's words are never lost.
- `post_message` grounds every reply on `app.config["book_id"]`, not on the
  conversation's own `book_id`.
- `_coach_messages` reads the thread history after the user's message is
  stored, then appends that message again. The model sees it twice.

The old grounding searched `book_chunks`, then fell back to whole chapters
with term counting. book-model-v1 adds `passages` and `passages_fts`, which are
the better source.

## What Changes

- One thread per card. New column `conversations.card_id` with a unique index.
  The thread is made on the first comment.
- `GET /api/cards/<id>/comments` returns the thread.
- `POST /api/cards/<id>/comments` stores the comment, marks the card responded
  (feed-v1 `card_state.responded_at`), and streams the coach reply over SSE.
- When the model call fails, the comment stays. The reply slot shows "The coach
  could not reply. Retry". `POST /api/cards/<id>/comments/retry` makes a reply
  for the last comment that has none.
- New column `messages.reaction`. `PUT /api/messages/<id>/reaction` sets like,
  dislike, or none on a coach reply only.
- The coach reply fits the comment: a few warm words and at most one question
  for a journal entry or check-in, a real answer for a direct question. Each
  type's `coach_instruction` goes into the prompt.
- Grounding uses the card's book, the card's content and quote, the card's
  passage and its neighbors, the top 3 `passages_fts` hits for the comment, and
  the thread so far. It lives in a new `lifekit/serve/coach.py`.
- Under each feed card: the last 2 messages, "View all N comments" that expands
  in place, and a comment box. The box grows as you type and takes markdown.
  The hint comes from the card type. Post with the button or Ctrl/Cmd+Enter.
- User comments render as markdown. Coach replies render through the OpenUI
  chat library and stream in with "Coach is writing…".
- A question card shows the author's answer after the user's first comment
  (ROADMAP D8).
- The feed entry gains `comment_count` and the last 2 messages, so the feed
  needs no extra request per card.
- Remove the `python -m lifekit.store` ingest path. The `book_chunks` and
  `chapters` tables stay, frozen.

## After this slice

What you will see in the app (v1 is complete):
- A comment box under each card. The hint fits the card type, for example
  "Write your entry…" on a reflect card.
- The coach replies to every comment. The reply streams in after "Coach is
  writing…".
- If the model is off, your comment stays, and the reply slot shows "The coach
  could not reply." with a Retry button.
- Like and dislike on each coach reply.
- Each card shows its last 2 messages and "View all N comments".
- A question card shows the author's answer after your first comment.

Removed:
- The old `python -m lifekit.store` ingest. Use `lifekit ingest`.

Not in v1 (expected, not a bug):
- Posts without a card (the "+" button) and worksheet cards come in v2.
- Sharing a card comes in v4. Spaced repetition is parked.

Decide when this slice is done:
- The dogfood exit check (ROADMAP → Dogfood exit check), before the 14 days of
  dogfood start.

## Capabilities

### New Capabilities

- `card-comments`: the thread under each card, the coach reply, the failure
  path, reactions on coach replies, and how the reply is grounded.

### Modified Capabilities

None. `openspec/specs/` holds no capabilities yet. feed-v1's `card-feed`
gains two entry fields; the delta is listed in design.md D5.

## Impact

- Backend: new `lifekit/serve/coach.py` (prompt and grounding),
  `lifekit/serve/comments.py` (thread, store, retry, reaction),
  `lifekit/serve/feed.py` (entry fields), `lifekit/serve/server.py` (routes),
  `lifekit/db/schema.py` (migration: two columns, one index).
- Removed: `lifekit/store/__main__.py` ingest entry and its `book_chunks`
  writer, and the Makefile `ingest` target's old command.
- Frontend: new `frontend/src/components/feed/CommentThread.tsx`,
  `CommentBox.tsx`, `frontend/src/hooks/useComments.ts`; `FeedCardView.tsx`
  (thread slot, `CardContext.answered`).
- Depends on: feed-v1, card-generation (cards, chat library `Quote`),
  book-model-v1 (`passages`, `passages_fts`), card-types-v1
  (`comment_hint`, `coach_instruction`).
- feed-only-ui (slice 0) already removed the `/api/conversations*` routes, the
  chat pages, and `MessageList.tsx`.
