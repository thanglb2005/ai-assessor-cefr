"""Durable M07 repository over the versioned M08 SQLite metadata store."""

from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Callable
from datetime import datetime

from aicefr.contracts import (
    Actor,
    ActorRole,
    AssessmentStatus,
    AuditEvent,
    Band,
    ReasonCode,
    ReviewCandidate,
    ReviewDecision,
    ReviewState,
)
from aicefr.review.service import (
    InvalidReviewTransition,
    ReviewActionRequest,
    ReviewNotFound,
    ReviewOutcome,
    StaleReview,
    claim_expired,
    decision_shape,
)
from aicefr.storage.sqlite import SQLiteStore


class SQLiteReviewRepository:
    """Persist queue state, decision and append-only audit in one transaction.

    The response revision captured by M02/M03/M05 is verified before every
    teacher mutation.  This rejects a decision made against an input that the
    pipeline has since replaced, in addition to the candidate revision used to
    prevent two teachers from silently overwriting one another.
    """

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def add(self, candidate: ReviewCandidate) -> ReviewCandidate:
        with self._store.transaction() as connection:
            self._require_response_revision(connection, candidate)
            try:
                connection.execute(
                    """INSERT INTO review_candidates (
                    response_id, response_revision, assessment_status, proposed_band,
                    reasons_json, source_versions_json, state, revision, created_at, updated_at,
                    claimed_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        candidate.response_id,
                        candidate.response_revision,
                        candidate.assessment_status,
                        candidate.proposed_band,
                        self._json(tuple(reason.value for reason in candidate.reasons)),
                        self._json(candidate.source_versions),
                        candidate.state,
                        candidate.revision,
                        candidate.created_at.isoformat(),
                        candidate.updated_at.isoformat(),
                        candidate.claimed_by,
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "review candidate already exists or response is unavailable"
                ) from error
        return candidate

    def get(self, response_id: str) -> ReviewCandidate | None:
        row = self._store.connection.execute(
            "SELECT * FROM review_candidates WHERE response_id=?", (response_id,)
        ).fetchone()
        return self._candidate_from_row(row) if row is not None else None

    def list_queue(self) -> tuple[ReviewCandidate, ...]:
        rows = self._store.connection.execute(
            """SELECT * FROM review_candidates
            WHERE state IN (?, ?) ORDER BY updated_at, response_id""",
            (ReviewState.PENDING, ReviewState.IN_REVIEW),
        ).fetchall()
        return tuple(self._candidate_from_row(row) for row in rows)

    def list_audit(self) -> tuple[AuditEvent, ...]:
        rows = self._store.connection.execute(
            """SELECT * FROM audit
            WHERE action IN (?, ?, ?, ?, ?) ORDER BY rowid""",
            (
                "review_claimed",
                "review_released",
                "review_approve",
                "review_override",
                "review_reject",
            ),
        ).fetchall()
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

    def verify_decision(self, decision: ReviewDecision) -> bool:
        """M06 uses this to reject a fabricated or uncommitted review result."""
        row = self._store.connection.execute(
            """SELECT d.decision_id, d.response_id, d.teacher_id, d.action, d.old_state,
            d.new_state, d.candidate_revision, d.proposed_band, d.final_band, d.reason,
            d.audit_id, d.recorded_at, a.actor_id, a.action, a.object_id
            FROM review_decisions AS d JOIN audit AS a ON a.event_id=d.audit_id
            WHERE d.decision_id=?""",
            (decision.decision_id,),
        ).fetchone()
        if row is None:
            return False
        return (
            row[1] == decision.response_id
            and row[2] == decision.teacher_id
            and row[3] == decision.action
            and row[4] == decision.old_state
            and row[5] == decision.new_state
            and row[6] == decision.candidate_revision
            and row[7] == decision.proposed_band
            and row[8] == decision.final_band
            and row[9] == decision.reason
            and row[10] == decision.audit_id
            and datetime.fromisoformat(row[11]) == decision.recorded_at
            and row[12] == decision.teacher_id
            and row[13] == f"review_{decision.action.value.lower()}"
            and row[14] == decision.response_id
        )

    def claim(
        self,
        *,
        actor: Actor,
        response_id: str,
        expected_revision: int,
        now: datetime,
    ) -> ReviewCandidate:
        with self._store.transaction() as connection:
            current = self._require_current(connection, response_id, expected_revision)
            self._require_response_revision(connection, current)
            if current.state is not ReviewState.PENDING and not claim_expired(current, now):
                raise InvalidReviewTransition("only PENDING candidates can be claimed")
            updated = current.model_copy(
                update={
                    "state": ReviewState.IN_REVIEW,
                    "claimed_by": actor.actor_id,
                    "revision": current.revision + 1,
                    "updated_at": now,
                }
            )
            self._update_candidate(connection, current, updated)
            self._store.record_audit(
                connection,
                AuditEvent(
                    event_id=uuid.uuid4().hex,
                    actor_id=actor.actor_id,
                    action="review_claimed",
                    object_id=response_id,
                    recorded_at=now,
                ),
            )
        return updated

    def release(
        self, *, actor: Actor, response_id: str, expected_revision: int, now: datetime
    ) -> ReviewCandidate:
        with self._store.transaction() as connection:
            current = self._require_current(connection, response_id, expected_revision)
            self._require_response_revision(connection, current)
            if current.state is not ReviewState.IN_REVIEW or (
                current.claimed_by != actor.actor_id
                and actor.role is not ActorRole.ADMIN
                and not claim_expired(current, now)
            ):
                raise InvalidReviewTransition("only the claimant or administrator can release")
            updated = current.model_copy(
                update={
                    "state": ReviewState.PENDING,
                    "claimed_by": None,
                    "revision": current.revision + 1,
                    "updated_at": now,
                }
            )
            self._update_candidate(connection, current, updated)
            self._store.record_audit(
                connection,
                AuditEvent(
                    event_id=uuid.uuid4().hex,
                    actor_id=actor.actor_id,
                    action="review_released",
                    object_id=response_id,
                    recorded_at=now,
                ),
            )
        return updated

    def decide(
        self,
        *,
        actor: Actor,
        response_id: str,
        request: ReviewActionRequest,
        now: datetime,
        on_decision: Callable[[ReviewDecision], object] | None = None,
    ) -> ReviewOutcome:
        with self._store.transaction() as connection:
            current = self._require_current(connection, response_id, request.expected_revision)
            self._require_response_revision(connection, current)
            if current.state not in {ReviewState.PENDING, ReviewState.IN_REVIEW}:
                raise InvalidReviewTransition("candidate is already final")
            if (
                current.claimed_by is not None
                and current.claimed_by != actor.actor_id
                and not claim_expired(current, now)
            ):
                raise InvalidReviewTransition("candidate is claimed by another reviewer")
            new_state, final_band = decision_shape(current, request)
            audit = AuditEvent(
                event_id=uuid.uuid4().hex,
                actor_id=actor.actor_id,
                action=f"review_{request.action.value.lower()}",
                object_id=response_id,
                recorded_at=now,
                reason=request.reason,
            )
            decision = ReviewDecision(
                decision_id=uuid.uuid4().hex,
                response_id=response_id,
                teacher_id=actor.actor_id,
                action=request.action,
                old_state=current.state,
                new_state=new_state,
                candidate_revision=current.revision,
                proposed_band=current.proposed_band,
                final_band=final_band,
                reason=request.reason,
                audit_id=audit.event_id,
                recorded_at=now,
            )
            updated = current.model_copy(
                update={"state": new_state, "revision": current.revision + 1, "updated_at": now}
            )
            self._update_candidate(connection, current, updated)
            self._store.record_audit(connection, audit)
            connection.execute(
                """INSERT INTO review_decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    decision.decision_id,
                    decision.response_id,
                    decision.teacher_id,
                    decision.action,
                    decision.old_state,
                    decision.new_state,
                    decision.candidate_revision,
                    decision.proposed_band,
                    decision.final_band,
                    decision.reason,
                    decision.audit_id,
                    decision.recorded_at.isoformat(),
                ),
            )
            # The verifier sees the append-only audit and decision on the same
            # connection.  A sink error aborts this metadata transaction.
            if on_decision is not None:
                on_decision(decision)
        return ReviewOutcome(candidate=updated, decision=decision, audit=audit)

    @staticmethod
    def _json(value: object) -> str:
        return json.dumps(value, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def _candidate_from_row(row: tuple[object, ...]) -> ReviewCandidate:
        reasons = tuple(ReasonCode(value) for value in json.loads(str(row[4])))
        source_versions = json.loads(str(row[5]))
        if not isinstance(source_versions, dict):
            raise ValueError("stored source_versions must be an object")
        return ReviewCandidate(
            response_id=str(row[0]),
            response_revision=int(row[1]),
            assessment_status=AssessmentStatus(str(row[2])),
            proposed_band=Band(str(row[3])) if row[3] is not None else None,
            reasons=reasons,
            source_versions={str(key): str(value) for key, value in source_versions.items()},
            state=ReviewState(str(row[6])),
            revision=int(row[7]),
            created_at=datetime.fromisoformat(str(row[8])),
            updated_at=datetime.fromisoformat(str(row[9])),
            claimed_by=str(row[10]) if row[10] is not None else None,
        )

    @staticmethod
    def _require_response_revision(
        connection: sqlite3.Connection, candidate: ReviewCandidate
    ) -> None:
        row = connection.execute(
            "SELECT revision FROM responses WHERE response_id=?", (candidate.response_id,)
        ).fetchone()
        if row is None:
            raise ReviewNotFound(candidate.response_id)
        if row[0] != candidate.response_revision:
            raise StaleReview("response revision changed after review candidate creation")

    def _require_current(
        self, connection: sqlite3.Connection, response_id: str, expected_revision: int
    ) -> ReviewCandidate:
        row = connection.execute(
            "SELECT * FROM review_candidates WHERE response_id=?", (response_id,)
        ).fetchone()
        if row is None:
            raise ReviewNotFound(response_id)
        current = self._candidate_from_row(row)
        if current.revision != expected_revision:
            raise StaleReview("candidate revision is stale")
        return current

    @staticmethod
    def _update_candidate(
        connection: sqlite3.Connection,
        current: ReviewCandidate,
        updated: ReviewCandidate,
    ) -> None:
        cursor = connection.execute(
            """UPDATE review_candidates SET state=?, revision=?, updated_at=?, claimed_by=?
            WHERE response_id=? AND revision=?""",
            (
                updated.state,
                updated.revision,
                updated.updated_at.isoformat(),
                updated.claimed_by,
                current.response_id,
                current.revision,
            ),
        )
        if cursor.rowcount != 1:
            raise StaleReview("candidate revision is stale")
