"""Fixture-only normalizer for ia_manuals_library."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h8_manuals_docs_fixture

SOURCE_ID = "ia_manuals_library"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h8_manuals_docs_fixture(raw_fixture, SOURCE_ID, policy=policy)
