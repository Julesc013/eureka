"""Fixture-only normalizer for Nixpkgs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h3_os_package_archives.normalizer_common import normalize_h3_os_package_fixture


def normalize(raw_fixture: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return normalize_h3_os_package_fixture(raw_fixture, "nixpkgs", policy)
