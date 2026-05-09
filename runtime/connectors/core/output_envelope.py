"""Connector output envelope builders and validators."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.connectors.core.connector_interface import validate_no_boundary_violations


ALLOWED_OUTPUT_TYPES = {
    "normalized_source_record",
    "source_cache_candidate",
    "evidence_candidate_preview",
    "review_queue_seed_preview",
    "connector_health_summary",
    "policy_blocked_output",
}
FORBIDDEN_OUTPUT_TYPES = {
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_record",
    "public_index_mutation",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "downloaded_file",
    "executed_artifact",
}


def build_connector_output_envelope(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Wrap connector output as a candidate-only envelope."""

    output_type = str(inputs.get("output_type") or "normalized_source_record")
    if output_type in FORBIDDEN_OUTPUT_TYPES:
        raise ValueError(f"forbidden connector output type: {output_type}")
    if output_type not in ALLOWED_OUTPUT_TYPES:
        raise ValueError(f"unknown connector output type: {output_type}")
    connector_id = str(inputs.get("connector_id") or "unknown_connector")
    source_id = str(inputs.get("source_id") or "unknown_source")
    native_id = inputs.get("source_native_id")
    envelope = {
        "schema_version": "source_connector_output_envelope.v0",
        "output_envelope_id": str(inputs.get("output_envelope_id") or f"connector_output.{connector_id}.{source_id}.v0"),
        "connector_id": connector_id,
        "source_id": source_id,
        "output_status": str(inputs.get("output_status") or "candidate_preview"),
        "output_type": output_type,
        "source_native_id": native_id,
        "normalized_record": inputs.get("normalized_record"),
        "source_cache_candidate": inputs.get("source_cache_candidate"),
        "evidence_candidate_preview": inputs.get("evidence_candidate_preview"),
        "review_queue_seed_preview": inputs.get("review_queue_seed_preview"),
        "limitations": list(inputs.get("limitations") or ["connector output is not accepted truth"]),
        "warnings": list(inputs.get("warnings") or []),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": list(inputs.get("notes") or ["Output envelope is candidate-only and review-gated."]),
    }
    validate_connector_output_envelope(envelope, policy)
    return envelope


def validate_connector_output_envelope(envelope: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate candidate-only connector output semantics."""

    output_type = envelope.get("output_type")
    if output_type in FORBIDDEN_OUTPUT_TYPES:
        raise ValueError(f"forbidden connector output type: {output_type}")
    if output_type not in ALLOWED_OUTPUT_TYPES:
        raise ValueError(f"unknown connector output type: {output_type}")
    validate_no_boundary_violations(envelope, policy)
    return {"status": "valid", "output_type": output_type}


def _truth_boundary() -> dict[str, bool]:
    return {
        "connector_output_is_public_truth": False,
        "connector_output_is_accepted_evidence": False,
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
