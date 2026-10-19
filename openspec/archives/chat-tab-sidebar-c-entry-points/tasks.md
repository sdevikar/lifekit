# Chat Tab c — Entry Points + Deep Links — Tasks

- [ ] `feed/page.tsx` — the three `handleTalkAbout*` handlers swap `router.push('/c/${convId}')` for `setActiveTab("chat")` + `setSelectedConvId(convId)`; drop the now-unused `useRouter` import <!-- id: 0 -->
- [ ] `app/c/[id]/page.tsx` — reduce to a wrapper that resolves the route id and sets tab + selected id together, rendering nothing. Keeps `/c/[id]` working for pasted and bookmarked URLs <!-- id: 1 -->
- [ ] Delete the `← Feed` buttons (`page.tsx:43` and `:69` — one per header branch, do not miss the loading branch) — the sidebar Feed icon is the way back. This is the change that collapses two navigation models into one <!-- id: 2 -->
- [ ] Do not touch `MasterComposer.tsx` — it is unreferenced, so restyling it is work on dead code. Its fate is a separate decision <!-- id: 3 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; all three "Talk about this" entry points; hard-reload a `/c/[id]` URL; `/c/<unknown-id>` shows the error state instead of a blank page; no `← Feed` left <!-- id: 4 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 5 -->
- [ ] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md`, then archive all three a/b/c specs under `openspec/archives/` <!-- id: 6 -->