import unittest
from unittest.mock import patch

from analyze import analyze


SAMPLE_PROBLEMS = (
    (
        "Farmers need an agriculture platform to monitor crop health using sensor data.",
        "Agriculture",
    ),
    (
        "Build a healthcare tool that helps patients find nearby clinics and medical support.",
        "Healthcare",
    ),
    (
        "Create a fintech app to detect unusual payment transactions using banking data.",
        "Fintech",
    ),
    (
        "Develop an education website that helps students practice lessons with teachers.",
        "Education",
    ),
    (
        "Create a cybersecurity system to detect phishing attacks and protect users.",
        "Hacking",
    ),
)


class AnalyzeTests(unittest.TestCase):
    def test_five_sample_problem_statements(self):
        for problem, expected_category in SAMPLE_PROBLEMS:
            with self.subTest(category=expected_category):
                result = analyze(problem)
                self.assertEqual(result["category"], expected_category)
                self.assertGreaterEqual(result["score"], 0)
                self.assertLessEqual(result["score"], 100)
                self.assertEqual(
                    set(result["breakdown"]),
                    {"impact", "feasibility", "novelty", "clarity", "data"},
                )
                self.assertTrue(all(0 <= value <= 10 for value in result["breakdown"].values()))

    def test_empty_text_returns_safe_fallback(self):
        result = analyze("")
        self.assertEqual(result["score"], 0)
        self.assertTrue(result["reason"])
        self.assertEqual(result["similar"], [])

    def test_very_short_text_does_not_crash(self):
        result = analyze("Fix this.")
        self.assertIsInstance(result["category"], str)
        self.assertTrue(0 <= result["score"] <= 100)

    def test_very_long_text_does_not_exceed_score_ranges(self):
        result = analyze(("Farmers need crop data to improve farming. " * 2000).strip())
        self.assertLessEqual(result["score"], 100)
        self.assertTrue(all(0 <= value <= 10 for value in result["breakdown"].values()))

    def test_symbols_only_text_does_not_crash(self):
        result = analyze("!@#$%^&*()")
        self.assertIn(result["score"], range(101))

    def test_hinglish_text_does_not_crash(self):
        result = analyze("Gaon ke farmers ke liye crop health monitor karne wala agriculture app.")
        self.assertEqual(result["category"], "Agriculture")

    def test_duplicate_detection_and_novelty(self):
        original = "Build an app that helps farmers monitor crop health using sensor data."
        result = analyze(
            original,
            existing_problems=[
                {"id": 12, "text": original},
                {"id": 13, "text": "A space satellite studies distant planets."},
            ],
        )
        self.assertEqual(result["similar"], [{"id": 12, "similarity": 1.0}])
        self.assertEqual(result["breakdown"]["novelty"], 0)

    def test_invalid_input_returns_safe_fallback(self):
        result = analyze(None)  # type: ignore[arg-type]
        self.assertEqual(result["score"], 0)
        self.assertTrue(result["reason"])

    def test_invalid_similarity_inputs_are_ignored(self):
        result = analyze(
            "Build an app that helps farmers monitor crop health using sensor data.",
            existing_problems=[
                42,
                {"id": 99, "text": 123},
                "valid text",
                {"id": 1, "text": "A different problem statement."},
            ],
        )
        self.assertIsInstance(result["similar"], list)
        self.assertTrue(0 <= result["score"] <= 100)

    def test_numeric_text_is_converted_to_string(self):
        result = analyze(12345)
        self.assertIsInstance(result["category"], str)
        self.assertTrue(0 <= result["score"] <= 100)

    def test_punctuation_only_similarity_corpus_does_not_fail_analysis(self):
        result = analyze("!!!", existing_problems=["???"])

        self.assertEqual(result["category"], "Uncategorized")
        self.assertEqual(result["similar"], [])
        self.assertTrue(0 <= result["score"] <= 100)

    def test_single_character_tokens_are_compared(self):
        result = analyze("X", existing_problems=["X"])

        self.assertEqual(result["similar"], [{"id": 0, "similarity": 1.0}])
        self.assertEqual(result["breakdown"]["novelty"], 0)

    def test_missing_similarity_dependency_is_reported_without_losing_score(self):
        with patch.dict("sys.modules", {"sklearn.feature_extraction.text": None}):
            result = analyze(
                "Farmers need an agriculture app.",
                existing_problems=["Farmers need an app."],
            )

        self.assertGreater(result["score"], 0)
        self.assertIn("scikit-learn is not installed", result["reason"])

    def test_score_matches_clamped_breakdown(self):
        llm_breakdown = {
            "impact": 20,
            "feasibility": -1,
            "novelty": 4,
            "clarity": 5,
            "data": 3,
        }
        with patch("analyze._score_with_llm", return_value=llm_breakdown):
            result = analyze("A valid problem statement.")

        expected_score = round(
            sum(
                result["breakdown"][key] * weight
                for key, weight in {
                    "impact": 0.30,
                    "feasibility": 0.25,
                    "novelty": 0.20,
                    "clarity": 0.15,
                    "data": 0.10,
                }.items()
            )
            * 10
        )
        self.assertEqual(result["score"], expected_score)
        self.assertEqual(result["breakdown"]["impact"], 10)
        self.assertEqual(result["breakdown"]["feasibility"], 0)


if __name__ == "__main__":
    unittest.main()