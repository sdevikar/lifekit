# AGENTS.md — LifeKit coding-agent instructions

How to work in this codebase as the coding agent (OpenCode). The vision,
roles, non-negotiables, stages, and the workflow that governs them live in
`.agents/intent.md` (`.claude/intent.md` symlinks to it) — this file does not
restate them.

> **Start here.** Read `.agents/intent.md`, then `docs/product/KANBAN.md` for
> current state, then the newest handoff in `.devflow/handoffs/`, then this
> file's Quick reference. Read `DESIGN.md` before any UI work.

## Workflow (the rules live in intent.md → "How we build")

1. No code without a spec: when the human describes a change, draft it as an
   `openspec/changes/<slug>/` proposal (see intent.md → "How we build").
2. Check every proposal against intent.md's non-negotiables, never-build list,
   and stages. If the request contradicts them, surface the conflict before
   doing anything else.
3. The human approves; the agent commits. Never self-approve. `.agents/intent.md`
   changes only with explicit approval — propose the exact diff (intent.md →
   "Changing this file").
4. The old `intent/` per-change proto-spec workflow was retired 2026-09-26.
   Don't resurrect it.

## Code intelligence (MCP)

Serena was retired for this project (2026-10-15); `trace-mcp` replaces it —
see the "trace Tool Routing" block below. After `git pull/merge/rebase` or a
long pause, call `register_edit` only for files you edit; freshness otherwise
comes from trace's file watcher (`trace doctor` if lookups look stale).

## Skills — reach for these

Use the `skill` tool when a task matches. The ones that matter here:

- `impeccable` and `frontend-design` — any UI work or critique.
- `reverse-engineer-anything` — inspecting DeepTutor or any binary/artifact with REA.
- `ponytail` — active for all code work (the laziness ladder).
- superpowers process skills: `brainstorming` (before building),
  `systematic-debugging`, `test-driven-development`, `verification-before-completion`.

## Quick reference

| Thing | Command | Notes |
|-------|---------|-------|
| Run the app | `lifekit ui` | Feed API `127.0.0.1:8765` + Next.js `127.0.0.1:3783`, localhost only. Always rebuilds Next.js. |
| Run the app (alt) | `./deploy_local.sh` / `--stop` / `--dev` | Feed `:8765`, web `:3000` (`NEXT_PORT`). Auto-copies dogfood DB if missing. |
| Ingest a book | `python -m lifekit.store --pdf <path>` | Or `make ingest PDF=<path>`. Slice 2 adds `lifekit ingest <file>`; slice 6 removes this path. |
| MCP server | `python -m lifekit.mcp.server` | FastMCP stdio. Or `make serve`. |
| Plan forge | `python -m lifekit.plan_forge.forge --intent "..."` | Or `make forge INTENT="..."`. |
| Init DB | `python -m lifekit.db.schema` or `init_db()` | `~/.lifekit/lifekit.db` (`$LIFEKIT_DB`). Idempotent + migrates. |
| LLM provider config | `lifekit config` | Ollama default + OpenRouter. Never stores keys. Order: CLI > env > `~/.lifekit/config.json` > defaults. |
| Tests | `uv run pytest tests/ -v` | Or `make test`. 1 known failure (`test_split_dyl_pdf`). See Verification. |

**Python entrypoint:** `lifekit = lifekit.__main__:main` (subcommands `ui`,
`config`); other tools run as `python -m lifekit.<submodule>`. The codebase is
one monolith package under `lifekit/` — no separate installs per pillar.
Package manager is `uv` (`uv.lock`).

## Verification

- **Tests:** `uv run pytest tests/ -v` (or `make test` = `python -m pytest
  tests/ -v`). **1 known failure** (`test_split_dyl_pdf`, hardcoded VM path —
  KANBAN P2). Run a single file with `uv run pytest tests/test_coach.py -v`.
  If collection fails with `No module named 'flask'` (or `fsrs`, `mcp`,
  `pypdf`), the local `.venv` is out of date: run `uv sync` first.
- **No conftest.py.** Tests skip gracefully when fixtures are absent.
- **Zero tests hit a real LLM** — all model calls are stubbed/mocked. The
  suite proves the pipeline is *plumbed*, not that it *extracts*. The real-
  model eval (`qwen3.8:27b-q8_0` on home Ollama, ≥90% recall) is the quality
  gate (results in `evals/`).
- **Lint:** `make lint` runs `py_compile` over `lifekit/**/*.py`. There is
  **no ruff/black/typecheck** configured — don't invent them.
- **Frontend:** `cd frontend && npx next build` / `npx eslint`. The
  `useConversation` regression test runs via `node --experimental-strip-types`
  against `:3783` (override with `LIFEKIT_UI`). Slice 0 deletes it; slice 6
  adds a `useComments` test the same way.

## Architecture at a glance

This section describes the code on `main` today, which is still the PoC. The
v1 slices change it (`docs/product/ROADMAP.md` → "v1 slices"):

| Slice | What changes here |
|-------|-------------------|
| 0 `feed-only-ui` | The sidebar, the chat pages, and the conversations API go. |
| 2 `book-model-v1` | `lifekit ingest` and the `sections` and `passages` tables arrive. |
| 3, 4 | The pipeline becomes `structure → items → cards`. |
| 5 `feed-v1` | `/api/feed` and card reactions replace the briefing. |
| 6 `card-comments` | Card comments and coach replies; grounding moves to `lifekit/serve/coach.py`. |

Update the bullets below in the same commit that lands each slice.

- **Store is the hub:** SQLite at `~/.lifekit/lifekit.db` (or `$LIFEKIT_DB`).
  Every pillar (pipeline, scheduler, coach tools, feed API, chat) reads/writes
  it; nothing talks behind its back. FSRS resurfacing, scheduling, and state
  live in code — the LLM only writes conversational prose (intent.md →
  non-negotiables).
