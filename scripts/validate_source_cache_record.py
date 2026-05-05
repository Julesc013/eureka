#!/usr/bin/env python3
"""Validate Eureka Source Cache Record v0 examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from _p70_contract_common import (
    check_allowed,
    check_sensitive,
    load_json_object,
    print_report,
    require_false,
    require_fields,
    require_true,
    validate_checksums,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_cache"
RECORD_FILE = "SOURCE_CACHE_RECORD.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "source_cache_record_id",
    "source_cache_record_kind",
    "status",
    "created_by_tool",
    "source_ref",
    "cache_identity",
    "cache_kind",
    "source_policy",
    "acquisition_context",
    "cached_payload_summary",
    "normalized_metadata",
    "freshness",
    "provenance",
    "fixity",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
STATUSES = {"draft_example", "dry_run_validated", "fixture_example", "recorded_fixture", "cache_candidate_future", "cached_future", "stale_future", "invalidated_future", "rejected_by_policy", "quarantined"}
SOURCE_FAMILIES = {"internet_archive", "wayback", "github_releases", "pypi", "npm", "software_heritage", "wikidata_open_library", "sourceforge", "manual_source_pack", "local_fixture", "recorded_fixture", "unknown"}
SOURCE_STATUSES = {"active_fixture", "active_recorded_fixture", "placeholder", "future", "disabled", "approval_required", "unknown"}
CACHE_KINDS = {"source_metadata", "source_availability", "source_identifier_metadata", "release_metadata", "package_metadata", "wayback_capture_metadata", "file_listing_metadata", "source_health_metadata", "fixture_metadata", "recorded_fixture_metadata", "unknown"}
PAYLOAD_POLICIES = {"metadata_summary_only", "no_raw_payload", "synthetic_example", "recorded_fixture_summary", "future_bounded_source_response"}
SOURCE_POLICIES = {"no_source_call", "manual_only", "fixture_only", "recorded_fixture_only", "source_sync_after_approval_future", "live_metadata_sync_after_approval_future", "unknown"}
ACQUISITION_KINDS = {"fixture_example", "recorded_fixture", "source_pack", "evidence_pack", "manual_observation", "source_sync_worker_future", "live_connector_future", "unknown"}
ACQUIRED_AT = {"example_static", "recorded_fixture_metadata", "future_runtime", "unknown"}
PAYLOAD_SUMMARY_KINDS = {"metadata_fields", "availability_summary", "release_summary", "package_summary", "file_listing_summary", "source_health_summary", "fixture_summary", "absence_summary", "unknown"}
FRESHNESS_STATUSES = {"example_static", "fresh_future", "stale_future", "invalidated_future", "unknown"}
FRESHNESS_BASIS = {"fixture_static", "recorded_fixture_date", "source_sync_time_future", "source_change_token_future", "source_policy_future"}
TTL_POLICIES = {"none_for_example", "until_source_cache_refresh_future", "bounded_ttl_future", "source_policy_defined_future"}
PROVENANCE_KINDS = {"fixture_example", "recorded_fixture", "source_pack", "evidence_pack", "manual_observation", "source_sync_worker_future", "live_connector_future", "unknown"}
HASH_ALGORITHMS = {"sha256", "none_for_example"}
CHECKSUM_STATUSES = {"not_applicable", "present", "verified", "failed_future", "unknown"}
CHECKSUM_SCOPES = {"metadata_summary", "raw_payload_future", "fixture_file", "unknown"}
PRIVACY_CLASSES = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}
RIGHTS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
RISKS = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}

RUNTIME_FALSE = {"source_cache_runtime_implemented", "cache_write_performed", "live_source_called", "external_calls_performed", "arbitrary_url_fetched", "raw_payload_stored", "private_data_stored", "executable_payload_stored", "telemetry_exported", "credentials_used"}
MUTATION_FALSE = {"evidence_ledger_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"}
PRIVACY_FALSE = {"contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query", "contains_local_result"}
RIGHTS_FALSE = {"rights_clearance_claimed", "malware_safety_claimed", "downloads_enabled", "installs_enabled", "execution_enabled"}


def validate_record_path(path: Path, *, record_root: Path | None = None, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = load_json_object(path, errors, str(path))
    if payload:
        validate_record(payload, errors, warnings)
        check_sensitive(payload, errors, str(path))
    root = record_root or path.parent
    if root and (root / "CHECKSUMS.SHA256").exists():
        validate_checksums(root, RECORD_FILE, errors)
    elif strict:
        errors.append(f"{root}/CHECKSUMS.SHA256 missing.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_cache_record_validator_v0",
        "record": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "source_cache_record_id": payload.get("source_cache_record_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_record(payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    require_fields(payload, REQUIRED_TOP_LEVEL, errors, "source_cache_record")
    if payload.get("source_cache_record_kind") != "source_cache_record":
        errors.append("source_cache_record_kind must be source_cache_record.")
    check_allowed(payload.get("status"), STATUSES, errors, "status")

    source_ref = _section(payload, "source_ref", errors)
    check_allowed(source_ref.get("source_family"), SOURCE_FAMILIES, errors, "source_ref.source_family")
    check_allowed(source_ref.get("source_status"), SOURCE_STATUSES, errors, "source_ref.source_status")
    if not source_ref.get("source_locator"):
        errors.append("source_ref.source_locator is required.")

    identity = _section(payload, "cache_identity", errors)
    fingerprint = identity.get("cache_fingerprint", {})
    if not isinstance(fingerprint, Mapping) or fingerprint.get("algorithm") != "sha256" or fingerprint.get("reversible") is not False:
        errors.append("cache_identity.cache_fingerprint must be sha256 and non-reversible.")

    cache_kind = _section(payload, "cache_kind", errors)
    check_allowed(cache_kind.get("kind"), CACHE_KINDS, errors, "cache_kind.kind")
    check_allowed(cache_kind.get("payload_policy"), PAYLOAD_POLICIES, errors, "cache_kind.payload_policy")
    if cache_kind.get("raw_payload_allowed") is not False:
        errors.append("cache_kind.raw_payload_allowed must be false.")

    source_policy = _section(payload, "source_policy", errors)
    check_allowed(source_policy.get("source_policy_kind"), SOURCE_POLICIES, errors, "source_policy.source_policy_kind")
    if source_policy.get("live_source_enabled_now") is not False:
        errors.append("source_policy.live_source_enabled_now must be false.")

    acquisition = _section(payload, "acquisition_context", errors)
    check_allowed(acquisition.get("acquisition_kind"), ACQUISITION_KINDS, errors, "acquisition_context.acquisition_kind")
    check_allowed(acquisition.get("acquired_at_policy"), ACQUIRED_AT, errors, "acquisition_context.acquired_at_policy")
    require_false(acquisition, {"live_network_used", "external_call_performed", "credentials_used"}, errors, "acquisition_context")

    summary = _section(payload, "cached_payload_summary", errors)
    check_allowed(summary.get("payload_summary_kind"), PAYLOAD_SUMMARY_KINDS, errors, "cached_payload_summary.payload_summary_kind")
    if summary.get("raw_payload_included") is not False:
        errors.append("cached_payload_summary.raw_payload_included must be false.")
    if summary.get("public_safe") is not True:
        errors.append("cached_payload_summary.public_safe must be true.")

    freshness = _section(payload, "freshness", errors)
    check_allowed(freshness.get("freshness_status"), FRESHNESS_STATUSES, errors, "freshness.freshness_status")
    check_allowed(freshness.get("freshness_basis"), FRESHNESS_BASIS, errors, "freshness.freshness_basis")
    check_allowed(freshness.get("ttl_policy"), TTL_POLICIES, errors, "freshness.ttl_policy")
    require_true(freshness, {"stale_if_source_policy_changes", "stale_if_connector_contract_changes", "stale_if_rights_policy_changes"}, errors, "freshness")

    provenance = _section(payload, "provenance", errors)
    check_allowed(provenance.get("provenance_kind"), PROVENANCE_KINDS, errors, "provenance.provenance_kind")
    if not provenance.get("provenance_refs"):
        errors.append("provenance.provenance_refs must be present.")

    fixity = _section(payload, "fixity", errors)
    check_allowed(fixity.get("hash_algorithm"), HASH_ALGORITHMS, errors, "fixity.hash_algorithm")
    check_allowed(fixity.get("checksum_status"), CHECKSUM_STATUSES, errors, "fixity.checksum_status")
    check_allowed(fixity.get("checksum_scope"), CHECKSUM_SCOPES, errors, "fixity.checksum_scope")

    privacy = _section(payload, "privacy", errors)
    check_allowed(privacy.get("privacy_classification"), PRIVACY_CLASSES, errors, "privacy.privacy_classification")
    require_false(privacy, PRIVACY_FALSE, errors, "privacy")

    rights = _section(payload, "rights_and_risk", errors)
    check_allowed(rights.get("rights_classification"), RIGHTS, errors, "rights_and_risk.rights_classification")
    check_allowed(rights.get("risk_classification"), RISKS, errors, "rights_and_risk.risk_classification")
    require_false(rights, RIGHTS_FALSE, errors, "rights_and_risk")

    require_false(_section(payload, "no_runtime_guarantees", errors), RUNTIME_FALSE, errors, "no_runtime_guarantees")
    require_false(_section(payload, "no_mutation_guarantees", errors), MUTATION_FALSE, errors, "no_mutation_guarantees")


def validate_all_examples(strict: bool = False) -> dict[str, Any]:
    results = []
    errors: list[str] = []
    for root in sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir() and (path / RECORD_FILE).is_file()):
        result = validate_record_path(root / RECORD_FILE, record_root=root, strict=True or strict)
        result["record_root"] = str(root.relative_to(REPO_ROOT))
        results.append(result)
        errors.extend(result["errors"])
    if not results:
        errors.append("no source cache examples found.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "source_cache_record_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": [],
    }


def _section(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object.")
        return {}
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record")
    parser.add_argument("--record-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    if args.all_examples:
        report = validate_all_examples(strict=args.strict)
    else:
        path = Path(args.record) if args.record else (Path(args.record_root) / RECORD_FILE if args.record_root else None)
        if path is None:
            parser.error("provide --record, --record-root, or --all-examples")
        report = validate_record_path(path, record_root=Path(args.record_root) if args.record_root else None, strict=args.strict)
    print_report(report, args.json)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
