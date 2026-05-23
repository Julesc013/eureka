"""Compatibility package for runtime.candidate_index; canonical package is runtime.index.candidate."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'index' / 'candidate'
__path__ = [str(_CANONICAL_PATH)]

from runtime.index.candidate import *  # noqa: E402,F401,F403
