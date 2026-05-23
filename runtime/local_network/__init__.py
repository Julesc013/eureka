"""Compatibility package for runtime.local_network; canonical package is runtime.local.network."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'network'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.network import *  # noqa: E402,F401,F403
