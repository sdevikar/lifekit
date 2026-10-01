# Sidebar Refinements — Proposal

## Why

The sidebar layout shell shipped with the collapse toggle at the bottom of the icon strip. The user wants it at the top right of the panel for better discoverability and ergonomics.

## What Changes

- **`frontend/src/components/Sidebar.tsx`** — move the collapse toggle button from the bottom of the icon strip to the top right of the panel. When the panel is collapsed, show the toggle in the icon strip (top right).

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. The collapse toggle appears at the top right of the panel when the panel is open.
3. The collapse toggle appears in the icon strip when the panel is collapsed.
4. The toggle still persists state to `localStorage`.
5. `docs/product/STATUS.md` updated in the same change.
