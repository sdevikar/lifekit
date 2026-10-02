# AGENTS.md — LifeKit coding-agent instructions

These instructions are for the coding agent (OpenCode). The product owner is
Atlas; the human (Swapnil) writes the code with you and makes all product
decisions.

> **Start here.** Read `.agents/intent.md` (vision) and `docs/product/STATUS.md`
> (current state) before acting. Then glance at this file's Quick reference.

## Quick reference

| Thing | Command | Notes |
|-------|---------|-------|
| Run the app | `lifekit ui` | Feed API `127.0.0.1:8765` + Next.js `127.0.0.1:3783`, localhost only. Always rebuilds Next.js. |
| Run the app (alt) | `./deploy_local.sh` / `--stop` / `--dev` | Feed `:8765`, web `:3000` (`NEXT_PORT`). Auto-copies dogfood DB if missing. |
| Ingest a book | `python -m lifekit.store --pdf <path>` | Or `make ingest PDF=<path>`. |
| MCP server | `python -m lifekit.mcp.server` | FastMCP stdio. Or `make serve`. |
| Plan forge | `python -m lifekit.plan_forge.forge --intent "..."` | Or `make forge INTENT="..."`. |
| Init DB | `python -m lifekit.db.schema` or `init_db()` | `~/.lifekit/lifekit.db` (`$LIFEKIT_DB`). Idempotent + migrates. |
| LLM provider config | `lifekit config` | Ollama default + OpenRouter. Never stores keys. Order: CLI > env > `~/.lifekit/config.json` > defaults. |
| Tests | `uv run pytest tests/ -v` | Or `make test`. 117 tests, 1 pre-existing fail (`test_split_dyl_pdf`). See Verification. |

**Python entrypoint:** `lifekit = lifekit.__main__:main` (subcommands `ui`,
`config`); other tools run as `python -m lifekit.<submodule>`. The codebase is
one monolith package under `lifekit/` — no separate installs per pillar.
Package manager is `uv` (`uv.lock`); `poetry.lock` is vestigial.

## Intent: one vision file, one workflow

`.agents/intent.md` is the standing product vision (`.claude/intent.md`
symlinks to it). On any conflict with other docs, it wins. The old
`intent/` per-change proto-spec workflow was retired 2026-09-26; changes go
straight to OpenSpec proposals, checked against `.agents/intent.md`.

### The workflow (this is what keeps the SDLC in check)

1. **Every change starts as an OpenSpec proposal.** No code without a spec;
   tests and done criteria defined before implementation. When the human
   describes a change in chat, draft it as `openspec/changes/<slug>/`.
2. **Keep proposals small:** one independently testable slice per proposal
   (a/b/c/d slices for UI-sized work, as in Step 13). The local coding
   harness chokes on large proposals — never hand it a whole step at once.
3. **Check against the vision.** Every proposal must be consistent with
   `.agents/intent.md` (non-negotiables, never-build list, stages). If the
   human asks for something contradicting it, surface the conflict before
   doing anything else.
4. **The human approves.** The agent commits changes after approval. The agent never self-approves.
5. **`.agents/intent.md` changes only on human approval.** Propose the exact
   diff and wait for explicit approval; never amend it unilaterally. If work
   reveals it is stale, flag it and propose an update — do not silently drift.

At the start of every task or session: read `.agents/intent.md` first, then
`docs/product/STATUS.md` for current project state.

## Working agreements

- **Minimal diffs:** the smallest change that satisfies the spec. No
  speculative generality, no drive-by refactors.
- **Docs stay true:** keep `docs/product/STATUS.md`, `docs/product/ROADMAP.md`, `docs/product/ASSUMPTIONS.md`,
  `docs/product/BACKLOG.md` accurate with every change.
- **Ask for a visual check when a human can just look.** For changes a human
  can verify by opening the app — styling, theming, layout, copy, any UI
  behavior — do not spend turns trying to prove it with headless screenshots or
  probe pages. Get the code building, then say "please look at it" and let the
  human be the check. Reserve automation for things only a machine can confirm
  (contrast ratios, OS-preference resolution, build and test suites), and say
  plainly what you verified versus what they verified. Directed 2026-09-29 after
  the dark-theme change, where a throwaway probe page and repeated
  screenshot-flag guesswork produced nothing the human could not have confirmed
  in ten seconds by opening http://127.0.0.1:3783.
- **Use serena for code work.** Call `tools.serena.initial_instructions()` once per session, then `read_memory` for `conventions` and `tech_stack` (plus `backend/core` / `frontend/core` as relevant). Prefer `find_symbol`, `find_referencing_symbols`, and `search_for_pattern` over blind `read` + grep; use `replace_symbol_body` / `replace_content` for edits inside a symbol.
- **Serena index maintenance.** Do all edits through Serena tools to keep the index in sync. After external changes (git pull/merge/rebase), re-run `tools.serena.onboarding()` to refresh. If symbol lookups return stale results, refresh the index.
- **Local-first:** long evals run on the home workstation's Ollama, never
  on this VM. Never commit secrets.

## Verification

- **Tests:** `uv run pytest tests/ -v` (or `make test` = `python -m pytest
  tests/ -v`). **117 tests, 1 pre-existing failure** (`test_split_dyl_pdf`,
  hardcoded VM path — BACKLOG P2). Run a single file with
  `uv run pytest tests/test_coach.py -v`.
- **No conftest.py.** Tests skip gracefully when fixtures are absent.
- **Zero tests hit a real LLM** — all model calls are stubbed/mocked. The
  suite proves the pipeline is *plumbed*, not that it *extracts*. The real-
  model eval (`qwen3.8:27b-q8_0` on home Ollama, ≥90% recall) is the quality
  gate (results in `evals/`).
- **Lint:** `make lint` runs `py_compile` over `lifekit/**/*.py`.
  There is **no ruff/black/typecheck** configured — don't invent them.
- **Frontend:** `cd frontend && npx next build` / `npx eslint`. The
  `useConversation` regression test runs via
  `node --experimental-strip-types` against `:3783` (override with `LIFEKIT_UI`).

## Architecture at a glance

- **Store is the hub:** SQLite at `~/.lifekit/lifekit.db` (or `$LIFEKIT_DB`).
  Every pillar (pipeline, scheduler, coach tools, feed API, chat) reads/writes
  it; nothing talks behind its back. FSRS resurfacing, scheduling, and state
  live in code — the LLM only writes conversational prose.
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
- **Long model runs go to the home workstation Ollama over Tailscale — never
  this VM.** Phone access uses the workstation's tailnet IP on `:3783`.
- **Secrets:** `.env` is git-ignored and never committed; `.env.example` shows
  `LIFEKIT_DB`, `OLLAMA_MODEL`, `OLLAMA_BASE_URL`. Config **never** stores API
  keys.

## Push discipline

- **Plan commits:** Plan individual commits before implementing changes
- **Fetch first:** Fetch `origin/main` first; one consolidated commit per unit of work; verify the
  remote tree after pushing
- **Review after each commit:** Run `ponytail-review` on the commit diff. Apply worthwhile simplifications in a follow-up commit.
- **Hooks (recommended):** Add a local `post-commit` hook to remind about ponytail-review. Since `.git/hooks/` are local, document this as a recommended practice.
