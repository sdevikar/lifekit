# OpenUI System Prompt Assembly — Proposal

**Status: proposal only — do not implement yet.**

## Why

The backend (`lifekit/serve/server.py::_coach_reply`) currently instructs the
model to "Answer in Markdown" and returns the reply as a string. To render
coach replies through OpenUI, the model must emit OpenUI Lang. This proposal
changes the system prompt assembly: prepend the OpenUI system prompt (generated
from the component library spec) before the book context, and instruct the model
to emit OpenUI Lang instead of Markdown. The JSON schema and transport stay
unchanged.

## What Changes

Backend only (`lifekit/serve/server.py`). No frontend changes (those live in
`openui-hybrid-chat`).

## Decisions (locked)

- **Prepend, don't replace.** OpenUI system prompt first (teaches the language),
  then the book context (grounding). Keep both.
- **JSON schema unchanged.** Still `{"reply": string}`. The reply string now
  contains OpenUI Lang instead of Markdown.
- **No streaming.** Whole-reply call via `provider.chat_json_schema`.
- **Assume it works.** No research ticket; if output breaks, fix prompt/model.

## Implementation

1. Generate the OpenUI system prompt from the library spec. Options:
   - Run `npx @openuidev/cli generate src/lib/openui.tsx --spec` to produce
     `openui.spec.json`, then `generateSystemPrompt({ cloud: false, library })`
     (or `library.prompt()`) in Python. Since the backend is Python, either
     (a) commit the generated spec JSON and load it in Python, or (b) keep
     prompt generation in a small Node step invoked at build time.
   - Decision deferred to implementation: pick the option that keeps the prompt
     in sync with the component library with least glue.
2. In `_coach_reply`, replace:
   ```
   Answer in Markdown: bulleted lists for steps or options, **bold** for the key
   term, short paragraphs.
   ```
   with the OpenUI system prompt + "Emit only OpenUI Lang. Use Card as the root.
   Keep replies concise and actionable."
3. Keep the RAG context block (`\n\nBook context:\n{context}`) after the OpenUI
   prompt.
4. Parsing fallback unchanged: `json.loads(raw)` → `parsed.get("reply", "")`;
   on failure return `raw.strip()`.

## Not In Scope

- Frontend rendering (separate proposal: `openui-hybrid-chat`).
- Autofix / Gateway (cloud; not used — local-first).
- Coach-tool rendering (deferred).

## Done Criterion

1. `_coach_reply` system message contains the OpenUI system prompt + book
   context.
2. A real chat reply returns parseable OpenUI Lang (manual check).
3. `tests/test_feed_api.py::TestConversationMessages` still passes.