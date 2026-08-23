## ADDED Requirements

### Requirement: Plan forge teaches using a configurable method
The system SHALL allow users to select a teaching method from five options when generating a plan: `auto`, `socratic`, `feynman`, `analogical`, or `spaced_recall`. When `auto` is selected the system defaults to `socratic`. The teaching method SHALL be stored in the `plans.teaching_method` column (TEXT NOT NULL) and used to shape the LLM prompt's system message, controlling *how* tasks are framed — not just *what* they are.

#### Teaching methods definitions
| Value | How it frames tasks | Key behavioural instruction injected into system prompt |
|-------|--------------------|----------------------------------------------------------|
| `auto` | Falls back to socratic | Same as socratic |
| `socratic` | Guided inquiry and self-discovery | "Frame every task as questions pushing toward self-discovery" |
| `feynman` | Teaching to a beginner with simple analogies | "Frame every task as explaining to a 10-year-old" with daily-life metaphors |
| `analogical` | Cross-domain connections (music, sports, cooking, etc.) | "Compare concepts to unrelated domains to build rich mental models" |
| `spaced_recall` | Active retrieval following the Leitner principle | "Frame every task as memory recall — never passive re-reading" |

#### Scenario: User selects a teaching method
- **WHEN** `forge_plan(book_id, intent, duration_weeks, teaching_method='feynman')` is called
- **THEN** the `plans.teaching_method` column stores `'feynman'` and the LLM system prompt includes Feynman-method behavioural instructions that shape every generated task's framing

#### Scenario: User selects 'auto' (default)
- **WHEN** `forge_plan(book_id, intent, duration_weeks)` is called without specifying `teaching_method`
- **THEN** the parameter resolves to `'socratic'`, it is stored in `plans.teaching_method` as `'socratic'`, and socratic-style queries drive task generation

#### Scenario: Invalid teaching method is rejected
- **WHEN** `forge_plan(teaching_method='telepathy')` is called
- **THEN** a `ValueError` is raised with the message listing all allowed values before any Ollama call or DB operation occurs

### Requirement: Plan forge generates a SMART weekly plan via Ollama (unchanged)
The system SHALL call the Ollama Python client with the configured model (`OLLAMA_MODEL` env var, default `qwen3.6:latest`). The prompt SHALL include: book title, author, the first 1000 tokens of book content (from `book_chunks`), and the user's `intent` string. The model SHALL be instructed to return a JSON array of tasks.

#### Scenario: Successful plan generation
- **WHEN** `forge_plan(book_id, intent, duration_weeks)` is called and Ollama is running
- **THEN** a `plans` row is created and `tasks` rows are inserted, one per day up to `duration_weeks * 7`

#### Scenario: Plan forge uses the correct book
- **WHEN** `forge_plan(book_id=X)` is called
- **THEN** only content from book X is sent to Ollama (not content from other books)

### Requirement: Ollama response is validated against a Pydantic schema
The system SHALL parse the Ollama response as JSON and validate it against a `PlanResponse` Pydantic model with fields: `weekly_plan: list[TaskItem]` where `TaskItem` has: `day: int`, `title: str`, `description: str`, `estimated_minutes: int`, `exercise_type: str`, `context_source: str`.

#### Scenario: Valid JSON response is stored
- **WHEN** Ollama returns valid JSON matching the schema
- **THEN** tasks are inserted into the database with all fields populated

#### Scenario: Invalid JSON response is handled gracefully
- **WHEN** Ollama returns text that cannot be parsed as the expected JSON schema
- **THEN** a single fallback task is created with `title="Read and reflect"`, `description` set to the raw LLM response, and `exercise_type="reading"`, and the `raw_llm_response` column in `plans` stores the full raw text

### Requirement: Only one active plan per book is allowed
The system SHALL check whether an active plan already exists for the given `book_id`. If one exists, `forge_plan()` SHALL raise a `PlanExistsError` with a message indicating the existing plan ID.

#### Scenario: Duplicate plan attempt
- **WHEN** `forge_plan()` is called for a book that already has tasks in status 'pending'
- **THEN** a `PlanExistsError` is raised and no new plan is created

### Requirement: Ollama connection failure is surfaced clearly
The system SHALL catch `ollama.ResponseError` and `ConnectionRefusedError` from the Ollama client. On failure, a `RuntimeError` SHALL be raised with message: "Ollama not reachable. Is it running? Try: ollama serve".

#### Scenario: Ollama is not running
- **WHEN** `forge_plan()` is called but Ollama is not running
- **THEN** a `RuntimeError` is raised with the instructional message
