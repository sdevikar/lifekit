# Tasks — retire-free-chat

## 1. Frontend

- [ ] 1.1 Strip `app/layout.tsx` to `<main>{children}</main>` and update its metadata (D2); verify the feed renders with no sidebar.
- [ ] 1.2 Delete the pages, components, hooks, and `test_useConversation.mjs` listed in the proposal; verify `npx next build` and `npx eslint src` pass.
- [ ] 1.3 Add the redirects (D1); verify "Old chat link" and "Old journal link" with `curl -sI` against `lifekit ui`.

## 2. Backend

- [ ] 2.1 Delete the conversation routes, `_generate_title`, and the card-less `build_messages` path (D3) and their tests; verify "Old API route" and `uv run pytest tests/ -q` shows only the known `test_split_dyl_pdf` failure.
- [ ] 2.2 Verify "Card threads kept": a dogfood DB copy still shows its card threads after the change.

## 3. Docs

- [ ] 3.1 Update `AGENTS.md` (Verification, Quick reference), `docs/arch/testing.md`, and `docs/arch/README.md`; verify `grep -rn "useConversation\|/api/conversations\|Sidebar" AGENTS.md docs/arch` finds nothing.

## Workflow follow-up

- Move the KANBAN row for slice 7 to Done and archive this change after merge.
