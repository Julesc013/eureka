"""Fixture-only normalizer for local_disk_image_metadata."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import normalize_h13_local_private_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h13_local_private_fixture(raw_fixture, "local_disk_image_metadata", policy)
