"""Sorting helpers for scored PSRank problem statements."""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import Decimal
from numbers import Number
from typing import cast


def _score_key(value: object) -> float:
    """Return a clamped score, treating invalid values as zero."""
    if isinstance(value, bool) or not isinstance(value, (Number, Decimal)):
        return 0.0

    try:
        score = float(cast(float, value))
    except (OverflowError, TypeError, ValueError):
        if isinstance(value, int):
            return 100.0 if value > 0 else 0.0
        return 0.0

    if math.isnan(score):
        return 0.0
    return max(0.0, min(100.0, score))


def _created_at_key(value: object) -> tuple[int, int, int, int, int, int, int, int]:
    """Convert a datetime or ISO string to a sortable UTC key."""
    parsed: datetime | None = None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        iso_value = value.strip()
        if iso_value.endswith("Z"):
            iso_value = f"{iso_value[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(iso_value)
        except ValueError:
            pass

    if parsed is None:
        return (1, 0, 0, 0, 0, 0, 0, 0)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    try:
        parsed = parsed.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return (1, 0, 0, 0, 0, 0, 0, 0)
    return (
        0,
        parsed.year,
        parsed.month,
        parsed.day,
        parsed.hour,
        parsed.minute,
        parsed.second,
        parsed.microsecond,
    )


def _id_key(value: object) -> tuple[int, int | str, str]:
    """Order integer ids numerically and string ids lexicographically."""
    if isinstance(value, int) and not isinstance(value, bool):
        return (0, value, "")
    if isinstance(value, str):
        return (1, value, "")
    return (2, type(value).__qualname__, repr(value))


def rank_problems(
    items: Sequence[object] | None,
    category: str | None = None,
    top_n: int | None = None,
) -> list[dict[str, object]]:
    """Return copied problem dictionaries ordered by score, date, and id."""
    if items is None:
        return []

    problems: list[dict[str, object]] = [
        cast(dict[str, object], item) for item in items if isinstance(item, dict)
    ]
    if category is not None:
        normalized_category = category.strip().casefold()
        category_matches: list[dict[str, object]] = []
        for item in problems:
            item_category = item.get("category")
            if (
                isinstance(item_category, str)
                and item_category.strip().casefold() == normalized_category
            ):
                category_matches.append(item)
        problems = category_matches

    problems.sort(
        key=lambda item: (
            -_score_key(item.get("score")),
            _created_at_key(item.get("created_at")),
            _id_key(item.get("id")),
        )
    )

    ranked: list[dict[str, object]] = []
    for index, problem in enumerate(problems, 1):
        ranked_problem = dict(problem)
        ranked_problem["rank"] = index
        ranked.append(ranked_problem)

    if isinstance(top_n, int) and not isinstance(top_n, bool) and top_n > 0:
        return ranked[:top_n]
    return ranked
