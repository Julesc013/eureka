"""Live-probe request and blocked-result envelope helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.core.connector_interface import validate_no_boundary_violations


def build_live_probe_request_envelope(request: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a dry-run live-probe request envelope."""

    envelope = {
        "schema_version": "live_probe_request.v0",
        "live_probe_request_id": str(request.get("live_probe_request_id") or "live_probe_request.generic.v0"),
        "connector_id": str(request.get("connector_id") or "unknown_connector"),
        "source_id": str(request.get("source_id") or "unknown_source"),
        "requested_operation": str(request.get("requested_operation") or "metadata_identifier_lookup_future"),
        "requested_endpoint_class": str(request.get("requested_endpoint_class") or "metadata_endpoint_future"),
        "requested_identifier_or_query": request.get("requested_identifier_or_query"),
        "approval_refs": list(request.get("approval_refs") or []),
        "source_policy_refs": list(request.get("source_policy_refs") or []),
        "rate_limit_policy_refs": list(request.get("rate_limit_policy_refs") or []),
        "cache_policy_refs": list(request.get("cache_policy_refs") or []),
        "kill_switch_policy_refs": list(request.get("kill_switch_policy_refs") or []),
        "output_policy_refs": list(request.get("output_policy_refs") or []),
        "live_call_allowed": request.get("live_call_allowed") is True,
        "dry_run_only": request.get("dry_run_only") is not False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(request.get("notes") or ["Live-probe envelope is a policy object, not permission."]),
    }
    if envelope["live_call_allowed"]:
        raise ValueError("H0-BUNDLE-02 live probe envelopes must not allow live calls")
    validate_no_boundary_violations(envelope, policy)
    return envelope


def build_live_probe_blocked_result(request: Mapping[str, Any], policy: Mapping[str, Any] | None = None, reason: str | None = None) -> dict[str, Any]:
    """Build a blocked live-probe result without network use."""

    envelope = build_live_probe_request_envelope(request, policy)
    result = {
        "schema_version": "live_probe_result.v0",
        "live_probe_result_id": f"{envelope['live_probe_request_id']}.blocked",
        "live_probe_request_ref": envelope["live_probe_request_id"],
        "result_status": "blocked",
        "request_count": 0,
        "network_used": False,
        "endpoint_used": None,
        "response_summary": None,
        "normalized_output_refs": [],
        "source_cache_candidate_refs": [],
        "evidence_candidate_preview_refs": [],
        "review_seed_refs": [],
        "blocked_reason": reason or "missing explicit live-probe approval",
        "limitations": ["No network call was made.", "Live-probe envelope grants no permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["Blocked result is deterministic offline evidence."],
    }
    validate_no_boundary_violations(result, policy)
    return result


def _truth_boundary() -> dict[str, bool]:
    return {
        "live_probe_result_is_truth": False,
        "live_probe_envelope_grants_permission": False,
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "accepted_public_truth": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary() -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_live_probes": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "enabled_hosting": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
    }
