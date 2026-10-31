"""
TDD: Task 1 — Surface new raw fields in github.py meta.

Tests use httpx.MockTransport to intercept all HTTP calls inside fetch_repo
without requiring respx. fetch_repo builds its own AsyncClient internally, so
we monkeypatch app.github.httpx.AsyncClient with a wrapper that injects our
transport.
"""
import asyncio
import json
from functools import partial

import httpx
import pytest

import app.github as github_mod
from app.github import fetch_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_meta_fixture(**overrides) -> dict:
    """Minimal valid GitHub repo-meta JSON."""
    base = {
        "stargazers_count": 5,
        "language": "Python",
        "created_at": "2022-01-01T00:00:00Z",
        "archived": False,
        "open_issues_count": 3,
        # New fields under test:
        "forks_count": 12,
        "watchers_count": 30,
        "topics": ["cli", "tool"],
        "size": 400,
        "has_wiki": True,
        "has_pages": False,
        "fork": False,
        "license": {"spdx_id": "MIT"},
        "description": "a thing",
    }
    base.update(overrides)
    return base


def _handler(meta_json: dict, request: httpx.Request) -> httpx.Response:
    """Route mock requests to minimal valid responses."""
    path = request.url.path
    owner_repo = "/".join(path.strip("/").split("/")[1:3])  # repos/{owner}/{repo}

    if path.endswith(f"/{owner_repo}") and not any(
        path.endswith(x) for x in ["/commits", "/contributors", "/readme", "/releases", "/issues"]
    ):
        # GET /repos/{owner}/{repo}  — the meta endpoint
        return httpx.Response(200, json=meta_json)

    if "/commits" in path:
        return httpx.Response(200, json=[
            {"commit": {"author": {"date": "2023-01-01T00:00:00Z"}, "message": "init"},
             "author": {"login": "user"}}
        ])

    if "/contributors" in path:
        return httpx.Response(200, json=[])

    if "/readme" in path:
        return httpx.Response(404, json={"message": "Not Found"})

    if "/releases" in path:
        return httpx.Response(200, json=[])

    if "/issues" in path:
        return httpx.Response(200, json=[])

    return httpx.Response(404, json={"message": "Not Found"})


def _patched_async_client(meta_json: dict, *, timeout=None, headers=None, follow_redirects=False):
    """Replacement for httpx.AsyncClient that injects MockTransport."""
    handler = partial(_handler, meta_json)
    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        timeout=timeout,
        headers=headers,
        follow_redirects=follow_redirects,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fetch_repo_surfaces_new_meta_fields(monkeypatch):
    """All 9 new fields are exposed on RepoData.meta from the already-fetched meta JSON."""
    meta_json = _make_meta_fixture()
    monkeypatch.setattr(github_mod, "httpx", type("httpx", (), {
        **{k: getattr(httpx, k) for k in dir(httpx) if not k.startswith("_")},
        "AsyncClient": partial(_patched_async_client, meta_json),
    })())

    result = asyncio.run(fetch_repo("owner", "repo"))

    assert result.meta["forks_count"] == 12
    assert result.meta["watchers_count"] == 30
    assert result.meta["topics"] == ["cli", "tool"]
    assert result.meta["size"] == 400
    assert result.meta["has_wiki"] is True
    assert result.meta["has_pages"] is False
    assert result.meta["fork"] is False
    assert result.meta["license_present"] is True
    assert result.meta["description"] == "a thing"


def test_fetch_repo_missing_optional_meta_defaults_honestly(monkeypatch):
    """When topics/license/description are absent, honest empty defaults are returned."""
    # Omit topics, license, description entirely from the fixture
    meta_json = _make_meta_fixture()
    del meta_json["topics"]
    del meta_json["license"]
    del meta_json["description"]

    monkeypatch.setattr(github_mod, "httpx", type("httpx", (), {
        **{k: getattr(httpx, k) for k in dir(httpx) if not k.startswith("_")},
        "AsyncClient": partial(_patched_async_client, meta_json),
    })())

    result = asyncio.run(fetch_repo("owner", "repo"))

    assert result.meta["topics"] == []
    assert result.meta["license_present"] is False
    assert result.meta["description"] is None
