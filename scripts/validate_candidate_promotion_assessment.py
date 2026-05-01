#!/usr/bin/env python3
"""Validate Eureka Candidate Promotion Assessment v0 examples.

This validator is stdlib-only and local. It validates contract/example
artifacts only; it performs no network calls, telemetry, persistence, candidate
promotion, review queue writes, source cache writes, evidence ledger writes,
candidate-index mutation, public-index mutation, local-index mutation, or
master-index mutation.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "candidate_promotion"
ASSESSMENT_FILE_NAME = "CANDIDATE_PROMOTION_ASSESSMENT.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "assessment_id",
    "assessment_kind",
    "status",
    "created_by_tool",
    "candidate_ref",
    "candidate_summary",
    "assessment_scope",
    "eligibility_gates",
    "evidence_sufficiency",
    "provenance_sufficiency",
    "source_policy_assessment",
    "privacy_assessment",
    "rights_and_risk_assessment",
    "conflict_assessment",
    "confidence_assessment",
    "review_requirements",
    "recommended_decision",
    "decision_rationale",
    "future_outputs",
    "limitations",
    "no_auto_promotion_guarantees",
    "no_mutation_guarantees",
    "notes",
}
ALLOWED_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "review_required",
    "promotion_blocked",
    "rejection_recommended",
    "quarantine_recommended",
    "supersession_recommended",
    "promotion_eligible_future",
    "promoted_future",
}
ALLOWED_DECISIONS = {
    "no_action",
    "reject_candidate",
    "quarantine_candidate",
    "request_more_evidence",
    "request_source_policy_review",
    "request_rights_risk_review",
    "mark_duplicate_candidate",
    "supersede_candidate_future",
    "eligible_for_review_queue_future",
    "eligible_for_promotion_future",
    "not_eligible",
}
ALLOWED_GATE_TYPES = {
    "structure_valid",
    "candidate_type_allowed",
    "source_policy_allowed",
    "provenance_present",
    "evidence_sufficient",
    "privacy_safe",
    "rights_review_complete",
    "risk_review_complete",
    "conflict_review_complete",
    "duplicate_review_complete",
    "compatibility_review_complete",
    "member_evidence_present",
    "checksum_or_identifier_present",
    "human_review_complete",
    "policy_review_complete",
    "operator_review_complete",
    "external_source_policy_complete",
}
ALLOWED_GATE_STATUSES = {"passed", "failed", "not_applicable", "review_required", "future_only"}
ALLOWED_EVIDENCE_STATUS = {
    "none",
    "insufficient",
    "candidate_only",
    "source_backed",
    "multi_source_backed",
    "review_required",
    "sufficient_for_review_future",
}
ALLOWED_PROVENANCE_STATUS = {
    "missing",
    "partial",
    "pack_referenced",
    "source_referenced",
    "validation_report_referenced",
    "review_queue_referenced_future",
    "sufficient_for_review_future",
}
ALLOWED_SOURCE_POLICY_STATUS = {
    "allowed_fixture",
    "allowed_recorded_fixture",
    "allowed_source_cache_future",
    "live_probe_after_approval_future",
    "source_terms_review_required",
    "source_disallowed",
    "unknown",
}
ALLOWED_PRIVACY_STATUS = {"public_safe", "redacted", "local_private", "restricted", "rejected_sensitive", "unknown"}
ALLOWED_RIGHTS_STATUS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
ALLOWED_RISK_STATUS = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
ALLOWED_CONFLICT_STATUS = {
    "none_known",
    "possible_duplicate",
    "identity_conflict",
    "version_conflict",
    "source_conflict",
    "compatibility_conflict",
    "evidence_conflict",
    "rights_or_access_conflict",
    "unresolved",
    "unknown",
}
ALLOWED_REQUIRED_RESOLUTION = {
    "none",
    "preserve_conflict",
    "human_review_required",
    "policy_review_required",
    "future_merge_review_required",
}
ALLOWED_OUTPUT_KINDS = {
    "candidate_status_update_future",
    "review_queue_entry_future",
    "evidence_pack_candidate_future",
    "contribution_pack_candidate_future",
    "source_cache_candidate_future",
    "evidence_ledger_candidate_future",
    "master_index_candidate_future",
    "rejection_record_future",
    "quarantine_record_future",
}
NO_AUTO_FALSE_FIELDS = {"promotion_performed", "accepted_as_truth", "promoted_to_master_index"}
NO_MUTATION_FALSE_FIELDS = {
    "master_index_mutated",
    "local_index_mutated",
    "public_index_mutated",
    "source_registry_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
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
}
RIGHTS_FALSE_FIELDS = {
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
REQUIRED_REVIEW_KINDS = {
    "human_review",
    "policy_review",
    "evidence_review",
    "provenance_review",
    "rights_review",
    "risk_review",
    "conflict_review",
}
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:\\+(?:users|documents|temp|windows|projects|private|local)\\+", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[\s.-]+)?(?:\(?\d{2,4}\)?[\s.-]+){2,}\d{2,4}\b")),
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|private[_-]?key|secret|credential)\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("private_url", re.compile(r"\bhttps?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.)", re.IGNORECASE)),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\b", re.IGNORECASE)),
)


def validate_assessment_file(path: Path, *, strict: bool = False, example_root: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json_object(path, errors)
    if payload:
        _validate_assessment(payload, errors, warnings, strict=strict)
        _validate_no_sensitive_payload(payload, errors)
    if example_root is not None:
        _validate_checksums(example_root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "candidate_promotion_assessment_validator_v0",
        "assessment": _repo_relative(path),
        "assessment_id": payload.get("assessment_id") if payload else None,
        "errors": errors,
        "warnings": warnings,
    }


def validate_assessment_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    path = root / ASSESSMENT_FILE_NAME
    if not path.is_file():
        return {
            "status": "invalid",
            "created_by": "candidate_promotion_assessment_validator_v0",
            "assessment_root": _repo_relative(root),
            "assessment_id": None,
            "errors": [f"{ASSESSMENT_FILE_NAME}: missing assessment file."],
            "warnings": [],
        }
    report = validate_assessment_file(path, strict=strict, example_root=root)
    report["assessment_root"] = _repo_relative(root)
    return report


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict[str, Any]] = []
    if not EXAMPLES_ROOT.is_dir():
        errors.append("examples/candidate_promotion: missing examples root.")
    else:
        roots = sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())
        if not roots:
            errors.append("examples/candidate_promotion: no example roots found.")
        for root in roots:
            result = validate_assessment_root(root, strict=strict)
            results.append(result)
            errors.extend(f"{result.get('assessment_root')}: {error}" for error in result.get("errors", []))
            warnings.extend(f"{result.get('assessment_root')}: {warning}" for warning in result.get("warnings", []))
    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "candidate_promotion_assessment_validator_v0",
        "example_count": len(results),
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_assessment(payload: Mapping[str, Any], errors: list[str], warnings: list[str], *, strict: bool) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    if payload.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if payload.get("assessment_kind") != "candidate_promotion_assessment":
        errors.append("assessment_kind must be candidate_promotion_assessment.")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append("status is not allowed.")
    if strict and payload.get("status") == "promoted_future":
        errors.append("promoted_future must not be used in P65 examples.")

    _validate_candidate_ref(_require_mapping(payload, "candidate_ref", errors), errors)
    _validate_candidate_summary(_require_mapping(payload, "candidate_summary", errors), errors)
    _validate_scope(_require_mapping(payload, "assessment_scope", errors), errors)
    _validate_gates(payload.get("eligibility_gates"), errors)
    _validate_evidence(_require_mapping(payload, "evidence_sufficiency", errors), errors)
    _validate_provenance(_require_mapping(payload, "provenance_sufficiency", errors), errors)
    _validate_source_policy(_require_mapping(payload, "source_policy_assessment", errors), errors)
    _validate_privacy(_require_mapping(payload, "privacy_assessment", errors), errors)
    _validate_rights_risk(_require_mapping(payload, "rights_and_risk_assessment", errors), errors)
    _validate_conflicts(_require_mapping(payload, "conflict_assessment", errors), errors)
    _validate_confidence(_require_mapping(payload, "confidence_assessment", errors), errors)
    _validate_reviews(_require_mapping(payload, "review_requirements", errors), errors)
    _validate_decision(_require_mapping(payload, "recommended_decision", errors), errors)
    _validate_future_outputs(payload.get("future_outputs"), errors)
    _validate_no_auto(_require_mapping(payload, "no_auto_promotion_guarantees", errors), errors)
    _validate_mutation(_require_mapping(payload, "no_mutation_guarantees", errors), errors)
    if payload.get("recommended_decision", {}).get("decision") == "eligible_for_promotion_future":
        warnings.append("eligible_for_promotion_future is a future recommendation only and performs no promotion.")


def _validate_candidate_ref(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("candidate_id", "candidate_type", "candidate_status", "candidate_fingerprint", "candidate_source", "candidate_ref_status"):
        if key not in value:
            errors.append(f"candidate_ref.{key} is missing.")
    if not isinstance(value.get("candidate_fingerprint"), str) or not re.fullmatch(r"[a-f0-9]{64}", str(value.get("candidate_fingerprint", ""))):
        errors.append("candidate_ref.candidate_fingerprint must be a sha256 hex string.")


def _validate_candidate_summary(value: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(value.get("label"), str) or not value.get("label"):
        errors.append("candidate_summary.label must be non-empty.")
    if not isinstance(value.get("claim_types"), list) or not value.get("claim_types"):
        errors.append("candidate_summary.claim_types must be a non-empty list.")
    if not isinstance(value.get("limitations"), list):
        errors.append("candidate_summary.limitations must be a list.")


def _validate_scope(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("assessment_mode") not in {"policy_only_example", "dry_run", "future_review"}:
        errors.append("assessment_scope.assessment_mode is invalid.")
    assessed_for = value.get("assessed_for")
    if not isinstance(assessed_for, list) or not assessed_for:
        errors.append("assessment_scope.assessed_for must be a non-empty list.")
    if value.get("promotion_destination") not in {
        "none_v0",
        "evidence_pack_candidate_future",
        "contribution_pack_candidate_future",
        "master_index_review_queue_future",
        "source_cache_future",
        "evidence_ledger_future",
        "master_index_future",
    }:
        errors.append("assessment_scope.promotion_destination is invalid.")
    if value.get("destination_runtime_implemented") is not False:
        errors.append("assessment_scope.destination_runtime_implemented must be false.")


def _validate_gates(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("eligibility_gates must be a non-empty list.")
        return
    seen: set[str] = set()
    for index, gate in enumerate(value):
        label = f"eligibility_gates[{index}]"
        if not isinstance(gate, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        gate_type = gate.get("gate_type")
        seen.add(str(gate_type))
        if gate_type not in ALLOWED_GATE_TYPES:
            errors.append(f"{label}.gate_type is invalid.")
        if gate.get("status") not in ALLOWED_GATE_STATUSES:
            errors.append(f"{label}.status is invalid.")
        if not isinstance(gate.get("required"), bool):
            errors.append(f"{label}.required must be boolean.")
        if not isinstance(gate.get("evidence_refs"), list):
            errors.append(f"{label}.evidence_refs must be a list.")
        if not isinstance(gate.get("limitations"), list):
            errors.append(f"{label}.limitations must be a list.")
    required = {"structure_valid", "candidate_type_allowed", "source_policy_allowed", "provenance_present", "evidence_sufficient", "privacy_safe", "human_review_complete", "policy_review_complete"}
    missing = sorted(required - seen)
    if missing:
        errors.append(f"eligibility_gates missing required gate types: {', '.join(missing)}")


def _validate_evidence(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("evidence_status") not in ALLOWED_EVIDENCE_STATUS:
        errors.append("evidence_sufficiency.evidence_status is invalid.")
    for key in ("evidence_refs", "required_evidence_kinds", "missing_evidence_kinds", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"evidence_sufficiency.{key} must be a list.")
    if not isinstance(value.get("source_backed_required"), bool):
        errors.append("evidence_sufficiency.source_backed_required must be boolean.")
    if not isinstance(value.get("snippets_public_safe"), bool):
        errors.append("evidence_sufficiency.snippets_public_safe must be boolean.")


def _validate_provenance(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("provenance_status") not in ALLOWED_PROVENANCE_STATUS:
        errors.append("provenance_sufficiency.provenance_status is invalid.")
    for key in ("provenance_refs", "validator_refs", "pack_refs", "source_refs", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"provenance_sufficiency.{key} must be a list.")


def _validate_source_policy(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("source_policy_status") not in ALLOWED_SOURCE_POLICY_STATUS:
        errors.append("source_policy_assessment.source_policy_status is invalid.")
    if value.get("live_source_called") is not False:
        errors.append("source_policy_assessment.live_source_called must be false.")
    if value.get("live_probe_enabled") is not False:
        errors.append("source_policy_assessment.live_probe_enabled must be false.")
    for key in ("source_ids", "source_families", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"source_policy_assessment.{key} must be a list.")


def _validate_privacy(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("privacy_status") not in ALLOWED_PRIVACY_STATUS:
        errors.append("privacy_assessment.privacy_status is invalid.")
    for key in sorted(PRIVACY_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"privacy_assessment.{key} must be false for P65 public-safe examples.")
    if any(value.get(key) for key in PRIVACY_FALSE_FIELDS) and value.get("publishable") is True:
        errors.append("privacy_assessment.publishable must be false when sensitive flags are true.")
    for key in ("required_redactions", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"privacy_assessment.{key} must be a list.")


def _validate_rights_risk(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("rights_status") not in ALLOWED_RIGHTS_STATUS:
        errors.append("rights_and_risk_assessment.rights_status is invalid.")
    if value.get("risk_status") not in ALLOWED_RISK_STATUS:
        errors.append("rights_and_risk_assessment.risk_status is invalid.")
    for key in sorted(RIGHTS_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"rights_and_risk_assessment.{key} must be false.")


def _validate_conflicts(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("conflict_status") not in ALLOWED_CONFLICT_STATUS:
        errors.append("conflict_assessment.conflict_status is invalid.")
    if value.get("required_resolution") not in ALLOWED_REQUIRED_RESOLUTION:
        errors.append("conflict_assessment.required_resolution is invalid.")
    if value.get("destructive_merge_allowed") is not False:
        errors.append("conflict_assessment.destructive_merge_allowed must be false.")
    for key in ("conflict_refs", "duplicate_candidate_refs", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"conflict_assessment.{key} must be a list.")


def _validate_confidence(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("confidence_class") not in {"low", "medium", "high", "unknown"}:
        errors.append("confidence_assessment.confidence_class is invalid.")
    if value.get("confidence_not_truth") is not True:
        errors.append("confidence_assessment.confidence_not_truth must be true.")
    if value.get("confidence_sufficient_for_promotion") is not False:
        errors.append("confidence_assessment.confidence_sufficient_for_promotion must be false in P65 examples.")
    if not isinstance(value.get("confidence_basis"), list):
        errors.append("confidence_assessment.confidence_basis must be a list.")


def _validate_reviews(value: Mapping[str, Any], errors: list[str]) -> None:
    required_review_kinds = value.get("required_review_kinds")
    if not isinstance(required_review_kinds, list):
        errors.append("review_requirements.required_review_kinds must be a list.")
    else:
        missing = sorted(REQUIRED_REVIEW_KINDS - set(required_review_kinds))
        if missing:
            errors.append(f"review_requirements.required_review_kinds missing: {', '.join(missing)}")
    if value.get("promotion_allowed_now") is not False:
        errors.append("review_requirements.promotion_allowed_now must be false.")
    if value.get("promotion_policy_required") is not True:
        errors.append("review_requirements.promotion_policy_required must be true.")
    if value.get("master_index_review_queue_required") is not True:
        errors.append("review_requirements.master_index_review_queue_required must be true.")
    for key in ("reviews_completed", "reviews_missing", "limitations"):
        if not isinstance(value.get(key), list):
            errors.append(f"review_requirements.{key} must be a list.")


def _validate_decision(value: Mapping[str, Any], errors: list[str]) -> None:
    if value.get("decision") not in ALLOWED_DECISIONS:
        errors.append("recommended_decision.decision is invalid.")
    if value.get("decision_status") not in {"recommendation_only", "future_only", "blocked"}:
        errors.append("recommended_decision.decision_status is invalid.")
    if value.get("automatic") is not False:
        errors.append("recommended_decision.automatic must be false.")
    if not isinstance(value.get("requires_human_or_policy_review"), bool):
        errors.append("recommended_decision.requires_human_or_policy_review must be boolean.")
    if not isinstance(value.get("reasons"), list) or not value.get("reasons"):
        errors.append("recommended_decision.reasons must be a non-empty list.")


def _validate_future_outputs(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("future_outputs must be a list.")
        return
    for index, output in enumerate(value):
        label = f"future_outputs[{index}]"
        if not isinstance(output, Mapping):
            errors.append(f"{label} must be an object.")
            continue
        if output.get("output_kind") not in ALLOWED_OUTPUT_KINDS:
            errors.append(f"{label}.output_kind is invalid.")
        if output.get("output_runtime_implemented") is not False:
            errors.append(f"{label}.output_runtime_implemented must be false.")
        if output.get("requires_validation") is not True:
            errors.append(f"{label}.requires_validation must be true.")
        if output.get("requires_review") is not True:
            errors.append(f"{label}.requires_review must be true.")


def _validate_no_auto(value: Mapping[str, Any], errors: list[str]) -> None:
    for key in sorted(NO_AUTO_FALSE_FIELDS):
        if value.get(key) is not False:
            errors.append(f"no_auto_promotion_guarantees.{key} must be false.")


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
    for filename, expected_digest in sorted(expected.items()):
        path = root / filename
        if not path.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {filename}.")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_digest:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {filename}.")
    if ASSESSMENT_FILE_NAME not in expected:
        errors.append("CHECKSUMS.SHA256 must include CANDIDATE_PROMOTION_ASSESSMENT.json.")


def _read_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("assessment file is missing.")
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
    lines = ["Candidate Promotion Assessment validation", f"status: {report['status']}"]
    if "example_count" in report:
        lines.append(f"example_count: {report['example_count']}")
    if report.get("assessment_id"):
        lines.append(f"assessment_id: {report['assessment_id']}")
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", type=Path, help="Validate one CANDIDATE_PROMOTION_ASSESSMENT.json file.")
    parser.add_argument("--assessment-root", type=Path, help="Validate one example root containing CANDIDATE_PROMOTION_ASSESSMENT.json.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all committed candidate promotion examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Apply strict example posture checks.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = sum(1 for value in (args.assessment, args.assessment_root, args.all_examples) if value)
    if selected > 1:
        parser.error("choose only one of --assessment, --assessment-root, or --all-examples")

    if args.all_examples or selected == 0:
        report = validate_all_examples(strict=args.strict)
    elif args.assessment_root:
        report = validate_assessment_root(args.assessment_root, strict=args.strict)
    elif args.assessment:
        report = validate_assessment_file(args.assessment, strict=args.strict)
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
