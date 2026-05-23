"""Compatibility package for runtime.workunit_queue; canonical package is runtime.worker.workunit_queue."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'worker' / 'workunit_queue'
__path__ = [str(_CANONICAL_PATH)]

from runtime.worker.workunit_queue import *  # noqa: E402,F401,F403
