# LifeKit Book Model

**Status:** Draft proposal for review — 2026-09-20. Nothing here is approved
until the open questions are decided.

## What it is

A **code index for a book**:

| Code index | Book model |
|---|---|
| Module tree | Structure tree: book → parts → chapters → sections |
| Symbols | Typed actionable items: exercises, decision rules, anti-patterns, key ideas, principles |
| Call graph | Relations between items: prerequisite-of, reframes, feeds-into |

RAG answers *"what did the book say?"* — the book model answers *"what
should this person do now?"* The learning runtime reasons over the book
model; the RAG corpus stays as grounding, citations, and deep dives.

This is the proprietary layer. Retrieval, scheduling, and UI polish are
commodity — the per-book structured, relational, quote-grounded model is the
moat.

## Artifacts to extract

### 1. Structure tree (the skeleton)

`book → parts → chapters → sections`. Per node: title, order, 1–2 sentence
summary, source anchor (TOC entry / page range / chunk range). Every
actionable item hangs off a tree node. Largely derivable from the existing
TOC-first extraction — this is structuring, not new extraction.

### 2. Typed actionable items (the symbols)

| Type | Shape | Source |
|---|---|---|
| `exercise` | Prompt + steps + chapter ref + quote | Existing table (144 for DYL) |
| `key_idea` | Distilled claim, quote-grounded | Existing table (875 — noisy, needs typing/filtering) |
| `decision_rule` | "When X, do Y" conditional | BACKLOG F1 — structuring pass |
| `anti_pattern` | "Don't do X" / common mistake + correction | BACKLOG F2 — structuring pass |
| `principle` | Durable claim the book makes (candidate) | Structuring pass over key ideas |
| `faq` | Question the book answers (candidate) | BACKLOG F12 shape |

Per item: id, type, title, body, structure-node anchor, **≥1 verbatim quote**
(enforced by the existing validation harness — an item without a quote is not
real), tags (F14 auto-tagging), difficulty / time estimate (candidate).

### 3. Relations (the call graph)

Proposed starter set:

- `prerequisite-of` — do A before B makes sense (scheduling order).
- `reframes` — idea B reframes idea A (used when the user is stuck: offer the
  reframe).
- `feeds-into` — practice A builds toward outcome/capability B.

Candidates: `exemplifies` (story/example illustrates the item), `contradicts`
(two items in tension — the book acknowledging tradeoffs).

### 4. Quote grounding (non-negotiable)

Every item carries ≥1 verbatim quote. The existing Step-4 validation harness
enforces this. The book model never contains ungrounded LLM invention.

## Minimal v1 schema (SQLite, grows out of existing tables)

```sql
structure_nodes(id, book_id, parent_id, kind, -- 'part'|'chapter'|'section'
                ord, title, summary, source_anchor);

items(id, book_id, node_id, type, -- 'exercise'|'key_idea'|'decision_rule'|
                              -- 'anti_pattern'|'principle'|'faq'
            title, body, quotes,  -- quotes: JSON array of verbatim strings
            tags,                -- JSON array (F14)
            difficulty, minutes, -- candidate
            created_from);        -- 'extraction'|'structuring-pass'

relations(id, book_id, from_item, to_item,
          rel,                   -- 'prerequisite-of'|'reframes'|'feeds-into'
          evidence);             -- short why, quote-backed
```

One `items` table with a `type` column (not per-type tables): the runtime's
core query — "what should this person do now?" — cuts across types, and the
type enum can grow without schema migrations. Existing `exercises` /
`key_ideas` tables seed `items` via a migration, not a rewrite.

## Build path (no re-extraction)

Structuring passes over the existing extraction corpus:

1. F14 auto-tagging → tags on items.
2. F1 decision rules + F2 anti-patterns → new typed items from key ideas.
3. F12 FAQ shape → candidate `faq` items.
4. Key-idea typing/filtering → promote the real ideas, demote noise.
5. Relations pass → LLM proposes relations, each backed by quotes, human
   spot-checks.
6. Migration of `exercises` / `key_ideas` into `items` + `structure_nodes`.

## What the runtime does with it

- **Surfacing:** pick the next exercise/idea honoring `prerequisite-of`
  order; when the user stalls, offer the item that `reframes` the stuck one.
- **Teach-back grading:** judge the user's explanation against the item, its
  quotes, and its relations (`reframes` links are where misconceptions hide).
- **Briefs:** value-recall and milestone angles reference specific items,
  not vibes.

## Open questions

1. One `items` table with a type column, or per-type tables?
2. Starter relation set: the three proposed, or include
   `exemplifies` / `contradicts` from the start?
3. Key ideas: type them into subtypes, or keep flat with a quality filter?
4. `principle` as a first-class type, or fold into `key_ideas`?
5. Difficulty / time estimates per item — needed for scheduling, or skip for
   v1?
6. Relations pass: fully LLM-proposed with human spot-check, or
   human-authored for book one?
