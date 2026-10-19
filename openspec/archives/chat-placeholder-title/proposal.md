# Chat Placeholder Title — Proposal

## Why

Conversations are created eagerly (on "Talk about this" or composer open)
but often never used, leaving empty rows in the DB. Meanwhile, titles like
"Idea: card" are unhelpful. DeepTutor's pattern: create with a sentinel
title, replace it with a real one when content arrives.

## What Changes

### 1. Server — `lifekit/serve/server.py`

- `create_conversation`: always use `"New conversation"` as the title.
  Ignore any client-sent title for now.
- `post_message`: after persisting the first user message, auto-generate
  a title from the message text (first 60 chars, trimmed) and PATCH the
  conversation. Only on the first message (when `message_count === 1`).

### 2. Frontend — no changes

The sidebar already renders whatever title the server returns. The
sentinel "New conversation" is fine as a placeholder until the first
message replaces it.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: conversation titles are meaningful — either
  generated from the card content (existing fix) or from the first user
  message (this change). Empty conversations show "New conversation"
  until their first message.

## Not In Scope

- Filtering empty conversations from the sidebar — they show as
  "New conversation" which is acceptable.
- LLM-generated titles — first-message truncation is good enough.
- Migration of existing "Idea: card" titles — they'll be replaced
  naturally as users continue those conversations.

## Done Criteria

1. `uv run pytest tests/ -v` passes (no new failures beyond `test_split_dyl_pdf`).
2. Creating a conversation from a card uses the card text as title (already done).
3. Creating a conversation from the composer uses "New conversation" as title.
4. Sending the first message in a composer conversation replaces the title with the first 60 chars of the message.
5. The sidebar shows the updated title without a manual refresh.
6. `docs/product/STATUS.md` updated in the same change.
