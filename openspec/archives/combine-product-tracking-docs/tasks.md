# Combine product tracking docs — tasks

## Phase 1 — consolidate the tracker into `KANBAN.md`

- [x] 1.1 Create `docs/arch/testing.md` from the STATUS test-inventory rows
  (lines 52–64); delete that block from STATUS.
- [x] 1.2 Rebuild `docs/product/KANBAN.md` as the single tracker: open with a
  "How to use this file" section map, then current state / now / upcoming /
  deferred / known issues / future ideas / done / open questions / locked
  assumptions — merging STATUS + KANBAN + BACKLOG + ROADMAP + PHILOSOPHY per the
  proposal mapping. Reconcile the drifted open-issue lists and the "3 logged bugs".
- [x] 1.3 Delete `docs/product/STATUS.md`, `BACKLOG.md`, `ROADMAP.md`,
  `PHILOSOPHY.md`.
- [x] 1.4 `ASSUMPTIONS.md` line-13 pointer: `ROADMAP.md` → `KANBAN.md`.
- [x] 1.5 Repoint live references: `README.md`, `docs/index.md`,
  `docs/backend/README.md`, `docs/algorithms/README.md`,
  `docs/requirements/appendix.md`, pending `openspec/changes/*/tasks.md`.
- [x] 1.6 Serena was retired 2026-10-15 — no `.serena` update needed.
- [ ] 1.7 Commit Phase 1 (docs-only; `make lint` clean).

## Phase 2 — intent + agents

- [x] 2.1 `intent.md`: DeepTutor inspiration paragraph, "UI is a first-class
  investment" non-negotiable, doc-map + "Docs stay true" → `KANBAN.md`.
- [x] 2.2 `AGENTS.md`: "Skills — reach for these" section + "Design source is
  DeepTutor" agreement; "Start here" points at `KANBAN.md`.
- [ ] 2.3 Final grep: no live reference to the four deleted docs; `make lint`
  clean; mark this change Done in `KANBAN.md` and archive
  `openspec/changes/combine-product-tracking-docs/` → `openspec/archives/`.
