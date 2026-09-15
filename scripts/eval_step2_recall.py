#!/usr/bin/env python3
"""Step 2 done-criterion: full-book DYL extraction + recall vs. ground truth.

Dev-only runner: llama.cpp locally behind a tiny Ollama-interface shim
(``.chat(model, messages, format, options)``). Product code in
``lifekit/extract/`` stays Ollama-native; the shim lives only in this script.

Usage:
    python scripts/eval_step2_recall.py [--db DB] [--book-id ID] [--model PATH]

Writes JSON results to /home/hatch/workspace/lifekit-dev/.eval-step2/results.json and prints a summary.
"""
import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.extract.extractor import extract_chapter
import lifekit.extract.extractor as _ex_mod
from lifekit.store.chapter_splitter import Chapter

# Dev-eval only: smaller chunks + ctx to fit this machine's 7GB RAM.
# Product defaults (48k/60k chars) are unchanged in lifekit/extract/extractor.py.
_ex_mod.MAX_CHAPTER_CHARS = 16000
_ex_mod.SECTION_CHUNK_CHARS = 12000

GROUND_TRUTH = Path("/home/hatch/workspace/self-help-exercises/designing-your-life-exercises.md")


class LlamaCppShim:
    """Mimics ollama.Client.chat using llama.cpp with JSON-schema grammar."""

    def __init__(self, model_path: str, n_ctx: int = 8192, n_threads: int = 2):
        from llama_cpp import Llama

        self.llm = Llama(
            model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, verbose=False
        )

    def chat(self, model=None, messages=None, format=None, options=None):
        # Qwen3 "thinking" is verbose and slow on CPU; disable it for eval
        # speed (dev-only; product prompt is unchanged). The 8B model is
        # capable enough to follow the schema without thinking.
        msgs = []
        for m in messages or []:
            m = dict(m)
            if m.get("role") == "user" and isinstance(m.get("content"), str):
                m["content"] = m["content"].rstrip() + " /no_think"
            msgs.append(m)
        kwargs = {
            "messages": msgs,
            "temperature": (options or {}).get("temperature", 0.1),
        }
        if format:
            kwargs["response_format"] = {"type": "json_schema", "schema": format}
        import time as _t

        _t0 = _t.time()
        print(f"  [shim] request: {len(str(msgs))} chars prompt", flush=True)
        out = self.llm.create_chat_completion(**kwargs)
        _dt = _t.time() - _t0
        content = out["choices"][0]["message"]["content"]
        print(f"  [shim] done in {_dt:.0f}s, usage={out.get('usage', {})}", flush=True)
        # strip Qwen3 <think> blocks if present
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        return {"message": {"content": content}}


def load_chapters(db_path: str, book_id: str) -> list[Chapter]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT idx, title, content, page_start, page_end FROM chapters "
        "WHERE book_id = ? ORDER BY idx",
        (book_id,),
    ).fetchall()
    return [Chapter(index=r[0], title=r[1], text=r[2], page_start=r[3], page_end=r[4])
            for r in rows]