- **Feed API:** Flask on `127.0.0.1:8765` (`lifekit.serve.server`, `FeedAPI`).
  Default book is `dyl`. Endpoints: `/api/briefing/today`, completions,
  idea-signals, conversations CRUD, grounded chat. `/api/*` is rewritten through
  Next.js.
- **UI:** `frontend/`, Next.js 16 App Router + Tailwind. Serves `:3783`.
- **Pipeline (offline):** `split → extract → reduce → validate`, each gated by
  evals. Never sees the user. See `docs/arch/README.md` for the data-flow diagram.

## Gotchas

- **Next.js 16 has breaking changes** vs the training data. Read
  `node_modules/next/dist/docs/` (and `frontend/AGENTS.md`) before writing
  frontend code — don't rely on memorized APIs.
- **Don't `npx next start` from a managed subprocess.** The `npx` wrapper
  detaches, exits `1`, and leaves the real server orphaned. `ui/serve.py` runs
  `node <next-bin> start` directly — follow that pattern.
- **`lifekit ui` serves the web app on `:3783`, not `:3000`.** Port 3000 is held
  by `hermes-gateway`; binding there makes `lifekit ui` lose the port race.
  `deploy_local.sh` is the exception: it uses `:3000` (or `NEXT_PORT`).
- **Phone access** uses the workstation's tailnet IP on `:3783`. Long model runs
  follow intent.md's local-first rule — home Ollama over Tailscale, never this VM.
- **Secrets:** `.env` is git-ignored and never committed; `.env.example` shows
  `LIFEKIT_DB`, `OLLAMA_MODEL`, `OLLAMA_BASE_URL`. Config **never** stores API
  keys.

## Working agreements

- **Ask for a visual check when a human can just look.** For anything a human
  verifies by opening the app — styling, theming, layout, copy, UI behavior —
  don't burn turns on headless screenshots or probe pages. Get it building,
  say "please look at it", and state plainly what you verified vs. what they
  did. Reserve automation for what only a machine can confirm (contrast
  ratios, OS-preference resolution, build and test suites). Directed
  2026-09-29 after the dark-theme episode.
- **No fallback scope creep.** Don't keep a second code path "just in case"
  (e.g. a markdown fallback alongside a new renderer). One path, one source of
  truth; if it breaks, fix the cause, not the fallback.
- **Plan commits before implementing.** Then fetch `origin/main` first, one
  consolidated commit per unit of work, and verify the remote tree after pushing.
- **Review after each commit:** run `ponytail-review` on the commit diff; apply
  worthwhile simplifications in a follow-up commit.
- **UI design source is `DESIGN.md`.** It applies ROADMAP D1 (one feed
  column, no sidebar or drawer) and D15 (design rules borrowed from Meta's
  Astryx), and names the Astryx record behind each rule. DeepTutor (`/home/swapnil/workspace/projects/DeepTutor`) inspires the
  runtime only, not the layout; read it with `reverse-engineer-anything`. Do
  not copy its quiz/mastery features (intent never-build).
- **Session files go in `.devflow/`** (devflow layout: `handoffs/`, `plans/`,
  `reviews/`, `research/`, `analysis/`, `artifacts/`). Git tracks only
  `handoffs/` there (`.devflow/.gitignore`), so the next session on any machine
  finds them. Research that shapes a decision goes in `docs/research/`
  (intent.md → "Where things live").
- **Hooks (recommended):** add a local `post-commit` hook to remind about
  ponytail-review. `.git/hooks/` is local, so document it as a practice.

<!-- trace:start -->
## trace Tool Routing

IMPORTANT: For ANY code exploration task, ALWAYS use trace tools first. NEVER use host file-reading, grep, glob, or shell (ls, find) tools for navigating source code.

| Task | trace tool | Instead of |
|------|------------|------------|
| Find a function/class/method | `search` | text grep |
| Understand a file before editing | `get_outline` | full-file read |
| Read one symbol's source | `get_symbol` | full-file read |
| What breaks if I change X | `get_change_impact` | guessing |
| All usages of a symbol | `find_usages` | text grep |
| All implementations of an interface | `get_implementations` | directory search (ls/find) |
| All classes implementing X | `search` with `implements` filter | text grep |
| Project health / coverage gaps | `self_audit` | manual inspection |
| Dead code / dead exports | `get_dead_code` (`mode: "exports_only"`) | text grep for unused |
| Context for a task | `get_feature_context` | reading 15 files |
| Tests for a symbol | `get_tests_for` | glob + grep |
| Untested symbols (deep) | `get_untested_symbols` (deferred — load via `load_tools`) | manual audit |
| HTTP request flow | `get_request_flow` (framework-gated) | reading route files |
| DB model relationships | `get_model_context` (framework-gated) | reading model + migrations |
| Component tree | `get_component_tree` (framework-gated) | reading component files |
| Circular dependencies | `get_circular_imports` | manual tracing |
| Task spanning many turns | `trace_state_init` once, then `trace_state_patch` / `trace_state_add_dead_end` per step, `trace_state_get` to re-read (deferred — `load_tools({preset:"state"})`) | re-reading the whole transcript every turn |

Use host file-reading and grep tools ONLY for non-code files (.md, .json, .yaml, config) or before edit.
Start sessions with `get_project_map` (summary_only=true).
<!-- trace:end -->

## Agent skills

### Issue tracker

Issues live as GitHub issues in sdevikar/lifekit; operations use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `GLOSSARY.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.
The `/domain-modeling` skill creates both when a term or a decision is first
resolved, so they do not exist yet. Until then, the decision record is
`docs/product/ROADMAP.md` (D1–D15).
