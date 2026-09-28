# LifeKit — API Design

## Feed API (Flask, localhost:8765)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/briefing/today` | Today's exercise, resurfaced idea, fading ideas | None |
| POST | `/api/completions` | Log exercise completion | None |
| POST | `/api/idea-signals` | Log idea signal ("Still with me") | None |
| GET | `/api/conversations` | List conversations | None |
| POST | `/api/conversations` | Create conversation | None |
| GET | `/api/conversations/:id` | Get conversation with messages | None |
| POST | `/api/conversations/:id/messages` | Send message, get grounded reply | None |

## MCP Tools (FastMCP stdio)

| Tool | Purpose |
|------|---------|
| `list_exercises` | Paginated exercise listing |
| `search_exercises` | Natural-language exercise search |
| `get_exercise` | Exercise details |
| `complete_exercise` | Log completion + FSRS review |
| `due_exercises` | FSRS-due exercises |
| `list_key_ideas` | Key idea listing |
| `book_progress` | Per-book progress summary |

## Proposed MCP Tools (Stage 5)

| Tool | Purpose | Step |
|------|---------|------|
| `start_coaching_session` | Idempotent open/resume -> in_session | 8 |
| `get_coaching_context` | Session-start brief | 8 |
| `next_coached_exercise` | Exercise + motivation brief + context | 8 |
| `record_attempt` | Log attempt + reflection + affect | 8 |
| `end_coaching_session` | Review + recap + optional if-then intention | 8 |
| `list_intentions` / `resolve_intention` | Intention lifecycle | 8 |
| `get_momentum` | Momentum score | 9 |
| `get_momentum_brief` | Priority-selected brief for exercise | 9 |
| `get_due_nudges` | Polled nudge list | 9 |
| `interview_start` / `interview_answer` | Scripted elicitation protocol | 10 |
| `link_book_to_goal` | Book-goal linking biases selection | 10 |

## API Constraints

- **Localhost only.** Flask binds `127.0.0.1:8765`.
- **No auth.** Single-user local trust boundary.
- **No CORS.** Next.js proxy handles same-origin.
- **Request/response format:** JSON.
- **Error format:** `{"error": "message"}` with appropriate HTTP status.
