from __future__ import annotations
import os, re
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
    commits: list[dict] = field(default_factory=list)   # [{date, author, message}]
    contributors: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    readme: str | None = None

def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "User-Agent": "autopsy-of-a-dead-project"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def _last_page_from_link(link: str | None) -> int | None:
    # GitHub paginates; the Link header's rel="last" URL ends in &page=N, and with
    # per_page=1 that N is the total item count. No Link header on a single-item
    # (or empty) response -> caller decides 0-vs-1 from the body. Any parse miss -> None.
    if not link:
        return None
    for part in link.split(","):
        if 'rel="last"' in part:
            m = re.search(r"[?&]page=(\d+)", part)
            if m:
                return int(m.group(1))
    return None


async def _fetch_release_signals(client: httpx.AsyncClient, owner: str, repo: str) -> tuple[int | None, str | None]:
    # release_count (via Link rel="last" page count at per_page=1) + last_release_at.
    # Honesty invariant: ANY failure -> (None, None), never coerced to 0, never crash.
    try:
        r = await client.get(
            f"{API}/repos/{owner}/{repo}/releases", params={"per_page": 1})
        if r.status_code != 200:
            return None, None
        body = r.json() if isinstance(r.json(), list) else []
        last = _last_page_from_link(r.headers.get("Link"))
        count = last if last is not None else len(body)
        published = (body[0].get("published_at") if body else None) or None
        return count, (published[:10] if published else None)
    except Exception:
        return None, None


async def _fetch_closed_issue_count(client: httpx.AsyncClient, owner: str, repo: str) -> int | None:
    # Closed-issue total via Link rel="last" page count at per_page=1. GitHub's issues
    # endpoint includes PRs, but the open count in repo meta (open_issues_count) counts
    # the same way, so the ratio stays internally consistent. Failure -> None, never 0.
    try:
        r = await client.get(
            f"{API}/repos/{owner}/{repo}/issues",
            params={"state": "closed", "per_page": 1})
        if r.status_code != 200:
            return None
        last = _last_page_from_link(r.headers.get("Link"))
        if last is not None:
            return last
        body = r.json() if isinstance(r.json(), list) else []
        return len(body)
    except Exception:
        return None


async def _fetch_readme(client: httpx.AsyncClient, owner: str, repo: str) -> str | None:
    # README is adjudicator evidence (Tier A). Any failure -> None, never crash.
    try:
        r = await client.get(
            f"{API}/repos/{owner}/{repo}/readme",
            headers={"Accept": "application/vnd.github.raw"})
        if r.status_code != 200:
            return None
        text = (r.text or "").strip()
        return text[:2000] or None
    except Exception:
        return None


async def fetch_repo(owner: str, repo: str) -> RepoData:
    async with httpx.AsyncClient(timeout=10.0, headers=_headers(), follow_redirects=True) as client:
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
                commit = c.get("commit", {}) or {}
                commit_author = commit.get("author", {}) or {}
                author = (c.get("author") or {}).get("login") or commit_author.get("name") or "unknown"
                message = (commit.get("message") or "")[:200]
                commits.append({"date": commit_author.get("date"), "author": author, "message": message})
            if len(batch) < 100:
                break
            page += 1
        contributors = []
        cr = await client.get(f"{API}/repos/{owner}/{repo}/contributors", params={"per_page": 100})
        if cr.status_code == 200:
            contributors = cr.json() if isinstance(cr.json(), list) else []
        if len(commits) < 1:
            raise RepoError("empty", "no commit history")
        readme = await _fetch_readme(client, owner, repo)
        release_count, last_release_at = await _fetch_release_signals(client, owner, repo)
        closed_issues = await _fetch_closed_issue_count(client, owner, repo)
        return RepoData(owner=owner, repo=repo, commits=commits, contributors=contributors, readme=readme, meta={
            "stars": meta.get("stargazers_count", 0),
            "primary_language": meta.get("language"),
            "created_at": (meta.get("created_at") or "")[:10] or None,
            "is_archived": bool(meta.get("archived")),
            # open_issues_count from repo meta is authoritative (same PR-inclusive
            # counting as the closed-issue probe). Tier B signals; None on failure.
            "open_issues_count": meta.get("open_issues_count"),
            "closed_issues_count": closed_issues,
            "release_count": release_count,
            "last_release_at": last_release_at,
        })
