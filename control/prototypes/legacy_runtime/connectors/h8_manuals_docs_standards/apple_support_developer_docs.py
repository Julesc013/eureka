"""Fixture-only normalizer for apple_support_developer_docs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h8_manuals_docs_fixture

SOURCE_ID = "apple_support_developer_docs"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h8_manuals_docs_fixture(raw_fixture, SOURCE_ID, policy=policy)
