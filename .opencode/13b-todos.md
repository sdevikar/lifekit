# Step 13b Tasks

- [x] 13b.1 Scaffold Next.js app (App Router, TS, Tailwind) in frontend/ + /api rewrites
- [x] 13b.2 Build 7 feed components (Today header, stage strip, exercise card, resurfaced-idea card, fading-ideas card, conversations list, master composer)
- [x] 13b.3 Wire Mark done + Still with me actions to API endpoints
- [x] 13b.4 Wire conversations list (reopen) + composer (create → /c/[id] stub)
- [x] 13b.5 Visual pass against the mock (layout, spacing, theme; no quiz framing)
- [x] 13b.6 Update STATUS.md + archive slice
- [x] Run lint/build/typecheck to verify

## Step 13c Tasks
- [ ] 13c.1 Build conversation screen: "‹ Feed" header + title, message list, bottom input
- [ ] 13c.2 Wire load (GET /api/conversations/:id) and send (POST /api/conversations/:id/messages) against the real API
- [ ] 13c.3 Implement card seeding display from seed_kind/seed_ref
- [ ] 13c.4 Verify the full loop on the dogfood DB: seed → message → grounded reply → reload → back to feed → reopen
- [ ] 13c.5 Update STATUS.md + archive slice