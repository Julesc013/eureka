"""Compatibility package for runtime.local_foundry; canonical package is runtime.local.foundry."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'foundry'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.foundry import *  # noqa: E402,F401,F403
