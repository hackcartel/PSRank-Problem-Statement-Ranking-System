"""Rule-based analysis for PSRank problem statements."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


_WEIGHTS: dict[str, float] = {
    "impact": 0.30,
    "feasibility": 0.25,
    "novelty": 0.20,
    "clarity": 0.15,
    "data": 0.10,
}

_CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Defence": ("defence", "defense", "military", "army", "soldier", "border"),
    "Marine": ("marine", "ocean", "sea", "ship", "fishing", "underwater"),
    "Web Development": ("website", "web app", "web development", "browser", "frontend"),
    "Hacking": ("cybersecurity", "cyber security", "hacking", "phishing", "malware"),
    "Gen AI": ("generative ai", "gen ai", "large language model", "llm", "chatbot"),
    "Education": (
        "education", "student", "students", "school", "schools",
        "teacher", "teachers", "classroom", "classrooms", "learning",
    ),
    "Analyzer/Predictor": ("analyzer", "analysis", "predictor", "prediction", "forecast"),
    "Medical Composition": ("drug composition", "medicine composition", "molecule", "formulation"),
    "Healthcare": ("healthcare", "hospital", "patient", "clinic", "diagnosis", "medical"),
    "Marketing": ("marketing", "advertising", "campaign", "customer", "brand"),
    "Space and Technology": (
        "space", "satellite", "astronomy", "rocket", "planet", "technology",
    ),
    "Fintech": ("fintech", "banking", "finance", "payment", "transaction", "digital wallet"),
    "Safety and Management": ("safety", "emergency", "disaster", "management", "incident"),
    "Agriculture": ("agriculture", "farmer", "farming", "crop", "irrigation", "soil"),
    "Hardware Integration": ("hardware", "iot", "sensor", "microcontroller", "embedded", "robotics"),
}

_IMPACT_KEYWORDS = (
    "improve", "reduce", "prevent", "access", "save", "protect", "support",
    "community", "people", "patient", "farmer", "student", "citizen",
)
_FEASIBILITY_KEYWORDS = (
    "build", "develop", "app", "platform", "system", "tool", "prototype",
    "automate", "connect", "monitor", "detect", "recommend",
)
_NOVELTY_KEYWORDS = ("novel", "innovative", "new approach", "unique", "first")
_DATA_KEYWORDS = (
    "dataset", "data", "database", "api", "survey", "sensor", "records",
    "open source", "public data", "historical data",
)


def _fallback(reason: str) -> dict[str, Any]:
    """Return a safe result matching the integration contract."""
    return {
        "score": 0,
        "breakdown": {name: 0 for name in _WEIGHTS},
        "category": "Uncategorized",
        "similar": [],
        "reason": reason,
    }


def _mentions(text: str, keywords: Sequence[str]) -> int:
    normalized = re.sub(r"[^\w]+", " ", text.lower()).strip()
    return sum(
        1
        for keyword in keywords
        if re.search(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", normalized)
    )


def _rule_based_breakdown(text: str) -> dict[str, int]:
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)

    impact = min(10, 2 + 2 * _mentions(text, _IMPACT_KEYWORDS))
    feasibility = min(10, 3 + 2 * _mentions(text, _FEASIBILITY_KEYWORDS))
    novelty = min(10, 4 + 2 * _mentions(text, _NOVELTY_KEYWORDS))
    data = min(10, 2 + 3 * _mentions(text, _DATA_KEYWORDS))

    clarity = min(10, max(1, word_count // 12))
    if re.search(r"\b(who|for|users|people|farmers|students|patients)\b", text, re.I):
        clarity += 2
    if re.search(r"\b(problem|because|so that|to help|solution)\b", text, re.I):
        clarity += 2
    if re.search(r"[.!?]", text):
        clarity += 1

    return {
        "impact": impact,
        "feasibility": feasibility,
        "novelty": novelty,
        "clarity": min(10, clarity),
        "data": data,
    }


def _category_for(text: str) -> str:
    matches = [
        (_mentions(text, keywords), category)
        for category, keywords in _CATEGORY_KEYWORDS.items()
    ]
    count, category = max(matches, key=lambda match: match[0], default=(0, "Uncategorized"))
    return category if count else "Uncategorized"


def _similar_problems(
    text: str,
    existing_problems: Sequence[str | Mapping[str, object]] | None,
) -> tuple[list[dict[str, object]], float]:
    if not existing_problems:
        return [], 0.0

    candidates: list[tuple[object, str]] = []
    for index, item in enumerate(existing_problems):
        if isinstance(item, str):
            candidate_id, candidate_text = index, item
        else:
            candidate_id: object = item.get("id", index)
            raw_text: object = item.get("text", item.get("problem", ""))
            candidate_text = raw_text if isinstance(raw_text, str) else ""
        if candidate_text.strip():
            candidates.append((candidate_id, candidate_text))

    if not candidates:
        return [], 0.0

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    texts = [text, *(candidate_text for _, candidate_text in candidates)]
    vectorizer: Any = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)
    similarities = [
        float(value) for value in cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    ]
    highest = max(similarities, default=0.0)
    similar: list[dict[str, object]] = []
    for (candidate_id, _), similarity in zip(candidates, similarities):
        if similarity > 0.6:
            similar.append({"id": candidate_id, "similarity": round(similarity, 2)})
    return similar, highest


def _score_with_llm() -> dict[str, int] | None:
    """LLM scoring is not configured yet; returning None selects rule-based scoring."""
    return None


def analyze(
    text: str,
    existing_problems: Sequence[str | Mapping[str, object]] | None = None,
) -> dict[str, Any]:
    """Score and categorize a problem statement, optionally comparing saved statements."""
    try:
        clean_text = text.strip()
        if not clean_text:
            return _fallback("Problem statement is empty; analysis could not be completed.")

        similar, highest_similarity = _similar_problems(clean_text, existing_problems)
        llm_breakdown = _score_with_llm()
        breakdown = llm_breakdown or _rule_based_breakdown(clean_text)
        if highest_similarity > 0:
            breakdown["novelty"] = round((1 - highest_similarity) * 10)

        score = round(sum(breakdown[key] * weight for key, weight in _WEIGHTS.items()) * 10)
        return {
            "score": max(0, min(100, score)),
            "breakdown": {
                key: max(0, min(10, int(breakdown[key]))) for key in _WEIGHTS
            },
            "category": _category_for(clean_text),
            "similar": similar,
            "reason": "Rule-based estimate using impact, feasibility, novelty, clarity, and data signals.",
        }
    except Exception:
        return _fallback("Analysis failed safely; please retry with a valid problem statement.")