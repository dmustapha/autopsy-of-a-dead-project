import pytest
from app.validators import parse_repo_url, BadRepoURL

@pytest.mark.parametrize("raw", [
    "https://github.com/owner/repo", "github.com/owner/repo", "owner/repo",
    "https://github.com/owner/repo/", "owner/repo.git",
])
def test_valid(raw):
    assert parse_repo_url(raw) == ("owner", "repo")

@pytest.mark.parametrize("raw", ["", "owner", "https://gitlab.com/o/r", "https://gist.github.com/x/y", "!!!"])
def test_invalid(raw):
    with pytest.raises(BadRepoURL):
        parse_repo_url(raw)
