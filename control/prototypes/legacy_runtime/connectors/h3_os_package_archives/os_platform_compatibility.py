"""OS/platform compatibility candidate helpers for H3 fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from control.prototypes.legacy_runtime.connectors.h3_os_package_archives.normalizer_common import build_h3_os_platform_compatibility_candidate


def build_compatibility_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h3_os_platform_compatibility_candidate(normalized_record, policy)
