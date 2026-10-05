from __future__ import annotations

from io import StringIO

from aicefr.auth.service import AuthService
from aicefr.contracts import ActorRole
from aicefr.local.__main__ import main
from aicefr.local.app import SQLiteSessionRepository
from aicefr.storage.sqlite import SQLiteStore


def test_init_demo_reads_password_from_stdin_and_persists_fixture(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "local-data"
    monkeypatch.setattr("sys.stdin", StringIO("fixture-secret\n"))
    exit_code = main(
        [
            "init-demo",
            "--data-dir",
            str(data_dir),
            "--actor-id",
            "fixture-student",
            "--role",
            "student",
            "--password-stdin",
        ]
    )
    assert exit_code == 0
    assert "fixture-secret" not in capsys.readouterr().out
    store = SQLiteStore(data_dir)
    auth = AuthService(store, SQLiteSessionRepository(store))
    token = auth.login("fixture-student", "fixture-secret")
    assert auth.resolve(token, allowed_roles=frozenset({ActorRole.STUDENT})).actor_id == (
        "fixture-student"
    )
    store.close()
