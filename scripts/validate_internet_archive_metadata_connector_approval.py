#!/usr/bin/env python3
"""Validate Internet Archive Metadata Connector Approval v0 examples."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
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
APPROVAL_FILE = "INTERNET_ARCHIVE_METADATA_CONNECTOR_APPROVAL.json"
MANIFEST_FILE = "INTERNET_ARCHIVE_METADATA_CONNECTOR_MANIFEST.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "approval_record_id",
    "approval_record_kind",
    "status",
    "created_by_tool",
    "connector_ref",
    "connector_scope",
    "allowed_capabilities",
    "forbidden_capabilities",
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
STATUSES = {"draft_example", "approval_required", "operator_required", "blocked_by_policy", "approved_future", "rejected_future", "superseded_future"}
SOURCE_STATUSES = {"approval_required", "future", "disabled", "unknown"}
SCOPE_KINDS = {"metadata_only"}
ALLOWED_TARGET_TYPES = {"item_identifier", "bounded_metadata_query_future", "collection_metadata_future", "file_listing_metadata_future"}
PROHIBITED_TARGET_TYPES = {"arbitrary_url", "item_file_download", "bulk_crawl", "full_text_scrape", "account_private_data", "access_restricted_download", "executable_download"}
ALLOWED_CAPABILITIES = {"item_metadata_lookup_future", "bounded_item_search_metadata_future", "file_listing_metadata_future", "collection_metadata_summary_future", "availability_metadata_future"}
ALLOWED_CAPABILITY_STATUSES = {"future_after_approval", "disabled_now"}
OUTPUT_DESTINATIONS = {"source_cache_future", "evidence_ledger_future", "candidate_index_future_after_review"}
FORBIDDEN_CAPABILITIES = {
    "file_download",
    "mirroring",
    "item_bulk_download",
    "account_access",
    "upload",
    "install",
    "execute",
    "arbitrary_url_fetch",
    "unbounded_crawl",
    "scraping",
    "bypass_access_restrictions",
    "raw_payload_dump",
    "malware_safety_decision",
    "rights_clearance_decision",
}
SOURCE_CACHE_OUTPUTS = {
    "internet_archive_item_metadata_summary",
    "internet_archive_file_listing_metadata_summary",
    "internet_archive_collection_metadata_summary",
    "internet_archive_availability_summary",
}
EVIDENCE_OUTPUTS = {
    "source_metadata_observation",
    "availability_observation",
    "file_listing_observation",
    "release_or_item_metadata_observation",
    "scoped_absence_observation",
}
APPROVAL_ITEMS = {
    "source_policy_review",
    "official_docs_review",
    "user_agent_contact_decision",
    "rate_limit_timeout_retry_policy",
    "circuit_breaker_policy",
    "cache_output_contract_review",
    "evidence_output_contract_review",
    "rights_access_risk_review",
    "privacy_review",
    "public_search_boundary_review",
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
    "enable_connector_flag_future",
    "monitor_connector_health_future",
    "record_approval_evidence",
}
RUNTIME_FALSE = {
    "connector_runtime_implemented",
    "connector_approved_now",
    "live_source_called",
    "external_calls_performed",
    "public_search_live_fanout_enabled",
    "downloads_enabled",
    "file_retrieval_enabled",
    "mirroring_enabled",
    "installs_enabled",
    "execution_enabled",
    "credentials_used",
    "telemetry_exported",
}
MUTATION_FALSE = {
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
}
QUERY_MUTATION_FALSE = {
    "query_observation_mutation_allowed_now",
    "result_cache_mutation_allowed_now",
    "miss_ledger_mutation_allowed_now",
    "search_need_mutation_allowed_now",
    "probe_queue_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
}
RIGHTS_FALSE = {"rights_clearance_claimed", "malware_safety_claimed", "downloads_enabled", "file_retrieval_enabled", "installs_enabled", "execution_enabled"}
PRIVACY_FALSE = {"private_data_allowed", "credentials_required_now", "account_access_allowed", "contains_private_path", "contains_secret", "contains_private_url"}
MANIFEST_RUNTIME_FALSE = {
    "runtime_implemented",
    "live_enabled_by_default",
    "public_query_fanout_allowed",
    "downloads_allowed",
    "arbitrary_url_fetch_allowed",
    "source_cache_mutation_allowed_now",
    "evidence_ledger_mutation_allowed_now",
    "candidate_index_mutation_allowed_now",
    "master_index_mutation_allowed_now",
}


def validate_approval_path(path: Path, *, approval_root: Path | None = None, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = load_json_object(path, errors, str(path))
    if payload:
        validate_approval(payload, errors, warnings)
        check_sensitive(payload, errors, str(path))
    root = approval_root or path.parent
    manifest_path = root / MANIFEST_FILE
    if manifest_path.is_file():
        manifest = load_json_object(manifest_path, errors, str(manifest_path))
        if manifest:
            validate_manifest(manifest, errors, warnings)
            check_sensitive(manifest, errors, str(manifest_path))
    elif strict:
        errors.append(f"{manifest_path} missing.")
    if (root / "CHECKSUMS.SHA256").exists():
        validate_checksums(root, [APPROVAL_FILE, MANIFEST_FILE, "README.md"], errors)
    elif strict:
        errors.append(f"{root}/CHECKSUMS.SHA256 missing.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "internet_archive_metadata_connector_approval_validator_v0",
        "approval": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "approval_record_id": payload.get("approval_record_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_approval(payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    require_fields(payload, REQUIRED_TOP_LEVEL, errors, "internet_archive_metadata_connector_approval")
    if payload.get("approval_record_kind") != "internet_archive_metadata_connector_approval":
        errors.append("approval_record_kind must be internet_archive_metadata_connector_approval.")
    check_allowed(payload.get("status"), STATUSES, errors, "status")

    connector_ref = _section(payload, "connector_ref", errors)
    if connector_ref.get("connector_id") != "internet_archive_metadata_connector":
        errors.append("connector_ref.connector_id must be internet_archive_metadata_connector.")
    if connector_ref.get("source_family") != "internet_archive":
        errors.append("connector_ref.source_family must be internet_archive.")
    check_allowed(connector_ref.get("source_status"), SOURCE_STATUSES, errors, "connector_ref.source_status")

    scope = _section(payload, "connector_scope", errors)
    check_allowed(scope.get("scope_kind"), SCOPE_KINDS, errors, "connector_scope.scope_kind")
    if scope.get("default_mode") != "disabled_until_approval":
        errors.append("connector_scope.default_mode must be disabled_until_approval.")
    _require_set_in_list(scope.get("allowed_target_types"), ALLOWED_TARGET_TYPES, "connector_scope.allowed_target_types", errors)
    _require_set_in_list(scope.get("prohibited_target_types"), PROHIBITED_TARGET_TYPES, "connector_scope.prohibited_target_types", errors)

    _validate_allowed_capabilities(payload.get("allowed_capabilities"), errors)
    _validate_forbidden_capabilities(payload.get("forbidden_capabilities"), errors)
    _validate_source_policy_review(_section(payload, "source_policy_review", errors), errors)
    _validate_user_agent_policy(_section(payload, "user_agent_and_contact_policy", errors), errors)
    _validate_rate_policy(_section(payload, "rate_limit_timeout_retry_circuit_breaker_policy", errors), errors)
    _validate_cache_first(_section(payload, "cache_first_policy", errors), errors)
    _validate_source_cache_outputs(payload.get("expected_source_cache_outputs"), errors)
    _validate_evidence_outputs(payload.get("expected_evidence_ledger_outputs"), errors)

    query_rel = _section(payload, "query_intelligence_relationship", errors)
    require_true(query_rel, {"demand_dashboard_can_prioritize_future", "search_need_can_reference_future", "probe_queue_can_request_future", "candidate_index_can_receive_future_after_review"}, errors, "query_intelligence_relationship")
    require_false(query_rel, QUERY_MUTATION_FALSE, errors, "query_intelligence_relationship")

    public = _section(payload, "public_search_boundary", errors)
    if public.get("public_search_live_fanout_allowed") is not False:
        errors.append("public_search_boundary.public_search_live_fanout_allowed must be false.")
    if public.get("public_search_may_read_live_connector_now") is not False:
        errors.append("public_search_boundary.public_search_may_read_live_connector_now must be false.")
    if public.get("static_site_claim_allowed_now") is not False:
        errors.append("public_search_boundary.static_site_claim_allowed_now must be false.")
    if public.get("hosted_backend_claim_allowed_now") is not False:
        errors.append("public_search_boundary.hosted_backend_claim_allowed_now must be false.")

    rights = _section(payload, "rights_access_and_risk_policy", errors)
    if rights.get("rights_classification") not in {"source_terms_apply", "review_required", "unknown"}:
        errors.append("rights_access_and_risk_policy.rights_classification has invalid value.")
    require_false(rights, RIGHTS_FALSE, errors, "rights_access_and_risk_policy")
    if rights.get("risk_review_required") is not True:
        errors.append("rights_access_and_risk_policy.risk_review_required must be true.")
    access_policy = rights.get("access_policy")
    if not isinstance(access_policy, list) or "metadata_only" not in access_policy or "no_downloads" not in access_policy:
        errors.append("rights_access_and_risk_policy.access_policy must include metadata_only and no_downloads.")

    privacy = _section(payload, "privacy_policy", errors)
    if privacy.get("privacy_classification") not in {"public_safe_metadata_policy", "review_required", "unknown"}:
        errors.append("privacy_policy.privacy_classification has invalid value.")
    require_false(privacy, PRIVACY_FALSE, errors, "privacy_policy")
    if privacy.get("publishable") is not True:
        errors.append("privacy_policy.publishable must be true for the public-safe example.")

    _validate_approval_checklist(payload.get("approval_checklist"), errors)
    _validate_operator_checklist(payload.get("operator_checklist"), errors)
    require_false(_section(payload, "no_runtime_guarantees", errors), RUNTIME_FALSE, errors, "no_runtime_guarantees")
    require_false(_section(payload, "no_mutation_guarantees", errors), MUTATION_FALSE, errors, "no_mutation_guarantees")


def validate_manifest(manifest: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    require_fields(
        manifest,
        {
            "schema_version",
            "connector_id",
            "connector_kind",
            "status",
            "source_family",
            "supported_capabilities",
            "disabled_capabilities",
            "default_policy",
            "source_sync_worker_relationship",
            "source_cache_relationship",
            "evidence_ledger_relationship",
            "safety_defaults",
            "no_runtime_guarantees",
            "notes",
        },
        errors,
        "internet_archive_metadata_connector_manifest",
    )
    if manifest.get("connector_id") != "internet_archive_metadata_connector":
        errors.append("manifest.connector_id must be internet_archive_metadata_connector.")
    if manifest.get("connector_kind") != "internet_archive_metadata_connector":
        errors.append("manifest.connector_kind must be internet_archive_metadata_connector.")
    if manifest.get("source_family") != "internet_archive":
        errors.append("manifest.source_family must be internet_archive.")
    check_allowed(manifest.get("status"), {"draft_example", "approval_required", "runtime_future", "disabled"}, errors, "manifest.status")
    _require_set_in_list(manifest.get("supported_capabilities"), ALLOWED_CAPABILITIES, "manifest.supported_capabilities", errors)
    _require_set_in_list(manifest.get("disabled_capabilities"), FORBIDDEN_CAPABILITIES, "manifest.disabled_capabilities", errors)
    defaults = _section(manifest, "default_policy", errors)
    require_true(defaults, {"metadata_only_scope", "approval_required_for_live_network_access", "source_policy_review_required", "cache_first_required", "evidence_attribution_required"}, errors, "manifest.default_policy")
    source_sync = _section(manifest, "source_sync_worker_relationship", errors)
    if source_sync.get("source_sync_worker_runtime_implemented_now") is not False:
        errors.append("manifest.source_sync_worker_relationship.source_sync_worker_runtime_implemented_now must be false.")
    source_cache = _section(manifest, "source_cache_relationship", errors)
    if source_cache.get("source_cache_runtime_implemented_now") is not False or source_cache.get("source_cache_mutation_allowed_now") is not False:
        errors.append("manifest.source_cache_relationship must keep runtime and mutation false.")
    evidence = _section(manifest, "evidence_ledger_relationship", errors)
    if evidence.get("evidence_ledger_runtime_implemented_now") is not False or evidence.get("evidence_ledger_mutation_allowed_now") is not False:
        errors.append("manifest.evidence_ledger_relationship must keep runtime and mutation false.")
    safety = _section(manifest, "safety_defaults", errors)
    require_true(safety, {"no_downloads", "no_file_retrieval", "no_mirroring", "no_arbitrary_url_fetch", "no_public_query_fanout", "no_credentials", "no_telemetry"}, errors, "manifest.safety_defaults")
    require_false(_section(manifest, "no_runtime_guarantees", errors), MANIFEST_RUNTIME_FALSE, errors, "manifest.no_runtime_guarantees")


def validate_all_examples(strict: bool = False) -> dict[str, Any]:
    results = []
    errors: list[str] = []
    for root in sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir() and (path / APPROVAL_FILE).is_file()):
        result = validate_approval_path(root / APPROVAL_FILE, approval_root=root, strict=True or strict)
        result["approval_root"] = str(root.relative_to(REPO_ROOT))
        results.append(result)
        errors.extend(result["errors"])
    if not results:
        errors.append("no Internet Archive connector approval examples found.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "internet_archive_metadata_connector_approval_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": [],
    }


def _validate_allowed_capabilities(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("allowed_capabilities must be a non-empty list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"allowed_capabilities[{index}] must be an object.")
            continue
        capability = item.get("capability")
        seen.add(capability)
        check_allowed(capability, ALLOWED_CAPABILITIES, errors, f"allowed_capabilities[{index}].capability")
        check_allowed(item.get("status"), ALLOWED_CAPABILITY_STATUSES, errors, f"allowed_capabilities[{index}].status")
        check_allowed(item.get("output_destination"), OUTPUT_DESTINATIONS, errors, f"allowed_capabilities[{index}].output_destination")
        require_true(item, {"requires_cache", "requires_evidence_attribution", "requires_rate_limit", "requires_timeout", "requires_circuit_breaker"}, errors, f"allowed_capabilities[{index}]")
    missing = ALLOWED_CAPABILITIES - seen
    if missing:
        errors.append(f"allowed_capabilities missing: {', '.join(sorted(missing))}")


def _validate_forbidden_capabilities(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("forbidden_capabilities must be a list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"forbidden_capabilities[{index}] must be an object.")
            continue
        capability = item.get("capability")
        seen.add(capability)
        check_allowed(capability, FORBIDDEN_CAPABILITIES, errors, f"forbidden_capabilities[{index}].capability")
        if item.get("forbidden_now") is not True:
            errors.append(f"forbidden_capabilities[{index}].forbidden_now must be true.")
    missing = FORBIDDEN_CAPABILITIES - seen
    if missing:
        errors.append(f"forbidden_capabilities missing: {', '.join(sorted(missing))}")


def _validate_source_policy_review(value: Mapping[str, Any], errors: list[str]) -> None:
    require_true(
        value,
        {
            "official_policy_review_required",
            "source_terms_review_required",
            "robots_or_source_policy_review_required",
            "automated_access_policy_review_required",
            "rate_limit_policy_review_required",
            "retry_after_policy_review_required",
            "cache_policy_review_required",
            "rights_access_policy_review_required",
        },
        errors,
        "source_policy_review",
    )
    if value.get("review_status") not in {"not_reviewed", "review_required", "reviewed_future"}:
        errors.append("source_policy_review.review_status has invalid value.")
    if value.get("review_status") == "reviewed_future":
        errors.append("source_policy_review.review_status must not claim reviewed_future in P71 examples.")
    refs = value.get("authoritative_docs_refs")
    if not isinstance(refs, list):
        errors.append("source_policy_review.authoritative_docs_refs must be a list.")
    elif any(isinstance(ref, str) and ref.startswith(("http://", "https://")) for ref in refs):
        errors.append("source_policy_review.authoritative_docs_refs must not include external URLs in P71 examples.")


def _validate_user_agent_policy(value: Mapping[str, Any], errors: list[str]) -> None:
    require_true(value, {"descriptive_user_agent_required_future", "contact_policy_required_future", "fake_contact_forbidden", "operator_decision_required"}, errors, "user_agent_and_contact_policy")
    require_false(value, {"contact_value_configured_now", "user_agent_value_configured_now"}, errors, "user_agent_and_contact_policy")
    if value.get("contact_value") is not None:
        errors.append("user_agent_and_contact_policy.contact_value must be null until approved.")
    if value.get("user_agent_value") is not None:
        errors.append("user_agent_and_contact_policy.user_agent_value must be null until approved.")


def _validate_rate_policy(value: Mapping[str, Any], errors: list[str]) -> None:
    require_true(value, {"rate_limit_required_future", "timeout_required_future", "retry_backoff_required_future", "retry_after_respect_required_future", "circuit_breaker_required_future", "cache_required_before_public_use", "operator_review_required"}, errors, "rate_limit_timeout_retry_circuit_breaker_policy")
    require_false(value, {"policy_values_configured_now"}, errors, "rate_limit_timeout_retry_circuit_breaker_policy")


def _validate_cache_first(value: Mapping[str, Any], errors: list[str]) -> None:
    require_true(value, {"source_cache_required_before_public_use", "evidence_ledger_required_for_claims", "public_search_reads_cache_not_live_source_future", "public_query_fanout_forbidden", "cache_invalidation_required_future", "freshness_policy_required_future"}, errors, "cache_first_policy")


def _validate_source_cache_outputs(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("expected_source_cache_outputs must be a list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"expected_source_cache_outputs[{index}] must be an object.")
            continue
        seen.add(item.get("output_kind"))
        check_allowed(item.get("output_kind"), SOURCE_CACHE_OUTPUTS, errors, f"expected_source_cache_outputs[{index}].output_kind")
        require_false(item, {"output_runtime_implemented", "raw_payload_allowed"}, errors, f"expected_source_cache_outputs[{index}]")
        require_true(item, {"public_safe_metadata_only", "requires_validation"}, errors, f"expected_source_cache_outputs[{index}]")
    missing = SOURCE_CACHE_OUTPUTS - seen
    if missing:
        errors.append(f"expected_source_cache_outputs missing: {', '.join(sorted(missing))}")


def _validate_evidence_outputs(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("expected_evidence_ledger_outputs must be a list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"expected_evidence_ledger_outputs[{index}] must be an object.")
            continue
        seen.add(item.get("output_kind"))
        check_allowed(item.get("output_kind"), EVIDENCE_OUTPUTS, errors, f"expected_evidence_ledger_outputs[{index}].output_kind")
        require_false(item, {"output_runtime_implemented", "accepted_as_truth"}, errors, f"expected_evidence_ledger_outputs[{index}]")
        require_true(item, {"requires_review", "requires_promotion_policy"}, errors, f"expected_evidence_ledger_outputs[{index}]")
    missing = EVIDENCE_OUTPUTS - seen
    if missing:
        errors.append(f"expected_evidence_ledger_outputs missing: {', '.join(sorted(missing))}")


def _validate_approval_checklist(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("approval_checklist must be a list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"approval_checklist[{index}] must be an object.")
            continue
        seen.add(item.get("item"))
        check_allowed(item.get("item"), APPROVAL_ITEMS, errors, f"approval_checklist[{index}].item")
        if item.get("required") is not True:
            errors.append(f"approval_checklist[{index}].required must be true.")
        if item.get("status") != "pending":
            errors.append(f"approval_checklist[{index}].status must remain pending in P71 examples.")
    missing = APPROVAL_ITEMS - seen
    if missing:
        errors.append(f"approval_checklist missing: {', '.join(sorted(missing))}")


def _validate_operator_checklist(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("operator_checklist must be a list.")
        return
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(f"operator_checklist[{index}] must be an object.")
            continue
        seen.add(item.get("item"))
        check_allowed(item.get("item"), OPERATOR_ITEMS, errors, f"operator_checklist[{index}].item")
        if item.get("required_future") is not True:
            errors.append(f"operator_checklist[{index}].required_future must be true.")
        if item.get("status") != "pending":
            errors.append(f"operator_checklist[{index}].status must remain pending in P71 examples.")
    missing = OPERATOR_ITEMS - seen
    if missing:
        errors.append(f"operator_checklist missing: {', '.join(sorted(missing))}")


def _section(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object.")
        return {}
    return value


def _require_set_in_list(value: Any, expected: set[str], field: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list.")
        return
    observed = {item for item in value if isinstance(item, str)}
    missing = expected - observed
    if missing:
        errors.append(f"{field} missing: {', '.join(sorted(missing))}")


def validate_checksums(root: Path, file_names: Iterable[str], errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        errors.append(f"{checksum_path} missing.")
        return
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2:
            expected[parts[1]] = parts[0]
    for file_name in file_names:
        path = root / file_name
        if not path.is_file():
            errors.append(f"{path} missing.")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected.get(file_name) != digest:
            errors.append(f"{file_name} checksum mismatch in {root}.")


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
