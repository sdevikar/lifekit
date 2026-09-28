"""lifekit.serve.server — Step 13a Feed API.

Minimal localhost-only HTTP API exposing the umbrella's endpoint list:
briefing, completions, idea-signals, conversations, messages.

Reuses:
  - lifekit.coach.tools (log_completion, get_exercise, search_exercises)
  - lifekit.schedule.scheduler (due_exercises)
  - lifekit.book_chunks FTS5 retrieval
  - lifekit.llm for grounded chat prose

The LLM only writes prose; the endpoint owns turn structure and persistence.
"""
from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

from lifekit.db.schema import init_db
from lifekit.llm import get_provider
from lifekit.llm.config import resolve_config

HOST = "127.0.0.1"
PORT = 8765

_IDEA_SIGNAL_SCHEMA = {"type": "object", "properties": {"remembered": {"type": "boolean"}}}


def _conn(db_path: str):
    init_db(db_path)
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def _book_info(c, book_id):
    row = c.execute("SELECT id, title FROM books WHERE id = ?", (book_id,)).fetchone()
    return {"id": row["id"], "title": row["title"]} if row else None


def _today_exercise(c, db_path, book_id):
    """Today's exercise: FSRS-due, fallback to first incomplete."""
    try:
        from lifekit.schedule.scheduler import due_exercises

        due = due_exercises(db_path, book_id, limit=5)
        if due:
            ex = c.execute(
                "SELECT * FROM exercises WHERE id = ?", (due[0]["id"],)
            ).fetchone()
            if ex:
                return _exercise_dict(ex)
    except Exception:
        pass

    # Fallback: first exercise with no completion
    row = c.execute(
        """SELECT e.* FROM exercises e
           WHERE e.book_id = ?
           AND NOT EXISTS (SELECT 1 FROM completions WHERE exercise_id = e.id)
           ORDER BY e.id LIMIT 1""",
        (book_id,),
    ).fetchone()
    if row:
        return _exercise_dict(row)

    # Last resort: any exercise
    row = c.execute(
        "SELECT * FROM exercises WHERE book_id = ? ORDER BY id LIMIT 1", (book_id,)
    ).fetchone()
    return _exercise_dict(row) if row else None


def _exercise_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "text": row["purpose"],
        "chapter_title": row["chapter_title"],
        "source_quote": row["source_quote"],
    }


