"""Compatibility package for runtime.source_observation; canonical package is runtime.source.observation."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'source' / 'observation'
__path__ = [str(_CANONICAL_PATH)]

from runtime.source.observation import *  # noqa: E402,F401,F403
