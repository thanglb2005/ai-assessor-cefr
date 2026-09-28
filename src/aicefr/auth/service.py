"""Authentication and consent services for explicit synthetic fixture accounts."""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

from aicefr.contracts import Actor, ActorRole, ConsentRecord, ConsentState, SessionRecord

IDLE_TTL = timedelta(minutes=30)
ABSOLUTE_TTL = timedelta(hours=8)


class AuthorizationError(Exception):
    """Controlled denial; no credential or existence details are exposed."""


class ResourceNotFound(AuthorizationError):
    """Same boundary error for absent and foreign-owned resources."""


@dataclass(frozen=True)
class AccountRecord:
    actor: Actor
    password_hash: str = field(repr=False)


class AccountRepository(Protocol):
    def get_account(self, actor_id: str) -> AccountRecord | None: ...
    def add_account(self, account: AccountRecord) -> None: ...


class SessionRepository(Protocol):
    def get_session(self, digest: str) -> SessionRecord | None: ...
    def put_session(self, session: SessionRecord) -> None: ...


class ConsentRepository(Protocol):
    def get_consent(self, participant_id: str) -> ConsentRecord | None: ...
    def put_consent(self, consent: ConsentRecord) -> None: ...


def utc_now() -> datetime:
    return datetime.now(UTC)


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def authorize_owner(actor: Actor, owner_id: str | None) -> None:
    """Fail identically for missing and foreign-owned records."""
    if owner_id is None or actor.actor_id != owner_id:
        raise ResourceNotFound("resource unavailable")


class AuthService:
    def __init__(
        self,
        accounts: AccountRepository,
        sessions: SessionRepository,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._accounts = accounts
        self._sessions = sessions
        self._clock = clock
        self._hasher = PasswordHasher(
            time_cost=2,
            memory_cost=19456,
            parallelism=1,
            hash_len=32,
            salt_len=16,
            type=Type.ID,
        )

    def bootstrap_fixture_account(self, actor_id: str, role: ActorRole, password: str) -> Actor:
        """Provision a synthetic account explicitly; no public signup or role claim."""
        if not actor_id.startswith("fixture-") or not password:
            raise ValueError("fixture account required")
        actor = Actor(actor_id=actor_id, role=role)
        self._accounts.add_account(AccountRecord(actor, self._hasher.hash(password)))
        return actor

    def login(self, actor_id: str, password: str) -> str:
        account = self._accounts.get_account(actor_id)
        if account is None:
            raise AuthorizationError("invalid credentials")
        try:
            valid = self._hasher.verify(account.password_hash, password)
        except (InvalidHashError, VerificationError):
            raise AuthorizationError("invalid credentials") from None
        if not valid:
            raise AuthorizationError("invalid credentials")
        now = self._clock()
        token = secrets.token_urlsafe(32)
        self._sessions.put_session(
            SessionRecord(
                token_digest=_digest(token),
                actor_id=account.actor.actor_id,
                role=account.actor.role,
                created_at=now,
                last_seen_at=now,
                idle_expires_at=now + IDLE_TTL,
                absolute_expires_at=now + ABSOLUTE_TTL,
            )
        )
        return token

    def resolve(self, token: str, *, allowed_roles: frozenset[ActorRole] | None = None) -> Actor:
        try:
            session = self._sessions.get_session(_digest(token))
        except UnicodeEncodeError:
            session = None
        now = self._clock()
        if session is None or now >= session.idle_expires_at or now >= session.absolute_expires_at:
            raise AuthorizationError("session unavailable")
        if allowed_roles is not None and session.role not in allowed_roles:
            raise AuthorizationError("access denied")
        actor = Actor(actor_id=session.actor_id, role=session.role)
        self._sessions.put_session(
            session.model_copy(
                update={
                    "last_seen_at": now,
                    "idle_expires_at": min(now + IDLE_TTL, session.absolute_expires_at),
                }
            )
        )
        return actor


class ConsentService:
    def __init__(
        self, consents: ConsentRepository, *, clock: Callable[[], datetime] = utc_now
    ) -> None:
        self._consents = consents
        self._clock = clock

    def activate(self, actor: Actor, consent_version: str) -> ConsentRecord:
        if actor.role != ActorRole.STUDENT:
            raise AuthorizationError("access denied")
        record = ConsentRecord(
            participant_id=actor.actor_id,
            consent_version=consent_version,
            state=ConsentState.ACTIVE,
            recorded_at=self._clock(),
        )
        self._consents.put_consent(record)
        return record

    def withdraw(self, actor: Actor) -> ConsentRecord:
        current = self._consents.get_consent(actor.actor_id)
        if actor.role != ActorRole.STUDENT or current is None:
            raise AuthorizationError("consent unavailable")
        record = current.model_copy(
            update={"state": ConsentState.WITHDRAWN, "recorded_at": self._clock()}
        )
        self._consents.put_consent(record)
        return record

    def require_active(self, actor: Actor, consent_version: str) -> ConsentRecord:
        current = self._consents.get_consent(actor.actor_id)
        if (
            actor.role != ActorRole.STUDENT
            or current is None
            or current.state != ConsentState.ACTIVE
            or current.consent_version != consent_version
        ):
            raise AuthorizationError("active consent required")
        return current
