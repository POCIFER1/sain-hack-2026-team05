from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


SCHEMA_PATH = (
    Path(__file__).resolve().parent
    / "schemas"
    / "Case3Answers.schema.json"
)

PROFILE_FIELDS = (
    "chronotype",
    "weekday_bedtime",
    "weekday_wake_time",
    "average_sleep_hours",
    "social_jetlag",
    "activity_level",
    "sedentary_hours",
    "training_days",
    "works_from_home",
    "phone_before_sleep",
    "movement_index",
)

_PROFILE_FIELD_SET = frozenset(PROFILE_FIELDS)


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    """Load and cache the official Case 3 answers validator."""
    with SCHEMA_PATH.open(encoding="utf-8") as source:
        schema = json.load(source)

    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def unknown_profile() -> dict[str, dict[str, Any]]:
    """Create a profile with no inferred values."""
    return {
        field: {
            "value": "unknown",
            "confidence": 0.0,
        }
        for field in PROFILE_FIELDS
    }


def make_week_answer(
    record_id: str,
    profile: Mapping[str, Mapping[str, Any]],
    hypotheses: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a week answer, defaulting unspecified profile fields to unknown."""
    unexpected_fields = set(profile) - _PROFILE_FIELD_SET

    if unexpected_fields:
        fields = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unexpected profile fields: {fields}")

    complete_profile = unknown_profile()

    for field, prediction in profile.items():
        complete_profile[field] = dict(prediction)

    return {
        "record_id": record_id,
        "profile": complete_profile,
        "hypotheses": [
            dict(hypothesis)
            for hypothesis in hypotheses
        ],
    }


def validate_case3_answers(
    answers: dict[str, Any],
    expected_record_ids: Iterable[str] | None = None,
) -> None:
    """Validate answer structure, record uniqueness, and dataset coverage."""
    validation_error = next(
        _validator().iter_errors(answers),
        None,
    )

    if validation_error is not None:
        path = "$"

        for segment in validation_error.absolute_path:
            if isinstance(segment, int):
                path += f"[{segment}]"
            else:
                path += f".{segment}"

        raise ValueError(
            f"Case3Answers schema violation at {path}: "
            f"{validation_error.validator}"
        ) from None

    record_ids = [
        week["record_id"]
        for week in answers["weeks"]
    ]

    actual_ids = set(record_ids)

    if len(record_ids) != len(actual_ids):
        raise ValueError(
            "Duplicate record_id in Case3Answers"
        )

    if expected_record_ids is None:
        return

    expected_ids = list(expected_record_ids)
    expected_set = set(expected_ids)

    if len(expected_ids) != len(expected_set):
        raise ValueError(
            "Duplicate record_id in dataset"
        )

    if actual_ids != expected_set:
        raise ValueError(
            "Case3Answers weeks do not match dataset record_ids"
        )
