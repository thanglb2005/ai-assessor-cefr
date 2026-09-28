"""Typed M07 API boundary over M08 session resolution."""

from __future__ import annotations

from aicefr.auth.service import AuthService
from aicefr.contracts import ActorRole, ReviewCandidate
from aicefr.review.service import ReviewActionRequest, ReviewOutcome, ReviewService


class ReviewApi:
    def __init__(self, auth: AuthService, service: ReviewService) -> None:
        self._auth = auth
        self._service = service

    def get_queue(self, session_token: str) -> tuple[ReviewCandidate, ...]:
        actor = self._teacher(session_token)
        return self._service.queue(actor)

    def claim(
        self, session_token: str, response_id: str, expected_revision: int
    ) -> ReviewCandidate:
        actor = self._teacher(session_token)
        return self._service.claim(actor, response_id, expected_revision)

    def decide(
        self, session_token: str, response_id: str, request: ReviewActionRequest
    ) -> ReviewOutcome:
        actor = self._teacher(session_token)
        return self._service.decide(actor, response_id, request)

    def _teacher(self, session_token: str):
        return self._auth.resolve(
            session_token, allowed_roles=frozenset({ActorRole.TEACHER})
        )
