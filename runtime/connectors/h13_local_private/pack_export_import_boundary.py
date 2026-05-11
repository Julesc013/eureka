"""H13 pack export import boundary candidate helper."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import build_h13_pack_export_import_boundary_candidate


def build_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h13_pack_export_import_boundary_candidate(normalized_record, policy)
