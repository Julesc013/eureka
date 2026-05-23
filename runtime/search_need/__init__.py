"""Compatibility package for runtime.search_need; canonical package is runtime.search.need."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'search' / 'need'
__path__ = [str(_CANONICAL_PATH)]

from runtime.search.need import *  # noqa: E402,F401,F403
