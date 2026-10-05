"""Small semantic HTML renderers for the student and teacher browser flow."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING
from urllib.parse import quote

from aicefr.api.student import StudentStatus

if TYPE_CHECKING:
    from aicefr.contracts import ReviewCandidate
    from aicefr.report.contracts import DiagnosticReport


LOCAL_CSS = """\
:root { color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.5; }
* { box-sizing: border-box; }
body { margin: 0; padding: 1rem; color: #182230; background: #f6f8fb; }
main { width: 100%; max-width: 52rem; margin: 0 auto; padding: 1rem; background: #fff; }
h1, h2 { line-height: 1.2; }
p, dd, li { overflow-wrap: anywhere; }
label { display: block; margin: .8rem 0 .25rem; font-weight: 600; }
input:not([type=file]), select, textarea {
  display: block; width: 100%; max-width: 32rem;
  min-height: 2.75rem; padding: .55rem; font: inherit;
}
input[type=file] { display: block; max-width: 100%; padding: .4rem 0; }
textarea { min-height: 5rem; }
button {
  min-height: 2.75rem; margin: .45rem .35rem .45rem 0;
  padding: .55rem .9rem; font: inherit;
}
a { color: #0759a5; }
:focus-visible { outline: 3px solid #1264a3; outline-offset: 2px; }
form { margin: 1rem 0; }
"""


def _document(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="/local.css"></head>
<body><main><h1>{escape(title)}</h1>{body}</main></body></html>"""


def _demo_note(demo: bool) -> str:
    if not demo:
        return ""
    return (
        '<p class="demo-note"><strong>Trình diễn local:</strong> chỉ dùng tài khoản '
        "fixture và dữ liệu kiểm thử do nhóm tạo.</p>"
    )


def render_upload_form(error: str | None = None, *, demo: bool = False) -> str:
    message = f'<p role="alert">{escape(error)}</p>' if error else ""
    body = f"""{_demo_note(demo)}{message}
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
<button type="submit">Nộp bài</button></form>{render_logout_form()}"""
    return _document("Nộp bài nói", body)


def render_login(error: str | None = None, *, demo: bool = False) -> str:
    message = f'<p role="alert">{escape(error)}</p>' if error else ""
    body = f"""{_demo_note(demo)}{message}<form method="post" action="/login">
<label for="actor-id">Tài khoản</label>
<input id="actor-id" name="actor_id" required autocomplete="username">
<label for="password">Mật khẩu</label>
<input id="password" name="password" type="password" required autocomplete="current-password">
<button type="submit">Đăng nhập</button></form>"""
    return _document("Đăng nhập", body)


def render_consent(version: str, active: bool, demo: bool) -> str:
    state = "Bạn đã đồng ý phiên bản hiện tại." if active else "Bạn chưa đồng ý phiên bản hiện tại."
    body = f"""{_demo_note(demo)}<p>{state}</p>
<p>Phiên bản nội dung: {escape(version)}. Bạn có thể rút lại đồng ý bất cứ lúc nào.</p>
<form method="post" action="/student/consent/accept"><button type="submit">Đồng ý</button></form>
<form method="post" action="/student/consent/withdraw">
<button type="submit">Rút lại đồng ý</button></form>
<p><a href="/student/upload">Nộp bài</a></p>{render_logout_form()}"""
    return _document("Đồng ý xử lý dữ liệu", body)


def render_student_status(status: StudentStatus, *, demo: bool = False) -> str:
    reason = f"<p>{escape(status.reason)}</p>" if status.reason else ""
    report_link = (
        f'<a href="/student/responses/{escape(status.response_id)}/report">Xem báo cáo</a>'
        if status.report_available
        else "<p>Báo cáo chưa sẵn sàng.</p>"
    )
    body = f"""{_demo_note(demo)}<dl><dt>Mã bài nộp</dt>
<dd>{escape(status.response_id)}</dd><dt>Trạng thái</dt>
<dd>{escape(status.status.value)}</dd></dl>{reason}{report_link}{render_logout_form()}"""
    return _document("Trạng thái bài nộp", body)


def render_notice(title: str, message: str) -> str:
    body = f'<p role="alert">{escape(message)}</p><p><a href="/login">Đăng nhập</a></p>'
    return _document(title, body)


def render_logout_form() -> str:
    return '<form method="post" action="/logout"><button type="submit">Đăng xuất</button></form>'


def render_report_content(report: DiagnosticReport) -> str:
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
    return f"""<section aria-labelledby="report-heading">
<h2 id="report-heading">Báo cáo chẩn đoán</h2>
<p>{verification}</p><p>{overall_label}: {escape(overall)}</p>{teacher_result}
<p>Interaction: insufficient_evidence</p><h3>Coverage</h3><ul>{coverage}</ul></section>"""


def render_report(report: DiagnosticReport, *, demo: bool = False) -> str:
    body = _demo_note(demo) + render_report_content(report) + render_logout_form()
    return _document("Báo cáo chẩn đoán", body)


def _coverage_row(criterion: str, coverage: float | None) -> str:
    value = f"{coverage:.2f}" if coverage is not None else "—"
    return f"<li>{escape(criterion)}: {value}</li>"


def render_review_queue(candidates: tuple[ReviewCandidate, ...], *, demo: bool = False) -> str:
    rows = "".join(_review_row(candidate) for candidate in candidates)
    if not rows:
        rows = "<li>Không có bài cần duyệt.</li>"
    body = f"{_demo_note(demo)}<ul>{rows}</ul>{render_logout_form()}"
    return _document("Hàng đợi giảng viên", body)


def render_review_detail(
    candidate: ReviewCandidate, report: DiagnosticReport | None, *, demo: bool = False
) -> str:
    report_html = (
        render_report_content(report) if report is not None else "<p>Báo cáo chưa sẵn sàng.</p>"
    )
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
    path_id = quote(candidate.response_id, safe="")
    body = f"""{_demo_note(demo)}<p>Trạng thái: {escape(candidate.state.value)}</p>
<p>Revision: {candidate.revision}</p>{report_html}
<p><a href="/teacher/reviews/{path_id}/audio">Nghe audio</a></p>{action_form}
<p><a href="/teacher/reviews">Quay lại hàng đợi</a></p>{render_logout_form()}"""
    return _document("Duyệt bài", body)


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
<label for="decision-{path_id}">Quyết định</label>
<select id="decision-{path_id}" name="action"><option value="APPROVE">Duyệt</option>
<option value="OVERRIDE">Sửa band</option><option value="REJECT">Từ chối</option></select>
<label for="band-{path_id}">Band cuối khi override</label>
<select id="band-{path_id}" name="final_band"><option value="">Không áp dụng</option>
<option value="A2">A2</option><option value="B1">B1</option><option value="B2">B2</option></select>
<label for="reason-{path_id}">Lý do</label>
<textarea id="reason-{path_id}" name="reason"></textarea>
<button type="submit">Lưu quyết định</button></form>"""
    detail = f'<a href="/teacher/reviews/{path_id}">Xem báo cáo và duyệt</a>'
    audio = f'<a href="/teacher/reviews/{path_id}/audio">Nghe audio</a>'
    return f"""<li><p>{response_id} — {escape(candidate.state.value)} (revision {revision})</p>
<p>{detail} · {audio}</p>{controls}</li>"""
