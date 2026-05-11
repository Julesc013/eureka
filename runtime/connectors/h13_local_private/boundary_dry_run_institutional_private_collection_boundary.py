"""Source-specific H13 boundary dry-run wrapper for institutional_private_collection_boundary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.h13_local_private.boundary_dry_run_common import (
    BOUNDARY_REQUEST_KEYS,
    build_h13_boundary_dry_run_blocked_result,
    build_h13_boundary_dry_run_result,
    build_h13_local_private_boundary_dry_run_request,
    validate_h13_boundary_dry_run_request,
)

SOURCE_ID = "institutional_private_collection_boundary"


def build_boundary_request(request: Mapping[str, Any] | None, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if request is not None:
        return dict(request)
    return build_h13_local_private_boundary_dry_run_request(SOURCE_ID, BOUNDARY_REQUEST_KEYS[SOURCE_ID], policy_bundle)


def evaluate_boundary_request(boundary_request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_h13_boundary_dry_run_request(boundary_request, policy_bundle)
    if not validation["approved"]:
        return build_h13_boundary_dry_run_blocked_result(boundary_request, validation["blocked_reasons"], policy_bundle)
    return build_h13_boundary_dry_run_result(SOURCE_ID, dict(boundary_request.get("boundary_payload") or {}), {"result_status": "boundary_dry_run_completed", "operation_count": 1, "request_key": boundary_request.get("approved_request_key")}, policy_bundle)


def normalize_boundary_payload(boundary_payload: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return build_h13_boundary_dry_run_result(SOURCE_ID, boundary_payload, {"result_status": "boundary_dry_run_completed", "operation_count": 1}, policy_bundle)["normalized_record"]