def ground_truth_titles() -> list[str]:
    titles = []
    for line in GROUND_TRUTH.read_text().splitlines():
        m = re.match(r"### (?:Exercise|Practice) \d+ — (.+)$", line.strip())
        if m:
            titles.append(m.group(1).strip())
    return titles


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def title_match(extracted: str, truth: str) -> bool:
    e, t = norm(extracted), norm(truth)
    if not e or not t:
        return False
    if t in e or e in t:
        return True
    et, tt = set(e.split()), set(t.split())
    overlap = len(et & tt) / max(len(tt), 1)
    return overlap >= 0.6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="/home/hatch/workspace/lifekit-dev/.eval-step2/lifekit.db")
    ap.add_argument("--book-id", default=None)
    ap.add_argument("--model", default=str(Path.home() / "workspace/models/Qwen3-4B-Q4_K_M.gguf"))
    ap.add_argument("--n-ctx", type=int, default=8192)
    ap.add_argument("--chapters", default=None, help="comma-separated idxs (default: all)")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    book_id = args.book_id
    if not book_id:
        row = conn.execute("SELECT book_id FROM chapters LIMIT 1").fetchone()
        if not row:
            sys.exit("no chapters in db; run the split CLI with --db-path first")
        book_id = row[0]
    chapters = load_chapters(args.db, book_id)
    if args.chapters:
        wanted = {int(x) for x in args.chapters.split(",")}
        chapters = [c for c in chapters if c.index in wanted]
    print(f"book_id={book_id}, {len(chapters)} chapters, model={args.model}", flush=True)

    client = LlamaCppShim(args.model, n_ctx=args.n_ctx)
    truths = ground_truth_titles()
    print(f"ground truth: {len(truths)} exercises", flush=True)

    out = Path("/home/hatch/workspace/lifekit-dev/.eval-step2/results.json")
    ext_path = Path("/home/hatch/workspace/lifekit-dev/.eval-step2/extractions.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Resumable: skip chapters already completed in a previous run.
    done = {}
    if out.exists():
        try:
            done = {r["idx"]: r for r in json.loads(out.read_text())["chapters"]
                    if r.get("ok")}
            print(f"resuming: {len(done)} chapters already done", flush=True)
        except Exception:
            done = {}
    extractions = {}
    if ext_path.exists():
        try:
            extractions = {int(k): v for k, v in json.loads(ext_path.read_text()).items()}
        except Exception:
            extractions = {}

    results = []
    for ch in chapters:
        if ch.index in done:
            results.append(done[ch.index])
            print(f"[{ch.index}] {ch.title}: skipped (already done)", flush=True)
            continue
        t0 = time.time()
        try:
            ext = extract_chapter(ch, client=client)
            ok = True
            err = None
            extractions[ch.index] = ext.model_dump()
        except Exception as e:  # noqa: BLE001
            ext, ok, err = None, False, f"{type(e).__name__}: {e}"
        dt = time.time() - t0

        grounded = total = 0
        ex_titles = []
        if ok:
            for ex in ext.exercises:
                total += 1
                ex_titles.append(ex.title)
                if ex.source_quote and ex.source_quote in ch.text:
                    grounded += 1
        rec = {
            "idx": ch.index, "title": ch.title, "ok": ok, "error": err,
            "seconds": round(dt, 1),
            "key_ideas": len(ext.key_ideas) if ok else 0,
            "exercises": ex_titles,
            "grounded": grounded, "total": total,
        }
        results.append(rec)
        # write-through progress (survives restarts)
        out.write_text(json.dumps({"chapters": results}, indent=2))
        ext_path.write_text(json.dumps({str(k): v for k, v in extractions.items()}))
        print(f"[{ch.index}] {ch.title}: ok={ok} "
              f"{len(ex_titles)} ex, {grounded}/{total} grounded, {dt:.0f}s", flush=True)

    all_extracted = [t for r in results for t in r["exercises"]]
    hits, misses = [], []
    for truth in truths:
        if any(title_match(e, truth) for e in all_extracted):
            hits.append(truth)
        else:
            misses.append(truth)
    total_q = sum(r["total"] for r in results)
    grounded_q = sum(r["grounded"] for r in results)

    summary = {
        "chapters": results,
        "extracted_titles": all_extracted,
        "recall": f"{len(hits)}/{len(truths)}",
        "hits": hits,
        "misses": misses,
        "quote_grounding": f"{grounded_q}/{total_q}",
    }
    out = Path("/home/hatch/workspace/lifekit-dev/.eval-step2/results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nRECALL: {len(hits)}/{len(truths)}")
    print(f"QUOTE GROUNDING: {grounded_q}/{total_q}")
    print("MISSES:")
    for m in misses:
        print(f"  - {m}")
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
