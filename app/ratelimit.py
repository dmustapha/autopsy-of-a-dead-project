from __future__ import annotations
import time
from collections import defaultdict
from fastapi import Request, HTTPException

_HITS: dict[str, list[float]] = defaultdict(list)
_WINDOW = 60.0      # seconds
_MAX = 10           # requests / IP / window


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    hits = [t for t in _HITS[ip] if now - t < _WINDOW]
    if len(hits) >= _MAX:
        raise HTTPException(status_code=429, detail="The crypt is busy — too many autopsies. Try again in a minute.")
    hits.append(now)
    _HITS[ip] = hits
