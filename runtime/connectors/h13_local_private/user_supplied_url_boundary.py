"""H13 user supplied url boundary candidate helper."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import build_h13_user_supplied_url_boundary_candidate


def build_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h13_user_supplied_url_boundary_candidate(normalized_record, policy)
