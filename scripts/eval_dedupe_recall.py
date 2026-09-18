#!/usr/bin/env python3
"""Dedupe-aware recall: run Step 3 reduce over the qwen eval extractions,
then score the 20 ground-truth exercises against the DEDUPED set.

Raw recall (19/20) was measured on 156 fragmented records. What the coach
consumes is the deduped `exercises` table, so this is the number that matters.
BACKLOG E2.
"""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.extract.extractor import ChapterExtraction
from lifekit.reduce.reducer import normalize_title, reduce_extractions

EVAL_DIR = Path(__file__).resolve().parent.parent / "evals" / "step2-recall-qwen3.8-27b-q8_0"
EXTRACTIONS = EVAL_DIR / "extractions_qwen3.8-27b-q8_0.json"

# Ground-truth keyword -> label. Keys chosen to match the eval's semantic
# review (see evals/.../README.md): fragmentation-aware.
GT = {
    "dashboard": "Health/Work/Play/Love Dashboard",
    "workview": "Workview and Lifeview",
    "good time journal": "Good Time Journal",
    "mining the mountaintop": "Mining the Mountaintop",
    "mind map": "Mind Mapping",
    "odyssey": "Odyssey Plans",
    "prototype": "Build Prototypes for Your Odyssey Questions",
    "life design interview": "Life Design Interview",
    "brainstorm": "Brainstorming Prototype Experiences",
    "résumé": "Internet Job Search Tips",  # fragmented into 8 tip records
    "hidden job market": "Cracking the Hidden Job Market",
    "choosing process": "Life Design Choosing Process",
    "grokking": "Grokking a Choice",
    "personal practices": "Personal Practices for Discernment",
    "failure reframe": "Failure Reframe",
    "building a team": "Build Your Life Design Team",
    "mentor": "Find and Use Mentors",
    "designing your way forward": "Designing Your Way Forward",
    "be curious": "Five Mind-Sets as Daily Questions",  # fragmented into 5
    "ask-for-help journal": "Ask-for-Help Journal",
}


def main() -> int:
    raw = json.loads(EXTRACTIONS.read_text())
    extractions = [
        ChapterExtraction.model_validate(raw[k])
        for k in sorted(raw.keys(), key=int)
    ]

    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "dedupe_eval.db")
        summary = reduce_extractions("dyl-eval", db, extractions)

    conn = sqlite3.connect(db) if False else None  # db was temp; re-run in place
    # Re-run into a persistent temp file so we can inspect below.
    db2 = "/tmp/dedupe_recall.db"
    Path(db2).unlink(missing_ok=True)
    summary = reduce_extractions("dyl-eval", db2, extractions)
    conn = sqlite3.connect(db2)
    titles = [r[0] for r in conn.execute(
        "SELECT title FROM exercises WHERE book_id = 'dyl-eval'").fetchall()]
    normed = [normalize_title(t) for t in titles]
    conn.close()

    print(f"raw records: {summary['candidates']}")
    print(f"deduped exercises: {summary['exercises']}")
    print(f"merges: {summary['merges']}")
    print(f"key_ideas: {summary['key_ideas']}")
    print()

    hits, misses = [], []
    for key, label in GT.items():
        found = [t for t in titles if key in t.lower()]
        if found:
            hits.append(label)
        else:
            misses.append(label)
    print(f"dedupe-aware recall: {len(hits)}/{len(GT)} = {len(hits)/len(GT):.0%}")
    if misses:
        print("missing:", misses)
    print()

    # Surviving fragmentation: near-duplicate titles that dedupe did NOT merge
    from collections import Counter
    words = Counter()
    for t in normed:
        words[t] += 1
    dups = {t: n for t, n in words.items() if n > 1}
    print(f"exact-duplicate titles surviving dedupe: {len(dups)}")
    for t, n in sorted(dups.items(), key=lambda x: -x[1])[:10]:
        print(f"  x{n}: {t[:70]}")

    # Near-dupes by shared first 3 words (fragmentation pattern detector)
    from collections import defaultdict
    buckets = defaultdict(list)
    for t in titles:
        w = normalize_title(t).split()[:3]
        buckets[" ".join(w)].append(t)
    near = {k: v for k, v in buckets.items() if len(v) > 1}
    print(f"\nnear-duplicate title groups (shared 3-word prefix): {len(near)}")
    for k in sorted(near, key=lambda k: -len(near[k]))[:12]:
        print(f"  [{k}] x{len(near[k])}:")
        for t in near[k][:4]:
            print(f"    - {t[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
