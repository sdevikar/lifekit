"""Step 4: LLM-as-judge sampling (10%)."""

import random
import sqlite3
from pathlib import Path

from lifekit.db.schema import init_db

JUDGE_PROMPT = """You are reviewing an exercise extracted from a self-help book chapter.

Exercise title: {title}
Purpose: {purpose}
Steps: {steps}
Source quote: {quote}

Chapter excerpt (first 2000 chars):
{excerpt}

Is this exercise faithfully grounded in the chapter? Rate 1-5 (5=perfectly
grounded, 1=hallucinated) and explain in one sentence. Respond as JSON:
{{"score": <1-5>, "rationale": "<one sentence>"}}"""


def sample_for_judge(exercise_ids: list[int], pct: float = 0.10, seed: int = 42) -> list[int]:
    """Deterministically sample pct of IDs (min 1)."""
    n = max(1, int(len(exercise_ids) * pct))
    rng = random.Random(seed)
    return sorted(rng.sample(exercise_ids, min(n, len(exercise_ids))))


def judge_exercise(exercise: dict, chapter_text: str, client=None, model: str = "qwen3.6:latest") -> dict:
    """Ask the model to rate grounding. Returns {score, rationale}."""
    if client is None:
        return {"score": None, "rationale": "no client; skipped"}
    import json
    prompt = JUDGE_PROMPT.format(
        title=exercise["title"],
        purpose=exercise["purpose"],
        steps=exercise["steps"],
        quote=exercise["source_quote"][:300],
        excerpt=chapter_text[:2000],
    )
    out = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    text = out["message"]["content"]
    try:
        data = json.loads(text)
        return {"score": int(data["score"]), "rationale": data["rationale"]}
    except Exception:
        return {"score": None, "rationale": f"unparseable: {text[:100]}"}


def run_judge_sample(db_path: str | Path, book_id: str, chapters: list[tuple[str, str]],
                     client=None, pct: float = 0.10) -> dict:
    """Sample 10%, judge each, persist to judge_log."""
    db_path = str(db_path)
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    text_by_title = {t: txt for t, txt in chapters}

    rows = conn.execute(
        "SELECT id, title, purpose, steps, source_quote, chapter_title FROM exercises WHERE book_id = ?",
        (book_id,),
    ).fetchall()
    ids = [r[0] for r in rows]
    sampled_ids = set(sample_for_judge(ids, pct=pct))
    by_id = {r[0]: r for r in rows}

    results = []
    for ex_id in sampled_ids:
        r = by_id[ex_id]
        ex = {"title": r[1], "purpose": r[2], "steps": r[3], "source_quote": r[4]}
        text = text_by_title.get(r[5], "")
        verdict = judge_exercise(ex, text, client=client)
        conn.execute(
            "INSERT INTO judge_log (book_id, exercise_id, score, rationale) VALUES (?, ?, ?, ?)",
            (book_id, ex_id, verdict["score"], verdict["rationale"]),
        )
        results.append((ex_id, verdict["score"]))

    conn.commit()
    conn.close()
    return {"sampled": len(results), "scores": results}
