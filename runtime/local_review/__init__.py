"""Compatibility package for runtime.local_review; canonical package is runtime.local.review."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'review'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.review import *  # noqa: E402,F401,F403
