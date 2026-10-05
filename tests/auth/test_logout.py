from __future__ import annotations

import hashlib

import pytest

from aicefr.auth.memory import MemoryIdentityRepository
from aicefr.auth.service import AuthorizationError, AuthService
from aicefr.contracts import ActorRole
from aicefr.storage.sqlite import SQLiteStore


def _exercise_revocation(auth: AuthService) -> tuple[str, str]:
    auth.bootstrap_fixture_account("fixture-student", ActorRole.STUDENT, "fixture-password")
    revoked = auth.login("fixture-student", "fixture-password")
    retained = auth.login("fixture-student", "fixture-password")
    auth.logout(revoked)
    auth.logout(revoked)
    with pytest.raises(AuthorizationError):
        auth.resolve(revoked)
    assert auth.resolve(retained).actor_id == "fixture-student"
    return revoked, retained


def test_memory_logout_is_idempotent_and_scoped_to_one_session():
    repository = MemoryIdentityRepository()
    auth = AuthService(repository, repository)
    revoked, retained = _exercise_revocation(auth)
    digest = hashlib.sha256(revoked.encode("ascii")).hexdigest()
    assert digest not in repository.sessions
    assert hashlib.sha256(retained.encode("ascii")).hexdigest() in repository.sessions


def test_sqlite_store_logout_survives_restart_and_preserves_other_session(tmp_path):
    data_dir = tmp_path / "local-data"
    store = SQLiteStore(data_dir)
    auth = AuthService(store, store)
    revoked, retained = _exercise_revocation(auth)
    revoked_digest = hashlib.sha256(revoked.encode("ascii")).hexdigest()
    retained_digest = hashlib.sha256(retained.encode("ascii")).hexdigest()
    store.close()

    reopened = SQLiteStore(data_dir)
    restarted_auth = AuthService(reopened, reopened)
    assert reopened.get_session(revoked_digest) is None
    assert reopened.get_session(retained_digest) is not None
    with pytest.raises(AuthorizationError):
        restarted_auth.resolve(revoked)
    assert restarted_auth.resolve(retained).actor_id == "fixture-student"
    reopened.close()
