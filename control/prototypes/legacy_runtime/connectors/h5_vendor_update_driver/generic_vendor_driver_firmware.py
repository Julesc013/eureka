"""Fixture-only normalizer for Generic vendor driver/firmware portal metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h5_vendor_update_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h5_vendor_update_fixture(raw_fixture, "generic_vendor_driver_firmware", policy)
