"""LifeKit dogfood UI — throwaway Streamlit app for the DYL MVP.

Run:  streamlit run ui/app.py
Reads the product DB (~/.lifekit/lifekit.db, override with LIFEKIT_DB).

MVP vision: "Every day, LifeKit gives you one exercise to do and one idea
to remember." Structure by default (Today), flexibility on demand (Chat),
browsing as a distant third (Library).
"""
import hashlib
import json
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st

DB = os.environ.get("LIFEKIT_DB", str(Path.home() / ".lifekit" / "lifekit.db"))
BOOK_ID = "dyl"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lifekit.coach.tools import (  # noqa: E402
    get_exercise as _get_exercise,
    next_exercise as _next_exercise,
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


@st.cache_data(ttl=60)
def get_book():
    c = conn()
    r = c.execute("SELECT title, author FROM books WHERE id = ?",
                  (BOOK_ID,)).fetchone()
    c.close()
    return dict(r) if r else None


@st.cache_data(ttl=60)
def get_chapters():
    c = conn()
    rows = c.execute(
        "SELECT idx, title FROM chapters WHERE book_id = ? ORDER BY idx",
        (BOOK_ID,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


@st.cache_data(ttl=60)
def all_ideas():
    c = conn()
    rows = c.execute(
        "SELECT idea FROM key_ideas WHERE book_id = ? ORDER BY id",
        (BOOK_ID,)).fetchall()
    c.close()
    return [r[0] for r in rows]


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
    return _get_exercise(DB, ex_id)


def get_ideas(chapter_idx=None, limit=60):
    c = conn()
    if chapter_idx is None:
        rows = c.execute(
            "SELECT idea FROM key_ideas WHERE book_id = ? ORDER BY id LIMIT ?",
            (BOOK_ID, limit)).fetchall()
    else:
        rows = c.execute(
            "SELECT idea FROM key_ideas WHERE book_id = ? AND chapter_idx = ? "
            "ORDER BY id LIMIT ?", (BOOK_ID, chapter_idx, limit)).fetchall()
    c.close()
    return [r[0] for r in rows]


def progress():
    c = conn()
    total = c.execute(
        "SELECT COUNT(*) FROM exercises WHERE book_id = ?", (BOOK_ID,)).fetchone()[0]
    done = c.execute("SELECT COUNT(DISTINCT exercise_id) FROM completions"
                     ).fetchone()[0]
    c.close()
    return total, done


def today_idea(offset=0):
    ideas = all_ideas()
    if not ideas:
        return None
    day = int(hashlib.md5(date.today().isoformat().encode()).hexdigest(), 16)
    return ideas[(day + offset) % len(ideas)]


def chapter_idx_for_number(n):
    for ch in get_chapters():
        if ch["title"].startswith(f"{n}."):
            return ch["idx"]
    return None


def route_query(q):
    """Rule-based router for the chat box. Returns (kind, payload)."""
    ql = q.lower()
    if re.search(r"\b(due|today|up next|what should i do)\b", ql):
        return ("due", _due_exercises(DB, BOOK_ID, limit=5))
    m = re.search(r"chapter\s+(\d+)", ql)
    if m or re.search(r"\b(lesson|about|remind me|recap|idea)\b", ql):
        idx = chapter_idx_for_number(m.group(1)) if m else None
        ideas = get_ideas(idx)
        label = next((c["title"] for c in get_chapters() if c["idx"] == idx),
                     "the book") if idx is not None else "the book"
        return ("ideas", (label, ideas))
    hits = _search_exercises(DB, q, BOOK_ID)
    return ("exercises", hits)


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
        rating = st.selectbox("How did it go?", ["good", "easy", "hard", "again"],
                              key=f"rating-{ex_id}")
    with col2:
        notes = st.text_input("Notes (optional)", key=f"notes-{ex_id}")
    if st.button("Mark complete", key=f"done-{ex_id}", type="primary"):
        res = _review_exercise(DB, ex_id, rating=rating, notes=notes or None)
        if res["ok"]:
            st.success(f"Logged. Next review: {res['due'][:10]}")
            st.cache_data.clear()
        else:
            st.error(res.get("error", "failed"))


def exercise_buttons(exercises, prefix):
    for ex in exercises:
        mark = "✓ " if ex.get("done") else ""
        if st.button(f"{mark}{ex['title']}", key=f"{prefix}-{ex['id']}"):
            st.session_state["open_ex"] = ex["id"]


# ---------- layout ----------
st.set_page_config(page_title="LifeKit", layout="wide")
book = get_book()
if not book:
    st.error(f"No book '{BOOK_ID}' in {DB}. Run scripts/ingest_eval_book.py first.")
    st.stop()

st.title("LifeKit")
st.caption(f"{book['title']} · by {book['author']}")

tab_today, tab_chat, tab_library = st.tabs(["Today", "Chat", "Library"])

with tab_today:
    total, done = progress()
    st.write(f"**{done}/{total}** exercises completed")
    st.subheader("Up next")
    due = _due_exercises(DB, BOOK_ID, limit=1)
    up_next = due[0] if due else _next_exercise(DB, "dyl")
    if up_next:
        st.markdown(f"### {up_next['title']}")
        st.caption(up_next["chapter_title"])
        if st.button("Start", type="primary", key="start-upnext"):
            st.session_state["open_ex"] = up_next["id"]
    else:
        st.write("All caught up. The book is fully practiced.")
    st.subheader("One idea")
    idea = today_idea(st.session_state.get("idea_offset", 0))
    if idea:
        st.info(idea)
        if st.button("Another idea", key="another-idea"):
            st.session_state["idea_offset"] = \
                st.session_state.get("idea_offset", 0) + 1
            st.rerun()
    st.subheader("Try")
    for chip in ["I want to do the mindmapping exercise",
                 "What was chapter 3 about?",
                 "What's due today?"]:
        if st.button(chip, key=f"chip-{chip[:12]}"):
            st.session_state["today_results"] = route_query(chip)
    if st.session_state.get("today_results"):
        kind, payload = st.session_state["today_results"]
        if kind == "exercises":
            exercise_buttons(payload, "chip-ex")
        elif kind == "due":
            exercise_buttons(payload, "chip-due")
        elif kind == "ideas":
            label, ideas = payload
            st.caption(f"Key ideas — {label}")
            for i in ideas[:15]:
                st.markdown(f"- {i}")
    if st.session_state.get("open_ex"):
        st.divider()
        show_exercise(st.session_state["open_ex"])

with tab_chat:
    q = st.text_input("What do you want to work on?",
                      placeholder="e.g. i want to do the mindmapping exercise",
                      key="chat-q")
    if st.button("Send", key="chat-send") and q:
        st.session_state.setdefault("chat_history", []).insert(
            0, (q, route_query(q)))
    for q, (kind, payload) in st.session_state.get("chat_history", []):
        st.markdown(f"**You:** {q}")
        if kind == "exercises":
            if payload:
                exercise_buttons(payload, f"chat-{abs(hash(q)) % 9999}")
            else:
                st.write("No matches. Try fewer words.")
        elif kind == "due":
            if payload:
                exercise_buttons(payload, f"chatd-{abs(hash(q)) % 9999}")
            else:
                st.write("Nothing due right now.")
        elif kind == "ideas":
            label, ideas = payload
            st.caption(f"Key ideas — {label}")
            for i in ideas[:15]:
                st.markdown(f"- {i}")
        st.divider()

with tab_library:
    chapters = get_chapters()
    by_title = {c["title"]: c["idx"] for c in chapters}
    sec = st.radio("Browse", ["Exercises", "Key ideas"], horizontal=True,
                   key="lib-sec")
    ch = st.selectbox("Chapter", ["All"] + list(by_title), key="lib-ch")
    idx = None if ch == "All" else by_title.get(ch)
    if sec == "Exercises":
        exercise_buttons(get_exercises(idx), "lib-ex")
    else:
        for idea in get_ideas(idx):
            st.markdown(f"- {idea}")
    if st.session_state.get("open_ex"):
        st.divider()
        show_exercise(st.session_state["open_ex"])
