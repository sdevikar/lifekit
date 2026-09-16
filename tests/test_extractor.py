"""Step 2 tests: extraction map.

Unit tests run with a stubbed LLM client (fast, no Ollama needed).
The real-model integration + full-book recall run lives in
scripts/eval_step2_recall.py (slow on CPU; results recorded in tasks.md).
"""
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.extract.extractor import (
    ChapterExtraction,
    Exercise,
    build_messages,
    extract_chapter,
)
from lifekit.store.chapter_splitter import Chapter


VALID_JSON = {
    "chapter_title": "Start Where You Are",
    "key_ideas": ["You can't know where you're going until you know where you are."],
    "exercises": [
        {
            "title": "Health / Work / Play / Love Dashboard",
            "purpose": "Take stock of where you are across four areas.",
            "steps": ["Write a few sentences about each area.", "Fill each gauge."],
            "materials": ["paper or notebook"],
            "source_quote": "You Are Here",
            "chapter": "Start Where You Are",
        }
    ],
}


class StubClient:
    """Mimics ollama.Client.chat; responses are queued JSON payloads."""

    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        payload = self.payloads.pop(0)
        return {"message": {"content": json.dumps(payload) if isinstance(payload, dict) else payload}}


def _chapter(text="Some chapter text. " * 50, title="Ch 1"):
    return Chapter(index=0, title=title, text=text, page_start=1, page_end=5)


def test_exercise_requires_source_quote():
    data = dict(VALID_JSON["exercises"][0])
    del data["source_quote"]
    with pytest.raises(ValidationError):
        Exercise(**data)


def test_empty_exercises_allowed():
    ex = ChapterExtraction(chapter_title="Intro", key_ideas=["idea"], exercises=[])
    assert ex.exercises == []


def test_extract_chapter_parses_stub_response():
    client = StubClient([VALID_JSON])
    result = extract_chapter(_chapter(), client=client, model="test-model")
    assert isinstance(result, ChapterExtraction)
    assert result.exercises[0].title == "Health / Work / Play / Love Dashboard"
    assert result.exercises[0].steps[0].startswith("Write a few sentences")
    # schema-constrained call was requested
    assert "format" in client.calls[0]
    assert client.calls[0]["model"] == "test-model"
    # low temperature
    assert client.calls[0]["options"]["temperature"] == pytest.approx(0.1)


def test_extract_chapter_retries_on_validation_error():
    bad = {"chapter_title": "x", "key_ideas": [], "exercises": [{"title": "no quote"}]}
    client = StubClient([bad, "not json at all", VALID_JSON])
    result = extract_chapter(_chapter(), client=client, model="m", max_attempts=3)
    assert len(client.calls) == 3
    assert result.exercises[0].title == "Health / Work / Play / Love Dashboard"


def test_extract_chapter_backfills_missing_chapter_title():
    """A response omitting chapter_title is repaired from the known chapter."""
    data = dict(VALID_JSON)
    del data["chapter_title"]
    client = StubClient([data])
    result = extract_chapter(_chapter(title="My Chapter"), client=client, model="m")
    assert result.chapter_title == "My Chapter"
    assert len(client.calls) == 1  # no retry needed


def test_extract_chapter_raises_after_max_attempts():
    client = StubClient(["junk"] * 3)
    with pytest.raises(ValidationError):
        extract_chapter(_chapter(), client=client, model="m", max_attempts=3)


def test_prompt_contains_grounding_instructions():
    system, user = build_messages(_chapter(title="Ch 9"))
    combined = (system + user).lower()
    assert "verbatim" in combined
    assert "only" in combined and "supplied chapter text" in combined
    assert "exercise" in combined


def test_oversized_chapter_splits_into_sections():
    chonkie = pytest.importorskip("chonkie")
    long_text = "word " * 22000  # > MAX_CHAPTER_CHARS (48000)
    client = StubClient([VALID_JSON] * 4)
    result = extract_chapter(_chapter(text=long_text), client=client, model="m")
    assert len(client.calls) >= 2
    assert len(result.exercises) == len(client.calls)  # concatenated sections


class StubProvider:
    """Mimics the lifekit.llm protocol: chat_json_schema returns a content string."""

    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def chat_json_schema(self, *, model, messages, json_schema, temperature):
        self.calls.append(
            {"model": model, "messages": messages, "json_schema": json_schema,
             "temperature": temperature}
        )
        payload = self.payloads.pop(0)
        return json.dumps(payload) if isinstance(payload, dict) else payload


def test_extract_chapter_accepts_protocol_provider():
    provider = StubProvider([VALID_JSON])
    result = extract_chapter(_chapter(), provider=provider, model="test-model")
    assert isinstance(result, ChapterExtraction)
    assert result.exercises[0].title == "Health / Work / Play / Love Dashboard"
    assert provider.calls[0]["temperature"] == pytest.approx(0.1)
    assert provider.calls[0]["model"] == "test-model"
    assert isinstance(provider.calls[0]["json_schema"], dict)
