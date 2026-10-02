# Dark Theme — Tasks

- [x] Convert the 17 `--lk-*` color tokens in `frontend/src/app/globals.css` to `light-dark()`; set `color-scheme: light dark` on `:root`; invert `--lk-primary`, `--lk-card`, `--lk-border`; lighten `--lk-brand-clay` to `#d97757`; switch shadow/alpha values to white-alpha <!-- id: 0 -->
- [x] Add `:root[data-theme="dark"]` / `:root[data-theme="light"]` overrides pinning `color-scheme` for the per-app manual override <!-- id: 1 -->
- [x] Add `components/ThemeToggle.tsx` (`"use client"`): resolve `localStorage` → `matchMedia` → OS, set `data-theme` on `<html>`, persist, expose an accessible icon button <!-- id: 2 -->
- [x] Add the pre-paint inline script in `frontend/src/app/layout.tsx` reading the same `localStorage` key so no wrong-theme flash occurs on load <!-- id: 3 -->
- [x] Place the toggle in `TodayHeader` (feed) and in **both** header branches of `frontend/src/app/c/[id]/page.tsx` — loading and loaded <!-- id: 4 -->
- [x] Verify: `npm run build` + `npm run lint` clean; screenshot `/feed` and `/c/<id>` in dark and light; confirm toggle overrides the OS both ways and survives reload <!-- id: 5 -->
- [x] Record the computed contrast ratio for all 12 text/background token pairs (AA: ≥4.5:1 body, ≥3:1 large/non-text) <!-- id: 6 -->
- [x] Run `node --experimental-strip-types test_useConversation.mjs` and `uv run pytest`; confirm no new failures beyond the known `test_split_dyl_pdf` (BACKLOG P2) <!-- id: 7 -->
- [x] Update `docs/product/STATUS.md` in the same change <!-- id: 8 -->