def _resurfaced_idea(c, book_id):
    """Resurfaced idea: tied to today's chapter, or just the first key idea."""
    # Pick first key idea; in v1 there is no idea-level FSRS yet
    row = c.execute(
        "SELECT id, idea, chapter_idx FROM key_ideas WHERE book_id = ? ORDER BY id LIMIT 1",
        (book_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "text": row["idea"],
        "why": f"Resurfaced from chapter {row['chapter_idx']}",
    }


def _fading_ideas(c, book_id, limit=5):
    """Key ideas with no associated completion signal."""
    rows = c.execute(
        """SELECT id, idea FROM key_ideas
           WHERE book_id = ?
           ORDER BY id LIMIT ?""",
        (book_id, limit),
    ).fetchall()
    return [{"id": r["id"], "text": r["idea"]} for r in rows]


def _briefing(c, book_id, db_path):
    book = _book_info(c, book_id)
    if not book:
        return None

    exercise = _today_exercise(c, db_path, book_id)

    seen_ideas = c.execute(
        "SELECT COUNT(*) FROM key_ideas WHERE book_id = ?", (book_id,)
    ).fetchone()[0]
    retained = c.execute(
        """SELECT COUNT(DISTINCT exercise_id) FROM completions
           JOIN exercises ON completions.exercise_id = exercises.id
           WHERE exercises.book_id = ?""",
        (book_id,),
    ).fetchone()[0]
    lived = retained

    return {
        "book": book,
        "day": datetime.now().strftime("%Y-%m-%d"),
        "stages": {"seen": seen_ideas, "retained": retained, "lived": lived},
        "exercise": exercise,
        "resurfaced_idea": _resurfaced_idea(c, book_id),
        "fading_ideas": _fading_ideas(c, book_id),
    }


def _fts_query(query: str) -> str:
    """Turn free text into a safe FTS5 MATCH expression.

    Users type sentences ("What is design thinking?"), but FTS5 treats
    punctuation as query syntax and raises on it. Keep alphanumerics, drop
    everything else, and quote each term so no term can be an operator.
    Returns "" when nothing searchable is left.
    """
    terms = re.findall(r"[\w]+", query, flags=re.UNICODE)
    return " OR ".join(f'"{t}"' for t in terms if len(t) > 1)


def _retrieve_passages(c, book_id, query, limit=3):
    """FTS5 keyword retrieval over book_chunks for grounding.

    book_chunks_fts indexes only `content` (content_rowid=book_chunks.id),
    so the book filter has to join back to book_chunks — querying a
    `book_id` column on the FTS table raises OperationalError, which used
    to be swallowed here and silently degrade to "first N chunks in
    insertion order", ignoring the query entirely.
    """
    match = _fts_query(query)
    rows = []
    if match:
        try:
            rows = c.execute(
                """SELECT bc.content
                   FROM book_chunks_fts
                   JOIN book_chunks bc ON bc.id = book_chunks_fts.rowid
                   WHERE book_chunks_fts MATCH ?
                   AND bc.book_id = ?
                   ORDER BY rank
                   LIMIT ?""",
                (match, book_id, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            # Malformed MATCH expression — fall through to the text search.
            rows = []
    if rows:
        return [r["content"] for r in rows]

    # No chunk hit. Fall back to the chapter text, which is what the eval
    # pipeline actually populates — the dogfood DB has 17 chapters of full
    # text and zero chunks, so without this the coach has nothing to ground
    # on and answers "I don't have any context".
    passages = _search_chapters(c, book_id, query, limit)
    if passages:
        return passages

    rows = c.execute(
        "SELECT content FROM book_chunks WHERE book_id = ? LIMIT ?", (book_id, limit)
    ).fetchall()
    return [r["content"] for r in rows]


def _search_chapters(c, book_id, query, limit=3, window=1200):
    """Rank chapters by query-term overlap and return a window around each hit.

    ponytail: naive term counting, no BM25/tfidf. Fine for 17 chapters; if
    retrieval quality matters, build real chunks and index them instead.
    """
    terms = {t.lower() for t in re.findall(r"\w+", query) if len(t) > 2}
    if not terms:
        return []
    rows = c.execute(
        "SELECT idx, content FROM chapters WHERE book_id = ? ORDER BY idx", (book_id,)
    ).fetchall()
    scored = []
    for r in rows:
        content = r["content"]
        low = content.lower()
        hits = [(m.start(), t) for t in terms for m in re.finditer(re.escape(t), low)]
        if not hits:
            continue
        hits.sort()
        # Keep the densest region rather than the first hit, so a term that
        # shows up in a table of contents doesn't drag in the wrong page.
        best_start, best_count = hits[0][0], 0
        for start, _ in hits:
            count = sum(1 for s, _ in hits if start <= s < start + window)
            if count > best_count:
                best_count, best_start = count, start
        start = max(0, best_start - window // 4)
        scored.append((best_count, f"[{r['idx']}] " + content[start : start + window]))
    scored.sort(key=lambda x: -x[0])
    return [text for _, text in scored[:limit]]


def _coach_reply(c, book_id, conv_id, message_text):
    """Grounded chat: retrieve context, call LLM for prose."""
    config = resolve_config()
    provider = get_provider(config)
    passages = _retrieve_passages(c, book_id, message_text, limit=3)

    context = "\n\n".join(passages) if passages else "No book context found."
    system_msg = {
        "role": "system",
        "content": (
            f"You are LifeKit's grounded coach for the book "
            f"'{book_id}'. Answer the user's question using only the book "
            f"context below. Keep replies concise and actionable."
            f"\n\nBook context:\n{context}"
        ),
    }

    history = c.execute(
        """SELECT role, text FROM messages
           WHERE conversation_id = ? ORDER BY id""",
        (conv_id,),
    ).fetchall()
    history_msgs = [
        {"role": m["role"], "content": m["text"]} for m in history
    ]

    messages = [system_msg, *history_msgs, {"role": "user", "content": message_text}]

    json_schema = {
        "type": "object",
        "properties": {"reply": {"type": "string"}},
        "required": ["reply"],
    }

    raw = provider.chat_json_schema(
        model=config.model,
        messages=messages,
        json_schema=json_schema,
        temperature=0.1,
    )
    try:
        parsed = json.loads(raw)
        return parsed.get("reply", "")
    except (json.JSONDecodeError, TypeError):
        return raw.strip()


class FeedAPI:
    """Localhost-only feed API server."""

    def __init__(self, db_path: str | Path | None = None, book_id: str | None = None):
        self.db_path = str(db_path) if db_path else str(Path.home() / ".lifekit" / "lifekit.db")
        self.book_id = book_id or "dyl"
        self.host = HOST
        self.port = PORT

    def run(self):
        """Run the Flask dev server bound to 127.0.0.1 only."""
        app = create_app(db_path=self.db_path, book_id=self.book_id)
        app.run(host=self.host, port=self.port, debug=False)


def create_app(db_path: str | Path | None = None, book_id: str | None = None) -> Flask:
    """Create the Flask application with all feed API routes."""
    db_path = str(db_path) if db_path else str(Path.home() / ".lifekit" / "lifekit.db")
    book_id = book_id or "dyl"

    app = Flask(__name__)
    app.config["db_path"] = db_path
    app.config["book_id"] = book_id

    @app.route("/api/briefing/today")
    def get_briefing():
        c = _conn(app.config["db_path"])
        try:
            data = _briefing(c, app.config["book_id"], app.config["db_path"])
            if data is None:
                return jsonify({"error": "book not found"}), 404
            return jsonify(data)
        finally:
            c.close()

    @app.route("/api/completions", methods=["POST"])
    def post_completion():
        data = request.get_json(silent=True) or {}
        if "exercise_id" not in data:
            return jsonify({"ok": False, "error": "exercise_id required"}), 400
        from lifekit.coach.tools import log_completion

        result = log_completion(app.config["db_path"], data["exercise_id"])
        status = 200 if result["ok"] else 400
        return jsonify(result), status

    @app.route("/api/idea-signals", methods=["POST"])
    def post_idea_signal():
        data = request.get_json(silent=True) or {}
        if "idea_id" not in data or "remembered" not in data:
            return jsonify({"ok": False, "error": "idea_id and remembered required"}), 400
        idea_id = data["idea_id"]
        remembered = data["remembered"]
        if not isinstance(idea_id, int) or not isinstance(remembered, bool):
            return jsonify({"ok": False, "error": "invalid types"}), 400
        c = _conn(app.config["db_path"])
        try:
            row = c.execute(
                "SELECT id FROM key_ideas WHERE id = ?", (idea_id,)
            ).fetchone()
            if not row:
                return jsonify({"ok": False, "error": "idea not found"}), 400
            c.execute(
                "INSERT INTO idea_signals (idea_id, remembered) VALUES (?, ?)",
                (idea_id, int(remembered)),
            )
            c.commit()
            return jsonify({"ok": True})
        finally:
            c.close()

    @app.route("/api/conversations", methods=["GET"])
    def list_conversations():
        c = _conn(app.config["db_path"])
        try:
            rows = c.execute(
                """SELECT id, title, updated_at FROM conversations
                   WHERE book_id = ? ORDER BY updated_at DESC""",
                (app.config["book_id"],),
            ).fetchall()
            return jsonify([dict(r) for r in rows])
        finally:
            c.close()

    @app.route("/api/conversations", methods=["POST"])
    def create_conversation():
        data = request.get_json(silent=True) or {}
        seed_kind = data.get("seed_kind")
        if seed_kind not in ("card", "composer"):
            return jsonify({"ok": False, "error": "seed_kind must be 'card' or 'composer'"}), 400
        c = _conn(app.config["db_path"])
        try:
            conv_id = uuid.uuid4().hex[:12]
            title = data.get("title") or (
                f"Idea: {seed_kind}" if seed_kind == "card" else "New conversation"
            )
            c.execute(
                """INSERT INTO conversations
                   (id, title, book_id, seed_kind, seed_ref)
                   VALUES (?, ?, ?, ?, ?)""",
                (conv_id, title, app.config["book_id"], seed_kind, data.get("seed_ref")),
            )
            c.commit()
            return jsonify({"id": conv_id})
        finally:
            c.close()

    @app.route("/api/conversations/<conv_id>")
    def get_conversation(conv_id):
        c = _conn(app.config["db_path"])
        try:
            conv = c.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            if not conv:
                return jsonify({"error": "not found"}), 404
            msgs = c.execute(
                """SELECT role, text, created_at FROM messages
                   WHERE conversation_id = ? ORDER BY id""",
                (conv_id,),
            ).fetchall()
            return jsonify({
                "conversation": {
                    "id": conv["id"],
                    "title": conv["title"],
                    "book_id": conv["book_id"],
                    "seed_kind": conv["seed_kind"],
                    "seed_ref": conv["seed_ref"],
                },
                "messages": [dict(m) for m in msgs],
            })
        finally:
            c.close()

    @app.route("/api/conversations/<conv_id>/messages", methods=["POST"])
    def post_message(conv_id):
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip() if isinstance(data.get("text"), str) else ""
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400

        c = _conn(app.config["db_path"])
        try:
            conv = c.execute(
                "SELECT id FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            if not conv:
                return jsonify({"error": "conversation not found"}), 404

            # Generate the reply *before* persisting anything: if the LLM
            # fails we must not leave a user message with no coach answer.
            # _coach_reply appends `text` to the history itself, so the
            # uncommitted insert is not needed for context.
            try:
                reply = _coach_reply(c, app.config["book_id"], conv_id, text)
            except Exception as e:  # provider/network/model failure
                c.rollback()
                app.logger.exception("coach reply failed")
                return (
                    jsonify({"ok": False, "error": f"Coach unavailable: {e}"}),
                    502,
                )

            c.execute(
                "INSERT INTO messages (conversation_id, role, text) VALUES (?, 'user', ?)",
                (conv_id, text),
            )
            c.execute(
                "INSERT INTO messages (conversation_id, role, text) VALUES (?, 'coach', ?)",
                (conv_id, reply),
            )
            c.commit()

            return jsonify({"reply": reply})
        finally:
            c.close()

    return app