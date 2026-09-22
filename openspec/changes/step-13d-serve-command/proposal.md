# Step 13d: Serve command + cutover — proposal

## Why

Two running pieces (Python API + Next.js) need one command, and the old
Streamlit UI needs a clean retirement. This slice is the cutover.

## What changes

- **`lifekit ui` CLI command:** starts the 13a feed API on `127.0.0.1:8765`
  and the Next.js production build (`next build` + `next start`) on
  `127.0.0.1:3000`; shuts both down cleanly on exit. Dev mode (`next dev`)
  documented for UI iteration.
- **Remove `ui/app.py`** (Streamlit dogfood UI) — superseded since
  2026-09-21; one UI, not two. Remove its run docs; keep `.devcontainer/`
  consistent with the new flow.
- **Docs:** `docs/product/STATUS.md` phone-access row → workstation tailnet
  IP on port 3000 (`uv sync`, copy `dogfood/lifekit.db` →
  `~/.lifekit/lifekit.db`, `lifekit ui`); `docs/product/USER_MANUAL.md` run
  instructions updated.

## Done criterion

1. On the home workstation: `lifekit ui` boots both processes; the full
   daily loop works in the browser; Ctrl-C stops both cleanly.
2. Phone on the tailnet reaches the UI at `<workstation-ip>:3000`.
3. `ui/app.py` gone; no references to the Streamlit flow remain in docs or
   `.devcontainer/`; suite green.

## Non-goals

- Packaging/distribution beyond the workstation. Anything in 13a–13c scope.
