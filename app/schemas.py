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

class Features(BaseModel):
    days_since_last_commit: float
    commit_cadence_decay: float
    lifespan_days: float
    contributor_count: float
    bus_factor: float
    velocity_ratio: float

class Verdict(BaseModel):
    mode: DeathMode
    confidence: float
    probs: dict[str, float] = {}
    engine: Literal["tabpfn", "rules"] = "tabpfn"

class AutopsyResult(BaseModel):
    owner: str
    repo: str
    meta: RepoMeta
    features: Features | None = None
    verdict: Verdict
    narration: str
    certificate_id: str

FEATURE_ORDER = [
    "days_since_last_commit", "commit_cadence_decay", "lifespan_days",
    "contributor_count", "bus_factor", "velocity_ratio",
]
