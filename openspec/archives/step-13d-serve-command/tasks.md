# Step 13d: Serve command + cutover — tasks (completed)

- [x] 13d.1 Implement `lifekit ui`: start feed API (:8765) + `next start` (:3000), localhost only; clean shutdown of both
- [x] 13d.2 Delete `ui/app.py`; remove Streamlit references from docs and `.devcontainer/`
- [x] 13d.3 Update `docs/product/STATUS.md` (phone-access row) and docs with the new run flow
- [x] 13d.4 End-to-end verified: `next start` production server proxies `/api/*` to feed API; Mark done, Still with me, conversation creation all work through the proxy against the dogfood DB
- [x] 13d.5 Update `docs/product/STATUS.md`; archive all Step 13 slices on completion

## Test results (2026-09-24)

- `python -m py_compile` clean on all new files
- `npx next build` — passes (existing build reused)
- `npx next start -p 3001` (test port) — production server runs and proxies `/api/*` to the feed API:
  - `GET /api/briefing/today` → briefing JSON through proxy
  - `POST /api/completions` → `{ok:true, completion_id:5}`
  - `POST /api/conversations` → `{id:"6a9704d6e14e"}`
- `lifekit ui` command starts both processes; both bind to 127.0.0.1 only
- Streamlit removed: `ui/app.py` deleted, `streamlit` dependency removed from `pyproject.toml`, `.devcontainer/devcontainer.json` updated (port 8501→3000)

New files: `lifekit/ui/{__init__,__main__,serve}.py`, `lifekit/__main__.py`.
Changed: `pyproject.toml` (added `[project.scripts]`, removed `streamlit`),
`.devcontainer/devcontainer.json` (port + start command), `docs/ux/README.md`,
`docs/product/STATUS.md`, `docs/product/ROADMAP.md`.
Deleted: `ui/app.py`.