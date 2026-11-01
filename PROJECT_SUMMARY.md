# PSRank: Project Summary and Workflow Guide

Quick read for anyone who clones this repo. It covers what we are building, who owns what, the order of work from 0% to 100%, and how we work together.

Last updated: 1 Nov 2026 | Target demo: 4 Nov 2026

---

## 1. What we are building (30 seconds)

PSRank is an internal HackCartel platform where members submit problem statements (PS), the system scores them, and everyone sees a ranked list.

```
Dashboard -> Login -> Submit PS (text) -> Analyzer (score) -> Sorting -> Ranked list for all users
```

Scope rule: build only this workflow. No extra modules. Simple and working beats fancy and broken.

---

## 2. Decisions so far

| Decision | Status |
|---|---|
| No admin login for now, only normal email login to add PS | Decided (Yash, 1 Nov) |
| Backend: FastAPI, database: Supabase, frontend: with Raj | Confirmed by Raj, details TBC |
| Analyzer is a standalone Python module, easy to import | Decided |
| Sorting: store the score, order by score (high to low) | Decided |
| Keep it simple and working (Yash) | Decided |
| Document everything in short form | Decided |

Note: the main README still mentions Admin Login. Update it once the final scope is confirmed.

---

## 3. Team and ownership

| Area | Owner | Notes |
|---|---|---|
| Analyzer (scoring) and Sorting logic | Haroon | Python module |
| Authentication, backend, dashboard | Raj Pandey and Ayush | FastAPI + Supabase |
| Backup and overview | Deven and Parv | Step in if anyone is blocked |
| Oversight and recommendations | Sairaj and Yash | Review and validate |

Rule: one owner per area. If you need something from another area, tag the owner in the group.

---

## 4. Integration contract (the most important part)

The analyzer is called by the backend. Both sides agree on this format.

Function: `analyze(text: str) -> dict`
Optional endpoint: `POST /analyze`

Input:
```json
{ "problem": "problem statement text" }
```

Output:
```json
{
  "score": 78,
  "breakdown": { "impact": 8, "feasibility": 7, "novelty": 6, "clarity": 9, "data": 7 },
  "category": "Healthcare",
  "similar": [{ "id": 12, "similarity": 0.81 }],
  "reason": "short explanation"
}
```

Rules:
- `score` is always 0-100. Every breakdown value is 0-10.
- Never crash. On any error, return a safe fallback result with a clear `reason`.
- Sorting is done by the database: save `score`, then `ORDER BY score DESC`.

---

## 5. Roadmap: 0% to 100%

Each step shows what must be done before it can start.

| % | Milestone | Owner | Depends on | Target |
|---|---|---|---|---|
| 0% | Roles decided, repo shared | All | - | 1 Nov |
| 10% | Everyone has repo access and works from own branch | All | 0% | 1 Nov |
| 20% | Integration contract agreed (section 4) | Haroon + Raj | 10% | 1 Nov |
| 35% | Analyzer v1: rule-based scoring working with 5 test PS | Haroon | 20% | 1-2 Nov |
| 40% | Database table and email login ready | Raj + Ayush | 20% | 2 Nov |
| 50% | Submit PS form saves to database | Raj + Ayush | 40% | 2 Nov |
| 60% | Analyzer connected to backend, score saved per PS | Haroon + Raj | 35%, 50% | 2-3 Nov |
| 70% | Sorted ranked list shown to all users | Raj + Ayush + Haroon | 60% | 3 Nov |
| 80% | Analyzer v2: category tagging + similar PS detection | Haroon | 60% | 3 Nov |
| 90% | Testing: edge cases, bug fixes, README updated | All | 70% | 3-4 Nov |
| 100% | Demo ready, short docs done | All | 90% | 4 Nov |

Optional (only if time remains): LLM scoring with reasons, admin weight sliders, charts. These never block the 100% line.

---

## 6. Analyzer plan (Haroon)

Scoring criteria (weights can be tuned):

| Criterion | Weight |
|---|---|
| Impact | 30% |
| Feasibility | 25% |
| Novelty | 20% |
| Clarity | 15% |
| Data availability | 10% |

Formula: `score = (0.30*impact + 0.25*feasibility + 0.20*novelty + 0.15*clarity + 0.10*data) * 10`

Versions:
- v1 (rule-based): word count, who/what/why checks, impact keywords, data keywords. No external service needed.
- v2: category tagging (15 categories by keywords), similar/duplicate detection (TF-IDF + cosine similarity, flag above 0.6). Novelty = 1 - highest similarity.
- v3 (optional): LLM scoring with a short reason. Low temperature, validate JSON, fall back to v1 if it fails.

Categories: Defence, Marine, Web Development, Hacking, Gen AI, Education, Analyzer/Predictor, Medical Composition, Healthcare, Marketing, Space and Technology, Fintech, Safety and Management, Agriculture, Hardware Integration.

Libraries: `fastapi`, `pydantic`, `scikit-learn` (v2), optional `sentence-transformers` and an LLM client (v3).

Edge cases to test: empty text, very short text, very long text, symbols only, Hinglish text, duplicate PS.

---

## 7. How we work

- Branches: `main` stays stable. Each person works on their own branch (for example `analyzer`, `backend`, `dashboard`).
- Commits: use your own GitHub account so credit is clear. Short messages like `analyzer: add v1 scoring`.
- Merge: open a pull request. A second person quickly checks, then merge to `main`.
- Updates: one short message in the group at the start and end of each work session. Tag the owner if you are blocked.
- Docs: keep a short README or notes in your own folder. Update the Status table below when you finish a milestone.
- No passwords or API keys in the repo. Use environment variables or a `.env` file that is not committed.

Suggested folder layout (adjust with the team):
```
/analyzer     scoring module (Haroon)
/backend      FastAPI + auth (Raj, Ayush)
/frontend     dashboard and forms
PROJECT_SUMMARY.md
README.md
```

---

## 8. Risks and fixes

| Risk | Fix |
|---|---|
| Stack or format changes late | Keep the analyzer standalone behind `analyze(text)` |
| External LLM fails or is slow | Fallback to rule-based scoring |
| Too many people on one tool | Stay with the 3 owners plus backup |
| Time is short | Ship the 70% line first, upgrade after |
| Scope creep | Follow the workflow in section 1 only |

---

## 9. Status tracker (update as you go)

| Milestone | Status | Updated by | Date |
|---|---|---|---|
| Roles and repo access | Done | Haroon | 1 Nov |
| Integration contract | In progress | Haroon + Raj | 1 Nov |
| Analyzer v1 | Not started | Haroon | - |
| Database and login | In progress | Raj | 1 Nov |
| Submit PS form | Not started | Raj + Ayush | - |
| Integration | Not started | - | - |
| Ranked list display | Not started | - | - |
| Analyzer v2 | Not started | Haroon | - |
| Testing and docs | Not started | All | - |

---

## 10. Definition of done (100%)

- A member can log in with email and submit a PS.
- The analyzer scores it and saves the result.
- The ranked list shows for all users, highest score first.
- Tested on at least 10 sample problem statements without crashes.
- README and this file are up to date.
