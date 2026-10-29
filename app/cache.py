from __future__ import annotations
import time
from collections import OrderedDict
from .schemas import AutopsyResult


class TTLCache:
    def __init__(self, capacity: int = 256, ttl: int = 3600):
        self.capacity, self.ttl = capacity, ttl
        self._d: "OrderedDict[str, tuple[float, AutopsyResult]]" = OrderedDict()

    def _key(self, owner: str, repo: str) -> str:
        return f"{owner.lower()}/{repo.lower()}"

    def get(self, owner: str, repo: str) -> AutopsyResult | None:
        k = self._key(owner, repo)
        item = self._d.get(k)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > self.ttl:
            self._d.pop(k, None)
            return None
        self._d.move_to_end(k)
        return val

    def set(self, owner: str, repo: str, val: AutopsyResult) -> None:
        k = self._key(owner, repo)
        self._d[k] = (time.time(), val)
        self._d.move_to_end(k)
        while len(self._d) > self.capacity:
            self._d.popitem(last=False)


cache = TTLCache()
