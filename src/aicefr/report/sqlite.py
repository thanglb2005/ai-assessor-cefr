"""Durable M06 reports stored in the shared M08 SQLite metadata database."""

from __future__ import annotations

from aicefr.report.contracts import DiagnosticReport
from aicefr.storage.sqlite import SQLiteStore


class SQLiteReportRepository:
    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def put(self, report: DiagnosticReport) -> None:
        payload = report.model_dump_json()
        connection = self._store.connection
        statement = """INSERT INTO diagnostic_reports(response_id, report_json) VALUES (?, ?)
            ON CONFLICT(response_id) DO UPDATE SET report_json=excluded.report_json"""
        if connection.in_transaction:
            connection.execute(statement, (report.response_id, payload))
        else:
            with self._store.transaction() as connection:
                connection.execute(statement, (report.response_id, payload))

    def get(self, response_id: str) -> DiagnosticReport | None:
        row = self._store.connection.execute(
            "SELECT report_json FROM diagnostic_reports WHERE response_id=?", (response_id,)
        ).fetchone()
        return DiagnosticReport.model_validate_json(row[0]) if row else None
