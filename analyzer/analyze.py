"""Rule-based analysis for PSRank problem statements."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, cast


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
        if re.search(
            r"(?<!\w)" + re.escape(keyword) + r"(?:s|es)?(?!\w)", normalized
        )
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


def _normalize_existing_problems(
    existing_problems: (
        Sequence[object] | Mapping[str, object] | str | bytes | None
    ),
) -> list[tuple[object, str]]:
    if existing_problems is None:
        return []

    if isinstance(existing_problems, (str, bytes)):
        candidate_text = existing_problems.decode() if isinstance(existing_problems, bytes) else existing_problems
        return [(0, candidate_text)] if candidate_text.strip() else []

    if isinstance(existing_problems, Mapping):
        candidate_id = existing_problems.get("id", 0)
        raw_text = existing_problems.get("text", existing_problems.get("problem", ""))
        candidate_text = raw_text if isinstance(raw_text, str) else ""
        return [(candidate_id, candidate_text)] if candidate_text.strip() else []

    try:
        items = list(existing_problems)
    except TypeError:
        return []

    candidates: list[tuple[object, str]] = []
    for index, item in enumerate(items):
        if isinstance(item, str):
            candidate_id, candidate_text = index, item
        elif isinstance(item, Mapping):
            problem = cast(Mapping[str, object], item)
            candidate_id = problem.get("id", index)
            raw_text = problem.get("text", problem.get("problem", ""))
            candidate_text = raw_text if isinstance(raw_text, str) else ""
        else:
            continue
        if candidate_text.strip():
            candidates.append((candidate_id, candidate_text))
    return candidates


def _similar_problems(
    text: str,
    existing_problems: (
        Sequence[object] | Mapping[str, object] | str | bytes | None
    ),
) -> tuple[list[dict[str, object]], float, str | None]:
    candidates = _normalize_existing_problems(existing_problems)
    if not candidates:
        return [], 0.0, None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as error:
        return [], 0.0, (
            "Similarity comparison was skipped because scikit-learn is not installed: "
            f"{error}"
        )

    texts = [text, *(candidate_text for _, candidate_text in candidates)]
    vectorizer: Any = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    if not any(re.search(r"\w", document) for document in texts):
        return [], 0.0, None

    matrix = vectorizer.fit_transform(texts)
    similarities = [
        float(value) for value in cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    ]
    highest = max(similarities, default=0.0)
    similar: list[dict[str, object]] = []
    for (candidate_id, _), similarity in zip(candidates, similarities):
        if similarity > 0.6:
            similar.append({"id": candidate_id, "similarity": round(similarity, 2)})
    return similar, highest, None


def _score_with_llm() -> dict[str, int] | None:
    """LLM scoring is not configured yet; returning None selects rule-based scoring."""
    return None


def analyze(
    text: object,
    existing_problems: (
        Sequence[object] | Mapping[str, object] | str | bytes | None
    ) = None,
) -> dict[str, Any]:
    """Score and categorize a problem statement, optionally comparing saved statements."""
    if text is None:
        return _fallback("Problem statement is empty; analysis could not be completed.")

    if not isinstance(text, str):
        text = str(text)

    clean_text = text.strip()
    if not clean_text:
        return _fallback("Problem statement is empty; analysis could not be completed.")

    similar, highest_similarity, similarity_note = _similar_problems(
        clean_text, existing_problems
    )
    has_existing_candidates = bool(_normalize_existing_problems(existing_problems))
    llm_breakdown = _score_with_llm()
    breakdown = llm_breakdown or _rule_based_breakdown(clean_text)
    if has_existing_candidates and similarity_note is None:
        breakdown["novelty"] = round((1 - highest_similarity) * 10)

    normalized_breakdown = {
        key: max(0, min(10, int(breakdown[key]))) for key in _WEIGHTS
    }
    score = round(
        sum(normalized_breakdown[key] * weight for key, weight in _WEIGHTS.items()) * 10
    )
    reason = (
        "Rule-based estimate using impact, feasibility, novelty, clarity, and data signals."
    )
    if similarity_note:
        reason = f"{reason} {similarity_note}"

    return {
        "score": max(0, min(100, score)),
        "breakdown": normalized_breakdown,
        "category": _category_for(clean_text),
        "similar": similar,
        "reason": reason,
    }