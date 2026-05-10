"""Fixture-only normalizer for Internet Archive Wayback / CDX / Memento metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h6_web_archive_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h6_web_archive_fixture(raw_fixture, "wayback_cdx_memento", policy)
