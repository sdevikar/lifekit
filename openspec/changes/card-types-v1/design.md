# Design — card-types-v1

## Context

See proposal.md → Why. Today the type of a feed card is implicit: the feed API
builds "exercise" and "idea" dicts in `lifekit/serve/server.py`
(`_exercise_dict`, `_resurfaced_idea`). No module owns the idea of a "card
type". The project rule is "classes + config over flag-heavy scripts", and
Pydantic already validates model output in `lifekit/extract/extractor.py`.

ROADMAP D2 and D9 fix the interaction: the user acts only by commenting, and
cards have no done state. So this slice has no status machine.

## Goals / Non-Goals

**Goals:**
- One file that lists the five types, and one module that validates card
  content against it.
- The type definitions are plain enough that a person can edit the TOML file to
  change a hint or a coach instruction.

**Non-Goals:**
- No database tables (card-generation and feed-v1 add them).
- No UI components (card-generation adds them).
- No card status, done actions, or surfaces (retired, ROADMAP D2 and D9).
- No `worksheet` type (v2, ROADMAP D7).
- No user-defined or per-book card types.

## Decisions

### D1. TOML for labels and prompts, Pydantic for content shape

`lifekit/cards/card_types.toml` holds, per type: `description`, `item_kinds`,
`allowed_stances`, `source_label`, `comment_hint`, and `coach_instruction`.

`lifekit/cards/types.py` holds one Pydantic model per type for the content
fields (for example `PracticeContent(purpose: str, steps: list[str])` with
`min_length=1, max_length=12`). Field shapes are code because Pydantic gives
JSON schemas for free (`model_json_schema()`); item extraction and question
generation pass that schema to `LLMProvider.chat_json_schema` (see
`lifekit/llm/base.py`).

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
comment_hint = "Write your entry…"
coach_instruction = """
The user's comment is a journal entry. Reply in two or three sentences: name
one thing they wrote, and ask at most one follow-up question. Do not interpret
their personality or label them."""
```

### D2. Public API of `lifekit.cards.types`

| Name | What it does |
|------|--------------|
| `CARD_TYPES` | Ordered tuple of the five type names. |
| `TypeSpec` | Frozen dataclass loaded from the TOML table. `spec(type)` returns it. |
| `content_model(type)` | Returns the Pydantic model class for a type. |
| `card_type_for(item_kind)` | Returns the card type or `None`. |
| `validate_card(type, title, quote, stance, content)` | Raises `CardValidationError` with every problem listed, not only the first. |
| `source_label(stance)` | "From the book" or "LifeKit question". |

### D3. Templates become practice cards

A template in a book is a form or self-assessment, for example "Rate Health,
Work, Play, and Love from 0 to full". In v1 the extractor writes it as a
practice item: `purpose` is the template's goal and each field becomes one
step ("Rate your Health from 0 to full."). The user answers all of them in one
comment. This keeps the content in v1 with no extra type. v2 adds `worksheet`
with a form that posts as one comment (ROADMAP D7). Twelve steps, not ten,
leave room for the larger templates.

### D4. Question cards are derived, one per body chapter

Books seldom print self-check questions with answers. A question card is made
by the card generator from the highest-rated insight item of each body chapter.
It carries stance `inferred` and the label "LifeKit question", so the user can
tell it apart from the author's words. The author's answer is the item's text
plus its quote. This keeps the "grounded" principle: the answer always points
to a passage.

Alternative: the extractor emits questions. Rejected: the model would invent
questions without a passage that answers them.

## Risks / Trade-offs

- [Five types are too few — for example "a list of resources" has no home] →
  The mapping returns `None` for unknown kinds and the extractor counts them.
  Review the counts in the usefulness report before adding a type.
- [A long template is clumsy as steps in one comment] → Accepted for v1. The
  dogfood review notes which templates felt clumsy; they are the test set for
  the v2 worksheet.
- [The `practice` vs `habit` split depends on the model reading "every day" or
  "each week" in the text] → The golden-set labels in item-extraction-v2
  measure it; fix the prompt if the report shows confusion.

## Open Questions

- Exact wording of each hint and coach instruction. It can change in the TOML
  file at any time without changing specs or tasks.
