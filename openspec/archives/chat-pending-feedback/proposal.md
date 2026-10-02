# Chat Pending Feedback — Proposal

One of two proposals splitting the responsiveness problem found while reviewing
[`../chat-tab-sidebar/`](../chat-tab-sidebar/). The other is
[`../chat-markdown-rendering/`](../chat-markdown-rendering/), which is
independent and can ship first.

## Why

Sending a message currently looks broken. `useConversation.sendMessage`
(`frontend/src/hooks/useConversation.ts:41-65`) awaits the whole
`POST .../messages` round trip before it touches state:

```ts
const resp = await apiPost(`/api/conversations/${convId}/messages`, { text });
setMessages((prev) => [...prev, userMsg, coachMsg]);
```

The server calls the LLM synchronously before it persists anything — correctly,
so a provider failure never leaves an orphan user message
(`lifekit/serve/server.py:429-435`). The consequence on screen is that after
pressing send, **the user's own message does not appear until the coach has
finished answering**. On a local 27B model that is tens of seconds of an input
that cleared itself (`ChatInput.tsx:19`) and an unchanged screen. The only
signal is the button label flipping to "Sending…".

The interface looks hung, and the user cannot tell their message went anywhere.

## What Changes

- **`frontend/src/hooks/useConversation.ts`** — append the user message to
  `messages` immediately, before the request resolves, then append the coach
  reply when it arrives. If the request fails, remove the optimistic user
  message and surface the error — do not leave a message the server never
  stored.

  This is a client-state change only. The server keeps its
  reply-before-persist ordering; that invariant is what makes the rollback
  correct and must not move.

- **A visible pending state.** `sendMessage` already exposes `sending`, and
  `MessageList` needs a pending indicator while it is true: a "Coach is
  thinking…" row, styled like an existing message rather than a new component
  hierarchy. It needs to be distinguishable from a real message and clearly
  not one — this is a status, not content, and `.agents/intent.md` forbids
  dressing state up as achievement.

- **`frontend/src/components/conversation/ChatInput.tsx`** — while `disabled`,
  show why ("Coach is thinking…" or similar) instead of the bare "Sending…"
  label, and keep the field empty-but-disabled rather than silently accepting
  nothing.

## Capabilities

### Modified Capabilities

- `ui-feed-conversations`: the user's message appears immediately on send, with
  a visible pending state until the coach replies.

## Not In Scope

- **Token streaming.** Real streaming means an SSE endpoint, a partial-flush
  persistence path, and a client reader — a separate proposal, and the reason
  this is split out rather than done properly in one go. Decide after dogfooding
  the pending state; if the wait is tolerable once the screen responds,
  streaming may not be worth it. Note the current `_coach_reply` already
  carries a `ponytail:` comment about naive retrieval — the local model latency
  story is not solved anywhere yet.
- Markdown rendering — see [`../chat-markdown-rendering/`](../chat-markdown-rendering/).
- Cancellation of an in-flight request.
- Optimistic rendering in feed cards.

## Done Criterion

1. `npm run build` and `npm run lint` pass in `frontend/`.
2. Pressing send shows the user's message immediately, before the reply lands.
3. A pending indicator is visible until the reply arrives, and is gone after.
4. When the provider fails (502), the optimistic user message is removed — the
   transcript matches what the server stored.
5. A failed send restores the text to the input, which `ChatInput.tsx:20-22`
   already does; that path still works after the optimistic change.
6. Sending a second message while one is pending is prevented.
7. `uv run pytest tests/ -v` shows no new failures beyond `test_split_dyl_pdf`.
8. `docs/product/STATUS.md` updated in the same change.