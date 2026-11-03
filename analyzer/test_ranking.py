"""Tests for PSRank problem ranking and sorting."""

import unittest
from datetime import datetime, timezone
from typing import cast

from analyze import analyze
from ranking import rank_problems


class RankProblemsTests(unittest.TestCase):
    def test_orders_by_score_descending(self):
        result = rank_problems(
            [
                {"id": 1, "score": 40, "created_at": "2025-01-01"},
                {"id": 2, "score": 90, "created_at": "2025-01-01"},
                {"id": 3, "score": 70, "created_at": "2025-01-01"},
            ]
        )
        self.assertEqual([problem["id"] for problem in result], [2, 3, 1])

    def test_ties_use_created_at_then_id(self):
        result = rank_problems(
            [
                {"id": 8, "score": 50, "created_at": "2025-02-01T00:00:00Z"},
                {"id": 3, "score": 50, "created_at": "2025-01-01T00:00:00Z"},
                {"id": 1, "score": 50, "created_at": "2025-01-01T00:00:00Z"},
            ]
        )
        self.assertEqual([problem["id"] for problem in result], [1, 3, 8])

    def test_mixed_id_types_sort_safely(self):
        result = rank_problems(
            [
                {"id": "1", "score": 10, "created_at": "2025-01-01"},
                {"id": 2, "score": 10, "created_at": "2025-01-01"},
                {"id": 1, "score": 10, "created_at": "2025-01-01"},
            ]
        )
        self.assertEqual([problem["id"] for problem in result], [1, 2, "1"])

    def test_invalid_scores_are_zero_and_numeric_scores_are_clamped(self):
        result = rank_problems(
            [
                {"id": 1, "score": None, "created_at": "2025-01-01"},
                {"id": 2, "score": "99", "created_at": "2025-01-01"},
                {"id": 3, "score": float("nan"), "created_at": "2025-01-01"},
                {"id": 4, "score": True, "created_at": "2025-01-01"},
                {"id": 5, "score": 101, "created_at": "2025-01-01"},
                {"id": 6, "score": -5, "created_at": "2025-01-01"},
                {"id": 7, "created_at": "2025-01-01"},
            ]
        )
        self.assertEqual([problem["id"] for problem in result], [5, 1, 2, 3, 4, 6, 7])
        self.assertEqual([problem["rank"] for problem in result], list(range(1, 8)))

    def test_empty_none_and_non_dict_items(self):
        self.assertEqual(rank_problems([]), [])
        self.assertEqual(rank_problems(None), [])
        self.assertEqual(rank_problems([None, 42, "not a problem"]), [])

    def test_input_list_and_dicts_are_not_mutated(self):
        original_item: dict[str, object] = {
            "id": 1,
            "score": 30,
            "created_at": "2025-01-01",
            "extra": ["x"],
        }
        original_list: list[dict[str, object]] = [original_item]
        result = rank_problems(original_list)

        self.assertEqual(original_list, [original_item])
        self.assertNotIn("rank", original_item)
        self.assertIsNot(result[0], original_item)
        self.assertIs(result[0]["extra"], original_item["extra"])
        self.assertEqual(result[0]["rank"], 1)

    def test_category_filter_and_top_n(self):
        items: list[dict[str, object]] = [
            {"id": 1, "score": 95, "created_at": "2025-01-01", "category": "Health"},
            {"id": 2, "score": 80, "created_at": "2025-01-01", "category": " education "},
            {"id": 3, "score": 90, "created_at": "2025-01-01", "category": "Education"},
        ]
        result = rank_problems(items, category=" EDUCATION ", top_n=1)
        self.assertEqual([problem["id"] for problem in result], [3])
        self.assertEqual([problem["rank"] for problem in result], [1])

    def test_invalid_top_n_is_ignored(self):
        items: list[dict[str, object]] = [
            {"id": 1, "score": 2, "created_at": "2025-01-01"},
            {"id": 2, "score": 1, "created_at": "2025-01-01"},
        ]
        invalid_limits: tuple[object, ...] = (None, 0, -1, 1.5, True, "1")
        for top_n in invalid_limits:
            with self.subTest(top_n=top_n):
                self.assertEqual(
                    len(rank_problems(items, top_n=cast(int | None, top_n))),
                    2,
                )

    def test_datetime_objects_and_invalid_dates(self):
        result = rank_problems(
            [
                {"id": 1, "score": 20, "created_at": None},
                {"id": 2, "score": 20, "created_at": "not a date"},
                {
                    "id": 3,
                    "score": 20,
                    "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
                },
                {"id": 4, "score": 20},
            ]
        )
        self.assertEqual([problem["id"] for problem in result], [3, 1, 2, 4])

    def test_ranks_are_consecutive_after_filter_and_limit(self):
        result = rank_problems(
            [
                {"id": 1, "score": 10, "created_at": "2025-01-01", "category": "A"},
                {"id": 2, "score": 9, "created_at": "2025-01-01", "category": "B"},
                {"id": 3, "score": 8, "created_at": "2025-01-01", "category": "A"},
            ],
            category="a",
            top_n=2,
        )
        self.assertEqual([problem["rank"] for problem in result], [1, 2])

    def test_extra_fields_are_preserved(self):
        item: dict[str, object] = {
            "id": 1,
            "score": 80,
            "created_at": "2025-01-01",
            "breakdown": {"impact": 8},
            "reason": "Good impact",
            "similar": [],
            "custom": "keep",
        }
        result = rank_problems([item])[0]
        self.assertEqual({key: value for key, value in result.items() if key != "rank"}, item)

    def test_integration_with_analyze(self):
        samples: list[dict[str, object]] = [
            {
                "id": 3,
                "text": "Build an app to help farmers monitor crop health using sensor data.",
                "created_at": "2025-01-03T00:00:00Z",
            },
            {
                "id": 2,
                "text": "Create a healthcare tool to help patients find clinics.",
                "created_at": "2025-01-02T00:00:00Z",
            },
            {
                "id": 1,
                "text": "Develop an education platform to support students and teachers.",
                "created_at": "2025-01-01T00:00:00Z",
            },
        ]
        analyzed: list[dict[str, object]] = []
        for sample in samples:
            analyzed.append({**sample, **analyze(sample["text"])})
        result = rank_problems(analyzed)

        self.assertEqual(len(result), 3)
        self.assertEqual([problem["rank"] for problem in result], [1, 2, 3])
        ranked_scores = [problem["score"] for problem in result]
        analyzed_scores = [problem["score"] for problem in analyzed]
        self.assertEqual(
            ranked_scores,
            sorted(analyzed_scores, key=lambda score: float(cast(float, score)), reverse=True),
        )


if __name__ == "__main__":
    unittest.main()
