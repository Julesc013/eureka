"""Fixture-only normalizer for source_lineage_provenance."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import normalize_h14_source_discovery_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h14_source_discovery_fixture(raw_fixture, "source_lineage_provenance", policy)
