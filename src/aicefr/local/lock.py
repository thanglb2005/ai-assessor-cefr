"""Exclusive local server lease so restart recovery cannot affect another server."""

from __future__ import annotations

import os

from aicefr.storage.paths import external_data_dir


def acquire_server_lock(data_dir):
    handle = (external_data_dir(data_dir) / "server.lock").open("a+b")
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            if handle.read(1) == b"":
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return handle
    except Exception:
        handle.close()
        raise
