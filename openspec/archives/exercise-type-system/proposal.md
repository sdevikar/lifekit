# Exercise Type System — Proposal

**Status: proposal only — do not implement yet.**

## Why

Every exercise in LifeKit is currently modeled identically: title, purpose,
steps, materials. Completion is always "did it / didn't it" with a free-text
note. But self-help books contain different **types** of exercises that need
different completion surfaces:

- An action is binary (done / not done).
- A journaling exercise produces a **text artifact**.
- A tracking exercise produces a **series of data points** over time.
- A questionnaire produces a **structured result** (scores, answers).
- A concept explanation produces a **written response** to a prompt.

The `completions` table can't represent any of that beyond a free-text note.
This proposal adds the type system and data model that makes all exercise
surfaces possible.

## What Changes

### Schema

**`lifekit/db/schema.py`** — add `exercise_type` and `exercise_config` to
`exercises`:

```sql
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    chapter_idx INTEGER,
    chapter_title TEXT NOT NULL,
    title TEXT NOT NULL,
    purpose TEXT NOT NULL,
    steps TEXT NOT NULL,  -- JSON list
    materials TEXT NOT NULL DEFAULT '[]',  -- JSON list
    source_quote TEXT NOT NULL,
    extra_quotes TEXT NOT NULL DEFAULT '[]',
    exercise_type TEXT NOT NULL DEFAULT 'action'
        CHECK(exercise_type IN (
            'action', 'journal', 'tracking',
            'questionnaire', 'concept_check', 'worksheet'
        )),
    exercise_config TEXT NOT NULL DEFAULT '{}',  -- JSON, type-specific
    UNIQUE(book_id, title)
);
```

`exercise_config` holds type-specific data:
- `journal`: `{ prompt: str }`
- `tracking`: `{ metric: str, unit: str, frequency: str }`
- `questionnaire`: `{ questions: [{ id, text, type, options? }] }`
- `concept_check`: `{ prompt: str }`
- `worksheet`: `{ fields: [{ id, label, type, options? }] }`

**New tables:**

```sql
CREATE TABLE IF NOT EXISTS exercise_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    response_type TEXT NOT NULL CHECK(response_type IN ('text', 'json')),
    response_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exercise_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    tracked_at TIMESTAMP NOT NULL,
    value TEXT NOT NULL,  -- JSON — flexible per metric
    note TEXT
);
```

### Feed API

**`lifekit/serve/server.py`** — include A2UI messages in exercise card responses:

```python
def _exercise_card(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "purpose": row["purpose"],
        "exercise_type": row["exercise_type"],
        "a2ui": {
            "type": row["exercise_type"],
            "exercise_id": row["id"],
            "config": json.loads(row["exercise_config"]),
        },
    }
```

New response endpoints:

| Route | Purpose |
|-------|---------|
| `POST /api/exercise/<id>/response` | Submit a text or JSON response |
| `POST /api/exercise/<id>/tracking` | Submit a tracking data point |
| `GET /api/exercise/<id>/tracking` | Get tracking history |

### Extraction pipeline

**`lifekit/extract/extractor.py`** — the LLM extraction assigns `exercise_type`
based on the exercise's characteristics:

| Signal | Type |
|--------|------|
| Has steps, is a behavior to do | `action` |
| Asks to write/reflect | `journal` |
| Asks to track/log over time | `tracking` |
| Has structured questions | `questionnaire` |
| Asks to explain/teach | `concept_check` |
| Has a template/fields to fill | `worksheet` |

The `Exercise` Pydantic model gains `exercise_type` and `exercise_config`
fields. The system prompt gains rules for type assignment.

### Component registry

**`frontend/src/components/exercises/registry.ts`** (new):

```ts
const registry: Record<ExerciseType, React.ComponentType<ExerciseProps>> = {
  action: ActionCard,
  journal: JournalPrompt,
  tracking: TrackingLog,
  questionnaire: QuestionnaireForm,
  concept_check: ConceptCheckInput,
  worksheet: WorksheetForm,
};
```

## Capabilities

### New Capabilities

- `exercise-types`: exercises carry a type; the feed returns A2UI messages;
  responses and tracking data persist in dedicated tables.

## Not In Scope

- The individual surface components (journal editor, tracking log, etc.) —
  separate proposals.
- The routing model (master-detail pane) — see
  `exercise-surface-routing/`.
- Migration of existing DYL exercises (all 144 default to `action`; can be
  re-extracted later).
- LLM-based type assignment heuristics — start with prompt engineering, upgrade
  to a classifier later.

## Done Criterion

1. Schema migration works: existing DBs gain the new columns and tables
   without data loss.
2. Feed API returns `a2ui` messages with the correct type.
3. `POST /api/exercise/<id>/response` and `POST /api/exercise/<id>/tracking`
   round-trip correctly.
4. Existing DYL exercises still work (all default to `action`).
5. `uv run pytest tests/ -v` passes.
6. `npm run build` and `npm run lint` pass in `frontend/`.
