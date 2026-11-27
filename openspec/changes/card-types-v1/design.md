# Design — card-types-v1

## Context

See proposal.md → Why. Today the type of a feed card is implicit: the feed API
builds "exercise" and "idea" dicts in `lifekit/serve/server.py`
(`_exercise_dict`, `_resurfaced_idea`). No module owns the idea of a "card
type". The project rule is "classes + config (JSON/YAML) over flag-heavy
scripts", and Pydantic already validates model output in
`lifekit/extract/extractor.py`.

## Goals / Non-Goals

**Goals:**
- One file that lists the six types, and one module that validates card content
  and status transitions against it.
- The type definitions are plain enough that a person can edit the TOML file to
  change a label or a coach instruction.

**Non-Goals:**
- No database tables (card-generation and feed-v1 add them).
- No UI components (card-generation adds them).
- No user-defined or per-book card types.

## Decisions

### D1. TOML for labels and prompts, Pydantic for content shape

`lifekit/cards/card_types.toml` holds, per type: `description`, `item_kinds`,
`allowed_stances`, `source_label`, `done_label`, `surface` (a short text that
tells the card generator which components the surface must use), and
`coach_instruction`.

`lifekit/cards/types.py` holds one Pydantic model per type for the content
fields (for example `PracticeContent(purpose: str, steps: list[str])` with
`min_length=1, max_length=10`). Field shapes are code because Pydantic gives
JSON schemas for free (`model_json_schema()`); card-generation passes that
schema to `LLMProvider.chat_json_schema` (see `lifekit/llm/base.py`).

Alternative: put field shapes in TOML too and build models at runtime. Rejected:
more code, worse error messages, and no editor help.

The module checks at import time that the TOML tables equal the Pydantic model
set. A mismatch raises at import, so a half-added type cannot ship.

Sketch of the TOML table:

```toml
[reflect]
description = "A journal prompt the author asks the reader to write about."
item_kinds = ["prompt"]
allowed_stances = ["author_instructs"]
source_label = "From the book"
done_label = "Save and finish"
surface = """
A TextArea named "entry" for the answer, then the follow-up prompts as
TextContent, then a DoneButton."""
coach_instruction = """
Ask one follow-up question at a time about what the user wrote. Do not
interpret their personality or label them."""
```

### D2. Public API of `lifekit.cards.types`

| Name | What it does |
|------|--------------|
| `CARD_TYPES` | Ordered tuple of the six type names. |
| `TypeSpec` | Frozen dataclass loaded from the TOML table. `spec(type)` returns it. |
| `content_model(type)` | Returns the Pydantic model class for a type. |
| `card_type_for(item_kind)` | Returns the card type or `None`. |
| `validate_card(type, title, quote, stance, content)` | Raises `CardValidationError` with every problem listed, not only the first. |
| `next_status(current, target, previous=None)` | Returns the new status or raises `InvalidTransition`. |
| `can_finish(type, content, surface_state)` | Returns `(ok, missing)` for the done action (worksheet required fields, question reveal). |
| `source_label(stance)` | "From the book" or "LifeKit question". |

`can_finish` reads the surface state keys that the card-generation slice fixes:
worksheet field values live under the field id, and the question reveal sets
`revealed: true`. These keys are part of this design so that both slices agree.

### D3. Status machine in code, not in the database

The transitions are a small dict in `types.py`. The database stores the current
status and the status before hiding (`card_state.prev_status`, added by
feed-v1). Alternative: a CHECK constraint per transition in SQLite. Rejected:
SQLite cannot check transitions, only values.

### D4. Question cards are derived, one per body chapter

Books seldom print self-check questions with answers. A question card is made
by the card generator from the highest-rated idea or rule item of each body
chapter. It carries stance `inferred` and the label "LifeKit question", so the
user can tell it apart from the author's words. The author's answer is the
item's text plus its quote. This keeps the "grounded" principle: the answer
always points to a passage.

Alternative: the extractor emits questions. Rejected: the model would invent
questions without a passage that answers them.

### D5. Insights have a done action

The user asked to brute-force the feed with every idea. Without a done action,
insights would stay in the feed forever and the feed would never get shorter.
"Got it" moves an insight to `done`, and done cards leave the feed.

## Risks / Trade-offs

- [Six types are too few — for example "a list of resources" has no home] →
  The mapping returns `None` for unknown kinds and the extractor counts them.
  Review the counts in the usefulness report before adding a type.
- [Habit cards never leave the feed until "Stop tracking"] → This is the
  intended behavior for v1. Revisit in dogfood if habits crowd the feed.
- [The `practice` vs `habit` split depends on the model reading "every day" or
  "each week" in the text] → The golden-set labels in item-extraction-v2
  measure it; fix the prompt if the report shows confusion.

## Open Questions

- Exact wording of each coach instruction. It can change in the TOML file at any time
  without changing specs or tasks.
