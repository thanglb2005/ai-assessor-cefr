"""Role-gated, optimistic-lock teacher review service for M07."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from aicefr.auth.service import AuthorizationError
from aicefr.contracts import (
    Actor,
    ActorRole,
    AuditEvent,
    Band,
    ReviewAction,
    ReviewCandidate,
    ReviewDecision,
    ReviewState,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReviewActionRequest(_Frozen):
    action: ReviewAction
    expected_revision: int = Field(ge=1)
    final_band: Band | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def _request_shape_is_safe(self) -> ReviewActionRequest:
        if self.action is ReviewAction.APPROVE and self.final_band is not None:
            raise ValueError("APPROVE uses the proposed band and must not carry final_band")
        if self.action is ReviewAction.OVERRIDE and (self.final_band is None or not self.reason):
            raise ValueError("OVERRIDE needs final_band and reason")
        if self.action is ReviewAction.REJECT and self.final_band is not None:
            raise ValueError("REJECT must not carry a final_band")
        return self


class ReviewNotFound(LookupError):
    pass


class StaleReview(RuntimeError):
    pass


class InvalidReviewTransition(RuntimeError):
    pass


@dataclass(frozen=True)
class ReviewOutcome:
    candidate: ReviewCandidate
    decision: ReviewDecision
    audit: AuditEvent


class ReviewUpdateSink(Protocol):
    def apply_review(self, decision: ReviewDecision) -> object: ...


class ReviewRepository(Protocol):
    """Storage boundary for review state, decisions and their audit events."""

    def add(self, candidate: ReviewCandidate) -> ReviewCandidate: ...

    def get(self, response_id: str) -> ReviewCandidate | None: ...

    def list_queue(self) -> tuple[ReviewCandidate, ...]: ...

    def list_audit(self) -> tuple[AuditEvent, ...]: ...

    def claim(
        self,
        *,
        actor: Actor,
        response_id: str,
        expected_revision: int,
        now: datetime,
    ) -> ReviewCandidate: ...

    def decide(
        self,
        *,
        actor: Actor,
        response_id: str,
        request: ReviewActionRequest,
        now: datetime,
        on_decision: Callable[[ReviewDecision], object] | None = None,
    ) -> ReviewOutcome: ...


def decision_shape(
    candidate: ReviewCandidate, request: ReviewActionRequest
) -> tuple[ReviewState, Band | None]:
    """Resolve only legal final state/band combinations for one candidate."""
    if request.action is ReviewAction.APPROVE:
        if candidate.proposed_band is None:
            raise InvalidReviewTransition("cannot approve a candidate without a proposed band")
        return ReviewState.APPROVED, candidate.proposed_band
    if request.action is ReviewAction.OVERRIDE:
        assert request.final_band is not None
        return ReviewState.OVERRIDDEN, request.final_band
    return ReviewState.REJECTED, None


class MemoryReviewRepository:
    """Atomic local review/audit store for fixture-backed W3 integration.

    The lock makes same-process concurrent updates deterministic. A later M08
    persistence adapter can implement the same public operations without
    changing API or report code.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._candidates: dict[str, ReviewCandidate] = {}
        self._decisions: dict[str, ReviewDecision] = {}
        self._audit: list[AuditEvent] = []

    def add(self, candidate: ReviewCandidate) -> ReviewCandidate:
        with self._lock:
            if candidate.response_id in self._candidates:
                raise ValueError("review candidate already exists")
            self._candidates[candidate.response_id] = candidate
            return candidate

    def get(self, response_id: str) -> ReviewCandidate | None:
        with self._lock:
            return self._candidates.get(response_id)

    def list_queue(self) -> tuple[ReviewCandidate, ...]:
        with self._lock:
            return tuple(
                candidate
                for candidate in self._candidates.values()
                if candidate.state in {ReviewState.PENDING, ReviewState.IN_REVIEW}
            )

    def list_audit(self) -> tuple[AuditEvent, ...]:
        with self._lock:
            return tuple(self._audit)

    def verify_decision(self, decision: ReviewDecision) -> bool:
        """Allow M06 to accept only a decision recorded by this repository."""
        with self._lock:
            audit = next(
                (event for event in self._audit if event.event_id == decision.audit_id),
                None,
            )
            return (
                self._decisions.get(decision.decision_id) == decision
                and audit is not None
                and audit.actor_id == decision.teacher_id
                and audit.object_id == decision.response_id
            )

    def claim(
        self,
        *,
        actor: Actor,
        response_id: str,
        expected_revision: int,
        now: datetime,
    ) -> ReviewCandidate:
        with self._lock:
            current = self._require_current(response_id, expected_revision)
            if current.state is not ReviewState.PENDING:
                raise InvalidReviewTransition("only PENDING candidates can be claimed")
            updated = current.model_copy(
                update={
                    "state": ReviewState.IN_REVIEW,
                    "revision": current.revision + 1,
                    "updated_at": now,
                }
            )
            event = AuditEvent(
                event_id=uuid.uuid4().hex,
                actor_id=actor.actor_id,
                action="review_claimed",
                object_id=response_id,
                recorded_at=now,
            )
            self._candidates[response_id] = updated
            self._audit.append(event)
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
        with self._lock:
            current = self._require_current(response_id, request.expected_revision)
            if current.state not in {ReviewState.PENDING, ReviewState.IN_REVIEW}:
                raise InvalidReviewTransition("candidate is already final")
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
            self._candidates[response_id] = updated
            self._decisions[decision.decision_id] = decision
            self._audit.append(audit)
            try:
                if on_decision is not None:
                    on_decision(decision)
            except Exception:
                # Keep the M06 callback and review outcome atomic in the
                # fixture adapter as well as in the SQLite implementation.
                self._candidates[response_id] = current
                del self._decisions[decision.decision_id]
                self._audit.pop()
                raise
            return ReviewOutcome(candidate=updated, decision=decision, audit=audit)

    def _require_current(self, response_id: str, expected_revision: int) -> ReviewCandidate:
        current = self._candidates.get(response_id)
        if current is None:
            raise ReviewNotFound(response_id)
        if current.revision != expected_revision:
            raise StaleReview("candidate revision is stale")
        return current

class ReviewService:
    """M07 use cases. Only M08-authenticated teachers can mutate review state."""

    def __init__(
        self,
        repository: ReviewRepository,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        report_sink: ReviewUpdateSink | None = None,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._report_sink = report_sink

    def add_candidate(self, candidate: ReviewCandidate) -> ReviewCandidate:
        return self._repository.add(candidate)

    def queue(self, actor: Actor) -> tuple[ReviewCandidate, ...]:
        self._require_teacher(actor)
        return self._repository.list_queue()

    def claim(self, actor: Actor, response_id: str, expected_revision: int) -> ReviewCandidate:
        self._require_teacher(actor)
        return self._repository.claim(
            actor=actor,
            response_id=response_id,
            expected_revision=expected_revision,
            now=self._clock(),
        )

    def decide(self, actor: Actor, response_id: str, request: ReviewActionRequest) -> ReviewOutcome:
        self._require_teacher(actor)
        callback = self._report_sink.apply_review if self._report_sink is not None else None
        return self._repository.decide(
            actor=actor,
            response_id=response_id,
            request=request,
            now=self._clock(),
            on_decision=callback,
        )

    @staticmethod
    def _require_teacher(actor: Actor) -> None:
        if actor.role is not ActorRole.TEACHER:
            raise AuthorizationError("access denied")
