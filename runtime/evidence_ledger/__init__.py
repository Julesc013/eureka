"""Compatibility package for runtime.evidence_ledger; canonical package is runtime.evidence.ledger."""

from pathlib import Path

_CANONICAL_PATH = Path(__file__).resolve().parents[1] / 'evidence' / 'ledger'
__path__ = [str(_CANONICAL_PATH)]

from runtime.evidence.ledger import *  # noqa: E402,F401,F403
