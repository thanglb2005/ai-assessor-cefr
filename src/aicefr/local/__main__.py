"""CLI for the single-process local demonstrator."""

from __future__ import annotations

import argparse
import getpass
import ipaddress
import sys
from pathlib import Path
from wsgiref.simple_server import make_server

from aicefr.auth.service import AuthService
from aicefr.contracts import ActorRole
from aicefr.local.app import SQLiteSessionRepository, create_runtime, load_config
from aicefr.storage.sqlite import SQLiteStore


def _demo_config() -> dict[str, object]:
    """Explicitly permissive QC configuration for synthetic demonstration only."""
    return {
        "demo": True,
        "consent_version": "demo-v1",
        "allowed_media_types": ["audio/wav", "audio/flac", "audio/ogg", "audio/mpeg"],
        "tasks": [{"task_id": "demo-speaking", "task_version": "1"}],
        "qc": {
            "version": "demo-qc-v1",
            "accepted_formats": ["wav", "flac", "ogg", "mp3"],
            "max_input_bytes": 20_000_000,
            "min_duration_s": 1.0,
            "max_duration_s": 180.0,
            "max_input_sample_rate_hz": 48_000,
            "silence_threshold": 0.01,
            "clipping_threshold": 0.99,
            "review_silence_ratio": 0.5,
            "reject_silence_ratio": 0.95,
            "review_clipping_ratio": 0.1,
            "reject_clipping_ratio": 0.5,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m aicefr.local", description="Ứng dụng chấm nói local"
    )
    commands = parser.add_subparsers(dest="command")
    init = commands.add_parser("init-demo", help="Tạo một tài khoản fixture local")
    init.add_argument("--data-dir", type=Path, required=True)
    init.add_argument("--actor-id", required=True, help="ID phải bắt đầu bằng fixture-")
    init.add_argument(
        "--role", choices=[ActorRole.STUDENT.value, ActorRole.TEACHER.value], required=True
    )
    init.add_argument("--password-stdin", action="store_true", help="Đọc mật khẩu từ stdin")
    serve = commands.add_parser("serve", help="Chạy giao diện local trên loopback")
    serve.add_argument("--data-dir", type=Path, required=True)
    serve.add_argument("--config", type=Path)
    serve.add_argument("--demo", action="store_true", help="Dùng QC demo-only cho fixture")
    serve.add_argument("--bind", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "init-demo":
        password = (
            sys.stdin.readline().rstrip("\r\n")
            if args.password_stdin
            else getpass.getpass("Mật khẩu fixture: ")
        )
        try:
            store = SQLiteStore(args.data_dir)
            try:
                auth = AuthService(store, SQLiteSessionRepository(store))
                auth.bootstrap_fixture_account(args.actor_id, ActorRole(args.role), password)
            finally:
                store.close()
        except Exception:
            print("Không thể tạo tài khoản fixture.", file=sys.stderr)
            return 2
        print(f"Đã tạo tài khoản fixture {args.actor_id} ({args.role}).")
        return 0
    try:
        address = ipaddress.ip_address(args.bind)
        if not address.is_loopback or not 1 <= args.port <= 65535:
            parser.error("serve chỉ chấp nhận bind loopback và port 1–65535")
        if args.demo and args.config:
            parser.error("chọn --demo hoặc --config")
        if not args.demo and args.config is None:
            parser.error("serve cần --config tường minh hoặc --demo")
        config = _demo_config() if args.demo else load_config(args.config)
        runtime = create_runtime(args.data_dir, config=config)
    except Exception:
        print("Cấu hình local không hợp lệ hoặc không khả dụng.", file=sys.stderr)
        return 2
    if args.demo:
        print("DEMO LOCAL: chỉ dùng tài khoản/audio giả; QC không đại diện cấu hình vận hành.")
    server = None
    try:
        server = make_server(str(address), args.port, runtime.app)
        print(f"Local server: http://{address}:{args.port}/login")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if server is not None:
            server.server_close()
        runtime.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
