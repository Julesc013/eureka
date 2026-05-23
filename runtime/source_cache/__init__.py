"""Compatibility package for runtime.source_cache; canonical package is runtime.source.cache."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'source' / 'cache'
__path__ = [str(_CANONICAL_PATH)]

from runtime.source.cache import *  # noqa: E402,F401,F403
