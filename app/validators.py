from __future__ import annotations
import re
from urllib.parse import urlparse

class BadRepoURL(ValueError):
    """Raised when the input is not a parseable public GitHub repo reference."""

_SLUG = re.compile(r"^[A-Za-z0-9_.-]+$")

def parse_repo_url(raw: str) -> tuple[str, str]:
    """Accept full URL, github.com/owner/repo, or bare owner/repo. Return (owner, repo).
    Rejects non-GitHub hosts, gists, and malformed input with BadRepoURL."""
    s = (raw or "").strip()
    if not s:
        raise BadRepoURL("empty")
    # strip scheme if present
    if s.startswith("http://") or s.startswith("https://"):
        u = urlparse(s)
        if u.netloc.lower() not in ("github.com", "www.github.com"):
            raise BadRepoURL("not a github.com URL")
        path = u.path
    elif s.startswith("github.com/") or s.startswith("www.github.com/"):
        path = "/" + s.split("/", 1)[1]
    else:
        path = "/" + s  # assume bare owner/repo
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        raise BadRepoURL("need owner/repo")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if owner.lower() == "gist" or not _SLUG.match(owner) or not _SLUG.match(repo):
        raise BadRepoURL("invalid owner/repo")
    return owner, repo
