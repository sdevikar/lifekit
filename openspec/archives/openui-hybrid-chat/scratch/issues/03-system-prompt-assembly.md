Type: task
Status: open

## Question

Assemble the backend system prompt for `_coach_reply`: prepend the OpenUI system prompt (generated from the library spec via `library.prompt()` / CLI spec) before the book context, and instruct the model to emit OpenUI Lang instead of Markdown. Verify the model emits parseable output.

## Blocked by

01