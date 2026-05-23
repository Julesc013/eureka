"""Compatibility package for runtime.review_queue; canonical package is runtime.review.queue."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'review' / 'queue'
__path__ = [str(_CANONICAL_PATH)]

from runtime.review.queue import *  # noqa: E402,F401,F403
