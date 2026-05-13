"""Path and locator safety checks for H13 public-safe fixture outputs."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import detect_h13_secret_or_private_data_violations, validate_h13_public_safe_path


def is_public_safe_locator(value: Any, policy: Mapping[str, Any] | None = None) -> bool:
    return validate_h13_public_safe_path(value, policy)


def private_data_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return detect_h13_secret_or_private_data_violations(record, policy)
