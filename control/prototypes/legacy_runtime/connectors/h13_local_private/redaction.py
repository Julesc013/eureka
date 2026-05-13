"""Public-safe locator redaction helpers for H13 fixtures."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import hash_h13_locator, redact_h13_locator


def redact(value: Any, policy: Mapping[str, Any] | None = None) -> str:
    return redact_h13_locator(value, policy)


def locator_hash(value: Any, policy: Mapping[str, Any] | None = None) -> str:
    return hash_h13_locator(value, policy)
