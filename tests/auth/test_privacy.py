from datetime import UTC, datetime

from aicefr.auth.memory import MemoryIdentityRepository
from aicefr.auth.service import AuthService
from aicefr.contracts import ActorRole


def test_auth_flow_does_not_log_secret_or_token(caplog):
    repository = MemoryIdentityRepository()
    service = AuthService(
        repository,
        repository,
        clock=lambda: datetime(2026, 9, 28, tzinfo=UTC),
    )
    service.bootstrap_fixture_account("fixture-private", ActorRole.STUDENT, "hidden-password")
    token = service.login("fixture-private", "hidden-password")
    service.resolve(token)
    assert "hidden-password" not in caplog.text
    assert token not in caplog.text
    assert repository.accounts["fixture-private"].password_hash not in caplog.text
