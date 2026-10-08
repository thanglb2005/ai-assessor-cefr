"""PARITY-001 native portal journeys on an isolated fixture database."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
from w3_app_browser import (
    ROOT,
    _assert_document_and_width,
    _attach_observers,
    _init_account,
    _login,
    _reserve_port,
    _wait_ready,
    _write_audio,
)


def run(config_path: Path, evidence: Path) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    metrics = {
        "console_errors": [],
        "failed_requests": [],
        "external_requests": [],
        "http_statuses": [],
    }
    checks = []
    with tempfile.TemporaryDirectory(prefix="aicefr-parity-browser-") as directory:
        root = Path(directory)
        config = json.loads(config_path.read_text())
        config.update(async_pipeline=True, long_response_windows=True)
        config["qc"]["accepted_formats"] = list(
            dict.fromkeys(config["qc"]["accepted_formats"] + ["webm", "mp4"])
        )
        config["allowed_media_types"] = list(
            dict.fromkeys(config["allowed_media_types"] + ["audio/webm", "audio/mp4"])
        )
        config["tasks"] = [
            {
                "task_id": "fixture-speaking",
                "task_version": "1",
                "title": "Fixture speaking",
                "prompt_text": "Talk about your learning routine.",
                "min_seconds": 1,
                "max_seconds": 180,
            }
        ]
        local_config = root / "config.json"
        local_config.write_text(json.dumps(config))
        audio = root / "fixture.wav"
        _write_audio(audio)
        env = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OMP_NUM_THREADS="1")
        passwords = {role: secrets.token_urlsafe(24) for role in ("student", "teacher", "admin")}
        for role, password in passwords.items():
            _init_account(root / "data", "fixture-" + role, role, password, env)
        port = _reserve_port()
        base = f"http://127.0.0.1:{port}"
        with (evidence / "server.log").open("w") as output:
            server = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    "-m",
                    "aicefr.local",
                    "serve",
                    "--data-dir",
                    str(root / "data"),
                    "--config",
                    str(local_config),
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            try:
                _wait_ready(server, base)
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--use-fake-ui-for-media-stream",
                            "--use-fake-device-for-media-stream",
                            f"--use-file-for-fake-audio-capture={audio}",
                        ],
                    )
                    contexts = {}
                    for role in passwords:
                        context = browser.new_context(viewport={"width": 1280, "height": 800})
                        _attach_observers(context, metrics)
                        page = context.new_page()
                        _login(page, base, "fixture-" + role, passwords[role])
                        contexts[role] = (context, page)
                    student, page = contexts["student"]
                    page.locator("input[name=research_allowed]").check()
                    page.get_by_role("button", name="Đồng ý", exact=True).click()
                    page.goto(base + "/student/tasks")
                    page.get_by_role("link", name="Làm bài", exact=True).click()
                    assert (
                        page.get_by_label("Mã bài", exact=True).input_value() == "fixture-speaking"
                    )
                    page.get_by_label("Tệp âm thanh").set_input_files(str(audio))
                    page.get_by_role("button", name="Nộp bài", exact=True).click()
                    page.wait_for_url("**/student/responses/*")
                    rid = page.url.rstrip("/").split("/")[-1]
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        status = student.request.get(
                            base + f"/api/student/responses/{rid}/status"
                        ).json()
                        if status["status"] not in {"QUEUED", "RUNNING"}:
                            break
                        time.sleep(0.1)
                    assert status["status"] == "REVIEW_REQUIRED", status
                    checks.append("async-submit-qc-review")
                    teacher, teacher_page = contexts["teacher"]
                    teacher_page.goto(base + f"/teacher/reviews/{rid}")
                    teacher_page.get_by_role("button", name="Nhận xử lý", exact=True).click()
                    teacher_page.goto(base + f"/teacher/reviews/{rid}")
                    assert "fixture-teacher" in teacher_page.inner_text("main")
                    teacher_page.get_by_role("button", name="Trả lại hàng đợi", exact=True).click()
                    teacher_page.goto(base + f"/teacher/reviews/{rid}")
                    teacher_page.get_by_label("Quyết định", exact=True).select_option("OVERRIDE")
                    teacher_page.get_by_label("Band cuối khi override", exact=True).select_option(
                        "B1"
                    )
                    teacher_page.get_by_label("Lý do", exact=True).fill("Fixture parity review")
                    teacher_page.get_by_role("button", name="Lưu quyết định", exact=True).click()
                    checks.append("claim-release-override")
                    teacher_page.goto(base + f"/teacher/reviews/{rid}")
                    teacher_page.get_by_label("Lý do mở lại", exact=True).fill(
                        "Fixture correction round"
                    )
                    teacher_page.get_by_role(
                        "button", name="Mở lại để hiệu chỉnh", exact=True
                    ).click()
                    teacher_page.get_by_label("Quyết định", exact=True).select_option("OVERRIDE")
                    teacher_page.get_by_label("Band cuối khi override", exact=True).select_option(
                        "B2"
                    )
                    teacher_page.get_by_label("Lý do", exact=True).fill("Fixture second decision")
                    teacher_page.get_by_role("button", name="Lưu quyết định", exact=True).click()
                    history = teacher.request.get(
                        base + f"/api/teacher/responses/{rid}/history"
                    ).json()
                    changes = [item for item in history if item["after_state"] is not None]
                    assert [(item["before_band"], item["after_band"]) for item in changes] == [
                        (None, "B1"),
                        ("B1", "B2"),
                    ]
                    checks.append("reopen-correction-history-before-after")
                    admin, admin_page = contexts["admin"]
                    admin_page.goto(base + "/admin/accounts")
                    create = admin_page.locator("form").filter(
                        has=admin_page.locator("input[name=password]")
                    )
                    create.get_by_label("ID fixture-...").fill("fixture-browser-created")
                    create.get_by_label("Mật khẩu (tối thiểu 8 ký tự)").fill(
                        secrets.token_urlsafe(16)
                    )
                    create.get_by_role("button", name="Tạo tài khoản", exact=True).click()
                    assert "fixture-browser-created" in admin_page.inner_text("main")
                    checks.append("admin-create-account")
                    admin_page.goto(base + "/admin/tasks")
                    task_form = admin_page.locator('form[action="/admin/tasks"]').last
                    task_form.get_by_label("Mã đề", exact=True).fill("fixture-new-task")
                    task_form.get_by_label("Tên đề", exact=True).fill("Fixture new prompt")
                    task_form.get_by_label("Nội dung đề", exact=True).fill("Describe a study goal.")
                    task_form.get_by_role("button", name="Lưu đề", exact=True).click()
                    assert (
                        admin_page.locator(
                            'input[name="task_id"][value="fixture-new-task"]'
                        ).count()
                        == 1
                    )
                    checks.append("admin-create-task")
                    admin_page.goto(base + "/admin/config")
                    admin_page.get_by_label("max_duration_s", exact=True).fill("250")
                    admin_page.get_by_role("button", name="Lưu cấu hình", exact=True).click()
                    assert (
                        admin_page.get_by_label("max_duration_s", exact=True).input_value()
                        == "250.0"
                    )
                    checks.append("admin-qc-update")
                    research = admin.request.get(base + "/admin/research.json").json()
                    assert research["row_count"] == 1
                    assert research["rows"][0]["teacher_final_band"] == "B2"
                    assert "fixture-student" not in json.dumps(research)
                    assert (
                        student.request.get(base + "/student/export.json").json()["row_count"] == 1
                    )
                    checks.append("exports-opt-in-final-band")
                    page.goto(base + "/student/upload?task_id=fixture-speaking&task_version=1")
                    page.get_by_role("button", name="Bắt đầu ghi âm", exact=True).click()
                    page.wait_for_timeout(1800)
                    page.get_by_role("button", name="Dừng ghi âm", exact=True).click()
                    page.locator("#record-preview").wait_for(state="visible")
                    page.get_by_role("button", name="Nộp bài", exact=True).click()
                    page.wait_for_url("**/student/responses/*")
                    recorded_id = page.url.rstrip("/").split("/")[-1]
                    deadline = time.monotonic() + 40
                    while time.monotonic() < deadline:
                        state = student.request.get(
                            base + f"/api/student/responses/{recorded_id}/status"
                        ).json()
                        if state["status"] not in {"QUEUED", "RUNNING"}:
                            break
                        time.sleep(0.2)
                    assert state["status"] in {"REVIEW_REQUIRED", "COMPLETED", "REJECTED"}, state
                    encoded = student.request.get(base + f"/student/responses/{recorded_id}/audio")
                    assert encoded.status == 200
                    assert encoded.headers["content-type"] == "audio/webm"
                    checks.append("browser-microphone-webm-submit-original-playback")
                    routes = {
                        "student": [
                            "/student/tasks",
                            "/student/responses",
                            "/student/progress",
                            f"/student/responses/{rid}/report",
                        ],
                        "teacher": [
                            "/teacher/reviews",
                            "/teacher/responses",
                            "/teacher/stats",
                            f"/teacher/responses/{rid}/report",
                            f"/teacher/responses/{rid}/history",
                        ],
                        "admin": [
                            "/admin",
                            "/admin/accounts",
                            "/admin/tasks",
                            "/admin/config",
                            "/admin/models",
                            "/admin/audit",
                            "/admin/erase",
                            "/admin/maintenance",
                            "/admin/health",
                        ],
                    }
                    for width in (1280, 390):
                        for role, paths in routes.items():
                            context, view = contexts[role]
                            view.set_viewport_size({"width": width, "height": 844})
                            for index, path in enumerate(paths):
                                response = view.goto(base + path, wait_until="networkidle")
                                assert response.status == 200, (path, response.status)
                                _assert_document_and_width(view, width)
                                view.screenshot(
                                    path=str(evidence / f"{role}-{width}-{index}.png"),
                                    full_page=True,
                                )
                                checks.append(f"{role}:{width}:{path}")
                    ready = admin.request.get(base + "/readyz")
                    assert ready.status == 200 and ready.json()["ready"], ready.text()
                    checks.append("real-model-readiness")
                    for context, _ in contexts.values():
                        context.close()
                    browser.close()
            finally:
                server.send_signal(signal.SIGINT)
                server.wait(timeout=40)
    result = {"result": "PASS", "check_count": len(checks), "checks": checks, **metrics}
    assert (
        not metrics["console_errors"]
        and not metrics["failed_requests"]
        and not metrics["external_requests"]
    )
    (evidence / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.config, args.evidence_dir)
    print(json.dumps({"result": result["result"], "checks": result["check_count"]}))
