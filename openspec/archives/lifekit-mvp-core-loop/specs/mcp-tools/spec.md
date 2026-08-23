## ADDED Requirements

### Requirement: MCP server exposes get_next_task tool
The system SHALL expose an MCP tool `get_next_task` (no required arguments, optional `plan_id: str`). It SHALL query the `tasks` table for the lowest `day_number` task with `status='pending'`. The response SHALL be a JSON object with fields: `task_id`, `day_number`, `title`, `description`, `estimated_minutes`, `exercise_type`, `context_source`.

#### Scenario: Active tasks exist
- **WHEN** an LLM calls `get_next_task()`
- **THEN** the tool returns `{"ok": true, "result": {task fields}}` with all task fields populated

#### Scenario: No pending tasks remain
- **WHEN** an LLM calls `get_next_task()` and there are no pending tasks
- **THEN** the tool returns `{"ok": false, "error": "All tasks complete. Run forge to generate a new plan."}`

#### Scenario: No plan exists at all
- **WHEN** an LLM calls `get_next_task()` and no plans exist in the database
- **THEN** the tool returns `{"ok": false, "error": "No plan found. Run 'make bootstrap', then ingest a book and run 'forge'."}`

### Requirement: MCP server exposes complete_task tool
The system SHALL expose an MCP tool `complete_task(task_id: int, notes: str = "")`. It SHALL update `tasks.status` to 'complete', set `tasks.completed_at`, and insert a row into `sessions` with the provided notes. All three MUST be wrapped in a single SQL transaction.

#### Scenario: Valid task is completed
- **WHEN** an LLM calls `complete_task(task_id=5, notes="Understood the 4 laws")`
- **THEN** `tasks` row 5 has `status='complete'` and a `sessions` row is inserted with the notes

#### Scenario: Already-completed task
- **WHEN** `complete_task()` is called with a task_id that is already complete
- **THEN** the tool returns `{"ok": false, "error": "task_already_completed"}` without modifying the database

#### Scenario: Invalid task_id
- **WHEN** `complete_task()` is called with a task_id that does not exist
- **THEN** the tool returns `{"ok": false, "error": "task_not_found"}`

### Requirement: MCP server exposes get_plan_status tool
The system SHALL expose an MCP tool `get_plan_status(plan_id: str = "")` (uses most recent plan if no ID given). It SHALL return a JSON object with: `plan_id`, `book_title`, `user_intent`, `total_tasks`, `completed_tasks`, `pending_tasks`, `completion_percentage` (0–100).

#### Scenario: Plan with mixed task statuses
- **WHEN** `get_plan_status()` is called and 3 of 10 tasks are complete
- **THEN** the tool returns `{"ok": true, "result": {"completion_percentage": 30}}` with accurate counts

#### Scenario: No plan exists
- **WHEN** `get_plan_status()` is called and no plans exist
- **THEN** the tool returns `{"ok": false, "error": "no_plan_found"}`

### Requirement: MCP server runs via stdio transport
The system SHALL start the FastMCP server using stdio transport when run as `python -m lifekit.mcp.server`. The server SHALL log startup information to stderr (not stdout) to avoid corrupting the MCP JSON stream.

#### Scenario: Server starts without error
- **WHEN** `python -m lifekit.mcp.server` is executed with a valid database path
- **THEN** the process blocks waiting for MCP client input and does not exit immediately

#### Scenario: Claude Desktop integration
- **WHEN** Claude Desktop is configured with `"command": "python", "args": ["-m", "lifekit.mcp.server"]`
- **THEN** the three LifeKit tools appear in Claude's tool list

### Requirement: All MCP tool responses follow consistent envelope format
The system SHALL use `{"ok": bool, "result": data | null, "error": string | null}` for all tool responses. When `ok=true`, `result` contains the payload and `error=null`. When `ok=false`, `error` contains the error code and `result=null`.
