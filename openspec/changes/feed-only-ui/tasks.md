# Tasks — feed-only-ui

## 1. Frontend

- [ ] 1.1 Strip `app/layout.tsx` to `<main>{children}</main>` with the theme script (D1); verify the feed renders with no sidebar.
- [ ] 1.2 Remove the "Talk about" buttons, their props, and `createConversation` (D1); verify "No chat buttons" in the browser.
- [ ] 1.3 Delete the pages, components, hooks, and `test_useConversation.mjs` listed in the proposal; verify `npx next build` and `npx eslint src` pass.

## 2. Backend

- [ ] 2.1 Delete the conversation routes and the helpers (D2) and their tests; verify `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.
- [ ] 2.2 Verify "Tables kept": on a copy of the dogfood DB, the row counts of `conversations` and `messages` are the same before and after `init_db()`.

## 3. Docs

- [ ] 3.1 Update `AGENTS.md` (Verification, Architecture), `docs/arch/testing.md`, and `docs/arch/README.md`; verify `grep -rn "useConversation\|/api/conversations\|Sidebar" AGENTS.md docs/arch` finds nothing.
- [ ] 3.2 Run `lifekit ui` and ask the human to look at the feed on a desktop and a phone.

## Workflow follow-up

- Move the KANBAN row for slice 0 to Done and archive this change after merge.
