"""FastAPI endpoints for the PSRank analyzer."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

try:
    from .analyze import analyze
    from .ranking import rank_problems
except ImportError:
    from analyze import analyze
    from ranking import rank_problems


class AnalyzeRequest(BaseModel):
    """Input for scoring one problem statement."""

    model_config = ConfigDict(extra="ignore")

    problem: str = Field(
        max_length=5000,
        validation_alias=AliasChoices("problem", "text"),
    )
    existing_problems: list[dict[str, Any]] | None = Field(default=None, max_length=500)


class RankRequest(BaseModel):
    """Input for ranking analyzed problem statements."""

    items: list[dict[str, Any]] = Field(max_length=2000)
    category: str | None = None
    top_n: int | None = None


app = FastAPI(title="PSRank Analyzer API")
allowed_origins = os.getenv("ALLOWED_ORIGINS")
origins = (
    ["http://localhost:5173", "http://127.0.0.1:5173"]
    if allowed_origins is None
    else [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def handle_unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
    """Return a generic response without exposing internal details."""
    _ = (_request, _exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the analyzer API is available."""
    return {"status": "ok"}


@app.post("/analyze")
def analyze_problem(request: AnalyzeRequest) -> dict[str, Any]:
    """Score one problem statement."""
    return analyze(request.problem, existing_problems=request.existing_problems)


@app.post("/rank")
def rank(request: RankRequest) -> dict[str, list[dict[str, Any]]]:
    """Return the requested problems with rank numbers."""
    return {
        "items": rank_problems(
            request.items,
            category=request.category,
            top_n=request.top_n,
        )
    }
