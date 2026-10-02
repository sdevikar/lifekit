# Chat Tab a — Conversation List — Tasks

- [ ] Add `frontend/src/hooks/useConversations.ts` — `GET /api/conversations`, exposes `{ conversations, loading, error, refresh }`, refetches when the Chat tab activates <!-- id: 0 -->
- [ ] Repurpose `components/feed/ConversationsList.tsx` — drop the `lk-card` wrapper and `Coaching` badge, keep the row markup and `onOpen(id)`, add an empty state. It is unreferenced since `e6da69c`, so this revives dead code instead of adding a near-copy <!-- id: 1 -->
- [ ] `Sidebar.tsx` — the Chat tab's section renders the conversation list below the nav rows <!-- id: 2 -->
- [ ] `New chat` is the trailing `+` on the Chat nav row (the hover/focus slot comes from `sidebar-nav-model`): POST `seed_kind: "composer"`, then `onOpen` the new id so the list shows it without a reload. Keyboard-operable with an `aria-label` <!-- id: 3 -->
- [ ] Wire `onOpen` to a no-op with a `TODO` naming slice b — the panel is a surface here, not yet a destination <!-- id: 4 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; list matches `GET /api/conversations`; empty state; `New chat` appears without reload; both themes; feed unchanged <!-- id: 5 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 6 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 7 -->