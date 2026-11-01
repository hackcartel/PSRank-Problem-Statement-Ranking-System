import unittest

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


if __name__ == "__main__":
    unittest.main()