"""OS package identity/dependency/file candidate helpers for H3 fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h3_os_package_archives.normalizer_common import (
    build_h3_dependency_candidates,
    build_h3_os_package_identity_candidate,
    build_h3_package_file_candidates,
)


def build_identity_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h3_os_package_identity_candidate(normalized_record, policy)


def build_dependency_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return build_h3_dependency_candidates(normalized_record, policy)


def build_file_candidates(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return build_h3_package_file_candidates(normalized_record, policy)
