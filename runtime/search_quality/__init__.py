"""Compatibility package for runtime.search_quality; canonical package is runtime.search.quality."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'search' / 'quality'
__path__ = [str(_CANONICAL_PATH)]

from runtime.search.quality import *  # noqa: E402,F401,F403
