## Destination

A spec + locked decisions for adopting OpenUI as a hybrid renderer in the chat surface (and a plan for absorbing the exercise surfaces), ready to hand off to implementation as an openspec change. No code in this map.

## Notes

Domain: OpenUI hybrid renderer for chat (and later exercise surfaces). Skills every session should consult: `frontend-design`, `impeccable`, `ponytail`. Standing preference: smallest change; no fallback code paths ("no fallback scope creep"); local-first (no cloud Gateway).

## Decisions so far

- [Do-over vs hybrid](issues/01-components-in-openui-library.md): hybrid — keep the Next.js shell/sidebar/theme/feed; OpenUI renders only inside assistant messages (and later exercise surfaces). Full redo buys nothing.
- [Components in OpenUI library](issues/01-components-in-openui-library.md): minimal custom library (`frontend/src/lib/openui.tsx`: Card + TextContent) — built-in's 53k prompt rejected for chat; OpenUI's Card replaces the message bubble (OpenUI owns the visual); user messages stay plain text.
- [Scope of surfaces](issues/01-components-in-openui-library.md): chat only first; exercise surfaces planned but later (they don't exist yet).
- [Backend risk](issues/01-components-in-openui-library.md): assume the local Ollama model emits valid OpenUI Lang; no research ticket. If output breaks, fix the prompt/model, not the renderer.
- [Coach tools](issues/01-components-in-openui-library.md): chat stays RAG-grounded only; no tool rendering in this slice.
- [Component library strategy](issues/01-components-in-openui-library.md): extend built-in `openuiChatLibrary` for the chat slice first; map `--lk-*` tokens in a follow-up.
- [Markdown fallback](issues/01-components-in-openui-library.md): dropped — one renderer, one path. No fallback scope creep.
- [Exercise surfaces alignment](issues/02-openui-to-exercise-surfaces.md): absorb A2UI into OpenUI — one library, one spec, one prompt. The A2UI component registry becomes OpenUI components.
- [Branch](issues/01-components-in-openui-library.md): plain branch `feature/openui-hybrid-chat` (no worktree).
- [System prompt assembly](issues/03-system-prompt-assembly.md): prepend OpenUI system prompt before the book context; keep both.
- [No fallback scope creep principle](issues/01-components-in-openui-library.md): recorded in project AGENTS.md working agreements.

## Not yet specified

- Exact CSS token mapping from `--lk-*` to OpenUI component styles (follow-up slice).
- Test updates: `useConversation` regression test and feed API tests assert markdown shapes; will need rewriting for OpenUI Lang output.
- Whether streaming should be added later (current chat is whole-reply; OpenUI renderer supports `isStreaming`).

## Out of scope

- Replacing the feed/sidebar/theme shell with OpenUI (ruled out: shell is shipped and working; OpenUI is a renderer, not a framework).
- CopilotKit (ruled out: cloud-dependent, replaces conversation layer, fights local-first).
- Coach tool rendering in chat (deferred to a future slice).
- Notifications, journal TipTap, RAG upgrade (intent never-build / deferred).