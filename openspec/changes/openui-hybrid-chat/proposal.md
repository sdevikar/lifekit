# OpenUI Hybrid Chat — Proposal

**Status: proposal only — do not implement yet.**

## Why

LifeKit's chat coach replies are currently rendered as Markdown (`react-markdown` +
`remark-gfm`) inside a hand-built card bubble. The product direction (exercise
surfaces, A2UI) already wants generative, component-based UI. OpenUI provides
exactly that as a drop-in renderer: the message list, composer, conversation
state, and transport stay the same; only the assistant message changes. This
proposal adopts OpenUI for the chat surface only, keeping the existing Next.js
shell/sidebar/theme/feed intact (hybrid, not a redo).

## What Changes

Frontend (primary) + one backend prompt change. No new routes, no new storage.

## Decisions (locked)

- **Hybrid, not redo.** Keep the Next.js shell, sidebar, theme, feed. OpenUI
  renders only inside coach replies (and later exercise surfaces).
- **Minimal custom library.** `frontend/src/lib/openui.tsx` defines only Card
  (root) + TextContent — ~2.6k-char prompt instead of the built-in's 53k.
  Built-in `openuiChatLibrary` was rejected for chat: its full catalog (105
  components) blows up the system prompt and starves context on local models.
  Exercise surfaces extend this library via `library.extend`.
- **OpenUI replaces the bubble.** OpenUI's Card replaces the hand-built card
  bubble (`max-w-[85%]`, bg-lk-card, border, font-serif). OpenUI owns the
  visual container; no custom wrapper. (Principle: OpenUI owns the visual.)
- **Emphasis via OpenUI props**, not inline markdown. One rendering path.
- **User messages stay plain text** (`whitespace-pre-wrap`). Only coach replies
  render OpenUI Lang.
- **No markdown fallback.** One renderer, one path. If output breaks, fix the
  prompt/model — not the renderer. (No fallback scope creep.)
- **No streaming.** Current chat is whole-reply; OpenUI renderer accepts a
  complete string with `isStreaming={false}`.

## Frontend changes

1. Add `@openuidev/react-lang` (and `@openuidev/react-ui` for the built-in
   library + its styles) to `frontend/package.json`.
2. Import built-in styles once in `frontend/src/app/globals.css`:
   `@import "@openuidev/react-ui/styles/index.css";`
3. In `frontend/src/components/conversation/MessageList.tsx`, replace the
   `<Markdown>` block inside coach bubbles with:
   ```tsx
   <Renderer response={msg.text} library={openuiChatLibrary} isStreaming={false} />
   ```
   Remove the `react-markdown` / `remark-gfm` imports from this file.
4. Keep the empty-state, pending "Thinking…" row, and user-message bubble
   unchanged.

## Backend changes

See `openui-system-prompt` proposal. `_coach_reply` swaps "Answer in Markdown"
for the OpenUI system prompt (prepended before book context) and instructs the
model to emit OpenUI Lang. The JSON schema stays `{"reply": string}`.

## Not In Scope

- Exercise surfaces (separate proposal: `openui-exercise-surfaces`).
- Design-token mapping from `--lk-*` to OpenUI component styles (follow-up).
- Coach-tool rendering in chat (deferred).
- Streaming (deferred).
- Removing `react-markdown` from `package.json` (keep dependency for now;
  only remove imports from `MessageList`).

## Done Criterion

1. A coach reply renders via `<Renderer>` using `openuiChatLibrary`.
2. No `react-markdown` import in `MessageList.tsx`.
3. `npm run build` and `npm run lint` pass.
4. Existing `useConversation` regression test still passes (text shape unchanged:
   `{ reply: string }`).
5. A real coach reply produces parseable OpenUI Lang (manual check).