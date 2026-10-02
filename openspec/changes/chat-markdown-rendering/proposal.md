# Chat Markdown Rendering — Proposal

One of two proposals splitting the responsiveness problem found while reviewing
[`../chat-tab-sidebar/`](../chat-tab-sidebar/). The other is
[`../chat-pending-feedback/`](../chat-pending-feedback/). This one is
independent of both and can ship first.

## Why

`MessageList.tsx:48` renders every message as
`<p className="whitespace-pre-wrap">{msg.text}</p>`. The coach is already
emitting Markdown — asterisks for emphasis, bullet lists, occasional headings —
and none of it renders. A reply that says:

```
- Name three people who ...
- **Constraint**: what they all share
```

displays as literal asterisks and hyphens in one run-on paragraph. The model is
doing the work; the renderer is throwing it away.

## What Changes

- **`lifekit/serve/server.py`** — the `_coach_reply` system prompt gains an
  explicit instruction to answer in Markdown (bullets for steps or options,
  bold for the key term, short paragraphs). Without this the model falls back to
  prose, and the renderer has nothing to render. One added clause, not a new
  prompt.

- **`frontend/src/components/conversation/MessageList.tsx`** — render coach
  messages through a Markdown component instead of a raw `<p>`. User messages
  stay plain text: they are typed by the human and should not be interpreted.

- **`frontend/package.json`** — add `react-markdown` and `remark-gfm`.

  `react-markdown` is the deliberate choice over `marked` +
  `dangerouslySetInnerHTML`: LLM output rendered as raw HTML is an injection
  vector, and local-first single-user is a distribution fact, not a security
  boundary. `react-markdown` escapes by default.

- **`frontend/src/app/globals.css`** — style the rendered elements
  (`.lk-prose`: `ul`/`ol` indentation, `strong` weight, `code`, `blockquote`,
  headings). Hand-written rules matching the existing `--lk-*` tokens.

  Do **not** add `@tailwindcss/typography` for this — it is a plugin plus a
  `prose` class vocabulary that fights the existing token set, and the surface
  is six elements. Hand-rolled `.lk-prose` is the smaller total change.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: coach replies render as formatted prose (lists,
  emphasis, headings). User messages remain plain.

## Not In Scope

- Streaming or token-by-token rendering — see
  [`../chat-pending-feedback/`](../chat-pending-feedback/).
- Code blocks with syntax highlighting, tables beyond GFM's default, images.
- Rendering Markdown in feed cards or exercise text.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. A coach reply containing a bulleted list renders as a real list, and
   `**bold**` renders as bold — verified in the running app.
3. User messages are unaffected and cannot inject formatting.
4. A reply containing literal `<script>` or `<img onerror=…>` renders as
   visible text, not as live markup.
5. Indentation and spacing of rendered lists/code read correctly in both light
   and dark themes (the tokens invert — check both).
6. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
7. `docs/product/STATUS.md` updated in the same change.