"""Compatibility package for runtime.source_registry; canonical package is runtime.source.registry."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'source' / 'registry'
__path__ = [str(_CANONICAL_PATH)]

from runtime.source.registry import *  # noqa: E402,F401,F403
