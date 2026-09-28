import hashlib
from datetime import UTC, datetime, timedelta

import pytest

from aicefr.auth.memory import MemoryIdentityRepository
from aicefr.auth.service import AuthorizationError, AuthService
from aicefr.contracts import ActorRole


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 28, tzinfo=UTC)

    def __call__(self):
        return self.now

    def advance(self, amount):
        self.now += amount


def test_fixture_account_password_role_and_digest():
    repo, clock = MemoryIdentityRepository(), Clock()
    service = AuthService(repo, repo, clock=clock)
    with pytest.raises(ValueError):
        service.bootstrap_fixture_account("real-person", ActorRole.ADMIN, "pw")
    with pytest.raises(ValueError):
        service.bootstrap_fixture_account("fixture-a", ActorRole.ADMIN, "")
    actor = service.bootstrap_fixture_account("fixture-a", ActorRole.STUDENT, "private-password")
    assert actor.role == ActorRole.STUDENT
    assert repo.accounts[actor.actor_id].password_hash.startswith("$argon2id$")
    with pytest.raises(ValueError):
        service.bootstrap_fixture_account("fixture-a", ActorRole.ADMIN, "other")
    with pytest.raises(AuthorizationError, match="invalid credentials"):
        service.login("missing", "private-password")
    with pytest.raises(AuthorizationError, match="invalid credentials"):
        service.login(actor.actor_id, "wrong")
    token = service.login(actor.actor_id, "private-password")
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    assert len(repo.sessions) == 1
    assert digest in repo.sessions
    assert token not in repr(repo.accounts[actor.actor_id])
    assert repo.sessions[digest].role == ActorRole.STUDENT
    assert service.resolve(token) == actor
    with pytest.raises(AuthorizationError, match="access denied"):
        service.resolve(token, allowed_roles=frozenset({ActorRole.ADMIN}))
    with pytest.raises(AuthorizationError, match="session unavailable"):
        service.resolve("wrong")


def test_idle_and_absolute_expiry_are_server_enforced():
    repo, clock = MemoryIdentityRepository(), Clock()
    service = AuthService(repo, repo, clock=clock)
    service.bootstrap_fixture_account("fixture-b", ActorRole.STUDENT, "pw")
    token = service.login("fixture-b", "pw")
    clock.advance(timedelta(minutes=29))
    assert service.resolve(token).actor_id == "fixture-b"
    clock.advance(timedelta(minutes=30))
    with pytest.raises(AuthorizationError):
        service.resolve(token)
    token = service.login("fixture-b", "pw")
    for _ in range(16):
        clock.advance(timedelta(minutes=29))
        assert service.resolve(token).actor_id == "fixture-b"
    clock.advance(timedelta(minutes=16))
    with pytest.raises(AuthorizationError):
        service.resolve(token)
