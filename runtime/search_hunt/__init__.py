"""Compatibility package for runtime.search_hunt; canonical package is runtime.search.hunt."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'search' / 'hunt'
__path__ = [str(_CANONICAL_PATH)]

from runtime.search.hunt import *  # noqa: E402,F401,F403
