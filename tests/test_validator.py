"""Tests for lifekit.validate (Step 4)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifekit.validate.validator import validate_exercise, should_flag_zero
from lifekit.validate.judge import sample_for_judge
from lifekit.extract.extractor import Exercise


def make_ex(quote="exact quote here", extra=None):
    return Exercise(
        title="Test Exercise",
        purpose="p",
        steps=["s1"],
        materials=[],
        source_quote=quote,
        chapter="Ch1",
    )


def test_verbatim_quote_passes():
    ex = make_ex(quote="exact quote here")
    result = validate_exercise(ex, "some text exact quote here more text")
    assert result["ok"] is True
    assert result["failures"] == []


def test_nonverbatim_quote_fails():
    ex = make_ex(quote="paraphrased quote not in text")
    result = validate_exercise(ex, "some text exact quote here more text")
    assert result["ok"] is False
    assert len(result["failures"]) == 1
    assert "source_quote" in result["failures"][0]


def test_extra_quotes_checked():
    ex = make_ex(quote="exact quote here")
    # Manually set extra_quotes (not in Exercise schema, so test via dict)
    # Actually extra_quotes is stored in DB, not Exercise. Skip detailed test;
    # validator checks a list passed separately.
    from lifekit.validate.validator import validate_quotes
    result = validate_quotes(
        "exact quote here",
        ["good extra", "bad extra not in text"],
        "text with exact quote here and good extra",
    )
    assert result["ok"] is False
    assert len(result["failures"]) == 1


def test_zero_flag_triggers_on_long_chapter():
    assert should_flag_zero(chapter_chars=10000, exercise_count=0) is True


def test_zero_flag_not_on_short_chapter():
    assert should_flag_zero(chapter_chars=3000, exercise_count=0) is False


def test_zero_flag_not_when_exercises_exist():
    assert should_flag_zero(chapter_chars=10000, exercise_count=3) is False


def test_judge_sampling_ten_percent():
    # 20 exercises → 2 sampled (10%)
    ids = list(range(20))
    sampled = sample_for_judge(ids, pct=0.10, seed=42)
    assert len(sampled) == 2
    # Deterministic
    assert sample_for_judge(ids, pct=0.10, seed=42) == sampled


def test_judge_sampling_min_one():
    ids = [1, 2, 3]
    sampled = sample_for_judge(ids, pct=0.10, seed=42)
    assert len(sampled) == 1
