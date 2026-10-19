# Chat Surface a — Route + Conversation List — Tasks

- [ ] `Sidebar.tsx` — remove the `TRAILING_PLUS` entry for `chat`; the Chat nav row becomes a link to `/chat` via `router.push("/chat")` <!-- id: 0 -->
- [ ] Add `frontend/src/app/chat/page.tsx` (`"use client"`) — two-pane layout: `ConversationsList` left, empty state right. Owns `useConversations` <!-- id: 1 -->
- [ ] Add `frontend/src/hooks/useConversations.ts` — `GET /api/conversations`, exposes `{ conversations, loading, error }`. No `refresh` <!-- id: 2 -->
- [ ] Repurpose `components/feed/ConversationsList.tsx` — drop `lk-card` wrapper, `Coaching` badge; add empty state; rows non-interactive (no `<button>`, no `onOpen`) <!-- id: 3 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; Chat nav row navigates to `/chat`; list matches API; empty state; rows not focusable; no `+`; both themes; feed unchanged <!-- id: 4 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 5 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 6 -->
