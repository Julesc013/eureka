"""Fixture-only normalizer for C-SPAN video/event metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h6_web_archive_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h6_web_archive_fixture(raw_fixture, "cspan_video_library", policy)
