# Tasks — card-comments

## 1. Backend

- [ ] 1.1 Add the migration (D1) to `lifekit/db/schema.py`; verify `init_db()` runs twice on a fresh DB and on a dogfood copy, and two get-or-create calls for one card return the same thread.
- [ ] 1.2 Write `lifekit/serve/coach.py` (D3); verify tests for "Type instruction in the prompt", "Grounded in the card's book", "Neighbor passages", "Missing passage", "No duplicate message", and the 6,000-character cap pass in `tests/test_coach_prompt.py`.
- [ ] 1.3 Write `lifekit/serve/comments.py` and the routes (D2, D4); verify tests for "Comment saved first", "Comment kept on failure", "Retry", "Nothing to retry", "Empty comment", "Too long", "React to a reply", and "No reaction on own comment" pass with a stub provider.
- [ ] 1.4 Add the entry fields (D5) to `feed.py`; verify "Feed shows recent comments" passes.
- [ ] 1.5 Remove the old grounding and ingest path (D7); verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.

## 2. Frontend

- [ ] 2.1 Write `useComments.ts`, `CommentThread.tsx`, and `CommentBox.tsx` (D6) and fill the `FeedCardView` thread slot; verify `npx next build` and `npx eslint src` pass.
- [ ] 2.2 Set `CardContext.answered` from the thread; verify "Author's answer after the first comment" in the browser.
- [ ] 2.3 Write a `node --experimental-strip-types` test for `useComments` (the old `useConversation` test in git history shows the pattern); verify one post against a running `lifekit ui` yields exactly one user bubble and one coach bubble.
- [ ] 2.4 Run `lifekit ui` and ask the human to check: a journal entry on a reflect card, a check-in on a habit card, a question card reveal, "View all N comments", Retry with Ollama stopped, markdown in a comment, and the phone view.

## 3. Docs

- [ ] 3.1 Update `docs/arch/README.md` (comment flow, D2 diagram, endpoints), `AGENTS.md` (Architecture: comments, coach grounding), and `docs/arch/testing.md`; verify the docs name no removed function.

## Workflow follow-up

- Move the KANBAN row for slice 6 to Done and archive this change after merge.
