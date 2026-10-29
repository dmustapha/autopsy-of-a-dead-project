from __future__ import annotations
import os
from dataclasses import dataclass, field
import httpx

API = "https://api.github.com"
COMMIT_WINDOW = int(os.environ.get("COMMIT_WINDOW", "1000"))

class RepoError(Exception):
    def __init__(self, kind: str, message: str):
        self.kind = kind  # not_found | empty | rate_limited | error
        super().__init__(message)

@dataclass
class RepoData:
    owner: str
    repo: str
    commits: list[dict] = field(default_factory=list)   # [{date, author}]
    contributors: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "autopsy-of-a-dead-project"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

async def fetch_repo(owner: str, repo: str) -> RepoData:
    async with httpx.AsyncClient(timeout=10.0, headers=_headers()) as client:
        meta_r = await client.get(f"{API}/repos/{owner}/{repo}")
        if meta_r.status_code == 404:
            raise RepoError("not_found", "repository not found or private")
        if meta_r.status_code == 403 and "rate limit" in meta_r.text.lower():
            raise RepoError("rate_limited", "github rate limit")
        meta_r.raise_for_status()
        meta = meta_r.json()
        commits: list[dict] = []
        page = 1
        while len(commits) < COMMIT_WINDOW:
            cr = await client.get(
                f"{API}/repos/{owner}/{repo}/commits",
                params={"per_page": 100, "page": page})
            if cr.status_code == 409:   # empty repo
                break
            cr.raise_for_status()
            batch = cr.json()
            if not batch:
                break
            for c in batch:
                commit = c.get("commit", {}).get("author", {}) or {}
                author = (c.get("author") or {}).get("login") or commit.get("name") or "unknown"
                commits.append({"date": commit.get("date"), "author": author})
            if len(batch) < 100:
                break
            page += 1
        contributors = []
        cr = await client.get(f"{API}/repos/{owner}/{repo}/contributors", params={"per_page": 100})
        if cr.status_code == 200:
            contributors = cr.json() if isinstance(cr.json(), list) else []
        if len(commits) < 1:
            raise RepoError("empty", "no commit history")
        return RepoData(owner=owner, repo=repo, commits=commits, contributors=contributors, meta={
            "stars": meta.get("stargazers_count", 0),
            "primary_language": meta.get("language"),
            "created_at": (meta.get("created_at") or "")[:10] or None,
            "is_archived": bool(meta.get("archived")),
        })
