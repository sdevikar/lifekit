# Chat Tab a — Conversation List — Tasks

- [ ] Add `frontend/src/hooks/useConversations.ts` — `GET /api/conversations`, exposes `{ conversations, loading, error, refresh }`, refetches when the Chat tab activates <!-- id: 0 -->
- [ ] Repurpose `components/feed/ConversationsList.tsx` — drop the `lk-card` wrapper and `Coaching` badge, keep the row markup and `onOpen(id)`, add an empty state. It is unreferenced since `e6da69c`, so this revives dead code instead of adding a near-copy <!-- id: 1 -->
- [ ] `Sidebar.tsx` — Chat panel renders a `Chat` heading, the list, and `New chat` (POST `seed_kind: "composer"`, then `onOpen` with the new id so the list shows it without a reload) <!-- id: 2 -->
- [ ] Resolve the header collision: the collapse toggle is already top-right (`Sidebar.tsx:87`), so the `+` goes elsewhere — after the heading, on hover/focus of the row <!-- id: 3 -->
- [ ] Keyboard path for `New chat`: `aria-label`, reachable by tab, visible on `focus-visible` as well as `hover` <!-- id: 4 -->
- [ ] Wire `onOpen` to a no-op with a `TODO` naming slice b — the panel is a surface here, not yet a destination <!-- id: 5 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; list matches `GET /api/conversations`; empty state; `New chat` appears without reload; both themes; feed unchanged <!-- id: 6 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 7 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 8 -->