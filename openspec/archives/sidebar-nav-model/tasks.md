# Sidebar Nav Model — Tasks

- [x] `Sidebar.tsx` — collapse the icon strip (`:36`) and panel (`:70`) into ONE column: icon-only when collapsed, icon + label rows when expanded, tab content below the rows <!-- id: 0 -->
- [x] Rework `IconTab` (`:95-122`) from a `flex-col` button with the label in a sibling `<span>` (`:119`) into a single row: icon, label, optional trailing action <!-- id: 1 -->
- [x] Labels render only when expanded — not shrunk, not clipped. Collapsed keeps each icon's `aria-label` and `title` so the strip stays labelled <!-- id: 2 -->
- [x] Row takes an optional trailing action rather than hardcoding `+`; reveal it via `group-hover` on the row and `focus-visible` within it. Hover alone is not an accessible control <!-- id: 3 -->
- [x] Wire the trailing action for Chat and Journal only; Feed and Settings get none. Journal's is shown and inert (human decision): `aria-disabled`, **not focusable**, native `title` saying it is not available yet — no tooltip component, the codebase only uses native `title` (`Sidebar.tsx:27,116`) <!-- id: 4 -->
- [x] Keep the collapse toggle where `sidebar-refinements` put it (panel top-right expanded, strip top collapsed) and keep `COLLAPSE_KEY` persistence (`:6`) unchanged <!-- id: 5 -->
- [x] Widths: collapsed `w-10` (40px, down from `w-14`), expanded stays `w-70` (280px) so conversation titles still fit on one line <!-- id: 6 -->
- [x] Keep nav ordering: Feed/Journal/Chat top, Settings pinned bottom by the existing `flex-1` spacer (`:59`) — matches the reference <!-- id: 7 -->
- [x] Per-tab panel content: Chat renders the conversation list (slice a), **Feed renders nothing — drop the `LifeKit / Today` block (`:74-76`)**, Journal/Settings keep their placeholder <!-- id: 8 -->
- [x] Verify: `npm run build` + `npm run lint` clean (3 lint problems, all pre-existing in `useBriefing.ts` / `useConversation.ts`); built bundle confirmed to contain `w-10`/`w-70`, the collapsed `justify-center px-2 py-2` row, the `group-hover`/`focus-visible` reveal, and `aria-disabled` — and to no longer contain `w-14`, the old `flex-col` row, or the `lk-card` feed chrome <!-- id: 9 -->
- [x] `uv run pytest tests/ -v` — 116 passed, 1 failed: only the known `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 10 -->
- [x] Update `docs/product/STATUS.md` and `docs/product/KANBAN.md` <!-- id: 11 -->
- [ ] User eyeballs collapsed and expanded in both light and dark themes — visual change, so the check is theirs. **Requires restarting `lifekit ui`**, which is still serving the pre-change build <!-- id: 12 -->