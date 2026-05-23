"""Compatibility package for runtime.local_appliance; canonical package is runtime.local.appliance."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'local' / 'appliance'
__path__ = [str(_CANONICAL_PATH)]

from runtime.local.appliance import *  # noqa: E402,F401,F403
