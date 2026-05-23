"""Compatibility package for runtime.local_operator; canonical package is runtime.local.operator."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'operator'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.operator import *  # noqa: E402,F401,F403
