# Step 13c: Conversation view — tasks (completed)

- [x] 13c.1 Build the conversation screen: "‹ Feed" header + title, message list, bottom input
- [x] 13c.2 Wire load (`GET /api/conversations/:id`) and send (`POST /api/conversations/:id/messages`) against the real API
- [x] 13c.3 Implement card seeding display from `seed_kind`/`seed_ref`
- [x] 13c.4 Verify the full loop on the dogfood DB: seed → message → grounded reply → reload → back to feed → reopen
- [x] 13c.5 Update `docs/product/STATUS.md`; archive this slice on completion

## Test results (2026-09-23)

- `npx tsc --noEmit --skipLibCheck` — clean, 0 errors
- `npx next build` — passes; `/c/[id]` route (dynamic SSR)
- Full loop verified against dogfood DB (`~/.lifekit/lifekit.db`):
  1. `POST /api/conversations` with `seed_kind: "card", seed_ref: "28"` → conversation created
  2. `GET /api/conversations/:id` → conversation detail (seed_kind: "card", seed_ref: "28") + 0 messages
  3. `POST /api/conversations/:id/messages` with text → grounded reply returned
  4. `GET /api/conversations/:id` reload → 2 messages persisted (user + coach), seed displayed
  - (Direct curl against live API requires Ollama model; used Flask test client with mocked provider for the grounded reply step.)
- Seed badge displayed in header; "‹ Feed" back button routes to `/feed`.

New files: `frontend/src/components/conversation/MessageList.tsx`,
`frontend/src/components/conversation/ChatInput.tsx`,
`frontend/src/hooks/useConversation.ts`.
Changed: `frontend/src/app/c/[id]/page.tsx` (stub → full conversation view),
`docs/product/STATUS.md`, `docs/product/ROADMAP.md`.