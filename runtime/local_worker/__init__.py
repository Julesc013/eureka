"""Compatibility package for runtime.local_worker; canonical package is runtime.local.worker."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'worker'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.worker import *  # noqa: E402,F401,F403
