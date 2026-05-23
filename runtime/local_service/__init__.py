"""Compatibility package for runtime.local_service; canonical package is runtime.local.service."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'service'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.service import *  # noqa: E402,F401,F403
