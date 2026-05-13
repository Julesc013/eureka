"""Fixture-only normalizer for Generic public event/source-trace metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h6_web_archive_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h6_web_archive_fixture(raw_fixture, "generic_public_event_trace", policy)
