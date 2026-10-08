"""Repeatable, local-only Playwright journey for W3-TEST-007."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import numpy as np
import soundfile as sf
from playwright.sync_api import BrowserContext, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIRECTORY = os.environ.get("AICEFR_MODEL_DIR")
DEFAULT_MODEL = Path(MODEL_DIRECTORY) / "ridge_resp_v2.json" if MODEL_DIRECTORY else None


def _write_audio(path: Path) -> bytes:
    """Generate two seconds with 70% silence to take the real QC REVIEW route."""
    rate = 16_000
    count = rate * 2
    samples = np.zeros(count, dtype=np.float32)
    offset = int(count * 0.7)
    active = count - offset
    samples[offset:] = 0.2 * np.sin(np.arange(active, dtype=np.float32) * (2 * np.pi * 220 / rate))
    sf.write(path, samples, rate, format="WAV", subtype="PCM_16")
    return path.read_bytes()


def _reserve_port() -> int:
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def _init_account(
    data_dir: Path, actor_id: str, role: str, password: str, env: dict[str, str]
) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "aicefr.local",
            "init-demo",
            "--data-dir",
            str(data_dir),
            "--actor-id",
            actor_id,
            "--role",
            role,
            "--password-stdin",
        ],
        cwd=ROOT,
        env=env,
        input=password + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("fixture account provisioning failed")
    if password in completed.stdout or password in completed.stderr:
        raise RuntimeError("fixture credential unexpectedly appeared in command output")


def _wait_ready(server: subprocess.Popen[str], base_url: str) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError("local WSGI process exited before readiness")
        try:
            with urllib.request.urlopen(base_url + "/login", timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)
    raise RuntimeError("local WSGI readiness timed out")


def _attach_observers(context: BrowserContext, metrics: dict[str, object]) -> None:
    def observe_page(page: Page) -> None:
        page.on(
            "response",
            lambda response: (
                metrics["http_statuses"].append(response.status)
                if urlsplit(response.url).hostname in {"127.0.0.1", "localhost"}
                else None
            ),
        )
        page.on(
            "console",
            lambda message: (
                metrics["console_errors"].append(message.type) if message.type == "error" else None
            ),
        )
        page.on("requestfailed", lambda request: metrics["failed_requests"].append(request.method))

    context.on("page", observe_page)

    def local_only(route) -> None:
        hostname = urlsplit(route.request.url).hostname
        if hostname in {"127.0.0.1", "localhost"}:
            route.continue_()
        else:
            metrics["external_requests"].append("blocked")
            route.abort()

    context.route("**/*", local_only)


def _assert_document_and_width(page: Page, viewport_width: int) -> None:
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(80)
    counts = page.evaluate(
        """() => ({
          html: document.querySelectorAll('html').length,
          head: document.querySelectorAll('head').length,
          body: document.querySelectorAll('body').length,
          viewport: Boolean(document.querySelector('meta[name=viewport]')),
          width: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          stylesheet: [...document.styleSheets].some(sheet => sheet.href?.endsWith('/local.css'))
        })"""
    )
    assert counts["html"] == counts["head"] == counts["body"] == 1, counts
    assert counts["viewport"] and counts["stylesheet"], counts
    assert counts["innerWidth"] == viewport_width, counts
    assert counts["width"] <= counts["innerWidth"], counts


def _login(page: Page, base_url: str, actor_id: str, password: str) -> None:
    page.goto(base_url + "/login", wait_until="networkidle")
    _assert_document_and_width(page, int(page.evaluate("window.innerWidth")))
    page.get_by_label("Tài khoản").fill(actor_id)
    page.get_by_label("Mật khẩu").fill(password)
    page.get_by_role("button", name="Đăng nhập").click()
    page.wait_for_load_state("networkidle")


def run(model_artifact: Path, evidence_dir: Path) -> dict[str, object]:
    if not model_artifact.is_file():
        raise ValueError("pinned model artifact path is unavailable")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    metrics: dict[str, object] = {
        "console_errors": [],
        "failed_requests": [],
        "external_requests": [],
        "http_statuses": [],
    }
    screenshots: dict[str, str] = {}
    viewport_checks = 0
    with tempfile.TemporaryDirectory(prefix="aicefr-w3-browser-") as temporary:
        temp_root = Path(temporary)
        data_dir = temp_root / "data"
        audio_path = temp_root / "fixture.wav"
        audio = _write_audio(audio_path)
        audio_sha256 = hashlib.sha256(audio).hexdigest()
        config_path = temp_root / "local-config.json"
        config = {
            "demo": True,
            "consent_version": "browser-v1",
            "allowed_media_types": ["audio/wav"],
            "tasks": [{"task_id": "fixture-speaking", "task_version": "v1"}],
            "model_artifact": str(model_artifact),
            "vad_enabled": True,
            "qc": {
                "version": "browser-review-v1",
                "accepted_formats": ["wav"],
                "max_input_bytes": 2_000_000,
                "min_duration_s": 1,
                "max_duration_s": 10,
                "max_input_sample_rate_hz": 16_000,
                "silence_threshold": 0.01,
                "clipping_threshold": 0.99,
                "review_silence_ratio": 0.5,
                "reject_silence_ratio": 0.95,
                "review_clipping_ratio": 0.1,
                "reject_clipping_ratio": 0.5,
            },
        }
        config_path.write_text(json.dumps(config), encoding="utf-8")
        passwords = {
            actor: secrets.token_urlsafe(24)
            for actor in ("fixture-student", "fixture-teacher", "fixture-other")
        }
        child_env = os.environ.copy()
        child_env["PYTHONPATH"] = str(ROOT / "src")
        child_env["AICEFR_MODEL_DIR"] = str(model_artifact.parent)
        for actor, role in (
            ("fixture-student", "student"),
            ("fixture-teacher", "teacher"),
            ("fixture-other", "student"),
        ):
            _init_account(data_dir, actor, role, passwords[actor], child_env)

        port = _reserve_port()
        base_url = f"http://127.0.0.1:{port}"
        server = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-m",
                "aicefr.local",
                "serve",
                "--data-dir",
                str(data_dir),
                "--config",
                str(config_path),
                "--bind",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        try:
            _wait_ready(server, base_url)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)

                student_context = browser.new_context(viewport={"width": 1280, "height": 800})
                _attach_observers(student_context, metrics)
                student_page = student_context.new_page()
                _login(student_page, base_url, "fixture-student", passwords["fixture-student"])
                assert student_page.url.endswith("/student/consent")
                _assert_document_and_width(student_page, 1280)
                viewport_checks += 1
                assert "dữ liệu kiểm thử do nhóm tạo" in student_page.locator("body").inner_text()
                consent_button = student_page.get_by_role("button", name="Đồng ý", exact=True)
                consent_button.focus()
                assert consent_button.evaluate("el => el.matches(':focus-visible')")
                consent_button.click()
                student_page.wait_for_url("**/student/consent")
                student_page.goto(base_url + "/student/upload", wait_until="networkidle")
                _assert_document_and_width(student_page, 1280)
                viewport_checks += 1
                upload_button = student_page.get_by_role("button", name="Nộp bài")
                upload_button.focus()
                assert upload_button.evaluate("el => el.matches(':focus-visible')")
                student_page.get_by_label("Mã bài").fill("fixture-speaking")
                student_page.get_by_label("Phiên bản bài").fill("v1")
                student_page.get_by_label("Phiên bản đồng ý").fill("browser-v1")
                student_page.get_by_label("Tệp âm thanh").set_input_files(str(audio_path))
                student_page.get_by_role("button", name="Nộp bài").click()
                student_page.wait_for_url("**/student/responses/*")
                response_id = student_page.url.rstrip("/").split("/")[-1]
                assert len(response_id) == 32
                assert "REVIEW_REQUIRED" in student_page.locator("body").inner_text()
                _assert_document_and_width(student_page, 1280)
                viewport_checks += 1
                student_page.get_by_role("link", name="Xem báo cáo").click()
                student_page.wait_for_url(f"**/student/responses/{response_id}/report")
                student_report = student_page.locator("body").inner_text()
                assert "Chưa đủ điều kiện ước lượng" in student_report
                assert "Overall" in student_report
                _assert_document_and_width(student_page, 1280)
                viewport_checks += 1
                student_screenshot = evidence_dir / "browser-qa-desktop-student-report.png"
                student_page.screenshot(path=str(student_screenshot), full_page=True)
                screenshots[student_screenshot.name] = hashlib.sha256(
                    student_screenshot.read_bytes()
                ).hexdigest()
                role_denial = student_context.request.get(base_url + "/teacher/reviews")
                assert role_denial.status == 403
                metrics["http_statuses"].append(role_denial.status)
                assert "không được phép" in role_denial.text().lower()
                role_denial.dispose()

                other_context = browser.new_context(viewport={"width": 1280, "height": 800})
                _attach_observers(other_context, metrics)
                other_page = other_context.new_page()
                _login(other_page, base_url, "fixture-other", passwords["fixture-other"])
                foreign_report = other_context.request.get(
                    f"{base_url}/student/responses/{response_id}/report"
                )
                assert foreign_report.status == 404
                metrics["http_statuses"].append(foreign_report.status)
                assert "Không tìm thấy nội dung" in foreign_report.text()
                foreign_report.dispose()
                other_context.close()

                teacher_context = browser.new_context(viewport={"width": 1280, "height": 800})
                _attach_observers(teacher_context, metrics)
                teacher_page = teacher_context.new_page()
                _login(teacher_page, base_url, "fixture-teacher", passwords["fixture-teacher"])
                assert teacher_page.url.endswith("/teacher/reviews")
                _assert_document_and_width(teacher_page, 1280)
                viewport_checks += 1
                teacher_page.get_by_role("button", name="Nhận xử lý").click()
                teacher_page.wait_for_url("**/teacher/reviews")
                teacher_page.get_by_role("link", name="Xem báo cáo và duyệt").click()
                teacher_page.wait_for_url(f"**/teacher/reviews/{response_id}")
                _assert_document_and_width(teacher_page, 1280)
                viewport_checks += 1
                assert "Chưa đủ điều kiện ước lượng" in teacher_page.locator("body").inner_text()
                audio_response = teacher_context.request.get(
                    f"{base_url}/teacher/reviews/{response_id}/audio"
                )
                assert audio_response.status == 200
                assert audio_response.headers.get("content-type", "").startswith("audio/wav")
                assert hashlib.sha256(audio_response.body()).hexdigest() == audio_sha256
                audio_response.dispose()
                teacher_screenshot = evidence_dir / "browser-qa-desktop-teacher-review.png"
                teacher_page.screenshot(path=str(teacher_screenshot), full_page=True)
                screenshots[teacher_screenshot.name] = hashlib.sha256(
                    teacher_screenshot.read_bytes()
                ).hexdigest()

                teacher_page.get_by_label("Quyết định").select_option("OVERRIDE")
                teacher_page.get_by_label("Band cuối khi override").select_option("B1")
                teacher_page.get_by_label("Lý do").fill("Đánh giá fixture do nhóm tạo")
                teacher_page.get_by_role("button", name="Lưu quyết định").click()
                teacher_page.wait_for_url("**/teacher/reviews")
                teacher_page.goto(
                    f"{base_url}/teacher/reviews/{response_id}", wait_until="networkidle"
                )
                assert "Kết quả giảng viên: B1" in teacher_page.locator("body").inner_text()
                assert "Overall AI tạm thời: Chưa đủ điều kiện ước lượng" in (
                    teacher_page.locator("body").inner_text()
                )

                student_page.goto(
                    f"{base_url}/student/responses/{response_id}/report",
                    wait_until="networkidle",
                )
                final_student_report = student_page.locator("body").inner_text()
                assert "Đã có giảng viên duyệt" in final_student_report
                assert "Kết quả giảng viên: B1" in final_student_report
                assert "Overall AI tạm thời: Chưa đủ điều kiện ước lượng" in final_student_report

                student_page.goto(base_url + "/student/consent", wait_until="networkidle")
                student_page.get_by_role("button", name="Rút lại đồng ý").click()
                student_page.wait_for_url("**/student/consent")
                stale_submit = student_context.request.post(
                    base_url + "/student/responses",
                    headers={"Origin": base_url},
                    multipart={
                        "task_id": "fixture-speaking",
                        "task_version": "v1",
                        "consent_version": "browser-v1",
                        "audio": {
                            "name": audio_path.name,
                            "mimeType": "audio/wav",
                            "buffer": audio,
                        },
                    },
                )
                assert stale_submit.status == 403
                metrics["http_statuses"].append(stale_submit.status)
                assert "đã thay đổi" in stale_submit.text()
                stale_submit.dispose()

                student_page.goto(base_url + "/student/consent", wait_until="networkidle")
                cookies = student_context.cookies(base_url)
                session_cookie = next(
                    cookie["value"] for cookie in cookies if cookie["name"] == "aicefr_session"
                )
                student_page.locator("form[action='/logout'] button").click()
                student_page.wait_for_url("**/login")
                revoked = student_context.request.get(
                    base_url + "/student/consent",
                    headers={"Cookie": f"aicefr_session={session_cookie}"},
                )
                assert revoked.status == 403
                metrics["http_statuses"].append(revoked.status)
                revoked.dispose()

                mobile_student_context = browser.new_context(viewport={"width": 390, "height": 844})
                _attach_observers(mobile_student_context, metrics)
                mobile_student = mobile_student_context.new_page()
                _login(mobile_student, base_url, "fixture-student", passwords["fixture-student"])
                _assert_document_and_width(mobile_student, 390)
                viewport_checks += 1
                mobile_student.goto(base_url + "/student/upload", wait_until="networkidle")
                _assert_document_and_width(mobile_student, 390)
                viewport_checks += 1
                mobile_upload = evidence_dir / "browser-qa-mobile-student-upload.png"
                mobile_student.screenshot(path=str(mobile_upload), full_page=True)
                screenshots[mobile_upload.name] = hashlib.sha256(
                    mobile_upload.read_bytes()
                ).hexdigest()
                mobile_student.goto(
                    f"{base_url}/student/responses/{response_id}/report",
                    wait_until="networkidle",
                )
                _assert_document_and_width(mobile_student, 390)
                viewport_checks += 1
                mobile_student_context.close()

                mobile_teacher_context = browser.new_context(viewport={"width": 390, "height": 844})
                _attach_observers(mobile_teacher_context, metrics)
                mobile_teacher = mobile_teacher_context.new_page()
                _login(
                    mobile_teacher,
                    base_url,
                    "fixture-teacher",
                    passwords["fixture-teacher"],
                )
                _assert_document_and_width(mobile_teacher, 390)
                viewport_checks += 1
                mobile_teacher.goto(
                    f"{base_url}/teacher/reviews/{response_id}", wait_until="networkidle"
                )
                _assert_document_and_width(mobile_teacher, 390)
                viewport_checks += 1
                mobile_detail = evidence_dir / "browser-qa-mobile-teacher-detail.png"
                mobile_teacher.screenshot(path=str(mobile_detail), full_page=True)
                screenshots[mobile_detail.name] = hashlib.sha256(
                    mobile_detail.read_bytes()
                ).hexdigest()
                mobile_teacher_context.close()
                student_context.close()
                teacher_context.close()
                browser.close()

            if metrics["console_errors"]:
                raise AssertionError(f"browser console errors: {len(metrics['console_errors'])}")
            if metrics["failed_requests"]:
                raise AssertionError(f"failed browser requests: {len(metrics['failed_requests'])}")
            if metrics["external_requests"]:
                raise AssertionError("external browser request attempted")
        finally:
            if server.poll() is None:
                server.send_signal(signal.SIGINT)
                try:
                    server.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)

        with sqlite3.connect(data_dir / "metadata.sqlite3") as connection:
            response_count = connection.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
            assert response_count == 1, "withdrawn consent must not create a second response"

    assert {403, 404}.issubset(set(metrics["http_statuses"]))
    return {
        "result": "PASS",
        "viewport_checks": viewport_checks,
        "desktop_viewport": "1280x800",
        "mobile_viewport": "390x844",
        "observed_http_statuses": sorted(set(metrics["http_statuses"])),
        "expected_denial_statuses": sorted(
            status for status in set(metrics["http_statuses"]) if status in {401, 403, 404}
        ),
        "audio_mime_and_sha256_verified": True,
        "response_count_after_withdrawal": response_count,
        "console_error_count": len(metrics["console_errors"]),
        "failed_request_count": len(metrics["failed_requests"]),
        "external_request_count": len(metrics["external_requests"]),
        "screenshots_sha256": screenshots,
        "generated_audio_sha256": audio_sha256,
        "asr_vad_real_smoke": "NOT_RUN; QC REVIEW bypasses ASR/VAD model execution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local W3 student/teacher browser QA")
    parser.add_argument(
        "--model-artifact", type=Path, default=DEFAULT_MODEL, required=DEFAULT_MODEL is None
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=ROOT / "docs/sdd/features/w3-local-integration/evidence",
    )
    args = parser.parse_args()
    try:
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/tmp/aicefr-w3-browsers")
        print(json.dumps(run(args.model_artifact, args.evidence_dir), indent=2))
    except Exception as error:
        print(f"W3 browser QA failed: {type(error).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
