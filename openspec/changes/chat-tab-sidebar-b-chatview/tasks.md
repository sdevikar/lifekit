# Chat Tab b — ChatView + Selection — Tasks

- [ ] `TabContext.tsx` — add `selectedConvId` / `setSelectedConvId` to the existing context value. Not a second `ChatContext`: the parent proposal offers both, and two providers for two adjacent values is worse <!-- id: 0 -->
- [ ] Add `frontend/src/components/ChatView.tsx` (`"use client"`) — header with conversation title, `MessageList` + `ChatInput`, calling `useConversation(selectedConvId)`. No `← Feed` button <!-- id: 1 -->
- [ ] Pass `pending={sending}` from `ChatView` into `MessageList` — that prop exists so this wiring is not invented here <!-- id: 2 -->
- [ ] `TabContent.tsx` — render `<ChatView />` for `activeTab === "chat"` instead of `Coming soon.`; journal and settings keep their placeholder <!-- id: 3 -->
- [ ] `Sidebar.tsx` — wire the `onOpen` handler from slice a to `setSelectedConvId(id)`; delete the `TODO` <!-- id: 4 -->
- [ ] Empty state for `selectedConvId === null` — not a blank area, not `Coming soon.` <!-- id: 5 -->
- [ ] Leave `app/c/[id]/page.tsx` untouched — it is still the only working route into a conversation until slice c <!-- id: 6 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; open, swap between conversations with no stale transcript, empty state, send still behaves as today, both themes; `/c/[id]` still works <!-- id: 7 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 8 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 9 -->