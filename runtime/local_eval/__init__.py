"""Compatibility package for runtime.local_eval; canonical package is runtime.local.eval."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'eval'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.eval import *  # noqa: E402,F401,F403
