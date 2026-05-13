"""Fixture-only normalizer for vendor_documentation_portal."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h8_manuals_docs_fixture

SOURCE_ID = "vendor_documentation_portal"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h8_manuals_docs_fixture(raw_fixture, SOURCE_ID, policy=policy)
