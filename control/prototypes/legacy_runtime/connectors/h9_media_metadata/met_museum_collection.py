"""Fixture-only normalizer for met_museum_collection."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h9_media_metadata_fixture

SOURCE_ID = "met_museum_collection"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h9_media_metadata_fixture(raw_fixture, SOURCE_ID, policy)
