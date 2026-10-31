from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

DeathMode = Literal["abandoned", "pivoted", "completed", "burned_out", "alive", "insufficient_history"]

class AutopsyRequest(BaseModel):
    repo_url: str = Field(..., min_length=3, max_length=200)

class RepoMeta(BaseModel):
    stars: int = 0
    primary_language: str | None = None
    created_at: str | None = None
    last_commit_at: str | None = None
    is_archived: bool = False
    readme_excerpt: str | None = None
    open_issues_count: int | None = None
    release_count: int | None = None
    last_release_at: str | None = None

class Features(BaseModel):
    days_since_last_commit: float
    commit_cadence_decay: float
    lifespan_days: float
    contributor_count: float
    bus_factor: float
    velocity_ratio: float
    # Tier B — richer, discriminative signals (all default 0.0 so direct
    # Features(...) construction and test fixtures never break).
    is_archived_flag: float = 0.0
    release_recency_days: float = 0.0
    has_releases: float = 0.0
    open_issue_ratio: float = 0.0

class Verdict(BaseModel):
    mode: DeathMode
    confidence: float
    probs: dict[str, float] = {}
    engine: Literal["tabpfn", "rules", "tabpfn+llm", "rules+llm"] = "tabpfn"

class AutopsyResult(BaseModel):
    owner: str
    repo: str
    meta: RepoMeta
    features: Features | None = None
    verdict: Verdict
    narration: str
    certificate_id: str
    death_note: str | None = None
    llm_hint: dict | None = None
    cohort: dict | None = None

FEATURE_ORDER = [
    "days_since_last_commit", "commit_cadence_decay", "lifespan_days",
    "contributor_count", "bus_factor", "velocity_ratio",
    # Tier B — same order as the appended CSV columns.
    "is_archived_flag", "release_recency_days", "has_releases", "open_issue_ratio",
]
