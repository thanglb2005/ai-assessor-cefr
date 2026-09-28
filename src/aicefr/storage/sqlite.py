"""Versioned SQLite repositories with explicit transactions for synthetic data."""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from aicefr.auth.service import AccountRecord
from aicefr.contracts import (
    Actor,
    ActorRole,
    AuditEvent,
    BlobRef,
    ConsentRecord,
    ConsentState,
    ResponseRecord,
    SessionRecord,
)
from aicefr.storage.paths import external_data_dir


class SQLiteStore:
    SCHEMA_VERSION = 1

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = external_data_dir(data_dir)
        self.connection = sqlite3.connect(self.data_dir / "metadata.sqlite3", isolation_level=None)
        self.connection.execute("PRAGMA foreign_keys=ON")
        try:
            self._migrate()
        except Exception:
            self.connection.close()
            raise

    def close(self) -> None:
        self.connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def _migrate(self) -> None:
        version = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if version != 0 and version != self.SCHEMA_VERSION:
            raise RuntimeError("unsupported SQLite schema version")
        if version == self.SCHEMA_VERSION:
            return
        try:
            self.connection.executescript(
                """
                BEGIN IMMEDIATE;
                CREATE TABLE accounts (
                    actor_id TEXT PRIMARY KEY, role TEXT NOT NULL, password_hash TEXT NOT NULL
                );
                CREATE TABLE sessions (
                    token_digest TEXT PRIMARY KEY,
                    actor_id TEXT NOT NULL REFERENCES accounts(actor_id),
                    role TEXT NOT NULL, created_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
                    idle_expires_at TEXT NOT NULL, absolute_expires_at TEXT NOT NULL
                );
                CREATE TABLE consents (
                    participant_id TEXT PRIMARY KEY REFERENCES accounts(actor_id),
                    consent_version TEXT NOT NULL, state TEXT NOT NULL, recorded_at TEXT NOT NULL
                );
                CREATE TABLE responses (
                    response_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL REFERENCES accounts(actor_id),
                    task_id TEXT NOT NULL, task_version TEXT NOT NULL,
                    blob_id TEXT UNIQUE NOT NULL, sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL,
                    status TEXT NOT NULL, revision INTEGER NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE audit (
                    event_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, action TEXT NOT NULL,
                    object_id TEXT NOT NULL, recorded_at TEXT NOT NULL, reason TEXT
                );
                CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit
                    BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
                CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit
                    BEGIN SELECT RAISE(ABORT, 'audit is append-only'); END;
                PRAGMA user_version=1;
                COMMIT;
                """
            )
        except Exception:
            self.connection.rollback()
            raise

    def _audit(self, connection: sqlite3.Connection, event: AuditEvent) -> None:
        connection.execute(
            "INSERT INTO audit VALUES (?, ?, ?, ?, ?, ?)",
            (
                event.event_id,
                event.actor_id,
                event.action,
                event.object_id,
                event.recorded_at.isoformat(),
                event.reason,
            ),
        )

    def get_account(self, actor_id: str) -> AccountRecord | None:
        row = self.connection.execute(
            "SELECT actor_id, role, password_hash FROM accounts WHERE actor_id=?", (actor_id,)
        ).fetchone()
        if row is None:
            return None
        return AccountRecord(Actor(actor_id=row[0], role=ActorRole(row[1])), row[2])

    def add_account(self, account: AccountRecord) -> None:
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO accounts VALUES (?, ?, ?)",
                (account.actor.actor_id, account.actor.role, account.password_hash),
            )

    def get_session(self, digest: str) -> SessionRecord | None:
        row = self.connection.execute(
            "SELECT * FROM sessions WHERE token_digest=?", (digest,)
        ).fetchone()
        if row is None:
            return None
        return SessionRecord(
            token_digest=row[0],
            actor_id=row[1],
            role=ActorRole(row[2]),
            created_at=datetime.fromisoformat(row[3]),
            last_seen_at=datetime.fromisoformat(row[4]),
            idle_expires_at=datetime.fromisoformat(row[5]),
            absolute_expires_at=datetime.fromisoformat(row[6]),
        )

    def put_session(self, session: SessionRecord) -> None:
        with self.transaction() as connection:
            connection.execute(
                """INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(token_digest) DO UPDATE SET
                last_seen_at=excluded.last_seen_at, idle_expires_at=excluded.idle_expires_at""",
                (
                    session.token_digest,
                    session.actor_id,
                    session.role,
                    session.created_at.isoformat(),
                    session.last_seen_at.isoformat(),
                    session.idle_expires_at.isoformat(),
                    session.absolute_expires_at.isoformat(),
                ),
            )

    def get_consent(self, participant_id: str) -> ConsentRecord | None:
        row = self.connection.execute(
            "SELECT * FROM consents WHERE participant_id=?", (participant_id,)
        ).fetchone()
        if row is None:
            return None
        return ConsentRecord(
            participant_id=row[0],
            consent_version=row[1],
            state=ConsentState(row[2]),
            recorded_at=datetime.fromisoformat(row[3]),
        )

    def put_consent(self, consent: ConsentRecord) -> None:
        event = AuditEvent(
            event_id=uuid.uuid4().hex,
            actor_id=consent.participant_id,
            action=f"consent_{consent.state}",
            object_id=consent.participant_id,
            recorded_at=consent.recorded_at,
        )
        with self.transaction() as connection:
            connection.execute(
                """INSERT INTO consents VALUES (?, ?, ?, ?)
                ON CONFLICT(participant_id) DO UPDATE SET
                consent_version=excluded.consent_version, state=excluded.state,
                recorded_at=excluded.recorded_at""",
                (
                    consent.participant_id,
                    consent.consent_version,
                    consent.state,
                    consent.recorded_at.isoformat(),
                ),
            )
            self._audit(connection, event)

    def get_response(self, response_id: str) -> ResponseRecord | None:
        row = self.connection.execute(
            "SELECT * FROM responses WHERE response_id=?", (response_id,)
        ).fetchone()
        if row is None:
            return None
        return ResponseRecord(
            response_id=row[0],
            owner_id=row[1],
            task_id=row[2],
            task_version=row[3],
            blob=BlobRef(blob_id=row[4], sha256=row[5], size_bytes=row[6]),
            status=row[7],
            revision=row[8],
            created_at=datetime.fromisoformat(row[9]),
        )

    def save_response(self, response: ResponseRecord, event: AuditEvent) -> None:
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    response.response_id,
                    response.owner_id,
                    response.task_id,
                    response.task_version,
                    response.blob.blob_id,
                    response.blob.sha256,
                    response.blob.size_bytes,
                    response.status,
                    response.revision,
                    response.created_at.isoformat(),
                ),
            )
            self._audit(connection, event)

    def list_audit(self) -> tuple[AuditEvent, ...]:
        rows = self.connection.execute("SELECT * FROM audit ORDER BY rowid").fetchall()
        return tuple(
            AuditEvent(
                event_id=row[0],
                actor_id=row[1],
                action=row[2],
                object_id=row[3],
                recorded_at=datetime.fromisoformat(row[4]),
                reason=row[5],
            )
            for row in rows
        )

    def referenced_blob_ids(self) -> set[str]:
        return {row[0] for row in self.connection.execute("SELECT blob_id FROM responses")}
