# Step 13b: Feed screen — proposal

## Why

The home screen is the product: one exercise to do, one idea to remember.
This slice builds the feed exactly as the approved mock drew it — no
conversation view yet (13c), no serving plumbing (13d).

## What changes

- **Next.js app scaffold** (App Router, TypeScript, Tailwind) in
  `frontend/` — replacing the stub. Rewrites proxy `/api/*` to the 13a feed
  API (`127.0.0.1:8765`).
- **Feed screen**, pixel-faithful to the mock's component inventory
  (umbrella proposal): Today header → stage strip → today's-exercise card
  (Mark done + Talk about this) → resurfaced-idea card (Still with me +
  Talk about this + why-note) → fading-ideas card (per-idea Talk about
  this) → conversations list → bottom master composer.
- **Actions wired:** Mark done → `POST /api/completions`; Still with me →
  `POST /api/idea-signals`; composer submit → `POST /api/conversations`
  then navigate to `/c/[id]` (stub page in this slice — 13c fills it).
- Build against the 13a API contract; a lightweight mock of
  `/api/briefing/today` is acceptable for component work, but the slice
  ships against the real API.

## Done criterion

1. Feed renders all seven components from a real `/api/briefing/today`
   response (dogfood DB) with the mock's layout.
2. Mark done and Still with me persist via the API (verified in the DB).
3. Composer creates a conversation and routes to `/c/[id]`.
4. No quiz framing, percentages, grades, or extra tabs anywhere.

## Non-goals

- Conversation view (13c). `lifekit ui` command (13d). Streaming replies.
