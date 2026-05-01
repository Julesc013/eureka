#!/usr/bin/env python3
"""Validate Eureka Evidence Ledger Record v0 examples."""

from __future__ import annotations

import argparse
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "evidence_ledger"
RECORD_FILE = "EVIDENCE_LEDGER_RECORD.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "evidence_ledger_record_id",
    "evidence_ledger_record_kind",
    "status",
    "created_by_tool",
    "evidence_identity",
    "evidence_kind",
    "subject_ref",
    "claim",
    "source_cache_refs",
    "provenance",
    "observation",
    "confidence",
    "review",
    "conflicts",
    "privacy",
    "rights_and_risk",
    "limitations",
    "no_truth_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
STATUSES = {"draft_example", "dry_run_validated", "fixture_example", "recorded_fixture", "evidence_candidate_future", "source_backed_future", "review_required", "rejected_future", "superseded_future", "promoted_future"}
EVIDENCE_KINDS = {"source_metadata_observation", "availability_observation", "release_metadata_observation", "package_metadata_observation", "compatibility_observation", "member_listing_observation", "checksum_observation", "absence_observation", "source_health_observation", "manual_observation", "fixture_observation", "unknown"}
EVIDENCE_FAMILIES = {"source", "availability", "release", "package", "compatibility", "member", "checksum", "absence", "health", "manual", "fixture", "unknown"}
SUBJECT_KINDS = {"software", "software_version", "driver", "manual_or_documentation", "source_code_release", "package_metadata", "web_capture", "article_or_scan_segment", "file_inside_container", "compatibility_evidence", "source_identity", "absence", "unknown"}
CLAIM_TYPES = {"describes", "has_version", "supports_platform", "does_not_support_platform", "contains_member", "has_checksum", "source_available", "source_unavailable", "source_matches_query", "scoped_absence", "compatibility_claim", "release_metadata", "package_metadata", "unknown"}
CLAIM_STATUSES = {"observation_only", "candidate", "review_required", "rejected_future", "accepted_future"}
CONFIDENCE_CLASSES = {"low", "medium", "high", "unknown"}
CONFIDENCE_BASIS = {"source_cache_record", "fixture_example", "manual_observation", "evidence_pack", "compatibility_observation", "insufficient_evidence", "unknown"}
REVIEW_STATUSES = {"unreviewed", "structurally_valid", "evidence_required", "human_review_required", "policy_review_required", "rights_review_required", "risk_review_required", "conflict_review_required", "rejected_future", "promoted_future"}
CONFLICT_STATUSES = {"none_known", "possible_duplicate", "source_conflict", "version_conflict", "compatibility_conflict", "evidence_conflict", "rights_or_access_conflict", "absence_conflict", "unknown"}
PRESERVATION = {"preserve_conflict", "review_required", "not_applicable"}
PRIVACY_CLASSES = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}
RIGHTS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
RISKS = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
TRUTH_FALSE = {"accepted_as_truth"}
RUNTIME_FALSE = {"evidence_ledger_runtime_implemented", "ledger_write_performed", "live_source_called", "external_calls_performed", "telemetry_exported", "credentials_used"}
MUTATION_FALSE = {"source_cache_mutated", "candidate_index_mutated", "public_index_mutated", "local_index_mutated", "master_index_mutated"}
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
        "created_by": "evidence_ledger_record_validator_v0",
        "record": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "evidence_ledger_record_id": payload.get("evidence_ledger_record_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_record(payload: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    require_fields(payload, REQUIRED_TOP_LEVEL, errors, "evidence_ledger_record")
    if payload.get("evidence_ledger_record_kind") != "evidence_ledger_record":
        errors.append("evidence_ledger_record_kind must be evidence_ledger_record.")
    check_allowed(payload.get("status"), STATUSES, errors, "status")

    identity = _section(payload, "evidence_identity", errors)
    fingerprint = identity.get("evidence_fingerprint", {})
    if not isinstance(fingerprint, Mapping) or fingerprint.get("algorithm") != "sha256" or fingerprint.get("reversible") is not False:
        errors.append("evidence_identity.evidence_fingerprint must be sha256 and non-reversible.")

    kind = _section(payload, "evidence_kind", errors)
    check_allowed(kind.get("kind"), EVIDENCE_KINDS, errors, "evidence_kind.kind")
    check_allowed(kind.get("evidence_family"), EVIDENCE_FAMILIES, errors, "evidence_kind.evidence_family")
    if kind.get("accepted_evidence_now") is not False:
        errors.append("evidence_kind.accepted_evidence_now must be false.")
    if kind.get("review_required") is not True:
        errors.append("evidence_kind.review_required must be true.")

    subject = _section(payload, "subject_ref", errors)
    check_allowed(subject.get("subject_kind"), SUBJECT_KINDS, errors, "subject_ref.subject_kind")

    claim = _section(payload, "claim", errors)
    check_allowed(claim.get("claim_type"), CLAIM_TYPES, errors, "claim.claim_type")
    check_allowed(claim.get("claim_status"), CLAIM_STATUSES, errors, "claim.claim_status")
    if claim.get("global_absence_claimed") is not False:
        errors.append("claim.global_absence_claimed must be false.")

    if not payload.get("source_cache_refs"):
        errors.append("source_cache_refs must be present.")

    provenance = _section(payload, "provenance", errors)
    if not provenance.get("provenance_refs"):
        errors.append("provenance.provenance_refs must be present.")

    observation = _section(payload, "observation", errors)
    if observation.get("snippet_public_safe") is not True:
        errors.append("observation.snippet_public_safe must be true.")

    confidence = _section(payload, "confidence", errors)
    check_allowed(confidence.get("confidence_class"), CONFIDENCE_CLASSES, errors, "confidence.confidence_class")
    check_allowed(confidence.get("confidence_basis"), CONFIDENCE_BASIS, errors, "confidence.confidence_basis")
    if confidence.get("confidence_not_truth") is not True:
        errors.append("confidence.confidence_not_truth must be true.")

    review = _section(payload, "review", errors)
    check_allowed(review.get("review_status"), REVIEW_STATUSES, errors, "review.review_status")
    require_true(review, {"promotion_policy_required", "master_index_review_required"}, errors, "review")

    conflicts = _section(payload, "conflicts", errors)
    check_allowed(conflicts.get("conflict_status"), CONFLICT_STATUSES, errors, "conflicts.conflict_status")
    check_allowed(conflicts.get("preservation_policy"), PRESERVATION, errors, "conflicts.preservation_policy")
    if conflicts.get("destructive_merge_allowed") is not False:
        errors.append("conflicts.destructive_merge_allowed must be false.")

    privacy = _section(payload, "privacy", errors)
    check_allowed(privacy.get("privacy_classification"), PRIVACY_CLASSES, errors, "privacy.privacy_classification")
    require_false(privacy, PRIVACY_FALSE, errors, "privacy")

    rights = _section(payload, "rights_and_risk", errors)
    check_allowed(rights.get("rights_classification"), RIGHTS, errors, "rights_and_risk.rights_classification")
    check_allowed(rights.get("risk_classification"), RISKS, errors, "rights_and_risk.risk_classification")
    require_false(rights, RIGHTS_FALSE, errors, "rights_and_risk")

    require_false(_section(payload, "no_truth_guarantees", errors), TRUTH_FALSE, errors, "no_truth_guarantees")
    require_false(_section(payload, "no_runtime_guarantees", errors), RUNTIME_FALSE, errors, "no_runtime_guarantees")
    require_false(_section(payload, "no_mutation_guarantees", errors), MUTATION_FALSE, errors, "no_mutation_guarantees")


def validate_all_examples(strict: bool = False) -> dict[str, Any]:
    results = []
    errors: list[str] = []
    for root in sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir()):
        result = validate_record_path(root / RECORD_FILE, record_root=root, strict=True or strict)
        result["record_root"] = str(root.relative_to(REPO_ROOT))
        results.append(result)
        errors.extend(result["errors"])
    if not results:
        errors.append("no evidence ledger examples found.")
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "evidence_ledger_record_validator_v0",
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
