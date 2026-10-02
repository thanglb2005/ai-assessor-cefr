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
    return (
        """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Nộp bài nói</title></head>
<body><main><h1>Nộp bài nói</h1>"""
        + error_html
        + """
<p>Kết quả là ước lượng phục vụ học tập và có thể cần giảng viên duyệt.</p>
<p>Chỉ tiếp tục khi bạn đã đồng ý xử lý dữ liệu cho bài này.</p>
<p>Có thể rút lại đồng ý tại <a href="/student/consent">trang đồng ý</a>.</p>
<form method="post" action="/student/responses" enctype="multipart/form-data">
  <label for="task-id">Mã bài</label><input id="task-id" name="task_id" required>
  <label for="task-version">Phiên bản bài</label>
  <input id="task-version" name="task_version" required>
  <label for="consent-version">Phiên bản đồng ý</label>
  <input id="consent-version" name="consent_version" required>
  <label for="audio">Tệp âm thanh</label>
  <input id="audio" name="audio" type="file" accept="audio/*" required>
  <button type="submit">Nộp bài</button>
</form>"""
        + render_logout_form()
        + "</main></body></html>"
    )


def render_login(error: str | None = None) -> str:
    message = f'<p role="alert">{escape(error)}</p>' if error else ""
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Đăng nhập</title></head>
<body><main><h1>Đăng nhập</h1>{message}<form method="post" action="/login">
<label for="actor-id">Tài khoản</label>
<input id="actor-id" name="actor_id" required autocomplete="username">
<label for="password">Mật khẩu</label>
<input id="password" name="password" type="password" required autocomplete="current-password">
<button type="submit">Đăng nhập</button></form></main></body></html>"""


def render_consent(version: str, active: bool, demo: bool) -> str:
    state = "Bạn đã đồng ý phiên bản hiện tại." if active else "Bạn chưa đồng ý phiên bản hiện tại."
    warning = "<p><strong>Trình diễn local với dữ liệu giả.</strong></p>" if demo else ""
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Đồng ý xử lý dữ liệu</title></head>
<body><main><h1>Đồng ý xử lý dữ liệu</h1>{warning}<p>{state}</p>
<p>Phiên bản nội dung: {escape(version)}. Bạn có thể rút lại đồng ý bất cứ lúc nào.</p>
<form method="post" action="/student/consent/accept"><button type="submit">Đồng ý</button></form>
<form method="post" action="/student/consent/withdraw">
<button type="submit">Rút lại đồng ý</button></form>
<p><a href="/student/upload">Nộp bài</a></p>{render_logout_form()}</main></body></html>"""


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
{render_logout_form()}</main></body></html>"""


def render_notice(title: str, message: str) -> str:
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title></head>
<body><main><h1>{escape(title)}</h1><p role="alert">{escape(message)}</p>
<p><a href="/login">Đăng nhập</a></p></main></body></html>"""


def render_logout_form() -> str:
    return '<form method="post" action="/logout"><button type="submit">Đăng xuất</button></form>'


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
{render_logout_form()}</main></body></html>"""


def _coverage_row(criterion: str, coverage: float | None) -> str:
    value = coverage if coverage is not None else "—"
    return f"<li>{escape(criterion)}: {value}</li>"


def render_review_queue(candidates: tuple[ReviewCandidate, ...]) -> str:
    rows = "".join(_review_row(candidate) for candidate in candidates)
    if not rows:
        rows = "<li>Không có bài cần duyệt.</li>"
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Hàng đợi giảng viên</title></head><body><main>
<h1>Hàng đợi giảng viên</h1><ul>{rows}</ul>{render_logout_form()}</main></body></html>"""


def render_review_detail(candidate: ReviewCandidate, report: DiagnosticReport | None) -> str:
    if report is None:
        report_html = "<p>Báo cáo chưa sẵn sàng.</p>"
    else:
        report_html = render_report(report)
    action_form = ""
    if candidate.state.value in {"PENDING", "IN_REVIEW"}:
        path_id = quote(candidate.response_id, safe="")
        action_form = f"""<form method="post" action="/teacher/reviews/{path_id}/decision">
<input type="hidden" name="expected_revision" value="{candidate.revision}">
<label for="decision">Quyết định</label><select id="decision" name="action">
<option value="APPROVE">Duyệt</option><option value="OVERRIDE">Sửa band</option>
<option value="REJECT">Từ chối</option></select>
<label for="final-band">Band cuối khi override</label><select id="final-band" name="final_band">
<option value="">Không áp dụng</option><option value="A2">A2</option>
<option value="B1">B1</option><option value="B2">B2</option></select>
<label for="reason">Lý do</label><textarea id="reason" name="reason"></textarea>
<button type="submit">Lưu quyết định</button></form>"""
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Duyệt bài</title></head>
<body><main><h1>Duyệt bài</h1><p>Trạng thái: {escape(candidate.state.value)}</p>
<p>Revision: {candidate.revision}</p>{report_html}
<p><a href="/teacher/reviews/{quote(candidate.response_id, safe="")}/audio">Nghe audio</a></p>
{action_form}<p><a href="/teacher/reviews">Quay lại hàng đợi</a></p>
{render_logout_form()}</main></body></html>"""


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
    audio = f'<p><a href="/teacher/reviews/{path_id}/audio">Nghe audio</a></p>'
    detail = f'<p><a href="/teacher/reviews/{path_id}">Xem báo cáo và duyệt</a></p>'
    return f"""<li><p>{response_id} — {escape(candidate.state.value)}
(revision {revision})</p>{detail}{audio}{controls}</li>"""
