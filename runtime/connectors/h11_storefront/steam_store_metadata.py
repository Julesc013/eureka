"""Offline normalizer for steam_store_metadata committed fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h11_storefront_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h11_storefront_fixture(raw_fixture, "steam_store_metadata", policy)
