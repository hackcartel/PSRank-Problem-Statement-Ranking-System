# PSRank
### Problem Statement Ranking System

**An internal HackCartel platform for submitting, analyzing, scoring, and ranking hackathon problem statements.**

---

## About the Project

PSRank is an internal platform being developed for the HackCartel community as part of our internal hackathon.

The platform provides a centralized system where members can submit problem statements (PS), get them analyzed and scored, and view an automatically sorted ranking based on their scores.

The objective is to make problem statement evaluation and comparison simple, structured, and accessible to all members.

## Workflow

```text
              DASHBOARD
                  |
   GITHUB SIGN-IN (VIA SUPABASE)
                  |
       SUBMIT PROBLEM STATEMENT
                  |
      FASTAPI ANALYZER API
       (Score and categorize)
                  |
          RANKING SYSTEM
                  |
       DISPLAY RANKED RESULTS
          FOR ALL USERS
```

## Core Features

| Module | Functionality |
|---|---|
| Dashboard | Central interface for the platform |
| GitHub sign-in (via Supabase) | Authenticates users |
| Text Input | Signed-in users can submit problem statements |
| FastAPI Analyzer API | Evaluates and scores each PS |
| Sorting System | Automatically sorts problem statements by score |
| Results Display | Makes ranked problem statements visible to all users |

## User Roles

**Signed-in user**
- Sign in with GitHub through Supabase.
- Submit problem statements.
- View ranked problem statements.

**All Users**
- View the final sorted problem statements.

## Project Scope

PSRank will focus strictly on the workflow defined for the HackCartel internal hackathon.

The development will follow a simple, structured approach without unnecessary features or additional modules.

## Development

The analyzer API, frontend, and Supabase integration are implemented. LLM scoring
and deployment remain pending.

## Docker (API)

Build and run the analyzer API:

```sh
docker build -f analyzer/Dockerfile -t psrank-api .
docker run --rm -p 8000:8000 -e ALLOWED_ORIGINS=http://localhost:5173 psrank-api
```

Set `ALLOWED_ORIGINS` to the URL of the frontend that will call the API.

## Organization

**Developed by [HackCartel](https://github.com/HackCartel)**

Building practical solutions through collaboration, technology, and innovation.

---

*PSRank — Making problem statement evaluation structured and accessible.*
