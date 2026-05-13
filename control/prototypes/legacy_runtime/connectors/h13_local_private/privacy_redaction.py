"""H13 privacy redaction candidate helper."""

from __future__ import annotations

from typing import Any, Mapping

from .normalizer_common import build_h13_privacy_redaction_candidate


def build_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h13_privacy_redaction_candidate(normalized_record, policy)
