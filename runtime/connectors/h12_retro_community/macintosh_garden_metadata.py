"""Fixture-only normalizer for macintosh_garden_metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h12_retro_community_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h12_retro_community_fixture(raw_fixture, "macintosh_garden_metadata", policy)
