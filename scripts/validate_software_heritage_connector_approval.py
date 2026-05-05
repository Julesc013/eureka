#!/usr/bin/env python3
"""Validate Software Heritage Connector Approval v0 examples."""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
from _p70_contract_common import (  # noqa: E402
    check_allowed,
    check_sensitive,
    load_json_object,
    print_report,
    require_false,
    require_fields,
    require_true,
)

EXAMPLES_ROOT = REPO_ROOT / "examples/connectors"
APPROVAL_FILE = "SOFTWARE_HERITAGE_CONNECTOR_APPROVAL.json"
MANIFEST_FILE = "SOFTWARE_HERITAGE_CONNECTOR_MANIFEST.json"

REQ = {
    "schema_version",
    "approval_record_id",
    "approval_record_kind",
    "status",
    "created_by_tool",
    "connector_ref",
    "connector_scope",
    "allowed_capabilities",
    "forbidden_capabilities",
    "swhid_origin_repository_policy",
    "source_code_content_risk_policy",
    "source_policy_review",
    "user_agent_and_contact_policy",
    "rate_limit_timeout_retry_circuit_breaker_policy",
    "cache_first_policy",
    "expected_source_cache_outputs",
    "expected_evidence_ledger_outputs",
    "query_intelligence_relationship",
    "public_search_boundary",
    "rights_access_and_risk_policy",
    "privacy_policy",
    "approval_checklist",
    "operator_checklist",
    "implementation_prerequisites",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
STAT = {"draft_example", "approval_required", "operator_required", "blocked_by_policy", "approved_future", "rejected_future", "superseded_future"}
ALLOWED = {
    "swhid_metadata_summary_future",
    "origin_metadata_summary_future",
    "visit_metadata_summary_future",
    "snapshot_metadata_summary_future",
    "release_metadata_summary_future",
    "revision_metadata_summary_future",
    "directory_metadata_summary_future",
    "content_identifier_metadata_summary_future",
    "archival_presence_observation_future",
    "historical_source_identity_observation_future",
}
FORBID = {
    "arbitrary_origin_fetch",
    "direct_public_query_fanout",
    "private_repository_access",
    "credentialed_repository_access",
    "token_required_access",
    "repository_clone",
    "source_code_content_fetch",
    "content_blob_fetch",
    "raw_file_fetch",
    "directory_content_fetch",
    "source_archive_download",
    "graph_crawl",
    "origin_bulk_crawl",
    "account_access",
    "upload",
    "install",
    "execute",
    "unbounded_crawl",
    "scraping",
    "bypass_access_restrictions",
    "raw_payload_dump",
    "malware_safety_decision",
    "rights_clearance_decision",
    "source_code_safety_decision",
    "source_completeness_decision",
}
SCOPE_ALLOWED = {
    "swhid_from_reviewed_source_record",
    "origin_url_from_reviewed_source_record",
    "repository_identity_from_source_pack_future",
    "reviewed_search_need_future",
    "bounded_swhid_metadata_query_future",
    "bounded_origin_metadata_query_future",
    "snapshot_metadata_summary_future",
    "release_metadata_summary_future",
    "revision_metadata_summary_future",
}
SCOPE_FORBID = {
    "arbitrary_public_query_origin_url",
    "private_repository",
    "credentialed_repository",
    "local_repository_path",
    "repository_clone",
    "source_code_content_fetch",
    "content_blob_fetch",
    "directory_content_fetch",
    "raw_file_fetch",
    "source_archive_download",
    "origin_crawl",
    "bulk_graph_traversal",
    "account_private_data",
    "executable_download",
}
CACHE_OUT = {
    "software_heritage_swhid_metadata_summary",
    "software_heritage_origin_metadata_summary",
    "software_heritage_visit_metadata_summary",
    "software_heritage_snapshot_metadata_summary",
    "software_heritage_release_metadata_summary",
    "software_heritage_revision_metadata_summary",
    "software_heritage_directory_metadata_summary",
    "software_heritage_archival_presence_summary",
}
EVID_OUT = {
    "software_identity_observation",
    "archival_presence_observation",
    "origin_metadata_observation",
    "release_metadata_observation",
    "revision_metadata_observation",
    "snapshot_metadata_observation",
    "SWHID_observation",
    "scoped_absence_observation",
}
APPROVAL_ITEMS = {
    "source_policy_review",
    "official_docs_review",
    "swhid_policy_review",
    "origin_url_policy_review",
    "repository_identity_policy_review",
    "source_code_content_risk_policy_review",
    "user_agent_contact_decision",
    "rate_limit_timeout_retry_policy",
    "circuit_breaker_policy",
    "cache_output_contract_review",
    "evidence_output_contract_review",
    "rights_access_risk_review",
    "privacy_review",
    "public_search_boundary_review",
    "token_policy_review",
    "operator_approval",
    "human_approval",
}
OPERATOR_ITEMS = {
    "configure_user_agent",
    "configure_contact_policy",
    "configure_timeout",
    "configure_rate_limit",
    "configure_retry_backoff",
    "configure_circuit_breaker",
    "configure_cache_destination",
    "configure_evidence_destination",
    "configure_swhid_filter",
    "configure_origin_url_filter",
    "configure_repository_identity_filter",
    "confirm_no_token_required_for_v0",
    "confirm_no_source_code_download_clone_or_content_fetch",
    "enable_connector_flag_future",
    "monitor_connector_health_future",
    "record_approval_evidence",
}
RUNTIME_FALSE = {
    "connector_runtime_implemented",
    "connector_approved_now",
    "live_source_called",
    "external_calls_performed",
    "software_heritage_api_called",
    "swhid_resolved_live",
    "origin_lookup_performed",
    "visit_lookup_performed",
    "snapshot_lookup_performed",
    "release_lookup_performed",
    "revision_lookup_performed",
    "directory_lookup_performed",
    "content_blob_lookup_performed",
    "repository_cloned",
    "source_code_downloaded",
    "source_archive_downloaded",
    "source_file_retrieved",
    "public_search_live_fanout_enabled",
    "downloads_enabled",
    "file_retrieval_enabled",
    "mirroring_enabled",
    "installs_enabled",
    "execution_enabled",
    "credentials_used",
    "software_heritage_token_used",
    "telemetry_exported",
}
MUTATION_FALSE = {"source_cache_mutated", "evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"}
QUERY_FALSE = {
    "query_observation_mutation_allowed_now",
    "result_cache_mutation_allowed_now",
    "miss_ledger_mutation_allowed_now",
    "search_need_mutation_allowed_now",
    "probe_queue_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
}
MANIFEST_FALSE = {
    "runtime_implemented",
    "live_enabled_by_default",
    "public_query_fanout_allowed",
    "downloads_allowed",
    "arbitrary_url_fetch_allowed",
    "repository_clone_allowed",
    "source_code_download_allowed",
    "source_archive_download_allowed",
    "content_blob_fetch_allowed",
    "origin_crawl_allowed",
    "token_required_now",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed_now",
}
BAD_SECRET = re.compile(r"\b(?:api[_-]?key|auth[_-]?token|software[_-]?heritage[_-]?token|swh[_-]?token|password|secret)\s*[:=]", re.IGNORECASE)
BAD_IDENTITY = re.compile(
    r"\b(?:private|credentialed|token-required)/(?:repository|origin|swhid|repo)\b|"
    r"\b(?:file|data|javascript):|https?://[^\s/]*@|archive\.softwareheritage\.org|softwareheritage\.org",
    re.IGNORECASE,
)


def validate_approval_path(path: Path, *, approval_root: Path | None = None, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = load_json_object(path, errors, str(path))
    if payload:
        validate_approval(payload, errors)
        check_sensitive(payload, errors, str(path))
        check_forbidden_strings(payload, errors, str(path))
    root = approval_root or path.parent
    manifest_path = root / MANIFEST_FILE
    if manifest_path.is_file():
        manifest = load_json_object(manifest_path, errors, str(manifest_path))
        if manifest:
            validate_manifest(manifest, errors)
            check_sensitive(manifest, errors, str(manifest_path))
            check_forbidden_strings(manifest, errors, str(manifest_path))
    elif strict:
        errors.append(f"{manifest_path} missing.")
    if (root / "CHECKSUMS.SHA256").exists():
        validate_checksums(root, [APPROVAL_FILE, MANIFEST_FILE, "README.md"], errors)
    elif strict:
        errors.append(f"{root}/CHECKSUMS.SHA256 missing.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "software_heritage_connector_approval_validator_v0",
        "approval": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "approval_record_id": payload.get("approval_record_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_approval(p: Mapping[str, Any], errors: list[str]) -> None:
    require_fields(p, REQ, errors, "software_heritage_connector_approval")
    if p.get("approval_record_kind") != "software_heritage_connector_approval":
        errors.append("approval_record_kind must be software_heritage_connector_approval.")
    check_allowed(p.get("status"), STAT, errors, "status")
    ref = sec(p, "connector_ref", errors)
    if ref.get("connector_id") != "software_heritage_connector":
        errors.append("connector_ref.connector_id must be software_heritage_connector.")
    if ref.get("source_family") != "software_heritage":
        errors.append("connector_ref.source_family must be software_heritage.")
    check_allowed(ref.get("source_status"), {"approval_required", "future", "disabled", "unknown"}, errors, "connector_ref.source_status")

    scope = sec(p, "connector_scope", errors)
    if scope.get("scope_kind") != "software_identity_and_archive_metadata_only":
        errors.append("connector_scope.scope_kind must be software_identity_and_archive_metadata_only.")
    if scope.get("default_mode") != "disabled_until_approval":
        errors.append("connector_scope.default_mode must be disabled_until_approval.")
    require_list(scope.get("allowed_target_types"), SCOPE_ALLOWED, "connector_scope.allowed_target_types", errors)
    require_list(scope.get("prohibited_target_types"), SCOPE_FORBID, "connector_scope.prohibited_target_types", errors)

    validate_caps(p.get("allowed_capabilities"), errors)
    validate_forbidden(p.get("forbidden_capabilities"), errors)
    validate_identity_policy(sec(p, "swhid_origin_repository_policy", errors), errors)
    validate_source_code_policy(sec(p, "source_code_content_risk_policy", errors), errors)

    source = sec(p, "source_policy_review", errors)
    require_true(source, {"official_policy_review_required", "API_terms_review_required", "automated_access_policy_review_required", "rate_limit_policy_review_required", "retry_after_or_abuse_limit_policy_review_required", "cache_policy_review_required", "rights_access_policy_review_required"}, errors, "source_policy_review")
    if source.get("review_status") != "review_required":
        errors.append("source_policy_review.review_status must be review_required in P76 examples.")
    refs = source.get("authoritative_docs_refs")
    if not isinstance(refs, list) or any(isinstance(r, str) and r.startswith(("http://", "https://")) for r in refs):
        errors.append("source_policy_review.authoritative_docs_refs must be local refs only.")

    ua = sec(p, "user_agent_and_contact_policy", errors)
    require_true(ua, {"descriptive_user_agent_required_future", "contact_policy_required_future", "fake_contact_forbidden", "operator_decision_required"}, errors, "user_agent_and_contact_policy")
    require_false(ua, {"contact_value_configured_now", "user_agent_value_configured_now"}, errors, "user_agent_and_contact_policy")
    if ua.get("contact_value") is not None or ua.get("user_agent_value") is not None:
        errors.append("User-Agent/contact values must remain null until approved.")

    rate = sec(p, "rate_limit_timeout_retry_circuit_breaker_policy", errors)
    require_true(rate, {"rate_limit_required_future", "timeout_required_future", "retry_backoff_required_future", "retry_after_or_abuse_limit_respect_required_future", "circuit_breaker_required_future", "cache_required_before_public_use", "operator_review_required"}, errors, "rate_limit_timeout_retry_circuit_breaker_policy")
    require_false(rate, {"policy_values_configured_now"}, errors, "rate_limit_timeout_retry_circuit_breaker_policy")

    cache = sec(p, "cache_first_policy", errors)
    require_true(cache, {"source_cache_required_before_public_use", "evidence_ledger_required_for_claims", "public_search_reads_cache_not_live_source_future", "public_query_fanout_forbidden", "cache_invalidation_required_future", "freshness_policy_required_future", "no_source_code_payload_cache", "no_content_blob_cache", "no_repository_clone_cache", "no_source_archive_cache"}, errors, "cache_first_policy")

    validate_outputs(p.get("expected_source_cache_outputs"), CACHE_OUT, {"output_runtime_implemented", "raw_payload_allowed", "source_code_payload_allowed", "content_blob_allowed", "repository_clone_allowed", "source_archive_allowed"}, {"public_safe_metadata_only", "requires_validation"}, "expected_source_cache_outputs", errors)
    validate_outputs(p.get("expected_evidence_ledger_outputs"), EVID_OUT, {"output_runtime_implemented", "accepted_as_truth", "global_absence_claimed", "rights_clearance_claimed", "malware_safety_claimed", "source_code_safety_claimed", "source_completeness_claimed"}, {"requires_review", "requires_promotion_policy"}, "expected_evidence_ledger_outputs", errors)

    q = sec(p, "query_intelligence_relationship", errors)
    require_true(q, {"demand_dashboard_can_prioritize_future", "search_need_can_reference_future", "probe_queue_can_request_future", "candidate_index_can_receive_future_after_review", "known_absence_can_reference_future"}, errors, "query_intelligence_relationship")
    require_false(q, QUERY_FALSE, errors, "query_intelligence_relationship")

    public = sec(p, "public_search_boundary", errors)
    require_false(public, {"public_search_live_fanout_allowed", "public_search_may_read_live_connector_now", "public_search_may_accept_arbitrary_origin_url_param", "public_search_may_accept_arbitrary_swhid_param", "public_search_may_fetch_source_content", "static_site_claim_allowed_now", "hosted_backend_claim_allowed_now"}, errors, "public_search_boundary")

    rights = sec(p, "rights_access_and_risk_policy", errors)
    require_false(rights, {"rights_clearance_claimed", "malware_safety_claimed", "source_code_safety_claimed", "source_completeness_claimed", "downloads_enabled", "file_retrieval_enabled", "source_code_download_enabled", "content_blob_fetch_enabled", "repository_clone_enabled", "source_archive_download_enabled", "installs_enabled", "execution_enabled"}, errors, "rights_access_and_risk_policy")
    if rights.get("risk_review_required") is not True:
        errors.append("rights_access_and_risk_policy.risk_review_required must be true.")
    access = rights.get("access_policy")
    if not isinstance(access, list) or not {"metadata_only", "no_source_code_download", "no_content_blob_fetch", "no_repository_clone", "no_source_archive_download", "no_private_repositories"}.issubset(set(access)):
        errors.append("rights_access_and_risk_policy.access_policy missing required restrictions.")

    privacy = sec(p, "privacy_policy", errors)
    require_false(privacy, {"private_data_allowed", "credentials_required_now", "account_access_allowed", "contains_private_path", "contains_secret", "contains_private_repository", "contains_private_origin_url", "contains_private_url"}, errors, "privacy_policy")
    if privacy.get("privacy_classification") not in {"public_safe_metadata_policy", "swhid_review_required", "origin_url_review_required", "repository_identity_review_required", "review_required", "unknown"}:
        errors.append("privacy_policy.privacy_classification invalid.")
    if privacy.get("publishable") is not True:
        errors.append("privacy_policy.publishable must be true for example.")

    checklist(p.get("approval_checklist"), APPROVAL_ITEMS, "required", "approval_checklist", errors)
    checklist(p.get("operator_checklist"), OPERATOR_ITEMS, "required_future", "operator_checklist", errors)
    require_false(sec(p, "no_runtime_guarantees", errors), RUNTIME_FALSE, errors, "no_runtime_guarantees")
    require_false(sec(p, "no_mutation_guarantees", errors), MUTATION_FALSE, errors, "no_mutation_guarantees")
    for key in ("arbitrary_origin_fetch_allowed", "arbitrary_swhid_fetch_allowed", "repository_clone_allowed", "source_code_download_allowed", "source_archive_download_allowed", "content_blob_fetch_allowed", "origin_crawl_allowed", "token_required_now", "rights_clearance_claimed", "malware_safety_claimed", "source_code_safety_claimed", "source_completeness_claimed"):
        if any_key_true(p, key):
            errors.append(f"{key} must not be true anywhere in the approval record.")


def validate_manifest(m: Mapping[str, Any], errors: list[str]) -> None:
    require_fields(m, {"schema_version", "connector_id", "connector_kind", "status", "source_family", "supported_capabilities", "disabled_capabilities", "default_policy", "source_sync_worker_relationship", "source_cache_relationship", "evidence_ledger_relationship", "safety_defaults", "no_runtime_guarantees", "notes"}, errors, "software_heritage_connector_manifest")
    for k, v in {"connector_id": "software_heritage_connector", "connector_kind": "software_heritage_connector", "source_family": "software_heritage"}.items():
        if m.get(k) != v:
            errors.append(f"manifest.{k} must be {v}.")
    check_allowed(m.get("status"), {"draft_example", "approval_required", "runtime_future", "disabled"}, errors, "manifest.status")
    require_list(m.get("supported_capabilities"), ALLOWED, "manifest.supported_capabilities", errors)
    require_list(m.get("disabled_capabilities"), FORBID, "manifest.disabled_capabilities", errors)
    d = sec(m, "default_policy", errors)
    require_true(d, {"software_identity_metadata_only_scope", "swhid_review_required", "origin_url_review_required", "repository_identity_review_required", "source_code_content_risk_policy_required", "token_policy_review_required", "no_token_required_now", "no_source_code_download_clone_or_content_fetch", "approval_required_for_live_network_access", "source_policy_review_required", "cache_first_required", "evidence_attribution_required"}, errors, "manifest.default_policy")
    if sec(m, "source_sync_worker_relationship", errors).get("source_sync_worker_runtime_implemented_now") is not False:
        errors.append("manifest.source_sync_worker_runtime_implemented_now must be false.")
    if sec(m, "source_cache_relationship", errors).get("source_cache_mutation_allowed_now") is not False:
        errors.append("manifest.source_cache_mutation_allowed_now must be false.")
    if sec(m, "evidence_ledger_relationship", errors).get("evidence_ledger_mutation_allowed_now") is not False:
        errors.append("manifest.evidence_ledger_mutation_allowed_now must be false.")
    safety = sec(m, "safety_defaults", errors)
    require_true(safety, {"no_downloads", "no_file_retrieval", "no_mirroring", "no_arbitrary_origin_fetch", "no_arbitrary_swhid_fetch", "no_repository_clone", "no_source_code_download", "no_source_archive_download", "no_content_blob_fetch", "no_directory_content_fetch", "no_origin_crawl", "no_public_query_fanout", "no_credentials", "no_software_heritage_token", "no_telemetry"}, errors, "manifest.safety_defaults")
    require_false(sec(m, "no_runtime_guarantees", errors), MANIFEST_FALSE, errors, "manifest.no_runtime_guarantees")


def validate_caps(v: Any, errors: list[str]) -> None:
    if not isinstance(v, list):
        errors.append("allowed_capabilities must be list.")
        return
    seen = set()
    for i, item in enumerate(v):
        if not isinstance(item, Mapping):
            errors.append(f"allowed_capabilities[{i}] must be object.")
            continue
        seen.add(item.get("capability"))
        check_allowed(item.get("capability"), ALLOWED, errors, f"allowed_capabilities[{i}].capability")
        check_allowed(item.get("status"), {"future_after_approval", "disabled_now"}, errors, f"allowed_capabilities[{i}].status")
        check_allowed(item.get("output_destination"), {"source_cache_future", "evidence_ledger_future", "candidate_index_future_after_review"}, errors, f"allowed_capabilities[{i}].output_destination")
        require_true(item, {"requires_cache", "requires_evidence_attribution", "requires_rate_limit", "requires_timeout", "requires_circuit_breaker", "requires_identity_review"}, errors, f"allowed_capabilities[{i}]")
    if ALLOWED - seen:
        errors.append("allowed_capabilities missing: " + ", ".join(sorted(ALLOWED - seen)))


def validate_forbidden(v: Any, errors: list[str]) -> None:
    if not isinstance(v, list):
        errors.append("forbidden_capabilities must be list.")
        return
    seen = set()
    for i, item in enumerate(v):
        if not isinstance(item, Mapping):
            errors.append(f"forbidden_capabilities[{i}] must be object.")
            continue
        seen.add(item.get("capability"))
        check_allowed(item.get("capability"), FORBID, errors, f"forbidden_capabilities[{i}].capability")
        if item.get("forbidden_now") is not True:
            errors.append(f"forbidden_capabilities[{i}].forbidden_now must be true.")
    if FORBID - seen:
        errors.append("forbidden_capabilities missing: " + ", ".join(sorted(FORBID - seen)))


def validate_identity_policy(v: Mapping[str, Any], errors: list[str]) -> None:
    require_true(v, {"swhid_review_required", "origin_url_review_required", "repository_identity_review_required", "normalized_origin_publication_allowed_after_review", "swhid_publication_allowed_after_review", "origin_hashing_allowed_future", "origin_redaction_required_for_sensitive_inputs"}, errors, "swhid_origin_repository_policy")
    require_false(v, {"arbitrary_public_query_origin_allowed", "private_repository_allowed", "credentialed_repository_allowed", "token_required_repository_allowed", "local_repository_path_allowed", "raw_origin_url_publication_allowed"}, errors, "swhid_origin_repository_policy")
    require_list(v.get("allowed_identity_sources"), {"source_record", "source_pack_future", "reviewed_search_need_future", "manual_observation_future", "fixture_example"}, "swhid_origin_repository_policy.allowed_identity_sources", errors)
    require_list(v.get("prohibited_identity_sources"), {"raw_public_query_parameter", "user_private_repository", "credentialed_repository", "local_path", "uploaded_file"}, "swhid_origin_repository_policy.prohibited_identity_sources", errors)
    origin = v.get("example_origin_url")
    if isinstance(origin, str) and not origin.startswith("https://example.invalid/"):
        errors.append("swhid_origin_repository_policy.example_origin_url must use example.invalid if present.")


def validate_source_code_policy(v: Mapping[str, Any], errors: list[str]) -> None:
    require_true(v, {"metadata_only_scope", "code_snippet_publication_requires_review"}, errors, "source_code_content_risk_policy")
    require_false(v, {"source_code_content_fetch_allowed", "content_blob_fetch_allowed", "raw_file_fetch_allowed", "directory_content_fetch_allowed", "repository_clone_allowed", "source_archive_download_allowed", "source_code_execution_allowed", "source_code_safety_claim_allowed", "source_completeness_claim_allowed", "source_license_or_rights_clearance_claim_allowed"}, errors, "source_code_content_risk_policy")


def validate_outputs(v: Any, kinds: set[str], false: set[str], true: set[str], label: str, errors: list[str]) -> None:
    if not isinstance(v, list):
        errors.append(f"{label} must be list.")
        return
    seen = set()
    for i, item in enumerate(v):
        if not isinstance(item, Mapping):
            errors.append(f"{label}[{i}] must be object.")
            continue
        seen.add(item.get("output_kind"))
        check_allowed(item.get("output_kind"), kinds, errors, f"{label}[{i}].output_kind")
        require_false(item, false, errors, f"{label}[{i}]")
        require_true(item, true, errors, f"{label}[{i}]")
    if kinds - seen:
        errors.append(f"{label} missing: " + ", ".join(sorted(kinds - seen)))


def checklist(v: Any, items: set[str], flag: str, label: str, errors: list[str]) -> None:
    if not isinstance(v, list):
        errors.append(f"{label} must be list.")
        return
    seen = set()
    for i, item in enumerate(v):
        if not isinstance(item, Mapping):
            errors.append(f"{label}[{i}] must be object.")
            continue
        seen.add(item.get("item"))
        check_allowed(item.get("item"), items, errors, f"{label}[{i}].item")
        if item.get(flag) is not True:
            errors.append(f"{label}[{i}].{flag} must be true.")
        if item.get("status") != "pending":
            errors.append(f"{label}[{i}].status must remain pending.")
    if items - seen:
        errors.append(f"{label} missing: " + ", ".join(sorted(items - seen)))


def validate_all_examples(strict: bool = False) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for root in sorted(p for p in EXAMPLES_ROOT.iterdir() if p.is_dir() and (p / APPROVAL_FILE).is_file()):
        result = validate_approval_path(root / APPROVAL_FILE, approval_root=root, strict=True or strict)
        result["approval_root"] = str(root.relative_to(REPO_ROOT))
        results.append(result)
        errors.extend(result["errors"])
    if not results:
        errors.append("no Software Heritage connector approval examples found.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "software_heritage_connector_approval_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": [],
    }


def sec(p: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    v = p.get(key)
    if not isinstance(v, Mapping):
        errors.append(f"{key} must be object.")
        return {}
    return v


def require_list(v: Any, expected: set[str], field: str, errors: list[str]) -> None:
    if not isinstance(v, list):
        errors.append(f"{field} must be list.")
        return
    observed = {x for x in v if isinstance(x, str)}
    if expected - observed:
        errors.append(f"{field} missing: " + ", ".join(sorted(expected - observed)))


def strings(v: Any) -> Iterable[str]:
    if isinstance(v, str):
        yield v
    elif isinstance(v, Mapping):
        for nested in v.values():
            yield from strings(nested)
    elif isinstance(v, Sequence) and not isinstance(v, (bytes, bytearray)):
        for nested in v:
            yield from strings(nested)


def check_forbidden_strings(payload: Any, errors: list[str], prefix: str) -> None:
    text = "\n".join(strings(payload))
    if BAD_SECRET.search(text):
        errors.append(f"{prefix} contains prohibited secret/token/API key marker.")
    if BAD_IDENTITY.search(text):
        errors.append(f"{prefix} contains prohibited private, credentialed, local, Software Heritage host, or API identity reference.")


def any_key_true(value: Any, key: str) -> bool:
    if isinstance(value, Mapping):
        return value.get(key) is True or any(any_key_true(v, key) for v in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(any_key_true(v, key) for v in value)
    return False


def validate_checksums(root: Path, names: Iterable[str], errors: list[str]) -> None:
    path = root / "CHECKSUMS.SHA256"
    if not path.is_file():
        errors.append(f"{path} missing.")
        return
    expected = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2:
            expected[parts[1]] = parts[0]
    for name in names:
        p = root / name
        if not p.is_file():
            errors.append(f"{p} missing.")
            continue
        if expected.get(name) != hashlib.sha256(p.read_bytes()).hexdigest():
            errors.append(f"{name} checksum mismatch in {root}.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approval")
    parser.add_argument("--approval-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    if args.all_examples:
        report = validate_all_examples(strict=args.strict)
    else:
        path = Path(args.approval) if args.approval else (Path(args.approval_root) / APPROVAL_FILE if args.approval_root else None)
        if path is None:
            parser.error("provide --approval, --approval-root, or --all-examples")
        report = validate_approval_path(path, approval_root=Path(args.approval_root) if args.approval_root else None, strict=args.strict)
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
