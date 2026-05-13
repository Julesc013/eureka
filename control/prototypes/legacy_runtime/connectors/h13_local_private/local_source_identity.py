"""H13 local source identity candidate helper."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import build_h13_local_source_identity_candidate


def build_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h13_local_source_identity_candidate(normalized_record, policy)
