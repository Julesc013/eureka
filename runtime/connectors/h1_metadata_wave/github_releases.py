"""GitHub Releases fixture normalizer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h1_metadata_wave.normalizer_common import normalize_h1_fixture

SOURCE_ID = "github_releases"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h1_fixture(raw_fixture, SOURCE_ID, policy)
