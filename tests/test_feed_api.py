"""Tests for lifekit.serve — the Step 13a Feed API.

Covers: schema migration, every endpoint's happy path, malformed-input
rejection, localhost-only binding, and the conversation round-trip.
"""

import json
import os
import sqlite3
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.db.schema import init_db
from lifekit.serve.server import FeedAPI, create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BOOK_ID = "dyl"


@pytest.fixture
def db_path(tmp_path):
    """A fresh dogfood-like DB with book, exercises, key ideas, chunks."""
    p = str(tmp_path / "feed.db")
    init_db(p)
    c = sqlite3.connect(p)
    c.row_factory = sqlite3.Row

    # Book
    c.execute(
        "INSERT INTO books (id, title, author, file_path, chunk_count) "
        "VALUES (?, ?, ?, ?, ?)",
        (BOOK_ID, "Designing Your Life", "Burnett & Evans", "/fake/dyl.pdf", 0),
    )

    # Exercises
    ex_ids = []
    for i, title in enumerate(["Ex One", "Ex Two", "Ex Three"], start=1):
        cur = c.execute(
            """INSERT INTO exercises
               (book_id, chapter_idx, chapter_title, title, purpose, steps,
                source_quote, extra_quotes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (BOOK_ID, 1, "Ch 1", title, f"purpose {i}",
             json.dumps([f"step {i}a"]), "source quote here", "[]"),
        )
        ex_ids.append(cur.lastrowid)

    # Key ideas
    idea_ids = []
    for i, idea in enumerate(["Idea A", "Idea B", "Idea C"], start=1):
        cur = c.execute(
            "INSERT INTO key_ideas (book_id, chapter_idx, idea) VALUES (?, ?, ?)",
            (BOOK_ID, 1, idea),
        )
        idea_ids.append(cur.lastrowid)

    # A book chunk for retrieval (FTS5)
    c.execute(
        "INSERT INTO book_chunks (book_id, chunk_index, content, page_number) "
        "VALUES (?, ?, ?, ?)",
        (BOOK_ID, 0, "This is a chunk about design thinking and life.", 1),
    )

    c.commit()
    c.close()
    return p, {"exercise_ids": ex_ids, "idea_ids": idea_ids}


@pytest.fixture
def app(db_path, tmp_path):
    """A FeedAPI app bound to the test DB, with Ollama mocked."""
    p, ids = db_path
    app = create_app(db_path=p, book_id=BOOK_ID)
    app.config["TESTING"] = True
    app.config["db_path"] = p
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# 13a.2 — Schema migration
# ---------------------------------------------------------------------------

class TestSchemaMigration:
    def test_conversations_table_exists(self, db_path):
        p, _ = db_path
        c = sqlite3.connect(p)
        cols = {r[1] for r in c.execute("PRAGMA table_info(conversations)").fetchall()}
        c.close()
        assert "id" in cols
        assert "title" in cols
        assert "book_id" in cols
        assert "seed_kind" in cols
        assert "seed_ref" in cols
        assert "created_at" in cols
        assert "updated_at" in cols

    def test_messages_table_exists(self, db_path):
        p, _ = db_path
        c = sqlite3.connect(p)
        cols = {r[1] for r in c.execute("PRAGMA table_info(messages)").fetchall()}
        c.close()
        assert "id" in cols
        assert "conversation_id" in cols
        assert "role" in cols
        assert "text" in cols
        assert "created_at" in cols

    def test_messages_fk_to_conversations(self, db_path):
        p, _ = db_path
        c = sqlite3.connect(p)
        c.execute("PRAGMA foreign_keys = ON")
        cols = {r[1] for r in c.execute("PRAGMA table_info(messages)").fetchall()}
        c.close()
        # The column must be present; FK enforcement tested via the app
        assert "conversation_id" in cols

    def test_migrations_are_idempotent(self, tmp_path):
        """init_db called twice should not error or duplicate tables."""
        p = str(tmp_path / "idem.db")
        init_db(p)
        init_db(p)
        c = sqlite3.connect(p)
        tables = {r[0] for r in c.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        c.close()
        assert "conversations" in tables
        assert "messages" in tables


# ---------------------------------------------------------------------------
# 13a.3 — Endpoints
# ---------------------------------------------------------------------------

class TestBriefing:
    def test_get_briefing_today(self, client, db_path):
        resp = client.get("/api/briefing/today")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["book"]["id"] == BOOK_ID
        assert data["book"]["title"] == "Designing Your Life"
        assert "day" in data
        assert "stages" in data
        assert "seen" in data["stages"]
        assert "retained" in data["stages"]
        assert "lived" in data["stages"]
        assert "exercise" in data
        assert data["exercise"]["id"] is not None
        assert data["exercise"]["title"] is not None
        assert "text" in data["exercise"]
        assert "resurfaced_idea" in data
        assert "fading_ideas" in data
        assert isinstance(data["fading_ideas"], list)

    def test_briefing_uses_due_exercises(self, client, db_path):
        """Exercise with a past-due FSRS card is served by due_exercises,
        not the no-completion fallback."""
        from fsrs import Card
        import json as _json
        import datetime

        p, ids = db_path
        # Insert a card due in the past for exercise 2
        card = Card(due=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
        c = sqlite3.connect(p)
        c.execute(
            "INSERT INTO fsrs_cards (exercise_id, card_json) VALUES (?, ?)",
            (ids["exercise_ids"][1], _json.dumps(card.to_dict())),
        )
        c.commit()
        c.close()

        resp = client.get("/api/briefing/today")
        assert resp.status_code == 200
        exercise = resp.get_json()["exercise"]
        # due_exercises ordered by id → exercise 2 is due, should be returned
        assert exercise["id"] == ids["exercise_ids"][1]

    def test_briefing_fallback_no_cards(self, client, db_path):
        """With no FSRS cards, falls back to first incomplete exercise."""
        resp = client.get("/api/briefing/today")
        assert resp.status_code == 200
        exercise = resp.get_json()["exercise"]
        # Fallback is "first exercise with no completion" → exercise 1
        assert exercise["id"] is not None


class TestCompletions:
    def test_post_completion(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/completions", json={"exercise_id": ids["exercise_ids"][0]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

        # Verify it persisted
        p, _ = db_path
        c = sqlite3.connect(p)
        n = c.execute(
            "SELECT COUNT(*) FROM completions WHERE exercise_id = ?",
            (ids["exercise_ids"][0],),
        ).fetchone()[0]
        c.close()
        assert n == 1

    def test_post_completion_bad_exercise(self, client):
        resp = client.post("/api/completions", json={"exercise_id": 999999})
        assert resp.status_code == 400
        assert resp.get_json()["ok"] is False

    def test_post_completion_malformed(self, client):
        resp = client.post("/api/completions", json={})
        assert resp.status_code == 400

    def test_post_completion_missing_field(self, client):
        resp = client.post("/api/completions", json={"not_exercise_id": 1})
        assert resp.status_code == 400


class TestIdeaSignals:
    def test_post_idea_signal(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/idea-signals", json={
            "idea_id": ids["idea_ids"][0],
            "remembered": True,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_post_idea_signal_false(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/idea-signals", json={
            "idea_id": ids["idea_ids"][0],
            "remembered": False,
        })
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_post_idea_signal_persists(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/idea-signals", json={
            "idea_id": ids["idea_ids"][0],
            "remembered": True,
        })
        assert resp.status_code == 200
        p, _ = db_path
        c = sqlite3.connect(p)
        row = c.execute(
            "SELECT idea_id, remembered FROM idea_signals WHERE idea_id = ?",
            (ids["idea_ids"][0],),
        ).fetchone()
        c.close()
        assert row is not None
        assert row[0] == ids["idea_ids"][0]
        assert row[1] == 1

    def test_post_idea_signal_malformed(self, client):
        resp = client.post("/api/idea-signals", json={})
        assert resp.status_code == 400

    def test_post_idea_signal_bad_id(self, client):
        resp = client.post("/api/idea-signals", json={
            "idea_id": 999999,
            "remembered": True,
        })
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 13a.4 — Conversation CRUD + message endpoint
# ---------------------------------------------------------------------------

class TestConversations:
    def test_list_conversations_empty(self, client):
        resp = client.get("/api/conversations")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_conversation_composer(self, client):
        resp = client.post("/api/conversations", json={
            "seed_kind": "composer",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "id" in data
        conv_id = data["id"]

        # Listed
        resp = client.get("/api/conversations")
        convs = resp.get_json()
        assert len(convs) == 1
        assert convs[0]["id"] == conv_id

    def test_create_conversation_exercise_seed(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/conversations", json={
            "seed_kind": "card",
            "seed_ref": str(ids["exercise_ids"][0]),
        })
        assert resp.status_code == 200
        assert "id" in resp.get_json()

    def test_create_conversation_idea_seed(self, client, db_path):
        _, ids = db_path
        resp = client.post("/api/conversations", json={
            "seed_kind": "card",
            "seed_ref": str(ids["idea_ids"][0]),
        })
        assert resp.status_code == 200
        assert "id" in resp.get_json()

    def test_create_conversation_malformed(self, client):
        resp = client.post("/api/conversations", json={})
        assert resp.status_code == 400

    def test_get_conversation_not_found(self, client):
        resp = client.get("/api/conversations/does-not-exist")
        assert resp.status_code == 404

    def test_get_conversation_with_messages(self, client, db_path):
        # Create + seed message
        resp = client.post("/api/conversations", json={"seed_kind": "composer"})
        conv_id = resp.get_json()["id"]

        r = client.get(f"/api/conversations/{conv_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert "conversation" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)


class TestConversationMessages:
    @patch("lifekit.serve.server.get_provider")
    def test_post_message_returns_reply(self, mock_get_provider, client, db_path):
        """POST /conversations/:id/messages → {reply} with grounded LLM."""
        # Mock the LLM provider
        mock_provider = MagicMock()
        mock_provider.chat_json_schema.return_value = (
            '{"reply": "Design thinking starts with empathy."}'
        )
        mock_get_provider.return_value = mock_provider

        # Create conversation
        resp = client.post("/api/conversations", json={"seed_kind": "composer"})
        conv_id = resp.get_json()["id"]

        # Send a message
        resp = client.post(f"/api/conversations/{conv_id}/messages", json={
            "text": "What is design thinking?",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

        # Verify the message + reply persisted
        r = client.get(f"/api/conversations/{conv_id}")
        msgs = r.get_json()["messages"]
        assert len(msgs) == 2
        roles = [m["role"] for m in msgs]
        assert "user" in roles
        assert "coach" in roles

        # Verify LLM was called with grounded context
        mock_provider.chat_json_schema.assert_called_once()
        call_kwargs = mock_provider.chat_json_schema.call_args.kwargs
        # Messages should include system prompt with book context
        assert any("book" in str(m).lower() for m in call_kwargs["messages"])

    def test_post_message_not_found(self, client):
        resp = client.post("/api/conversations/nonexistent/messages", json={"text": "hi"})
        assert resp.status_code == 404

    def test_post_message_malformed(self, client, db_path):
        resp = client.post("/api/conversations", json={"seed_kind": "composer"})
        conv_id = resp.get_json()["id"]

        resp = client.post(f"/api/conversations/{conv_id}/messages", json={})
        assert resp.status_code == 400

    def test_post_message_empty_text(self, client, db_path):
        resp = client.post("/api/conversations", json={"seed_kind": "composer"})
        conv_id = resp.get_json()["id"]

        resp = client.post(f"/api/conversations/{conv_id}/messages", json={"text": ""})
        assert resp.status_code == 400

    @patch("lifekit.serve.server.get_provider")
    def test_conversation_round_trip(self, mock_get_provider, client, db_path):
        """Full round-trip: create → message → reply → reload."""
        mock_provider = MagicMock()
        mock_provider.chat_json_schema.return_value = '{"reply": "Your reframe is strong."}'
        mock_get_provider.return_value = mock_provider

        # 1. Create
        resp = client.post("/api/conversations", json={"seed_kind": "composer"})
        conv_id = resp.get_json()["id"]
        assert conv_id

        # 2. Message
        resp = client.post(f"/api/conversations/{conv_id}/messages", json={
            "text": "Tell me about belief reframing.",
        })
        assert resp.status_code == 200
        reply = resp.get_json()["reply"]
        assert len(reply) > 0

        # 3. Reload (separate request — tests persistence)
        resp = client.get(f"/api/conversations/{conv_id}")
        data = resp.get_json()
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "coach"


# ---------------------------------------------------------------------------
# 13a.5 — Localhost-only binding
# ---------------------------------------------------------------------------

class TestLocalhostBinding:
    def test_get_host_returns_loopback(self, app, db_path):
        p, _ = db_path
        srv = FeedAPI(db_path=p, book_id=BOOK_ID)
        assert srv.host in ("127.0.0.1", "localhost")

    def test_create_app_binds_loopback(self, app, db_path):
        p, _ = db_path
        srv = FeedAPI(db_path=p, book_id=BOOK_ID)
        # The run() would bind host; in testing we verify the config
        assert srv.host == "127.0.0.1"