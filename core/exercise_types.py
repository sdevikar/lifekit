"""Core exercise taxonomy — Pydantic models for the 4 exercise types."""

from __future__ import annotations
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

class ExerciseType(str, Enum):
    CONCEPT_CHECK = "concept_check"
    HABIT_LOG = "habit_log"
    JOURNAL = "journal"
    CONTENT_DIGEST = "content_digest"

class ConceptCheckExercise(BaseModel):
    """Feynman technique: explain concept in your own words."""
    exercise_type: ExerciseType = ExerciseType.CONCEPT_CHECK
    source_book: Optional[str] = None
    source_chapter: Optional[int] = None
    prompt: str
    context_snapshot: Optional[dict] = None

class HabitLogExercise(BaseModel):
    """Daily habit tracking with mood context."""
    exercise_type: ExerciseType = ExerciseType.HABIT_LOG
    habits_in_place: List[str]
    mood_before: Optional[float] = None  # 1-5 scale
    mood_after: Optional[float] = None

class JournalExercise(BaseModel):
    """Guided journaling with specific prompt."""
    exercise_type: ExerciseType = ExerciseType.JOURNAL
    prompt: str
    time_spent_minutes: Optional[int] = None
    reflection: Optional[str] = None

class ContentDigestExercise(BaseModel):
    """Process content from books/videos and generate insights."""
    exercise_type: ExerciseType = ExerciseType.CONTENT_DIGEST
    source_type: str  # 'book', 'video', 'article'
    source_url_or_path: str
    excerpt: Optional[str] = None
    key_insights: Optional[List[str]] = None

class IntentBubble(BaseModel):
    """LifeKit's way of inviting the user into a specific cognitive frame."""
    type: ExerciseType
    title: str
    subtitle: Optional[str] = None
    context_snapshot: dict = {}
    expected_duration_minutes: int = 10
