"""Fixture-only normalizer for vimeo_creative_commons_policy_limited."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h9_media_metadata_fixture

SOURCE_ID = "vimeo_creative_commons_policy_limited"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h9_media_metadata_fixture(raw_fixture, SOURCE_ID, policy)
