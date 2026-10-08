"""One local worker with a separate SQLite connection and durable pending jobs."""

from __future__ import annotations

import logging
from threading import Event, Thread

from aicefr.contracts import ResponseStatus

log = logging.getLogger(__name__)


class BackgroundPipeline:
    def __init__(self, store, factory, *, capacity: int = 8) -> None:
        if not 1 <= capacity <= 100:
            raise ValueError("worker capacity must be between 1 and 100")
        self.store, self.factory, self.capacity = store, factory, capacity
        self._wake, self._stop = Event(), Event()
        self._thread = Thread(target=self._run, name="aicefr-local-worker", daemon=True)
        self._thread.start()

    def enqueue(self, response) -> None:
        count = self.store.connection.execute(
            "SELECT COUNT(*) FROM responses WHERE status IN (?,?)",
            (ResponseStatus.QUEUED, ResponseStatus.RUNNING),
        ).fetchone()[0]
        if count > self.capacity:
            raise ValueError("pipeline queue is full")
        self._wake.set()

    def _run(self) -> None:
        runtime = None
        try:
            runtime = self.factory()
            while not self._stop.is_set():
                row = runtime.store.connection.execute(
                    "SELECT * FROM responses WHERE status=? ORDER BY created_at LIMIT 1",
                    (ResponseStatus.QUEUED,),
                ).fetchone()
                if row is None:
                    self._wake.wait(1)
                    self._wake.clear()
                    continue
                runtime.control.reload()
                runtime.control.pipeline.enqueue(runtime.store._response_from_row(row))
        except Exception:
            log.error("local worker stopped; operator inspection required")
        finally:
            if runtime is not None:
                runtime.close()

    def close(self) -> None:
        self._stop.set()
        self._wake.set()
        self._thread.join(timeout=30)
