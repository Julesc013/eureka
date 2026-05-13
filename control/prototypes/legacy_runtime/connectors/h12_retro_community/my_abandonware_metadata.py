"""Fixture-only normalizer for my_abandonware_metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h12_retro_community_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h12_retro_community_fixture(raw_fixture, "my_abandonware_metadata", policy)
