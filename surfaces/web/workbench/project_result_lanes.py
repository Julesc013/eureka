"""Surface-local helpers for rendering-safe result lane projections.

This module intentionally does not import runtime internals. It accepts
already-built packets/view models and performs surface-local shape checks.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


OPERATOR_ONLY_FIELDS = frozenset(
    {
        "operator_notes",
        "source_record_ids",
        "source_cache_entry_ids",
        "evidence_refs",
        "candidate_refs",
        "review_refs",
        "workunit_refs",
        "private_local_path_refs",
        "debug",
    }
)


def project_result_lane_page_for_web(page_view: Mapping[str, Any], projection_profile: str) -> dict[str, Any]:
    projected = deepcopy(dict(page_view))
    projected["projection_profile"] = projection_profile
    if projection_profile == "operator_workbench":
        return projected
    projected["lanes"] = [_strip_operator_fields(lane) for lane in projected.get("lanes", [])]
    boundary = dict(projected.get("boundary_report", {}))
    boundary["operator_fields_hidden"] = True
    projected["boundary_report"] = boundary
    return _strip_operator_fields(projected)


def _strip_operator_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _strip_operator_fields(inner)
            for key, inner in value.items()
            if str(key) not in OPERATOR_ONLY_FIELDS
        }
    if isinstance(value, list):
        return [_strip_operator_fields(item) for item in value]
    return value
