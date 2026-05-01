#!/usr/bin/env python3
"""Validate Eureka Candidate Index Record v0 examples.

The validator is structural and stdlib-only. It validates P64 candidate index
examples without using telemetry, persistence, network calls, live probes,
candidate runtime storage, source cache writes, evidence ledger writes,
candidate promotion, public-search injection, local-index mutation, or
master-index writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "candidate_index"
RECORD_FILE_NAME = "CANDIDATE_INDEX_RECORD.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "candidate_id",
    "candidate_kind",
    "status",
    "created_by_tool",
    "candidate_identity",
    "candidate_type",
    "candidate_subject",
    "candidate_claims",
    "provenance",
    "input_refs",
    "evidence_refs",
    "source_policy",
    "confidence",
    "review",
    "conflicts",
    "visibility",
    "privacy",
    "rights_and_risk",
    "retention_policy",
    "limitations",
    "no_truth_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "observed_future",
    "normalized_future",
    "candidate_future",
    "review_required",
    "quarantined",
    "rejected_future",
    "superseded_future",
    "promoted_future",
}
ALLOWED_CANDIDATE_TYPES = {
    "object_identity_candidate",
    "software_version_candidate",
    "source_record_candidate",
    "evidence_record_candidate",
    "representation_candidate",
    "member_path_candidate",
    "compatibility_claim_candidate",
    "checksum_candidate",
    "release_metadata_candidate",
    "package_metadata_candidate",
    "source_match_candidate",
    "identity_match_candidate",
    "alias_candidate",
    "absence_candidate",
    "extraction_candidate",
    "OCR_text_candidate",
    "query_interpretation_candidate",
    "actionability_candidate",
    "unknown",
}
ALLOWED_TYPE_FAMILIES = {
    "object",
    "source",
    "evidence",
    "representation",
    "member",
    "compatibility",
    "identity",
    "absence",
    "extraction",
    "query",
    "actionability",
    "unknown",
}
ALLOWED_DESTINATIONS = {
    "evidence_pack_candidate",
    "contribution_pack_candidate",
    "candidate_index_only",
    "master_index_review_queue_future",
    "source_cache_future",
    "evidence_ledger_future",
}
ALLOWED_SUBJECT_KINDS = {
    "software",
    "software_version",
    "driver",
    "manual_or_documentation",
    "source_code_release",
    "package_metadata",
    "web_capture",
    "article_or_scan_segment",
    "file_inside_container",
    "compatibility_evidence",
    "source_identity",
    "query_interpretation",
    "absence",
    "unknown",
}
ALLOWED_CLAIM_TYPES = {
    "describes",
    "same_as_candidate",
    "variant_of_candidate",
    "has_version",
    "supports_platform",
    "does_not_support_platform",
    "contains_member",
    "has_checksum",
    "source_matches_query",
    "source_missing",
    "near_absence",
    "scoped_absence",
    "query_interpretation",
    "actionability_hint",
    "unknown",
}
ALLOWED_CLAIM_STATUSES = {
    "unreviewed",
    "structurally_valid",
    "evidence_required",
    "review_required",
    "rejected_future",
    "accepted_future",
}
ALLOWED_PROVENANCE_KINDS = {
    "query_intelligence",
    "source_cache_future",
    "evidence_pack",
    "source_pack",
    "contribution_pack",
    "AI_output_candidate",
    "manual_observation",
    "probe_result_future",
    "fixture_example",
    "unknown",
}
ALLOWED_SOURCE_POLICIES = {
    "no_source_call",
    "fixture_only",
    "recorded_fixture",
    "source_cache_future",
    "evidence_pack_reference",
    "source_pack_reference",
    "live_probe_after_approval_future",
    "unknown",
}
ALLOWED_EVIDENCE_STATUSES = {"none", "candidate", "source_backed", "review_required", "rejected_future"}
ALLOWED_CONFIDENCE_CLASSES = {"low", "medium", "high", "unknown"}
ALLOWED_CONFIDENCE_BASES = {
    "lexical_match",
    "source_backed_evidence",
    "compatibility_evidence",
    "member_evidence",
    "manual_observation",
    "AI_output_candidate",
    "fixture_example",
    "insufficient_evidence",
    "unknown",
}
ALLOWED_REVIEW_STATUSES = {
    "unreviewed",
    "structurally_valid",
    "evidence_required",
    "human_review_required",
    "policy_review_required",
    "rights_review_required",
    "risk_review_required",
    "conflict_review_required",
    "rejected_future",
    "promoted_future",
}
ALLOWED_CONFLICT_STATUSES = {
    "none_known",
    "possible_duplicate",
    "identity_conflict",
    "version_conflict",
    "source_conflict",
    "compatibility_conflict",
    "evidence_conflict",
    "rights_or_access_conflict",
    "unknown",
}
ALLOWED_VISIBILITY = {"local_private", "public_safe_candidate", "public_aggregate_only", "review_required", "restricted"}
ALLOWED_PRIVACY_CLASSIFICATIONS = {"public_safe_aggregate", "local_private", "rejected_sensitive", "redacted", "unknown"}
ALLOWED_RIGHTS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
ALLOWED_RISK = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}

NO_TRUTH_FALSE_FIELDS = {"accepted_as_truth", "promoted_to_master_index"}
NO_MUTATION_FALSE_FIELDS = {
    "master_index_mutated",
    "local_index_mutated",
    "public_index_mutated",
    "source_registry_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "result_cache_mutated",
    "miss_ledger_mutated",
    "search_need_mutated",
    "probe_queue_mutated",
    "telemetry_exported",
    "external_calls_performed",
    "live_source_called",
}
PRIVACY_FALSE_FIELDS = {
    "raw_query_retained",
    "contains_raw_query",
    "contains_private_path",
    "contains_secret",
    "contains_private_url",
    "contains_user_identifier",
    "contains_ip_address",
    "contains_local_result",
}
RIGHTS_FALSE_FIELDS = {
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[a-zA-Z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE)),
)


def validate_candidate_record_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_record(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "candidate_index_record_validator_v0",
        "record": _repo_relative(path),
        "candidate_id": payload.get("candidate_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_candidate_record_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    record_path = root / RECORD_FILE_NAME
    if not record_path.is_file():
        return {
            "status": "invalid",
            "created_by": "candidate_index_record_validator_v0",
            "record_root": _repo_relative(root),
            "candidate_id": None,
            "errors": [f"{RECORD_FILE_NAME}: missing candidate record file."],
            "warnings": [],
        }
    report = validate_candidate_record_file(record_path, strict=strict, example_root=root)
    report["record_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/candidate_index: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/candidate_index: no example roots found.")
        for root in roots:
            result = validate_candidate_record_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('record_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('record_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "candidate_index_record_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_record(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("candidate_kind") != "candidate_index_record":
        errors.append("candidate_kind must be candidate_index_record.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not an allowed candidate lifecycle status.")

    _validate_identity(_require_mapping(payload, "candidate_identity", errors), errors)
    _validate_candidate_type(_require_mapping(payload, "candidate_type", errors), errors)
    _validate_subject(_require_mapping(payload, "candidate_subject", errors), errors)
    _validate_claims(payload.get("candidate_claims"), errors, strict)
    _validate_provenance(_require_mapping(payload, "provenance", errors), errors)
    _validate_input_refs(_require_mapping(payload, "input_refs", errors), errors)
    _validate_evidence_refs(payload.get("evidence_refs"), errors)
    _validate_source_policy(_require_mapping(payload, "source_policy", errors), errors)
    _validate_confidence(_require_mapping(payload, "confidence", errors), errors)
    _validate_review(_require_mapping(payload, "review", errors), errors)
    _validate_conflicts(_require_mapping(payload, "conflicts", errors), errors)
    _validate_visibility(_require_mapping(payload, "visibility", errors), errors)
    _validate_privacy(_require_mapping(payload, "privacy", errors), errors, payload)
    _validate_rights_and_risk(_require_mapping(payload, "rights_and_risk", errors), errors)
    _validate_retention(_require_mapping(payload, "retention_policy", errors), errors)
    _validate_truth(_require_mapping(payload, "no_truth_guarantees", errors), errors)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)

    if payload.get("status") == "promoted_future":
        warnings.append("promoted_future is a lifecycle placeholder only; P64 examples should not use current promotion.")


def _validate_identity(value: Mapping[str, Any], errors: list[str]) -> None:
    fingerprint = _require_mapping(value, "candidate_fingerprint", errors)
    if fingerprint:
        if fingerprint.get("algorithm") != "sha256":
            errors.append("candidate_identity.candidate_fingerprint.algorithm must be sha256.")
        if not isinstance(fingerprint.get("value"), str) or not re.fullmatch(r"[a-f0-9]{64}", fingerprint["value"]):
            errors.append("candidate_identity.candidate_fingerprint.value must be a lowercase sha256 hex string.")
        if fingerprint.get("reversible") is not False:
            errors.append("candidate_identity.candidate_fingerprint.reversible must be false.")
        if fingerprint.get("salt_policy") not in {"unsalted_public_aggregate", "deployment_secret_salted_future", "local_private_salted_future"}:
            errors.append("candidate_identity.candidate_fingerprint.salt_policy is invalid.")
    if not isinstance(value.get("canonical_candidate_label"), str) or not value.get("canonical_candidate_label"):
        errors.append("candidate_identity.canonical_candidate_label must be a non-empty string.")
    for key in ("normalized_terms", "alias_terms"):
        if not isinstance(value.get(key), list):
            errors.append(f"candidate_identity.{key} must be a list.")


def _validate_candidate_type(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("type") not in ALLOWED_CANDIDATE_TYPES:
        errors.append("candidate_type.type is invalid.")
    if value.get("type_family") not in ALLOWED_TYPE_FAMILIES:
        errors.append("candidate_type.type_family is invalid.")
    destinations = value.get("allowed_future_destinations")
    if not isinstance(destinations, list) or not destinations:
        errors.append("candidate_type.allowed_future_destinations must be a non-empty list.")
    else:
        invalid = sorted(str(item) for item in destinations if item not in ALLOWED_DESTINATIONS)
        if invalid:
            errors.append(f"candidate_type.allowed_future_destinations contains invalid values: {', '.join(invalid)}")


def _validate_subject(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("subject_kind") not in ALLOWED_SUBJECT_KINDS:
        errors.append("candidate_subject.subject_kind is invalid.")
    if value.get("subject_kind") != "unknown" and not any(value.get(key) for key in ("product_name", "source_family", "source_id", "identifier")):
        errors.append("candidate_subject must include a public-safe product, source, or identifier hint for concrete examples.")
    if not isinstance(value.get("limitations"), list):
        errors.append("candidate_subject.limitations must be a list.")


def _validate_claims(value: Any, errors: list[str], strict: bool) -> None:
    if not isinstance(value, list) or not value:
        errors.append("candidate_claims must be a non-empty list.")
        return
    for index, claim in enumerate(value):
        label = f"candidate_claims[{index}]"
        if not isinstance(claim, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        for key in ("claim_id", "claim_type", "claim_value", "claim_status", "confidence", "limitations"):
            if key not in claim:
                errors.append(f"{label}.{key} is missing.")
        if claim.get("claim_type") not in ALLOWED_CLAIM_TYPES:
            errors.append(f"{label}.claim_type is invalid.")
        if claim.get("claim_status") not in ALLOWED_CLAIM_STATUSES:
            errors.append(f"{label}.claim_status is invalid.")
        if claim.get("claim_status") == "accepted_future" and strict:
            errors.append(f"{label}.claim_status must not be accepted_future in P64 examples.")
        if claim.get("confidence") not in ALLOWED_CONFIDENCE_CLASSES:
            errors.append(f"{label}.confidence is invalid.")
        if not isinstance(claim.get("limitations"), list):
            errors.append(f"{label}.limitations must be a list.")


def _validate_provenance(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("provenance_kind") not in ALLOWED_PROVENANCE_KINDS:
        errors.append("provenance.provenance_kind is invalid.")
    for key in ("source_refs", "pack_refs", "validator_refs", "tool_refs", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"provenance.{key} must be a list.")
    if not isinstance(value.get("created_from"), str) or not value.get("created_from"):
        errors.append("provenance.created_from must be a non-empty string.")


def _validate_input_refs(value: Mapping[str, Any], errors: list[str]) -> None:
    required = ("query_observation_refs", "search_result_cache_refs", "search_miss_ledger_refs", "search_need_refs", "probe_queue_refs")
    total_refs = 0
    for key in required:
        refs = value.get(key)
        if not isinstance(refs, list):
            errors.append(f"input_refs.{key} must be a list.")
            continue
        total_refs += len(refs)
        for index, ref in enumerate(refs):
            _validate_ref(ref, errors, f"input_refs.{key}[{index}]")
    for optional in ("typed_ai_output_refs", "manual_observation_refs", "source_pack_refs", "evidence_pack_refs", "contribution_pack_refs"):
        if optional in value:
            refs = value.get(optional)
            if not isinstance(refs, list):
                errors.append(f"input_refs.{optional} must be a list.")
                continue
            total_refs += len(refs)
            for index, ref in enumerate(refs):
                _validate_ref(ref, errors, f"input_refs.{optional}[{index}]")
    if total_refs == 0:
        errors.append("input_refs must include at least one synthetic or future reference.")


def _validate_ref(ref: Any, errors: list[str], label: str) -> None:
    if not isinstance(ref, Mapping):
        errors.append(f"{label} must be an object.")
        return
    for key in ("ref_id", "ref_kind", "status", "privacy_classification", "limitations"):
        if key not in ref:
            errors.append(f"{label}.{key} is missing.")
    if ref.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
        errors.append(f"{label}.privacy_classification is invalid.")
    if not isinstance(ref.get("limitations"), list):
        errors.append(f"{label}.limitations must be a list.")


def _validate_evidence_refs(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("evidence_refs must be a list.")
        return
    for index, ref in enumerate(value):
        label = f"evidence_refs[{index}]"
        if not isinstance(ref, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        for key in ("evidence_ref", "evidence_kind", "evidence_status", "limitations"):
            if key not in ref:
                errors.append(f"{label}.{key} is missing.")
        if ref.get("evidence_status") not in ALLOWED_EVIDENCE_STATUSES:
            errors.append(f"{label}.evidence_status is invalid.")
        if not isinstance(ref.get("limitations"), list):
            errors.append(f"{label}.limitations must be a list.")


def _validate_source_policy(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("source_policy_kind") not in ALLOWED_SOURCE_POLICIES:
        errors.append("source_policy.source_policy_kind is invalid.")
    if value.get("live_source_called") is not False:
        errors.append("source_policy.live_source_called must be false.")
    if value.get("live_probe_enabled") is not False:
        errors.append("source_policy.live_probe_enabled must be false.")
    for key in ("source_terms_review_required", "rights_review_required"):
        if not isinstance(value.get(key), bool):
            errors.append(f"source_policy.{key} must be boolean.")
    for key in ("allowed_source_ids", "allowed_source_families", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"source_policy.{key} must be a list.")


def _validate_confidence(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("confidence_class") not in ALLOWED_CONFIDENCE_CLASSES:
        errors.append("confidence.confidence_class is invalid.")
    bases = value.get("confidence_basis")
    if not isinstance(bases, list) or not bases:
        errors.append("confidence.confidence_basis must be a non-empty list.")
    else:
        invalid = sorted(str(item) for item in bases if item not in ALLOWED_CONFIDENCE_BASES)
        if invalid:
            errors.append(f"confidence.confidence_basis contains invalid values: {', '.join(invalid)}")
    if value.get("confidence_not_truth") is not True:
        errors.append("confidence.confidence_not_truth must be true.")
    if not isinstance(value.get("confidence_notes"), list):
        errors.append("confidence.confidence_notes must be a list.")


def _validate_review(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        errors.append("review.review_status is invalid.")
    if not isinstance(value.get("required_reviews"), list):
        errors.append("review.required_reviews must be a list.")
    if value.get("promotion_allowed_now") is not False:
        errors.append("review.promotion_allowed_now must be false.")
    if value.get("promotion_policy_required") is not True:
        errors.append("review.promotion_policy_required must be true.")


def _validate_conflicts(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("conflict_status") not in ALLOWED_CONFLICT_STATUSES:
        errors.append("conflicts.conflict_status is invalid.")
    if value.get("preservation_policy") not in {"preserve_conflict", "review_required", "not_applicable"}:
        errors.append("conflicts.preservation_policy is invalid.")
    if value.get("conflict_status") != "none_known" and value.get("preservation_policy") == "not_applicable":
        errors.append("conflicts.preservation_policy must preserve or require review when conflict_status is not none_known.")
    for key in ("conflicting_candidate_refs", "conflicting_source_refs"):
        if not isinstance(value.get(key), list):
            errors.append(f"conflicts.{key} must be a list.")


def _validate_visibility(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("visibility_class") not in ALLOWED_VISIBILITY:
        errors.append("visibility.visibility_class is invalid.")
    if value.get("public_result_visibility_allowed") is not False:
        errors.append("visibility.public_result_visibility_allowed must be false.")
    if not isinstance(value.get("public_candidate_visibility_allowed_future"), bool):
        errors.append("visibility.public_candidate_visibility_allowed_future must be boolean.")
    if not isinstance(value.get("limitations"), list):
        errors.append("visibility.limitations must be a list.")


def _validate_privacy(value: Mapping[str, Any], errors: list[str], payload: Mapping[str, Any]) -> None:
    if value.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSIFICATIONS:
        errors.append("privacy.privacy_classification is invalid.")
    for key in sorted(PRIVACY_FALSE_FIELDS):
        if value.get(key) is not False and payload.get("status") != "rejected_future":
            errors.append(f"privacy.{key} must be false for public-safe examples.")
    if any(value.get(key) for key in PRIVACY_FALSE_FIELDS) and value.get("publishable") is True:
        errors.append("privacy.publishable must be false when sensitive flags are true.")


def _validate_rights_and_risk(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("rights_classification") not in ALLOWED_RIGHTS:
        errors.append("rights_and_risk.rights_classification is invalid.")
    if value.get("risk_classification") not in ALLOWED_RISK:
        errors.append("rights_and_risk.risk_classification is invalid.")
    for key in sorted(RIGHTS_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"rights_and_risk.{key} must be false.")
    if not isinstance(value.get("limitations"), list):
        errors.append("rights_and_risk.limitations must be a list.")


def _validate_retention(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("raw_query_retention") != "none":
        errors.append("retention_policy.raw_query_retention must be none.")
    if not isinstance(value.get("notes"), list):
        errors.append("retention_policy.notes must be a list.")


def _validate_truth(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_TRUTH_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_truth_guarantees.{key} must be false.")


def _validate_mutation(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_MUTATION_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_mutation_guarantees.{key} must be false.")


def _require_mapping(payload: Mapping[str, Any], key: str, errors: list[str]) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object.")
        return {}
    return value


def _validate_no_sensitive_payload(payload: Mapping[str, Any], errors: list[str]) -> None:
    text = "\n".join(_iter_string_values(payload))
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"payload contains prohibited data pattern: {label}.")


def _iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from _iter_string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_string_values(child)


def _validate_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        errors.append("CHECKSUMS.SHA256: missing checksums file.")
        return
    expected: dict[str, str] = {}
    for line_number, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 2:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: expected '<sha256>  <file>'.")
            continue
        digest, filename = parts
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: invalid sha256 digest.")
            continue
        if "/" in filename or "\\" in filename:
            errors.append(f"CHECKSUMS.SHA256 line {line_number}: filename must be local to example root.")
            continue
        expected[filename] = digest
    for filename, digest in sorted(expected.items()):
        file_path = root / filename
        if not file_path.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {filename}.")
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {filename}.")
    if RECORD_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include CANDIDATE_INDEX_RECORD.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("candidate record file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append("top-level JSON must be an object.")
        return {}
    return payload


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Candidate Index Record validation",
        f"status: {report['status']}",
    ]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("candidate_id"):
        lines.append(f"candidate_id: {report['candidate_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="Validate one CANDIDATE_INDEX_RECORD.json file.")
    parser.add_argument("--record-root", type=Path, help="Validate one example root containing CANDIDATE_INDEX_RECORD.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed candidate index examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.record, args.record_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --record, --record-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.record_root:
        report = validate_candidate_record_root(args.record_root, strict=args.strict)
    elif args.record:
        report = validate_candidate_record_file(args.record, strict=args.strict)
    else:  # pragma: no cover
        report = {"status": "invalid", "errors": ["no selection"], "warnings": []}

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
