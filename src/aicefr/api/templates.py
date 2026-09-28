"""Small accessible HTML renderers used by M01/M07 browser adapters.

They intentionally render only pseudonymous IDs and public report fields; raw
audio, blob paths and transcript content are never interpolated into a page.
"""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING
from urllib.parse import quote

from aicefr.api.student import StudentStatus

if TYPE_CHECKING:
    from aicefr.contracts import ReviewCandidate
    from aicefr.report.contracts import DiagnosticReport


def render_upload_form(error: str | None = None) -> str:
    error_html = ""
    if error:
        error_html = f'<p role="alert">{escape(error)}</p>'
    return """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Nộp bài nói</title></head>
<body><main><h1>Nộp bài nói</h1>""" + error_html + """
<p>Kết quả là ước lượng phục vụ học tập và có thể cần giảng viên duyệt.</p>
<form method="post" action="/api/student/responses" enctype="multipart/form-data">
  <label for="task-id">Mã bài</label><input id="task-id" name="task_id" required>
  <label for="task-version">Phiên bản bài</label>
  <input id="task-version" name="task_version" required>
  <label for="consent-version">Phiên bản đồng ý</label>
  <input id="consent-version" name="consent_version" required>
  <label for="audio">Tệp âm thanh</label>
  <input id="audio" name="audio" type="file" accept="audio/*" required>
  <button type="submit">Nộp bài</button>
</form></main></body></html>"""


def render_student_status(status: StudentStatus) -> str:
    reason = f"<p>{escape(status.reason)}</p>" if status.reason else ""
    report_link = (
        f'<a href="/student/responses/{escape(status.response_id)}/report">Xem báo cáo</a>'
        if status.report_available
        else "<p>Báo cáo chưa sẵn sàng.</p>"
    )
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Trạng thái bài nộp</title></head><body><main>
<h1>Trạng thái bài nộp</h1><dl><dt>Mã bài nộp</dt><dd>{escape(status.response_id)}</dd>
<dt>Trạng thái</dt><dd>{escape(status.status.value)}</dd></dl>{reason}{report_link}
</main></body></html>"""


def render_report(report: DiagnosticReport) -> str:
    overall = "Chưa đủ điều kiện ước lượng"
    if report.overall_score is not None and report.overall_band is not None:
        overall = f"{report.overall_score:.2f} ({report.overall_band.value})"
    coverage = "".join(_coverage_row(row.criterion.value, row.coverage) for row in report.criteria)
    verification = "Đã có giảng viên duyệt" if report.teacher_verified else "Kết quả tạm thời"
    overall_label = "Overall AI tạm thời" if report.teacher_verified else "Overall"
    teacher_result = ""
    if report.teacher_final is not None:
        final_band = report.teacher_final.overall_band
        final_value = final_band.value if final_band is not None else "Không có band cuối"
        reason = (
            f"<p>Lý do giảng viên: {escape(report.teacher_final.reason)}</p>"
            if report.teacher_final.reason
            else ""
        )
        teacher_result = f"<p>Kết quả giảng viên: {escape(final_value)}</p>{reason}"
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Báo cáo chẩn đoán</title></head><body><main>
<h1>Báo cáo chẩn đoán</h1><p>{verification}</p><p>{overall_label}: {escape(overall)}</p>
{teacher_result}
<p>Interaction: insufficient_evidence</p><h2>Coverage</h2><ul>{coverage}</ul>
</main></body></html>"""


def _coverage_row(criterion: str, coverage: float | None) -> str:
    value = coverage if coverage is not None else "—"
    return f"<li>{escape(criterion)}: {value}</li>"


def render_review_queue(candidates: tuple[ReviewCandidate, ...]) -> str:
    rows = "".join(_review_row(candidate) for candidate in candidates)
    if not rows:
        rows = "<li>Không có bài cần duyệt.</li>"
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Hàng đợi giảng viên</title></head><body><main>
<h1>Hàng đợi giảng viên</h1><ul>{rows}</ul></main></body></html>"""


def _review_row(candidate: ReviewCandidate) -> str:
    response_id = escape(candidate.response_id)
    path_id = quote(candidate.response_id, safe="")
    revision = str(candidate.revision)
    controls = ""
    if candidate.state.value == "PENDING":
        controls += f"""<form method="post" action="/teacher/reviews/{path_id}/claim">
<input type="hidden" name="expected_revision" value="{revision}">
<button type="submit">Nhận xử lý</button></form>"""
    if candidate.state.value in {"PENDING", "IN_REVIEW"}:
        controls += f"""<form method="post" action="/teacher/reviews/{path_id}/decision">
<input type="hidden" name="expected_revision" value="{revision}">
<label>Quyết định <select name="action"><option value="APPROVE">Duyệt</option>
<option value="OVERRIDE">Sửa band</option><option value="REJECT">Từ chối</option></select></label>
<label>Band cuối <select name="final_band"><option value="">Không áp dụng</option>
<option value="A2">A2</option><option value="B1">B1</option>
<option value="B2">B2</option></select></label>
<label>Lý do <textarea name="reason"></textarea></label>
<button type="submit">Lưu quyết định</button></form>"""
    return f"""<li><p>{response_id} — {escape(candidate.state.value)}
(revision {revision})</p>{controls}</li>"""
