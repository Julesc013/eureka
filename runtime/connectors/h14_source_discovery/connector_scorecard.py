"""H14 connector scorecard candidate helper."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .normalizer_common import build_h14_connector_scorecard_candidate


def build(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return build_h14_connector_scorecard_candidate(normalized_record, policy)
