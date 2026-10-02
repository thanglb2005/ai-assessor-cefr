"""Local, single-process application entry point."""

from aicefr.local.app import LocalRuntime, create_runtime

__all__ = ["LocalRuntime", "create_runtime"]
