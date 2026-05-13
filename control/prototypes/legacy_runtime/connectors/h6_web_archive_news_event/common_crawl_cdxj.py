"""Fixture-only normalizer for Common Crawl CDXJ / WARC index metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h6_web_archive_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h6_web_archive_fixture(raw_fixture, "common_crawl_cdxj", policy)
