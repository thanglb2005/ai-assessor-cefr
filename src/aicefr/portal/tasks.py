"""Versioned speaking prompts and a durable submission gate."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from aicefr.api.student import SubmissionError
from aicefr.contracts import Actor, AuditEvent, ReasonCode
from aicefr.portal.contracts import TaskRecord
from aicefr.storage.sqlite import ConcurrentResponseUpdate, SQLiteStore


class TaskRepository:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    @staticmethod
    def _from_row(row: tuple) -> TaskRecord:
        return TaskRecord(
            task_id=row[0],
            task_version=row[1],
            title=row[2],
            prompt_text=row[3],
            min_seconds=row[4],
            max_seconds=row[5],
            active=bool(row[6]),
            revision=row[7],
        )

    def list(self, *, active_only: bool = False) -> tuple[TaskRecord, ...]:
        where = " WHERE active=1" if active_only else ""
        rows = self.store.connection.execute(
            "SELECT * FROM speaking_tasks" + where + " ORDER BY task_id, task_version"
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def get(self, task_id: str, task_version: str) -> TaskRecord | None:
        row = self.store.connection.execute(
            "SELECT * FROM speaking_tasks WHERE task_id=? AND task_version=?",
            (task_id, task_version),
        ).fetchone()
        return self._from_row(row) if row else None

    def seed(self, task: TaskRecord) -> None:
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO speaking_tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    task.task_id,
                    task.task_version,
                    task.title,
                    task.prompt_text,
                    task.min_seconds,
                    task.max_seconds,
                    int(task.active),
                    1,
                    datetime.now(UTC).isoformat(),
                ),
            )

    def save(self, actor: Actor, task: TaskRecord, expected_revision: int) -> TaskRecord:
        with self.store.transaction() as connection:
            current = self.get(task.task_id, task.task_version)
            if current is None:
                if expected_revision != 0:
                    raise ConcurrentResponseUpdate("task revision is stale")
                self.seed(task)
            else:
                if current.revision != expected_revision:
                    raise ConcurrentResponseUpdate("task revision is stale")
                used = connection.execute(
                    "SELECT 1 FROM responses WHERE task_id=? AND task_version=? LIMIT 1",
                    (task.task_id, task.task_version),
                ).fetchone()
                if used and (
                    current.title,
                    current.prompt_text,
                    current.min_seconds,
                    current.max_seconds,
                ) != (task.title, task.prompt_text, task.min_seconds, task.max_seconds):
                    raise ConcurrentResponseUpdate("create a new task version for revised wording")
                connection.execute(
                    "UPDATE speaking_tasks SET title=?, prompt_text=?, min_seconds=?, "
                    "max_seconds=?, active=?, revision=revision+1 "
                    "WHERE task_id=? AND task_version=? AND revision=?",
                    (
                        task.title,
                        task.prompt_text,
                        task.min_seconds,
                        task.max_seconds,
                        int(task.active),
                        task.task_id,
                        task.task_version,
                        expected_revision,
                    ),
                )
            self.store.record_audit(
                connection,
                AuditEvent(
                    event_id=uuid.uuid4().hex,
                    actor_id=actor.actor_id,
                    action="task_saved",
                    object_id=f"{task.task_id}:{task.task_version}",
                    recorded_at=datetime.now(UTC),
                ),
            )
            result = self.get(task.task_id, task.task_version)
            assert result is not None
            return result

    def require_open(self, task_id: str, task_version: str) -> None:
        task = self.get(task_id, task_version)
        if task is None or not task.active:
            raise SubmissionError(ReasonCode.TASK_NOT_OPEN, "Task is not open for submission")
