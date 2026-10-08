"""Bounded process counters without identities, paths or submitted content."""

from __future__ import annotations

from collections import Counter
from threading import Lock


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: Counter[tuple[str, int]] = Counter()

    def record(self, path: str, status: int) -> None:
        family = next(
            (
                name
                for name in ("student", "teacher", "admin")
                if path.startswith((f"/{name}", f"/api/{name}"))
            ),
            "other",
        )
        with self._lock:
            self._requests[family, status] += 1

    def render(self) -> str:
        with self._lock:
            rows = tuple(sorted(self._requests.items()))
        return "# TYPE aicefr_http_requests_total counter\n" + "".join(
            f'aicefr_http_requests_total{{family="{family}",status="{status}"}} {count}\n'
            for (family, status), count in rows
        )
