"""LifeKit dogfood UI — throwaway Streamlit app for the DYL MVP.

Run:  streamlit run ui/app.py
Reads the product DB (~/.lifekit/lifekit.db, override with LIFEKIT_DB).
Covers the three MVP user stories:
  1. browse book -> chapter -> exercise, do it, mark complete (FSRS scheduled)
  2. search box: "i want to do the mindmapping exercise" -> jump to it
  3. due-today view + progress
"""
import json
import os
import sqlite3
from pathlib import Path

import streamlit as st

DB = os.environ.get("LIFEKIT_DB", str(Path.home() / ".lifekit" / "lifekit.db"))
BOOK_ID = "dyl"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lifekit.coach.tools import (  # noqa: E402
    get_exercise as _get_exercise,
    list_exercises as _list_exercises,
    search_exercises as _search_exercises,
)
from lifekit.schedule.scheduler import (  # noqa: E402
    due_exercises as _due_exercises,
    review_exercise as _review_exercise,
)


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


@st.cache_data(ttl=30)
def get_book():
    c = conn()
    r = c.execute("SELECT title, author FROM books WHERE id = ?", (BOOK_ID,)).fetchone()
    c.close()
    return dict(r) if r else None


@st.cache_data(ttl=30)
def get_chapters():
    c = conn()
    rows = c.execute(
        "SELECT idx, title FROM chapters WHERE book_id = ? ORDER BY idx",
        (BOOK_ID,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_exercises(chapter_idx=None):
    c = conn()
    if chapter_idx is None:
        rows = c.execute(
            "SELECT id, title, chapter_title FROM exercises WHERE book_id = ? "
            "ORDER BY chapter_idx, id", (BOOK_ID,)).fetchall()
    else:
        rows = c.execute(
            "SELECT id, title, chapter_title FROM exercises WHERE book_id = ? "
            "AND chapter_idx = ? ORDER BY id", (BOOK_ID, chapter_idx)).fetchall()
    done = {r[0] for r in c.execute("SELECT DISTINCT exercise_id FROM completions")}
    c.close()
    return [dict(r) | {"done": r["id"] in done} for r in rows]


def get_exercise(ex_id):
    c = conn()
    r = c.execute("SELECT * FROM exercises WHERE id = ?", (ex_id,)).fetchone()
    c.close()
    if not r:
        return None
    d = dict(r)
    d["steps"] = json.loads(d["steps"])
    d["materials"] = json.loads(d["materials"])
    return d


def get_ideas(chapter_idx=None):
    c = conn()
    if chapter_idx is None:
        rows = c.execute(
            "SELECT idea FROM key_ideas WHERE book_id = ? ORDER BY id LIMIT 200",
            (BOOK_ID,)).fetchall()
    else:
        rows = c.execute(
            "SELECT idea FROM key_ideas WHERE book_id = ? AND chapter_idx = ? "
            "ORDER BY id", (BOOK_ID, chapter_idx)).fetchall()
    c.close()
    return [r[0] for r in rows]


def search_exercises(query):
    return _search_exercises(DB, query, BOOK_ID)


def progress():
    c = conn()
    total = c.execute(
        "SELECT COUNT(*) FROM exercises WHERE book_id = ?", (BOOK_ID,)).fetchone()[0]
    done = c.execute(
        "SELECT COUNT(DISTINCT exercise_id) FROM completions").fetchone()[0]
    last = c.execute(
        "SELECT e.title, c.completed_at FROM completions c "
        "JOIN exercises e ON e.id = c.exercise_id "
        "ORDER BY c.completed_at DESC LIMIT 5").fetchall()
    c.close()
    return total, done, [dict(r) for r in last]


def show_exercise(ex_id):
    ex = get_exercise(ex_id)
    if not ex:
        st.error("Exercise not found.")
        return
    st.header(ex["title"])
    st.caption(ex["chapter_title"])
    st.write(ex["purpose"])
    st.subheader("Steps")
    for i, s in enumerate(ex["steps"], 1):
        st.markdown(f"**{i}.** {s}")
    if ex["materials"]:
        st.subheader("Materials")
        for m in ex["materials"]:
            st.markdown(f"- {m}")
    with st.expander("Source quote"):
        st.caption(ex["source_quote"])
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        rating = st.selectbox("How did it go?",
                              ["good", "easy", "hard", "again"],
                              key=f"rating-{ex_id}")
    with col2:
        notes = st.text_input("Notes (optional)", key=f"notes-{ex_id}")
    if st.button("Mark complete", key=f"done-{ex_id}", type="primary"):
        res = review_exercise(DB, ex_id, rating=rating, notes=notes or None)
        if res["ok"]:
            st.success(f"Logged. Next review due: {res['due'][:10]}")
            st.cache_data.clear()
        else:
            st.error(res.get("error", "failed"))


# ---------- layout ----------
st.set_page_config(page_title="LifeKit (dogfood)", layout="wide")
book = get_book()
if not book:
    st.error(f"No book '{BOOK_ID}' in {DB}. Run scripts/ingest_eval_book.py first.")
    st.stop()
st.title(f"LifeKit — {book['title']}")
st.caption(f"by {book['author']} · dogfood build, unpolished on purpose")

view = st.sidebar.radio("Go to", ["Due today", "Exercises", "Key ideas"], key="view")
q = st.sidebar.text_input("Find an exercise",
                          placeholder="i want to do the mindmapping exercise")

if q:
    hits = search_exercises(q)
    st.subheader(f"Results for {q!r}")
    if not hits:
        st.write("No matches. Try fewer words.")
    for ex in hits:
        mark = "✓ " if ex["done"] else ""
        if st.button(f"{mark}{ex['title']}", key=f"hit-{ex['id']}"):
            st.session_state["open_ex"] = ex["id"]
            st.session_state["view"] = "Exercises"
elif view == "Due today":
    st.subheader("Due today")
    due = due_exercises(DB, BOOK_ID, limit=20)
    total, done, last = progress()
    st.write(f"Progress: **{done}/{total}** exercises completed at least once")
    if not due:
        st.write("Nothing due. Pick something from Exercises.")
    for ex in due:
        if st.button(f"{ex['title']}  ·  {ex['chapter_title']}",
                     key=f"due-{ex['id']}"):
            st.session_state["open_ex"] = ex["id"]
    if last:
        st.subheader("Recently completed")
        for r in last:
            st.caption(f"{r['title']} — {r['completed_at'][:10]}")
elif view == "Exercises":
    chapters = get_chapters()
    ch = st.selectbox("Chapter", ["All"] + [c["title"] for c in chapters])
    idx = None if ch == "All" else next(
        c["idx"] for c in chapters if c["title"] == ch)
    for ex in get_exercises(idx):
        mark = "✓ " if ex["done"] else ""
        if st.button(f"{mark}{ex['title']}", key=f"ex-{ex['id']}"):
            st.session_state["open_ex"] = ex["id"]
elif view == "Key ideas":
    chapters = get_chapters()
    ch = st.selectbox("Chapter", ["All"] + [c["title"] for c in chapters])
    idx = None if ch == "All" else next(
        c["idx"] for c in chapters if c["title"] == ch)
    for idea in get_ideas(idx):
        st.markdown(f"- {idea}")

if st.session_state.get("open_ex"):
    st.divider()
    show_exercise(st.session_state["open_ex"])
