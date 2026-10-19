# Chat Surface c — Entry Points + Deep Links — Tasks

- [ ] Verify `feed/page.tsx` "Talk about this" handlers already navigate to `/c/[id]` — no change needed <!-- id: 0 -->
- [ ] Verify `app/c/[id]/page.tsx` `← Feed` already navigates to `/feed` — no change needed <!-- id: 1 -->
- [ ] Verify: `npm run build` + `npm run lint` clean; all three "Talk about this" entry points; `/c/[id]` deep link; `← Feed` returns to feed <!-- id: 2 -->
- [ ] `uv run pytest tests/ -v` — no new failures beyond `test_split_dyl_pdf` (KANBAN P2) <!-- id: 3 -->
- [ ] Update `docs/product/KANBAN.md`, then archive all three a/b/c specs under `openspec/archives/` <!-- id: 4 -->
