"""Repology fixture normalizer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.normalizer_common import normalize_h1_fixture

SOURCE_ID = "repology"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h1_fixture(raw_fixture, SOURCE_ID, policy)
