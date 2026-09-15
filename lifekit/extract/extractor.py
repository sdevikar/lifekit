"""lifekit.extract.extractor -- per-chapter structured extraction (map step).

One schema-constrained Ollama call per chapter (``format=<Pydantic schema>``,
low temperature, retry on validation failure). Oversized chapters are split
with Chonkie's RecursiveChunker and extracted per section.

Usage:
    from lifekit.extract.extractor import extract_chapter

    result = extract_chapter(chapter)  # -> ChapterExtraction
"""
from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from lifekit.store.chapter_splitter import Chapter

DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.6:latest")
TEMPERATURE = 0.1
MAX_ATTEMPTS = 3

# Chapters longer than this are split into sections before extraction.
MAX_CHAPTER_CHARS = 48000
SECTION_CHUNK_CHARS = 60000


class Exercise(BaseModel):
    title: str
    purpose: str
    steps: list[str]
    materials: list[str] = Field(default_factory=list)
    source_quote: str
    chapter: str


class ChapterExtraction(BaseModel):
    chapter_title: str
    key_ideas: list[str]
    exercises: list[Exercise]


SYSTEM_PROMPT = """You are extracting structured content from a single chapter of a self-help book.

Rules:
- Extract ONLY what the supplied chapter text supports. Never invent exercises, steps, materials, or quotes.
- Include every distinct exercise, practice, prompt, routine, challenge, or worksheet described in the text.
- An empty exercise list is fine if the chapter genuinely contains none.
- Every exercise MUST include a `source_quote`: a VERBATIM quote from the chapter text (an exact substring) that grounds the exercise.
- `purpose`: one or two sentences on why the exercise exists.
- `steps`: the concrete instructions, in order, as a list of strings.
- `materials`: anything the reader needs (paper, notebook, etc.); empty list if none.
- `key_ideas`: the chapter's central ideas, as short statements.
- Respond with JSON matching the provided schema exactly."""


def build_messages(chapter: Chapter) -> tuple[str, str]:
    """Return (system, user) messages for a chapter."""
    user = f"Chapter title: {chapter.title}\n\nChapter text:\n{chapter.text}"
    return SYSTEM_PROMPT, user


def _default_client() -> Any:
    import ollama

    return ollama.Client()


def _extract_single(
    chapter: Chapter,
    client: Any,
    model: str,
    temperature: float,
    max_attempts: int,
) -> ChapterExtraction:
    """One schema-constrained extraction call with validation retry."""
    system, user = build_messages(chapter)
    last_err: ValidationError | None = None
    for _ in range(max_attempts):
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            format=ChapterExtraction.model_json_schema(),
            options={"temperature": temperature},
        )
        content = resp["message"]["content"]
        try:
            data = json.loads(content)
            # The model occasionally omits chapter_title even though the schema
            # requires it; backfill from the known chapter instead of failing.
            if isinstance(data, dict) and not data.get("chapter_title"):
                data["chapter_title"] = chapter.title
            return ChapterExtraction.model_validate(data)
        except json.JSONDecodeError:
            # Treat malformed JSON like a validation failure (retryable).
            try:
                ChapterExtraction.model_validate_json(content)
            except ValidationError as e:
                last_err = e
        except ValidationError as e:
            last_err = e
    assert last_err is not None
    raise last_err


def _split_sections(text: str) -> list[str]:
    """Split oversized chapter text into overlapping sections (Chonkie)."""
    from chonkie import RecursiveChunker

    chunker = RecursiveChunker(chunk_size=SECTION_CHUNK_CHARS)
    return [c.text for c in chunker.chunk(text)]


def extract_chapter(
    chapter: Chapter,
    client: Any | None = None,
    model: str | None = None,
    temperature: float = TEMPERATURE,
    max_attempts: int = MAX_ATTEMPTS,
) -> ChapterExtraction:
    """Extract exercises + key ideas from one chapter.

    Args:
        chapter: Chapter to extract from.
        client: Object with ``.chat(...)`` like ``ollama.Client``; a real
            client is created when omitted.
        model: Ollama model tag; defaults to ``OLLAMA_MODEL`` env or
            ``qwen3.6:latest``.
        temperature: Sampling temperature (default 0.1).
        max_attempts: Retries on Pydantic validation failure.
    """
    client = client if client is not None else _default_client()
    model = model or DEFAULT_MODEL

    if len(chapter.text) <= MAX_CHAPTER_CHARS:
        return _extract_single(chapter, client, model, temperature, max_attempts)

    merged = ChapterExtraction(chapter_title=chapter.title, key_ideas=[], exercises=[])
    for i, section in enumerate(_split_sections(chapter.text)):
        sub = Chapter(
            index=chapter.index,
            title=f"{chapter.title} (part {i + 1})",
            text=section,
            page_start=chapter.page_start,
            page_end=chapter.page_end,
        )
        part = _extract_single(sub, client, model, temperature, max_attempts)
        merged.key_ideas.extend(part.key_ideas)
        merged.exercises.extend(part.exercises)
    return merged
