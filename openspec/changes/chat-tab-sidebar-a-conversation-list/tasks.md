# Chat Tab a — Conversation List — Tasks

- [ ] Add `frontend/src/hooks/useConversations.ts` — `GET /api/conversations`, exposes `{ conversations, loading, error }`. No `refresh` and no "refetch on tab activate": the panel is behind an `activeTab === "chat"` conditional (`Sidebar.tsx:81`), so it unmounts on tab change and a plain mount-effect already refetches <!-- id: 0 -->
- [ ] Repurpose `components/feed/ConversationsList.tsx` — drop the `lk-card` wrapper, the `Coaching` badge, and the `onOpen` prop; add an empty state. It is unreferenced since `e6da69c`, so this revives dead code instead of adding a near-copy <!-- id: 1 -->
- [ ] Rows render as non-interactive content, not `<button>` with a dead `onClick` — no pointer cursor, not focusable. Slice b re-adds `onOpen` and wraps them in `<button>` <!-- id: 2 -->
- [ ] `Sidebar.tsx` — the Chat tab's section renders the conversation list below the nav rows <!-- id: 3 -->
- [ ] `New chat` is the trailing `+` on the Chat nav row (the hover/focus slot comes from `sidebar-nav-model`): POST `seed_kind: "composer"`, append to the list so it shows without a reload. Keyboard-operable with an `aria-label` <!-- id: 4 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; list matches `GET /api/conversations`; empty state; `New chat` appears without reload; rows not focusable and show no pointer cursor; both themes; feed unchanged <!-- id: 5 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 6 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 7 -->