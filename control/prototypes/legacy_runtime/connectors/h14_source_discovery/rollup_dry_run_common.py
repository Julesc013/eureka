"""Offline H14 Source OS rollup dry-run helpers."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import (
    CANDIDATE_CONFIGS,
    H14_SOURCE_CONFIGS,
    H14_SOURCE_IDS,
    PRODUCT_FORBIDDEN_TRUE_KEYS,
    TRUTH_FORBIDDEN_TRUE_KEYS,
    build_h14_connector_pack_manifest_candidate,
    build_h14_connector_scorecard_candidate,
    build_h14_coverage_manifest_candidate,
    build_h14_evidence_candidate_preview,
    build_h14_pack_import_export_boundary_candidate,
    build_h14_source_cache_candidate_preview,
    build_h14_source_candidate_candidate,
    build_h14_source_discovery_candidate,
    build_h14_source_dispute_revocation_candidate,
    build_h14_source_lineage_provenance_candidate,
    build_h14_source_need_candidate,
    build_h14_source_pack_manifest_candidate,
    build_h14_source_reliability_freshness_candidate,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
POLICY_PATHS = {
    "dry_run_policy": "control/inventory/connectors/h14_source_discovery_rollup_dry_run_policy.json",
    "allowed_requests": "control/inventory/connectors/h14_source_discovery_rollup_allowed_requests.json",
    "operation_policy": "control/inventory/connectors/h14_source_discovery_rollup_operation_policy.json",
    "input_policy": "control/inventory/connectors/h14_source_discovery_rollup_input_policy.json",
    "output_policy": "control/inventory/connectors/h14_source_discovery_rollup_output_policy.json",
    "path_policy": "control/inventory/connectors/h14_source_discovery_rollup_path_policy.json",
    "review_policy": "control/inventory/connectors/h14_source_discovery_rollup_review_policy.json",
    "truth_policy": "control/inventory/connectors/h14_source_discovery_rollup_truth_policy.json",
    "no_live_call_policy": "control/inventory/connectors/h14_source_discovery_rollup_no_live_call_policy.json",
    "no_pack_import_export_policy": "control/inventory/connectors/h14_source_discovery_rollup_no_pack_import_export_policy.json",
    "registry_mutation_policy": "control/inventory/connectors/h14_source_discovery_rollup_registry_mutation_policy.json",
    "kill_switch_policy": "control/inventory/connectors/h14_source_discovery_rollup_kill_switch_policy.json",
}
ROLLUP_REQUEST_KEYS = {'source_need_registry': 'example_source_need_rollup', 'source_candidate_registry': 'example_source_candidate_rollup', 'source_discovery_policy': 'example_source_discovery_rollup', 'source_pack_manifest': 'example_source_pack_manifest_rollup', 'connector_pack_manifest': 'example_connector_pack_manifest_rollup', 'coverage_manifest': 'example_coverage_manifest_rollup', 'connector_scorecard': 'example_scorecard_rollup', 'source_reliability_freshness': 'example_reliability_freshness_rollup', 'source_dispute_revocation': 'example_dispute_revocation_rollup', 'source_lineage_provenance': 'example_lineage_provenance_rollup', 'h14_policy_blocked': 'example_policy_blocked_rollup'}
REQUEST_FORBIDDEN_TRUE_KEYS = set(['source_discovery_runtime_requested', 'live_access_requested', 'network_access_requested', 'local_access_requested', 'private_source_access_requested', 'user_supplied_url_fetch_requested', 'authenticated_access_requested', 'restricted_source_access_requested', 'model_provider_requested', 'source_sync_requested', 'crawling_requested', 'scraping_requested', 'source_registry_mutation_requested', 'connector_registry_mutation_requested', 'source_pack_export_requested', 'source_pack_import_requested', 'connector_pack_export_requested', 'connector_pack_import_requested', 'pack_signing_requested', 'pack_publication_requested', 'source_cache_write_requested', 'evidence_write_requested', 'review_queue_write_requested', 'public_index_write_requested', 'master_index_write_requested', 'accepted_truth_output_requested'])
APPROVAL_FALSE_KEYS = tuple(['source_discovery_runtime_approved', 'live_access_approved', 'network_access_approved', 'local_access_approved', 'private_source_access_approved', 'user_supplied_url_fetch_approved', 'authenticated_access_approved', 'restricted_source_access_approved', 'model_provider_approved', 'source_sync_approved', 'crawling_approved', 'scraping_approved', 'source_registry_mutation_approved', 'connector_registry_mutation_approved', 'source_pack_export_approved', 'source_pack_import_approved', 'connector_pack_export_approved', 'connector_pack_import_approved', 'pack_signing_approved', 'pack_publication_approved', 'source_cache_write_approved', 'evidence_write_approved', 'review_queue_write_approved', 'public_index_write_approved', 'master_index_write_approved', 'accepted_truth_output_approved'])
ROLLUP_TRUTH_FORBIDDEN_TRUE_KEYS = set(TRUTH_FORBIDDEN_TRUE_KEYS) | {
    "rollup_dry_run_result_is_public_truth",
    "review_seed_is_review_decision",
    "source_cache_candidate_is_accepted_source",
    "evidence_candidate_preview_is_accepted_evidence",
}
ROLLUP_PRODUCT_FORBIDDEN_TRUE_KEYS = set(PRODUCT_FORBIDDEN_TRUE_KEYS) | {
    "source_discovery_runtime_used",
    "live_access_used",
    "network_used",
    "model_provider_used",
    "source_sync_used",
    "registry_mutation_performed",
    "pack_export_import_performed",
    "source_cache_write_performed",
    "evidence_write_performed",
    "review_queue_write_performed",
    "public_index_write_performed",
    "master_index_write_performed",
    "enabled_registry_mutation",
}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
PRIVATE_PAYLOAD_KEY_RE = re.compile(r"(network_output|api_output|model_provider_output|crawled_data|scraped_data|source_discovery_runtime_output|source_registry_write|connector_registry_write|source_cache_write|evidence_write|public_index_write|master_index_write|imported_pack|exported_pack|signed_pack|private_data_payload|artifact_payload)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")
ALLOWED_ARTIFACT_PREFIXES = (
    "control/audits/",
    "control/inventory/source_packs/",
    "control/inventory/connectors/",
    "examples/connectors/h14_source_discovery/",
    "examples/source_packs/",
    "examples/sources/",
)


def load_h14_rollup_policy_bundle(root: str | Path | None = None) -> dict[str, Any]:
    base = Path(root) if root is not None else REPO_ROOT
    return {key: json.loads((base / rel).read_text(encoding="utf-8")) for key, rel in POLICY_PATHS.items()}


def build_h14_source_discovery_rollup_dry_run_request(source_id: str, request_key: str, policy_bundle: Mapping[str, Any] | None = None, dry_run_requested: bool = True) -> dict[str, Any]:
    if source_id not in H14_SOURCE_CONFIGS:
        raise ValueError(f"unknown H14 source_id: {source_id}")
    cfg = H14_SOURCE_CONFIGS[source_id]
    request = {
        "schema_version": "h14_source_discovery_rollup_dry_run_request.v0",
        "rollup_dry_run_request_id": f"h14.rollup_request.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["primary"],
        "operation_scope": "rollup_dry_run_only",
        "rollup_operation_class": "rollup_preview_only",
        "approved_request_key": request_key,
        "input_artifact_scope": "committed_h0_h14_artifacts_only",
        "h0_h13_artifact_refs": list((policy_bundle or {}).get("input_policy", {}).get("default_committed_artifact_refs", [])),
        "source_need_context": "candidate_rollup_preview_only",
        "source_candidate_context": "candidate_rollup_preview_only",
        "source_discovery_context": "candidate_only_no_runtime_discovery",
        "source_pack_context": "manifest_preview_only_no_export_import",
        "connector_pack_context": "manifest_preview_only_no_export_import",
        "coverage_manifest_context": "candidate_only_non_exhaustive",
        "scorecard_context": "review_input_only_no_connector_approval",
        "reliability_freshness_context": "candidate_only_no_reliability_or_currentness_truth",
        "dispute_revocation_context": "candidate_only_no_automatic_deletion",
        "lineage_provenance_context": "candidate_only_no_lineage_truth_or_merge",
        "pack_boundary_context": "candidate_only_no_pack_permission",
        "approval_refs": [POLICY_PATHS["allowed_requests"]],
        "policy_refs": list(POLICY_PATHS.values()),
        "dry_run_requested": bool(dry_run_requested),
        "output_policy_ref": POLICY_PATHS["output_policy"],
        "review_policy_ref": POLICY_PATHS["review_policy"],
        "truth_policy_ref": POLICY_PATHS["truth_policy"],
        "product_boundary": _product_boundary(),
        "truth_boundary": _truth_boundary(),
        "limitations": ["Rollup request is fail-closed unless committed policy approves the exact source_id and request key."],
        "notes": ["H14-BUNDLE-03 rollup requests use committed artifacts only and do not perform discovery, access, registry mutation, pack import/export, writes, or truth acceptance."],
    }
    for key in REQUEST_FORBIDDEN_TRUE_KEYS:
        request[key] = False
    _raise_on_boundary_errors(request)
    return request


def validate_h14_rollup_dry_run_request(request: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source_id = str(request.get("source_id") or "")
    request_key = str(request.get("approved_request_key") or "")
    if source_id not in H14_SOURCE_CONFIGS:
        reasons.append(f"{source_id or 'missing_source'} is not a known H14 Source OS rollup concept")
    else:
        if request.get("operation_scope") != "rollup_dry_run_only":
            reasons.append("operation_scope must be rollup_dry_run_only")
        if request.get("rollup_operation_class") != "rollup_preview_only":
            reasons.append("approved operation class is not rollup_preview_only")
    if request.get("dry_run_requested") is not True:
        reasons.append("dry_run_requested must be true for a rollup preflight")
    for key in sorted(REQUEST_FORBIDDEN_TRUE_KEYS):
        if request.get(key) is True:
            reasons.append(f"{key} is forbidden for H14-BUNDLE-03 rollup dry-runs")
    if source_id in H14_SOURCE_CONFIGS:
        reasons.extend(validate_h14_rollup_approval(source_id, request_key, policy_bundle)["blocked_reasons"])
    reasons = _dedupe(reasons)
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": reasons}


def validate_h14_rollup_approval(source_id: str, request_key: str, policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    allowed = _source_policy(source_id, policy_bundle, "allowed_requests")
    if not allowed:
        reasons.append("source is not listed in H14 rollup allowed request policy")
    else:
        if allowed.get("approval_status") != "approved_for_rollup_dry_run":
            reasons.append("source approval_status is not approved_for_rollup_dry_run")
        if allowed.get("rollup_dry_run_approved") is not True:
            reasons.append("rollup_dry_run_approved is missing or false")
        if allowed.get("approved_source_id") != source_id:
            reasons.append("approved_source_id does not match requested source")
        if allowed.get("operation_scope") != "rollup_dry_run_only":
            reasons.append("operation_scope is not rollup_dry_run_only")
        if allowed.get("approved_operation_class") != "rollup_preview_only":
            reasons.append("approved operation class is not rollup_preview_only")
        if request_key not in (allowed.get("allowed_request_keys") or []):
            reasons.append("request key is not approved for this source")
        if int(allowed.get("max_operations_current") or 0) <= 0:
            reasons.append("request budget is not approved")
        if allowed.get("output_paths_allowlisted") is not True:
            reasons.append("output paths are not allowlisted")
        for key in APPROVAL_FALSE_KEYS:
            if allowed.get(key) is not False:
                reasons.append(f"{key} must remain false")
    global_policy = policy_bundle.get("dry_run_policy", {})
    if global_policy.get("allowed_operation_scope") != "rollup_dry_run_only":
        reasons.append("global allowed operation scope is not rollup_dry_run_only")
    for key, value in global_policy.items():
        if key.endswith("_enabled") and value is True:
            reasons.append(f"global policy {key} must remain false")
    kill = policy_bundle.get("kill_switch_policy", {})
    if kill.get("kill_switch_defaults_fail_closed") is not True:
        reasons.append("kill switch does not default fail-closed")
    if kill.get("rollup_dry_run_kill_switch_enabled") is True:
        reasons.append("rollup dry-run kill switch is enabled")
    return {"approved": not reasons, "result_status": _status_for_reasons(reasons), "blocked_reasons": _dedupe(reasons)}


def build_h14_rollup_blocked_result(request: Mapping[str, Any], reason: str | list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_id = str(request.get("source_id") or "unknown")
    cfg = H14_SOURCE_CONFIGS.get(source_id, {"connector_family": request.get("connector_family", "unknown"), "primary": request.get("source_record_kind", "unknown")})
    reasons = reason if isinstance(reason, list) else [reason]
    normalized = _normalized_rollup_record(source_id if source_id in H14_SOURCE_CONFIGS else "source_need_registry", str(request.get("approved_request_key") or "blocked"), [], "blocked_rollup_preflight")
    result = _base_result(request, source_id, cfg, normalized, _status_for_reasons(reasons), 0, reasons, policy_bundle)
    result["limitations"] = ["No rollup operation was approved or performed; output is blocked candidate/preview material only."]
    _raise_on_boundary_errors(result)
    return result


def load_h14_rollup_inputs(input_refs: list[str] | tuple[str, ...] | None, policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs = list(input_refs or policy_bundle.get("input_policy", {}).get("default_committed_artifact_refs", []))
    artifacts: list[dict[str, Any]] = []
    for ref in refs:
        path = _safe_artifact_path(ref)
        if not path.exists():
            artifacts.append({"artifact_ref": ref, "artifact_status": "missing_committed_optional_ref"})
            continue
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            artifacts.append({"artifact_ref": ref, "artifact_status": "loaded", "schema_version": payload.get("schema_version") if isinstance(payload, dict) else "unknown", "payload": payload})
        else:
            artifacts.append({"artifact_ref": ref, "artifact_status": "referenced_non_json_committed_artifact"})
    return artifacts


def build_h14_rollup_dry_run_result(source_id: str, input_artifacts: list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    if source_id not in H14_SOURCE_CONFIGS:
        raise ValueError(f"unknown H14 source_id: {source_id}")
    request = build_h14_source_discovery_rollup_dry_run_request(source_id, ROLLUP_REQUEST_KEYS[source_id], policy_bundle)
    normalized = _normalized_rollup_record(source_id, ROLLUP_REQUEST_KEYS[source_id], input_artifacts, "rollup_dry_run_completed")
    result = _base_result(request, source_id, H14_SOURCE_CONFIGS[source_id], normalized, "rollup_dry_run_completed", 1, [], policy_bundle)
    _raise_on_boundary_errors(result)
    return result


def build_h14_source_need_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_need_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_source_candidate_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_candidate_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_source_discovery_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_discovery_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_source_pack_manifest_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_pack_manifest_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_connector_pack_manifest_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_connector_pack_manifest_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_coverage_manifest_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_coverage_manifest_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_connector_scorecard_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_connector_scorecard_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_reliability_freshness_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_reliability_freshness_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_dispute_revocation_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_dispute_revocation_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_lineage_provenance_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_source_lineage_provenance_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_pack_import_export_boundary_candidates_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [build_h14_pack_import_export_boundary_candidate(_coerce_normalized(rollup_inputs))]


def build_h14_source_cache_candidate_preview_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return build_h14_source_cache_candidate_preview(_coerce_normalized(rollup_inputs))


def build_h14_evidence_candidate_preview_from_rollup(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return build_h14_evidence_candidate_preview(_coerce_normalized(rollup_inputs))


def build_h14_review_queue_seed_preview_from_rollup(result: Mapping[str, Any], source_cache_preview: Mapping[str, Any], evidence_preview: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    seed = {
        "schema_version": "h14_source_discovery_rollup_review_seed.v0",
        "review_seed_id": f"h14.rollup.review_seed.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "source_id": result.get("source_id"),
        "rollup_dry_run_result_ref": result.get("rollup_dry_run_result_id"),
        "source_cache_candidate_preview_ref": source_cache_preview.get("preview_id"),
        "evidence_candidate_preview_ref": evidence_preview.get("preview_id"),
        "review_seed_only": True,
        "review_decision": False,
        "review_queue_write_performed": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Review seed preview only; no review queue write or review decision occurs."],
    }
    _raise_on_boundary_errors(seed)
    return seed


def build_h14_source_os_rollup_health_summary(result: Mapping[str, Any], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    normalized = result.get("normalized_rollup_record") if isinstance(result.get("normalized_rollup_record"), Mapping) else {}
    artifact_refs = list(normalized.get("artifact_refs") or [])
    health = {
        "schema_version": "h14_source_os_rollup_health_summary.v0",
        "health_summary_id": f"h14.rollup.health.{result.get('source_id')}.{_short_fingerprint(result)}.v0",
        "rollup_scope": "committed_h0_h14_artifacts_only",
        "source_count": len(H14_SOURCE_IDS),
        "source_family_count": 1,
        "connector_family_count": len({cfg["connector_family"] for cfg in H14_SOURCE_CONFIGS.values()}),
        "h0_h13_artifact_count": len([ref for ref in artifact_refs if "/h14-" not in ref]),
        "coverage_manifest_count": len(result.get("coverage_manifest_candidates") or []),
        "scorecard_count": len(result.get("connector_scorecard_candidates") or []),
        "source_need_count": len(result.get("source_need_candidates") or []),
        "source_candidate_count": len(result.get("source_candidate_candidates") or []),
        "blocked_operation_count": 1 if result.get("blocked_reasons") else 0,
        "warnings": list(result.get("warnings") or []),
        "policy_blockers": list(result.get("blocked_reasons") or []),
        "known_gaps": ["review integration and quality delta remain H14-BUNDLE-04 work"],
        "next_recommended_action": "H14-BUNDLE-04 review integration and quality delta" if not result.get("blocked_reasons") else "Resolve rollup approval blockers or use fixture-equivalent outputs for review",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source OS rollup health summary is not production readiness, launch readiness, exhaustive coverage, connector approval, source approval, or public truth."],
    }
    _raise_on_boundary_errors(health)
    return health


def build_h14_rollup_dry_run_output_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    bundle = {
        "schema_version": "h14_source_discovery_rollup_output_bundle.v0",
        "rollup_dry_run_result": result,
        "normalized_rollup_record": result.get("normalized_rollup_record"),
        "source_need_candidates": result.get("source_need_candidates"),
        "source_candidate_candidates": result.get("source_candidate_candidates"),
        "source_discovery_candidates": result.get("source_discovery_candidates"),
        "source_pack_manifest_candidates": result.get("source_pack_manifest_candidates"),
        "connector_pack_manifest_candidates": result.get("connector_pack_manifest_candidates"),
        "coverage_manifest_candidates": result.get("coverage_manifest_candidates"),
        "connector_scorecard_candidates": result.get("connector_scorecard_candidates"),
        "source_reliability_freshness_candidates": result.get("source_reliability_freshness_candidates"),
        "source_dispute_revocation_candidates": result.get("source_dispute_revocation_candidates"),
        "source_lineage_provenance_candidates": result.get("source_lineage_provenance_candidates"),
        "pack_import_export_boundary_candidates": result.get("pack_import_export_boundary_candidates"),
        "source_cache_candidate_preview": result.get("source_cache_candidate_preview"),
        "evidence_candidate_preview": result.get("evidence_candidate_preview"),
        "review_queue_seed_preview": result.get("review_queue_seed_preview"),
        "source_os_rollup_health_summary": result.get("source_os_rollup_health_summary"),
        "validation_summary": {
            "truth_boundary_violations": detect_h14_rollup_truth_boundary_violations(result, {}),
            "product_boundary_violations": detect_h14_rollup_product_boundary_violations(result, {}),
            "registry_or_pack_mutation_violations": detect_h14_registry_or_pack_mutation_violations(result, {}),
        },
    }
    _raise_on_boundary_errors(bundle)
    return bundle


def build_h14_h0_h13_coverage_summary_preview(rollup_inputs: list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h14_h0_h13_coverage_summary_preview.v0",
        "coverage_basis": "committed_audit_and_preview_artifacts_only",
        "artifact_count": len(rollup_inputs),
        "coverage_truth_accepted": False,
        "coverage_manifest_is_exhaustive": False,
        "public_index_write_performed": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["H0-H13 coverage rollup is a preview only and does not prove completeness."],
    }


def build_h14_h0_h13_scorecard_summary_preview(rollup_inputs: list[Mapping[str, Any]], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "h14_h0_h13_scorecard_summary_preview.v0",
        "scorecard_basis": "committed_audit_and_preview_artifacts_only",
        "artifact_count": len(rollup_inputs),
        "scorecard_truth_accepted": False,
        "connector_approval_claimed": False,
        "production_readiness_claimed": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["H0-H13 scorecard rollup is a preview only and does not approve connectors."],
    }


def summarize_h14_rollup_dry_run_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": result.get("source_id"),
        "result_status": result.get("result_status"),
        "operation_count": int(result.get("operation_count") or 0),
        "network_used": bool(result.get("network_used")),
        "model_provider_used": bool(result.get("model_provider_used")),
        "registry_mutation_performed": bool(result.get("registry_mutation_performed")),
        "pack_export_import_performed": bool(result.get("pack_export_import_performed")),
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "source_need_candidate_count": len(result.get("source_need_candidates") or []),
        "source_candidate_candidate_count": len(result.get("source_candidate_candidates") or []),
        "coverage_manifest_candidate_count": len(result.get("coverage_manifest_candidates") or []),
        "connector_scorecard_candidate_count": len(result.get("connector_scorecard_candidates") or []),
        "truth_boundary_violations": detect_h14_rollup_truth_boundary_violations(result, {}),
        "product_boundary_violations": detect_h14_rollup_product_boundary_violations(result, {}),
        "registry_or_pack_mutation_violations": detect_h14_registry_or_pack_mutation_violations(result, {}),
    }


def detect_h14_rollup_truth_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, ROLLUP_TRUTH_FORBIDDEN_TRUE_KEYS, "truth", violations)
    return violations


def detect_h14_rollup_product_boundary_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, ROLLUP_PRODUCT_FORBIDDEN_TRUE_KEYS, "product", violations)
    return violations


def detect_h14_registry_or_pack_mutation_violations(result: Mapping[str, Any], policy_bundle: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, {"source_registry_mutation_requested", "connector_registry_mutation_requested", "source_pack_export_requested", "source_pack_import_requested", "connector_pack_export_requested", "connector_pack_import_requested", "pack_signing_requested", "pack_publication_requested", "registry_mutation_performed", "pack_export_import_performed", "source_cache_write_performed", "evidence_write_performed", "review_queue_write_performed", "public_index_write_performed", "master_index_write_performed", "source_registry_mutated", "connector_registry_mutated", "pack_export_import_permission_claimed"}, "mutation", violations)
    _collect_secret_or_private_data(result, "rollup", violations)
    return violations


def _base_result(request: Mapping[str, Any], source_id: str, cfg: Mapping[str, Any], normalized: Mapping[str, Any], status: str, operation_count: int, blocked_reasons: list[str], policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    source_cache = build_h14_source_cache_candidate_preview_from_rollup(normalized, policy_bundle)
    evidence = build_h14_evidence_candidate_preview_from_rollup(normalized, policy_bundle)
    result: dict[str, Any] = {
        "schema_version": "h14_source_discovery_rollup_dry_run_result.v0",
        "rollup_dry_run_result_id": f"h14.rollup_result.{source_id}.{_short_fingerprint(request)}.v0",
        "rollup_dry_run_request_ref": request.get("rollup_dry_run_request_id"),
        "source_id": source_id,
        "connector_family": cfg.get("connector_family"),
        "source_record_kind": cfg.get("primary"),
        "result_status": status,
        "operation_count": operation_count,
        "source_discovery_runtime_used": False,
        "live_access_used": False,
        "network_used": False,
        "model_provider_used": False,
        "source_sync_used": False,
        "registry_mutation_performed": False,
        "pack_export_import_performed": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "review_queue_write_performed": False,
        "public_index_write_performed": False,
        "master_index_write_performed": False,
        "normalized_rollup_record": normalized,
        "source_need_candidates": build_h14_source_need_candidates_from_rollup(normalized, policy_bundle),
        "source_candidate_candidates": build_h14_source_candidate_candidates_from_rollup(normalized, policy_bundle),
        "source_discovery_candidates": build_h14_source_discovery_candidates_from_rollup(normalized, policy_bundle),
        "source_pack_manifest_candidates": build_h14_source_pack_manifest_candidates_from_rollup(normalized, policy_bundle),
        "connector_pack_manifest_candidates": build_h14_connector_pack_manifest_candidates_from_rollup(normalized, policy_bundle),
        "coverage_manifest_candidates": build_h14_coverage_manifest_candidates_from_rollup(normalized, policy_bundle),
        "connector_scorecard_candidates": build_h14_connector_scorecard_candidates_from_rollup(normalized, policy_bundle),
        "source_reliability_freshness_candidates": build_h14_reliability_freshness_candidates_from_rollup(normalized, policy_bundle),
        "source_dispute_revocation_candidates": build_h14_dispute_revocation_candidates_from_rollup(normalized, policy_bundle),
        "source_lineage_provenance_candidates": build_h14_lineage_provenance_candidates_from_rollup(normalized, policy_bundle),
        "pack_import_export_boundary_candidates": build_h14_pack_import_export_boundary_candidates_from_rollup(normalized, policy_bundle),
        "source_cache_candidate_preview": source_cache,
        "evidence_candidate_preview": evidence,
        "review_queue_seed_preview": None,
        "source_os_rollup_health_summary": None,
        "blocked_reason": "; ".join(blocked_reasons) if blocked_reasons else None,
        "blocked_reasons": blocked_reasons,
        "warnings": [],
        "limitations": ["Rollup result is a committed-artifact-only dry-run preview and is not public truth."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["No source discovery runtime, live access, model/provider call, registry mutation, pack import/export, source-cache write, evidence write, review queue write, public-index write, or master-index write occurs."],
    }
    result["review_queue_seed_preview"] = build_h14_review_queue_seed_preview_from_rollup(result, source_cache, evidence, policy_bundle)
    result["source_os_rollup_health_summary"] = build_h14_source_os_rollup_health_summary(result, policy_bundle)
    return result


def _normalized_rollup_record(source_id: str, request_key: str, artifacts: list[Mapping[str, Any]], status: str) -> dict[str, Any]:
    cfg = H14_SOURCE_CONFIGS[source_id]
    artifact_refs = [str(item.get("artifact_ref") or "unknown") for item in artifacts]
    record = {
        "schema_version": "h14_source_discovery_rollup_normalized_record.v0",
        "normalized_record_id": f"h14.rollup.normalized.{source_id}.{_slug(request_key)}.v0",
        "source_id": source_id,
        "connector_family": cfg["connector_family"],
        "source_record_kind": cfg["primary"],
        "source_native_id": f"rollup-{source_id}-{request_key}",
        "metadata_summary": "H14 Source OS rollup dry-run over committed artifacts only.",
        "rollup_status": status,
        "artifact_refs": artifact_refs,
        "artifact_count": len(artifacts),
        "source_need_ref": f"h14-rollup-source-need:{source_id}",
        "source_candidate_ref": f"h14-rollup-source-candidate:{source_id}",
        "source_discovery_candidate_ref": f"h14-rollup-discovery-candidate:{source_id}",
        "source_pack_manifest_ref": f"h14-rollup-source-pack:{source_id}",
        "connector_pack_manifest_ref": f"h14-rollup-connector-pack:{source_id}",
        "coverage_manifest_ref": f"h14-rollup-coverage:{source_id}",
        "connector_scorecard_ref": f"h14-rollup-scorecard:{source_id}",
        "reliability_freshness_ref": f"h14-rollup-reliability-freshness:{source_id}",
        "dispute_revocation_ref": f"h14-rollup-dispute-revocation:{source_id}",
        "lineage_provenance_ref": f"h14-rollup-lineage-provenance:{source_id}",
        "pack_import_export_boundary_ref": f"h14-rollup-pack-boundary:{source_id}",
        "triggering_gap_ref": "committed_h0_h13_rollup_gap_preview",
        "triggering_search_need_ref": "not_evaluated_no_live_search",
        "triggering_source_gap_ref": "committed_scorecard_or_coverage_gap_preview",
        "query_family_ref": "source_os_rollup",
        "missing_source_family_candidate": "source_discovery_and_scorecards",
        "target_source_capability_candidate": "source_os_rollup_preview",
        "target_index_depth_candidate": "D0_source_known_preview_only",
        "workunit_preview_ref": f"h14-rollup-workunit-preview:{source_id}",
        "candidate_source_family": "source_discovery_and_scorecards",
        "candidate_connector_family": cfg["connector_family"],
        "candidate_locator_redacted_or_public": "redacted_or_public_policy_locator",
        "candidate_capabilities": ["source_os_rollup_preview", "coverage_scorecard_preview"],
        "candidate_trust_lane": cfg["trust_lane"],
        "candidate_reason": "Committed H0-H14 artifacts suggest reviewable Source OS rollup candidate.",
        "source_pack_kind": "source_intelligence_manifest_preview",
        "source_pack_scope": "committed_artifact_refs_only",
        "connector_pack_kind": "connector_policy_manifest_preview",
        "coverage_scope": "non_exhaustive_committed_artifact_preview",
        "coverage_depth": "D0_source_known_preview_only",
        "coverage_basis": "committed_artifact_rollup_preview",
        "scorecard_status": "candidate_only_review_input",
        "reliability_signal_candidates": ["committed_scorecard_status_preview"],
        "freshness_signal_candidates": ["committed_audit_timestamp_preview_not_currentness_truth"],
        "availability_signal_candidates": ["not_evaluated_no_live_access"],
        "error_signal_candidates": [],
        "dispute_kind": "not_evaluable",
        "source_status_candidate": "candidate_only_no_registry_change",
        "lineage_related_source_refs": artifact_refs[:8],
        "provenance_claim_candidates": ["committed_artifact_reference_only"],
        "exportability_label": "blocked_current_no_pack_export",
        "importability_label": "blocked_current_no_pack_import",
        "blocked_action_candidate": "pack_import_export_registry_mutation_live_access_blocked_current",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Missing rollup fields remain unknown and are not fabricated.", "No live source discovery, registry mutation, pack movement, write, or truth acceptance occurs."],
    }
    _raise_on_boundary_errors(record)
    return record


def _coerce_normalized(rollup_inputs: Mapping[str, Any] | list[Mapping[str, Any]]) -> Mapping[str, Any]:
    if isinstance(rollup_inputs, Mapping) and rollup_inputs.get("schema_version") == "h14_source_discovery_rollup_normalized_record.v0":
        return rollup_inputs
    if isinstance(rollup_inputs, Mapping) and "normalized_rollup_record" in rollup_inputs:
        nested = rollup_inputs.get("normalized_rollup_record")
        if isinstance(nested, Mapping):
            return nested
    return _normalized_rollup_record("source_need_registry", ROLLUP_REQUEST_KEYS["source_need_registry"], list(rollup_inputs) if isinstance(rollup_inputs, list) else [], "rollup_preview_only")


def _safe_artifact_path(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    repo = REPO_ROOT.resolve()
    try:
        rel = resolved.relative_to(repo).as_posix().lower()
    except ValueError as exc:
        raise ValueError("rollup input artifacts must be committed repo artifacts") from exc
    if any(rel == prefix.rstrip("/") or rel.startswith(prefix.rstrip("/") + "/") for prefix in ALLOWED_ARTIFACT_PREFIXES):
        return resolved
    raise ValueError("rollup input artifact path is outside the committed H0-H14 rollup allowlist")


def _source_policy(source_id: str, policy_bundle: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    for item in policy_bundle.get(key, {}).get("sources", []):
        if item.get("source_id") == source_id:
            return item
    return None


def _status_for_reasons(reasons: list[str]) -> str:
    if not reasons:
        return "rollup_dry_run_completed"
    text = " ".join(reasons).lower()
    if "kill switch" in text:
        return "blocked_by_kill_switch"
    if "live" in text:
        return "blocked_by_live_access_policy"
    if "network" in text:
        return "blocked_by_network_policy"
    if "model" in text:
        return "blocked_by_model_provider_policy"
    if "discovery" in text or "crawl" in text or "scrap" in text:
        return "blocked_by_discovery_runtime_policy"
    if "registry" in text:
        return "blocked_by_registry_mutation_policy"
    if "pack" in text:
        return "blocked_by_pack_import_export_policy"
    if "source_cache" in text or "evidence" in text or "review_queue" in text:
        return "blocked_by_source_cache_policy"
    if "index" in text:
        return "blocked_by_index_write_policy"
    if "approval" in text or "request key" in text or "approved" in text:
        return "blocked_by_missing_approval"
    return "blocked_by_policy"


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h14_rollup_truth_boundary_violations(record, {}) + detect_h14_rollup_product_boundary_violations(record, {}) + detect_h14_registry_or_pack_mutation_violations(record, {})
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden and item is True:
                errors.append(f"{prefix} boundary true claim: {key}")
            _collect_true_keys(item, forbidden, prefix, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_true_keys(item, forbidden, prefix, errors)


def _collect_secret_or_private_data(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "unknown", "blocked_current", "not_evaluated"):
                errors.append(f"{label} forbidden secret/account field: {key_text}")
            if PRIVATE_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}, "blocked_current", "preview_only_no_write"):
                errors.append(f"{label} forbidden private/network/artifact payload field: {key_text}")
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, str):
        if UNREDACTED_LOCATOR_RE.search(value):
            errors.append(f"{label} contains unrestricted local path or URL-like locator")


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in ROLLUP_TRUTH_FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in ROLLUP_PRODUCT_FORBIDDEN_TRUE_KEYS}


def _short_fingerprint(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def _slug(value: Any) -> str:
    text = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value or "unknown").lower()).strip("-")
    return text[:64] or "unknown"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
