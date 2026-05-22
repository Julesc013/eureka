"""Package identity/dependency/file candidate helpers for H2 fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from archive.prototypes.legacy_runtime.connectors.h2_package_registries.normalizer_common import (
    build_h2_dependency_candidates,
    build_h2_package_file_candidates,
    build_h2_package_identity_candidate,
)


def build_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h2_package_identity_candidate(normalized_record, policy)


def build_dependency_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return build_h2_dependency_candidates(normalized_record, policy)


def build_file_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return build_h2_package_file_candidates(normalized_record, policy)

