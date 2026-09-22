# Step 13: Feed + conversations UI — proposal (umbrella)

## Why

The CLI + MCP interface gives no daily coaching surface. LifeKit's mission —
"every day, one exercise to do and one idea to remember" — needs a home
screen. The approved intent (`../../intent/ui-feed-and-conversations.md`)
defines it: a feed of cards plus a grounded coach chat, local-only.

This proposal is the umbrella. The work is split into four small,
independently shippable slices (the local coding harness chokes on large
proposals — one slice per run):

- `step-13a-feed-api/` — Python HTTP feed API + conversation schema
- `step-13b-feed-screen/` — Next.js feed screen, pixel-faithful to the mock
- `step-13c-conversation/` — conversation view + grounded chat wiring
- `step-13d-serve-command/` — `lifekit ui` command, Streamlit removal, docs

## Stack

Next.js (App Router) + React + TypeScript + Tailwind — decided 2026-09-21,
recorded in `intent.md` Gates and A24. Mirrors the DeepTutor web stack
already surveyed; versions pinned at implementation time.

## Design decisions (answering the intent's open questions 2–4)

- **Serving (Q2):** a `lifekit ui` command orchestrates two localhost-only
  processes — the Python feed API on `127.0.0.1:8765` and the Next.js app on
  `127.0.0.1:3000`, with Next.js rewrites proxying `/api/*` to the Python
  API. Dev runs `next dev`; the command runs the production build
  (`next build` + `next start`). Phone access: workstation tailnet IP on
  port 3000 (replaces the old 8501 Streamlit route).
- **Conversation storage (Q3):** two new tables in the existing SQLite store —
  `conversations(id TEXT PK, title TEXT, book_id TEXT, seed_kind TEXT /*
  card|composer */, seed_ref TEXT /* exercise_id | idea_id | NULL */,
  created_at TEXT, updated_at TEXT)` and `messages(id INTEGER PK,
  conversation_id TEXT REFERENCES conversations(id), role TEXT /*
  user|coach */, text TEXT, created_at TEXT)`.
- **Streamlit (Q4):** `ui/app.py` is removed in slice 13d, when the new UI
  is dogfood-ready. One UI, not two.

## API contract (Python feed API → Next.js)

- `GET /api/briefing/today` → `{book:{id,title}, day, stages:{seen,retained,lived}, exercise:{id,title,text}, resurfaced_idea:{id,text,why}, fading_ideas:[{id,text}]}`
- `POST /api/completions` `{exercise_id}` → `{ok:true}` (backs "Mark done")
- `POST /api/idea-signals` `{idea_id, remembered:true}` → `{ok:true}` (backs "Still with me")
- `GET /api/conversations` → `[{id,title,updated_at}]`
- `POST /api/conversations` `{seed_kind, seed_ref?, title?}` → `{id}`
- `GET /api/conversations/:id` → `{conversation, messages:[{role,text,created_at}]}`
- `POST /api/conversations/:id/messages` `{text}` → `{reply}` — coach reply,
  grounded in the book via retrieval + the configured LLM (Ollama default).

Deterministic runtime owns every decision behind these endpoints; the LLM
only writes the chat prose.

## Visual spec

Pixel-fidelity to the approved mock (2026-09-21; the mock was transient —
the inventory below is the durable record). LifeKit visual theme, not
DeepTutor's.

**Feed screen:**
1. "Today" header — book title + day.
2. Stage strip — ideas seen → retained → lived in practice.
3. Today's-exercise card — exercise text, "Mark done" button, "Talk about this" button.
4. Resurfaced-idea card — idea text, why-it-resurfaced note, "Still with me" + "Talk about this".
5. Fading-ideas card — idea list, each row with its own "Talk about this".
6. Conversations list — existing conversations, tap to reopen.
7. Master composer — text input pinned at the bottom; submit opens a new conversation.

**Conversation screen:** header with "‹ Feed" back button + conversation
title; message list (user/coach); input box at the bottom. "Talk about this"
on any card opens this screen seeded on that card's content.

What the UI is *not*: quiz framing, retention percentages, grades, mastery
gates, browsing/library tabs. The feed is the venue, not a menu.

## Slice map

| Slice | Depends on | Shippable on its own |
|-------|-----------|----------------------|
| 13a feed API | Steps 5, 7 (done) | pytest green; endpoints curl-able against the dogfood DB |
| 13b feed screen | 13a contract (build against the contract; mock the API) | feed renders from mocked `/api/briefing/today`; actions hit the real API |
| 13c conversation | 13a, 13b | full chat loop against the real API |
| 13d serve command | 13a–13c | `lifekit ui` boots both processes; Streamlit removed |

## Done criterion (whole step)

Swapnil completes the intent's daily loop against real dogfood data — open
feed → do the exercise → Mark done → Talk about this → composer chat → back
to feed — all on localhost, no quiz framing, no probabilities, no mastery
gates. Suite stays green; `lifekit ui` is the documented way to run it.

## Non-goals

- Program layer (Steps 8–11: sessions, momentum, interviewer).
- RAG quality upgrade (BACKLOG F9–F11).
- Notifications, auth, multi-user, sync, mobile app, offline packaging.
- Any change to the book pipeline (pillar 1) or retrieval internals (pillar 5).
