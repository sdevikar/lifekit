# LifeKit — Runtime Design

## Resurfacing Engine

```
Daily Briefing
    |
    +-- 1. Today's Exercise
    |      FSRS scheduler picks from due exercises
    |      Ordered by retrievability (due first)
    |
    +-- 2. Resurfaced Idea
    |      Pick from previously-seen ideas
    |      Priority: ideas with fading priority
    |      User never sees the score
    |
    +-- 3. Fading Ideas
           List of ideas due for a touch
           Plain list, no streaks, no guilt
```

## FSRS Adaptation

| FSRS concept | LifeKit adaptation |
|--------------|-------------------|
| Card | Exercise or key idea |
| Review | Completion or idea signal |
| Rating | Implicit: completed=Good, partial=Hard, skipped=Again |
| Stability | Days until next resurface |
| Difficulty | How often the item is skipped |
| Retrievability | Priority for today's briefing |

**Constraint:** The user never sees Again/Hard/Good/Easy, retention percentages, or any number.

## Grounded Chat

```
User message
    |
    v
Retrieval: FTS5 query over exercises + key_ideas
    |
    v
Grounded context (citations from book)
    |
    v
LLM phrases reply (prose only, no decisions)
    |
    v
Persist turn -> return message
```

**Constraint:** The LLM never tests, scores, or gates the user. Conversation, not examination.

## Deterministic vs. Generative Split

| Decision | Owner |
|----------|-------|
| What resurfaces today | Deterministic runtime (FSRS) |
| When an idea fades | Deterministic runtime |
| What the user sees | Deterministic runtime -> UI |
| How the coach phrases a reply | LLM |
| Whether the user completed | Self-declared (user) |
| What counts as a completion | Deterministic runtime |
