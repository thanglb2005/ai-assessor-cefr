"""Bounded process-local sliding windows for the local HTTP surface."""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict, deque
from threading import Lock


class RateLimiter:
    def __init__(self, *, clock=time.monotonic, capacity: int = 4096) -> None:
        self.clock, self.capacity = clock, capacity
        self._entries = OrderedDict()
        self._lock = Lock()

    def allow(self, operation: str, key: str, *, limit: int, seconds: int = 60) -> bool:
        digest = hashlib.sha256((operation + "\0" + key).encode()).hexdigest()
        with self._lock:
            now = self.clock()
            hits = self._entries.pop(digest, deque())
            while hits and hits[0] <= now - seconds:
                hits.popleft()
            allowed = len(hits) < limit
            if allowed:
                hits.append(now)
            self._entries[digest] = hits
            while len(self._entries) > self.capacity:
                self._entries.popitem(last=False)
            return allowed
