"""Fixture-only normalizer for private_nas_metadata_boundary."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import normalize_h13_local_private_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h13_local_private_fixture(raw_fixture, "private_nas_metadata_boundary", policy)
