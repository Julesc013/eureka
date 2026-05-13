"""Maven Central Metadata fixture normalizer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from control.prototypes.legacy_runtime.connectors.h2_package_registries.normalizer_common import normalize_h2_package_fixture

SOURCE_ID = "maven_central"


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h2_package_fixture(raw_fixture, SOURCE_ID, policy)

