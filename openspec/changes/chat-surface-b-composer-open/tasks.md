# Chat Surface b — Composer + Open Conversation — Tasks

- [ ] `app/chat/page.tsx` — add `selectedConvId` local state; render `<ChatView>` when non-null, `<MasterComposer>` when null; pass `onOpen` to `ConversationsList` <!-- id: 0 -->
- [ ] Add `frontend/src/components/ChatView.tsx` (`"use client"`) — header with title, `MessageList` + `ChatInput`, calls `useConversation(convId)`. No `← Feed` <!-- id: 1 -->
- [ ] Pass `pending={sending}` from `ChatView` into `MessageList` <!-- id: 2 -->
- [ ] Wire `MasterComposer` into the `/chat` empty state — `onSubmit` creates a conversation via `POST /api/conversations` and calls `setSelectedConvId` <!-- id: 3 -->
- [ ] `ConversationsList.tsx` — rows become `<button>` with `onClick={() => onOpen(id)}` <!-- id: 4 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; open/swap conversations; composer creates and opens; send behaves as today; both themes <!-- id: 5 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (KANBAN P2) <!-- id: 6 -->
- [ ] Update `docs/product/KANBAN.md` <!-- id: 7 -->
