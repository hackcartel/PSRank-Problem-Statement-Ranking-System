"""Tests for the PSRank FastAPI wrapper."""

import unittest
from typing import Any, Protocol, cast
from unittest.mock import patch

from fastapi.testclient import TestClient
from httpx import Response

from api import app


class ApiTestClient(Protocol):
    """Typed surface of TestClient used by these tests."""

    def get(self, url: str, **kwargs: Any) -> Response: ...

    def post(self, url: str, **kwargs: Any) -> Response: ...

    def request(self, method: str, url: str, **kwargs: Any) -> Response: ...


class AnalyzerApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client: ApiTestClient = cast(
            ApiTestClient, TestClient(app, raise_server_exceptions=False)
        )

    def test_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_analyze_returns_expected_shape(self) -> None:
        response = self.client.post(
            "/analyze",
            json={
                "problem": (
                    "Farmers need an agriculture platform to monitor crop health "
                    "using sensor data."
                )
            },
        )
        result: dict[str, Any] = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            {"score", "breakdown", "category", "similar", "reason"}.issubset(result)
        )
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertEqual(
            set(result["breakdown"]),
            {"impact", "feasibility", "novelty", "clarity", "data"},
        )

    def test_text_alias(self) -> None:
        response = self.client.post(
            "/analyze", json={"text": "Farmers need help improving crop health."}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("score", response.json())

    def test_empty_and_whitespace_problems_return_safe_fallback(self) -> None:
        for problem in ("", "   \t\n"):
            with self.subTest(problem=repr(problem)):
                response = self.client.post("/analyze", json={"problem": problem})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["score"], 0)

    def test_problem_over_limit_is_rejected(self) -> None:
        response = self.client.post("/analyze", json={"problem": "x" * 5001})
        self.assertEqual(response.status_code, 422)

    def test_duplicate_existing_problem_is_reported_as_similar(self) -> None:
        problem = "Farmers need an app to monitor crop health using sensor data."
        response = self.client.post(
            "/analyze",
            json={
                "problem": problem,
                "existing_problems": [{"id": 12, "text": problem}],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["similar"])

    def test_analyze_existing_problems_limit(self) -> None:
        response = self.client.post(
            "/analyze",
            json={"problem": "A valid problem.", "existing_problems": [{}] * 501},
        )
        self.assertEqual(response.status_code, 422)

    def test_unexpected_error_is_generic(self) -> None:
        with patch("api.analyze", side_effect=RuntimeError("private details")):
            response = self.client.post(
                "/analyze", json={"problem": "do not echo this text"}
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Internal server error"})

    def test_rank_order_ties_ranks_and_extra_fields(self) -> None:
        items: list[dict[str, Any]] = [
            {"id": 1, "score": 80, "created_at": "2025-02-01", "custom": "kept"},
            {"id": 2, "score": 90, "created_at": "2025-03-01"},
            {"id": 3, "score": 80, "created_at": "2025-01-01"},
        ]
        response = self.client.post("/rank", json={"items": items})
        ranked: list[dict[str, Any]] = response.json()["items"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in ranked], [2, 3, 1])
        self.assertEqual([item["rank"] for item in ranked], [1, 2, 3])
        self.assertEqual(ranked[2]["custom"], "kept")

    def test_rank_category_filter_and_top_n(self) -> None:
        items: list[dict[str, Any]] = [
            {"id": 1, "score": 90, "created_at": "2025-01-01", "category": "Health"},
            {"id": 2, "score": 80, "created_at": "2025-01-01", "category": "Education"},
            {"id": 3, "score": 70, "created_at": "2025-01-01", "category": "Education"},
        ]
        response = self.client.post(
            "/rank", json={"items": items, "category": "Education", "top_n": 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()["items"]], [2])

    def test_rank_empty_list(self) -> None:
        response = self.client.post("/rank", json={"items": []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"items": []})

    def test_rank_items_limit(self) -> None:
        response = self.client.post("/rank", json={"items": [{}] * 2001})
        self.assertEqual(response.status_code, 422)

    def test_invalid_requests_return_422(self) -> None:
        invalid_requests: tuple[tuple[str, str, dict[str, Any]], ...] = (
            ("POST", "/analyze", {}),
            ("POST", "/analyze", {"problem": 42}),
            ("POST", "/analyze", {"problem": "valid", "existing_problems": "wrong"}),
            ("POST", "/rank", {}),
            ("POST", "/rank", {"items": "wrong"}),
        )
        for method, path, body in invalid_requests:
            with self.subTest(path=path, body=body):
                response = self.client.request(method, path, json=body)
                self.assertEqual(response.status_code, 422)

    def test_cors_allows_vite_origin(self) -> None:
        response = self.client.get(
            "/health", headers={"Origin": "http://localhost:5173"}
        )
        self.assertEqual(
            response.headers["access-control-allow-origin"], "http://localhost:5173"
        )

    def test_analyze_then_rank_three_problems(self) -> None:
        problems = (
            "Farmers need an agriculture platform to monitor crop health using sensor data.",
            "A healthcare tool should help patients find nearby clinics.",
            "An education platform can help students practice lessons with teachers.",
        )
        items: list[dict[str, Any]] = []
        for index, problem in enumerate(problems, 1):
            analyzed = self.client.post("/analyze", json={"problem": problem})
            self.assertEqual(analyzed.status_code, 200)
            items.append(
                {
                    "id": index,
                    "text": problem,
                    "created_at": f"2025-01-0{index}",
                    **analyzed.json(),
                }
            )

        ranked = self.client.post("/rank", json={"items": items})
        self.assertEqual(ranked.status_code, 200)
        self.assertEqual(
            [item["rank"] for item in ranked.json()["items"]], [1, 2, 3]
        )


if __name__ == "__main__":
    unittest.main()
