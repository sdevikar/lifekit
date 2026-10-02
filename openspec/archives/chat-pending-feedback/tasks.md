# Chat Pending Feedback — Tasks

- [x] `useConversation.ts` — append the user message before the request resolves; filter it out by object identity if the POST fails; guard a second send while `sending` <!-- id: 0 -->
- [x] `MessageList.tsx` — accept `pending` and render a "Coach is thinking…" status row (`role="status"`, `aria-live="polite"`, dashed border, no timestamp) styled with the existing bubble geometry <!-- id: 1 -->
- [x] `ChatInput.tsx` — placeholder reads "Coach is thinking…" while disabled; button label explains the wait instead of a bare "Sending…"; add `aria-label` <!-- id: 2 -->
- [x] `app/c/[id]/page.tsx` — pass `pending={sending}` into `MessageList` <!-- id: 3 -->
- [x] Extend `frontend/test_useConversation.mjs` with a stubbed-failure case: the optimistic user message is gone after a rejected POST and the transcript matches the server <!-- id: 4 -->
- [x] Verify: `npm run build` + `npm run lint` (no new lint problems); `node --experimental-strip-types test_useConversation.mjs` green; `uv run pytest` no new failures <!-- id: 5 -->
- [ ] User eyeballs the pending row in the running app: message appears instantly, indicator shows, and vanishes on reply <!-- id: 6 -->
- [x] Update `docs/product/STATUS.md`, `docs/product/KANBAN.md`, and archive the spec under `openspec/archives/` <!-- id: 7 -->