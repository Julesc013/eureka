"""Fixture-only normalizer for dpla."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h7_library_research_fixture

SOURCE_ID = "dpla"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h7_library_research_fixture(raw_fixture, SOURCE_ID, policy=policy)
