"""Compatibility package for runtime.public_index; canonical package is runtime.index.public."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'index' / 'public'
__path__ = [str(_CANONICAL_PATH)]

from runtime.index.public import *  # noqa: E402,F401,F403
