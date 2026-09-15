"""Test 4B extraction with plain JSON mode (no grammar) on 2 chapters."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.extract.extractor import (
    SYSTEM_PROMPT, build_messages, ChapterExtraction,
)
import lifekit.extract.extractor as ex_mod
from lifekit.store.chapter_splitter import Chapter
import sqlite3

# Small chapters with known exercises
CHAPTER_IDXS = [4, 5]  # 2. Building a Compass, 3. Wayfinding

def main():
    from llama_cpp import Llama
    model_path = str(Path.home() / "workspace/models/Qwen3-4B-Q4_K_M.gguf")
    print(f"loading {model_path}...", flush=True)
    llm = Llama(model_path=model_path, n_ctx=8192, n_threads=2, verbose=False)
    print("loaded", flush=True)

    db = sqlite3.connect("/home/hatch/workspace/lifekit-dev/.eval-step2/lifekit.db")
    # Recreate DB if missing (we deleted .eval-step2)
    import subprocess
    if not Path("/home/hatch/workspace/lifekit-dev/.eval-step2/lifekit.db").exists():
        print("DB missing, re-splitting PDF...", flush=True)
        pdf = "/home/hatch/workspace/user/files/Bill_Burnett_-_Designing_Your_Life__How_to_Build_a_Well-Lived__Joyful_Life__2016__Knopf_Doubleday_Publishing_Group__-_libgen.li.pdf"
        Path("/home/hatch/workspace/lifekit-dev/.eval-step2").mkdir(parents=True, exist_ok=True)
        subprocess.run([
            sys.executable, "-m", "lifekit.store.split",
            "--pdf", pdf,
            "--db-path", "/home/hatch/workspace/lifekit-dev/.eval-step2/lifekit.db",
        ], cwd="/home/hatch/workspace/lifekit-dev", check=True)
        db = sqlite3.connect("/home/hatch/workspace/lifekit-dev/.eval-step2/lifekit.db")

    for idx in CHAPTER_IDXS:
        row = db.execute(
            "select title, content from chapters where idx=?", (idx,)
        ).fetchone()
        title, content = row
        # Use a small excerpt (first 8000 chars) to keep it fast
        excerpt = content[:8000]
        ch = Chapter(title=title, text=excerpt)
        system, user = build_messages(ch)
        user = user.rstrip() + " /no_think"

        print(f"\n=== Chapter {idx}: {title} ({len(excerpt)} chars) ===", flush=True)
        t0 = time.time()
        # Plain JSON mode, NO grammar
        out = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        dt = time.time() - t0
        text = out["choices"][0]["message"]["content"]
        print(f"  done in {dt:.0f}s, {len(text)} chars", flush=True)
        print(f"  raw start: {text[:200]}", flush=True)

        try:
            data = json.loads(text)
            ext = ChapterExtraction.model_validate(data)
            # Backfill chapter_title if missing
            if not ext.chapter_title:
                ext.chapter_title = title
            print(f"  OK: {len(ext.exercises)} exercises", flush=True)
            for ex in ext.exercises[:3]:
                grounded = ex.source_quote in excerpt
                print(f"    - {ex.title[:50]} | quote grounded: {grounded}", flush=True)
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {str(e)[:200]}", flush=True)

if __name__ == "__main__":
    main()
