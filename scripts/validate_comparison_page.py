#!/usr/bin/env python3
"""Validate Eureka Comparison Page Contract v0 examples.

The validator is stdlib-only and local-only. It opens no network connections,
performs no live source calls, and mutates no source cache, evidence ledger,
candidate index, public index, local index, master index, or comparison-page
store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = REPO_ROOT / "examples" / "comparison_pages"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "comparison_page_id",
    "comparison_page_kind",
    "status",
    "created_by_tool",
    "comparison_identity",
    "comparison_type",
    "subjects",
    "criteria",
    "comparison_matrix",
    "identity_comparison",
    "version_state_release_comparison",
    "representation_member_comparison",
    "source_evidence_provenance_comparison",
    "compatibility_comparison",
    "rights_risk_action_comparison",
    "conflicts_and_disagreements",
    "absence_near_miss_gap_comparison",
    "result_card_object_source_projection",
    "api_projection",
    "static_projection",
    "privacy",
    "limitations",
    "no_winner_without_evidence_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_comparison_page_implemented",
    "persistent_comparison_page_store_implemented",
    "comparison_page_generated_from_live_source",
    "comparison_winner_claimed",
    "live_source_called",
    "external_calls_performed",
    "source_sync_worker_executed",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "source_trust_claimed",
    "telemetry_exported",
}
PAGE_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "fixture_comparison",
    "recorded_fixture_comparison",
    "candidate_comparison",
    "conflicted_comparison",
    "runtime_future",
    "rejected_by_policy",
}
COMPARISON_SCOPES = {
    "object_to_object",
    "version_to_version",
    "source_to_source",
    "representation_to_representation",
    "compatibility_claims",
    "evidence_to_evidence",
    "candidate_to_candidate",
    "near_miss_to_result",
    "mixed",
    "unknown",
}
COMPARISON_BASES = {
    "synthetic_example",
    "fixture_backed",
    "recorded_fixture_backed",
    "public_index_future",
    "source_cache_future",
    "evidence_ledger_future",
    "candidate_index_future",
    "manual_review_future",
    "unknown",
}
COMPARISON_TYPES = {
    "object_identity_comparison",
    "version_comparison",
    "source_coverage_comparison",
    "representation_comparison",
    "member_comparison",
    "compatibility_comparison",
    "evidence_strength_comparison",
    "provenance_comparison",
    "rights_risk_action_comparison",
    "conflict_comparison",
    "absence_near_miss_comparison",
    "candidate_review_comparison",
    "unknown",
}
COMPARISON_GOALS = {
    "explain_same_or_different",
    "choose_review_priority",
    "explain_conflict",
    "explain_source_coverage",
    "explain_compatibility",
    "explain_safe_action",
    "explain_absence",
    "unknown",
}
SUBJECT_KINDS = {
    "object_page",
    "source_page",
    "public_search_result",
    "public_index_document",
    "source_cache_record",
    "evidence_ledger_record",
    "candidate_index_record",
    "known_absence_page",
    "synthetic_example",
    "unknown",
}
SUBJECT_STATUSES = {"fixture_backed", "recorded_fixture_backed", "candidate", "review_required", "placeholder", "future", "conflicted", "unknown"}
CRITERION_TYPES = {
    "identity_match",
    "version_match",
    "platform_compatibility",
    "architecture_compatibility",
    "source_coverage",
    "evidence_strength",
    "provenance_quality",
    "representation_availability",
    "member_access",
    "rights_access",
    "risk_posture",
    "actionability",
    "conflict_status",
    "absence_scope",
    "user_cost",
    "unknown",
}
SCORING_POLICIES = {"descriptive_only", "categorical", "future_weighted", "not_scored"}
MATRIX_KINDS = {"descriptive", "categorical", "future_scored"}
CELL_STATUSES = {"supported", "unsupported", "unknown", "conflicting", "not_applicable", "evidence_required"}
CONFIDENCES = {"low", "medium", "high", "unknown"}
IDENTITY_RELATIONS = {"same_as", "likely_same", "variant_of", "different", "conflicting", "unknown"}
DUPLICATE_POLICIES = {"preserve_separate", "merge_review_required", "future_deduplication", "not_applicable"}
VERSION_STATUSES = {"known", "inferred", "unknown", "conflicting"}
AVAILABILITY_STATUSES = {"metadata_only", "available_source_unknown", "access_restricted", "unavailable", "future", "unknown"}
MEMBER_STATUSES = {"fixture_observed", "evidence_candidate", "future_extraction", "unknown"}
SOURCE_ROLES = {"primary", "supporting", "conflicting", "near_miss", "not_checked"}
EVIDENCE_STATUSES = {"fixture", "recorded_fixture", "source_cache_future", "evidence_ledger_future", "candidate", "review_required", "insufficient"}
COMPATIBILITY_RELATIONS = {"equivalent", "one_more_specific", "one_better_supported_by_evidence", "conflicting", "unknown"}
CONFLICT_STATUSES = {
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
RESOLUTION_STATUSES = {"not_needed", "unresolved", "review_required", "future_resolution"}
ABSENCE_STATUSES = {"not_absent", "scoped_absence", "no_verified_result", "mixed", "unknown"}
GAP_TYPES = {
    "source_coverage_gap",
    "capability_gap",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "query_interpretation_gap",
    "live_probe_disabled",
    "external_baseline_pending",
    "deep_extraction_missing",
    "OCR_missing",
    "source_cache_missing",
    "evidence_ledger_missing",
    "unknown",
}
PROJECTION_STATUSES = {"contract_only", "future", "demo"}
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "private_local_path",
    "raw_source_payload",
    "download_url",
    "install_url",
    "execute_url",
    "source_credentials",
    "comparison_page_path",
    "object_page_path",
    "source_page_path",
    "source_cache_path",
    "evidence_ledger_path",
    "connector_path",
    "candidate_path",
    "promotion_path",
    "index_path",
    "store_root",
    "local_path",
    "database_path",
    "source_root",
}


def validate_page(path: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payload = _read_json(path, errors)
    if isinstance(payload, Mapping):
        _validate_payload(payload, errors)
        _scan_sensitive_values(payload, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "page": _rel(path),
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def validate_page_root(root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    page_path = root / "COMPARISON_PAGE.json"
    page_report = validate_page(page_path, strict=strict)
    errors.extend(page_report["errors"])
    warnings.extend(page_report["warnings"])
    _validate_checksums(root, errors)
    return {
        "status": "valid" if not errors else "invalid",
        "page_root": _rel(root),
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def validate_all_examples(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    roots = [path for path in sorted(EXAMPLES_ROOT.iterdir()) if path.is_dir()] if EXAMPLES_ROOT.is_dir() else []
    if not roots:
        errors.append("examples/comparison_pages: no example roots found.")
    reports = []
    for root in roots:
        report = validate_page_root(root, strict=strict)
        reports.append(report)
        errors.extend(f"{report['page_root']}: {error}" for error in report["errors"])
        warnings.extend(f"{report['page_root']}: {warning}" for warning in report["warnings"])
    return {
        "status": "valid" if not errors else "invalid",
        "example_count": len(roots),
        "examples": [_rel(root) for root in roots],
        "reports": reports,
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
    }


def _validate_payload(page: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted((TOP_LEVEL_REQUIRED | HARD_FALSE_FIELDS) - set(page))
    if missing:
        errors.append(f"missing required top-level fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0.")
    if page.get("comparison_page_kind") != "comparison_page":
        errors.append("comparison_page_kind must be comparison_page.")
    if page.get("status") not in PAGE_STATUSES:
        errors.append("status is not an allowed Comparison Page v0 status.")
    for key in sorted(HARD_FALSE_FIELDS):
        if page.get(key) is not False:
            errors.append(f"{key} must be false.")

    identity = _mapping(page.get("comparison_identity"))
    if identity.get("comparison_scope") not in COMPARISON_SCOPES:
        errors.append("comparison_identity.comparison_scope is not allowed.")
    if identity.get("comparison_basis") not in COMPARISON_BASES:
        errors.append("comparison_identity.comparison_basis is not allowed.")

    comparison_type = _mapping(page.get("comparison_type"))
    if comparison_type.get("type") not in COMPARISON_TYPES:
        errors.append("comparison_type.type is not allowed.")
    if comparison_type.get("comparison_goal") not in COMPARISON_GOALS:
        errors.append("comparison_type.comparison_goal is not allowed.")
    if comparison_type.get("winner_allowed") is not False:
        errors.append("comparison_type.winner_allowed must be false.")

    subjects = _list(page.get("subjects"))
    if len(subjects) < 2:
        errors.append("subjects must contain at least two entries.")
    subject_refs: set[str] = set()
    for index, subject_value in enumerate(subjects):
        subject = _mapping(subject_value)
        ref = subject.get("subject_ref")
        if not isinstance(ref, str) or not ref:
            errors.append(f"subjects[{index}].subject_ref must be present.")
        else:
            subject_refs.add(ref)
        if subject.get("subject_kind") not in SUBJECT_KINDS:
            errors.append(f"subjects[{index}].subject_kind is not allowed.")
        if subject.get("subject_status") not in SUBJECT_STATUSES:
            errors.append(f"subjects[{index}].subject_status is not allowed.")

    criteria = _list(page.get("criteria"))
    if not criteria:
        errors.append("criteria must be present.")
    criterion_ids: set[str] = set()
    for index, criterion_value in enumerate(criteria):
        criterion = _mapping(criterion_value)
        criterion_id = criterion.get("criterion_id")
        if isinstance(criterion_id, str) and criterion_id:
            criterion_ids.add(criterion_id)
        else:
            errors.append(f"criteria[{index}].criterion_id must be present.")
        if criterion.get("criterion_type") not in CRITERION_TYPES:
            errors.append(f"criteria[{index}].criterion_type is not allowed.")
        if criterion.get("scoring_policy") not in SCORING_POLICIES:
            errors.append(f"criteria[{index}].scoring_policy is not allowed.")

    matrix = _mapping(page.get("comparison_matrix"))
    if matrix.get("matrix_kind") not in MATRIX_KINDS:
        errors.append("comparison_matrix.matrix_kind is not allowed.")
    for key in ("scoring_used_now", "ranking_used_now", "winner_selected_now"):
        if matrix.get(key) is not False:
            errors.append(f"comparison_matrix.{key} must be false.")
    cells = _list(matrix.get("cells"))
    if not cells:
        errors.append("comparison_matrix.cells must be present.")
    for index, cell_value in enumerate(cells):
        cell = _mapping(cell_value)
        if cell.get("subject_ref") not in subject_refs:
            errors.append(f"comparison_matrix.cells[{index}].subject_ref must match a subject_ref.")
        if cell.get("criterion_id") not in criterion_ids:
            errors.append(f"comparison_matrix.cells[{index}].criterion_id must match a criterion_id.")
        if cell.get("status") not in CELL_STATUSES:
            errors.append(f"comparison_matrix.cells[{index}].status is not allowed.")
        if cell.get("confidence") not in CONFIDENCES:
            errors.append(f"comparison_matrix.cells[{index}].confidence is not allowed.")
        if cell.get("confidence_not_truth") is not True:
            errors.append(f"comparison_matrix.cells[{index}].confidence_not_truth must be true.")

    no_winner = _mapping(page.get("no_winner_without_evidence_guarantees"))
    if no_winner.get("winner_allowed") is not False:
        errors.append("no_winner_without_evidence_guarantees.winner_allowed must be false.")
    if no_winner.get("comparison_winner_claimed") is not False:
        errors.append("no_winner_without_evidence_guarantees.comparison_winner_claimed must be false.")
    if no_winner.get("winner_selected_now") is not False:
        errors.append("no_winner_without_evidence_guarantees.winner_selected_now must be false.")

    identity_comparison = _mapping(page.get("identity_comparison"))
    if identity_comparison.get("identity_relation") not in IDENTITY_RELATIONS:
        errors.append("identity_comparison.identity_relation is not allowed.")
    if identity_comparison.get("duplicate_policy") not in DUPLICATE_POLICIES:
        errors.append("identity_comparison.duplicate_policy is not allowed.")
    if identity_comparison.get("destructive_merge_allowed") is not False:
        errors.append("identity_comparison.destructive_merge_allowed must be false.")

    versions = _mapping(page.get("version_state_release_comparison"))
    for index, version_value in enumerate(_list(versions.get("versions_compared"))):
        if _mapping(version_value).get("version_status") not in VERSION_STATUSES:
            errors.append(f"version_state_release_comparison.versions_compared[{index}].version_status is not allowed.")

    representations = _mapping(page.get("representation_member_comparison"))
    if representations.get("payload_included") is not False:
        errors.append("representation_member_comparison.payload_included must be false.")
    if representations.get("downloads_enabled") is not False:
        errors.append("representation_member_comparison.downloads_enabled must be false.")
    for index, rep_value in enumerate(_list(representations.get("representations_compared"))):
        if _mapping(rep_value).get("availability_status") not in AVAILABILITY_STATUSES:
            errors.append(f"representation_member_comparison.representations_compared[{index}].availability_status is not allowed.")
    for index, member_value in enumerate(_list(representations.get("members_compared"))):
        if _mapping(member_value).get("member_status") not in MEMBER_STATUSES:
            errors.append(f"representation_member_comparison.members_compared[{index}].member_status is not allowed.")

    source_evidence = _mapping(page.get("source_evidence_provenance_comparison"))
    if source_evidence.get("accepted_as_truth") is not False:
        errors.append("source_evidence_provenance_comparison.accepted_as_truth must be false.")
    for index, source_value in enumerate(_list(source_evidence.get("sources_compared"))):
        source = _mapping(source_value)
        if source.get("source_role") not in SOURCE_ROLES:
            errors.append(f"source_evidence_provenance_comparison.sources_compared[{index}].source_role is not allowed.")
        if source.get("source_trust_claimed") is not False:
            errors.append(f"source_evidence_provenance_comparison.sources_compared[{index}].source_trust_claimed must be false.")
    for index, evidence_value in enumerate(_list(source_evidence.get("evidence_compared"))):
        evidence = _mapping(evidence_value)
        if evidence.get("evidence_status") not in EVIDENCE_STATUSES:
            errors.append(f"source_evidence_provenance_comparison.evidence_compared[{index}].evidence_status is not allowed.")
        if evidence.get("confidence") not in CONFIDENCES:
            errors.append(f"source_evidence_provenance_comparison.evidence_compared[{index}].confidence is not allowed.")
        if evidence.get("confidence_not_truth") is not True:
            errors.append(f"source_evidence_provenance_comparison.evidence_compared[{index}].confidence_not_truth must be true.")

    compatibility = _mapping(page.get("compatibility_comparison"))
    if compatibility.get("compatibility_relation") not in COMPATIBILITY_RELATIONS:
        errors.append("compatibility_comparison.compatibility_relation is not allowed.")
    if compatibility.get("compatibility_claim_scoped") is not True:
        errors.append("compatibility_comparison.compatibility_claim_scoped must be true.")

    actions = _mapping(page.get("rights_risk_action_comparison"))
    for key in (
        "rights_clearance_claimed",
        "malware_safety_claimed",
        "downloads_enabled",
        "installs_enabled",
        "execution_enabled",
        "uploads_enabled",
        "mirroring_enabled",
        "arbitrary_url_fetch_enabled",
    ):
        if actions.get(key) is not False:
            errors.append(f"rights_risk_action_comparison.{key} must be false.")

    conflicts = _mapping(page.get("conflicts_and_disagreements"))
    if conflicts.get("conflict_status") not in CONFLICT_STATUSES:
        errors.append("conflicts_and_disagreements.conflict_status is not allowed.")
    conflict_items = _list(conflicts.get("conflicts"))
    if conflict_items and conflicts.get("disagreement_preserved") is not True:
        errors.append("conflicts_and_disagreements.disagreement_preserved must be true when conflicts exist.")
    if conflicts.get("disagreement_preserved") is not True:
        errors.append("conflicts_and_disagreements.disagreement_preserved must be true.")
    if conflicts.get("destructive_merge_allowed") is not False:
        errors.append("conflicts_and_disagreements.destructive_merge_allowed must be false.")
    if conflicts.get("resolution_status") not in RESOLUTION_STATUSES:
        errors.append("conflicts_and_disagreements.resolution_status is not allowed.")

    absence = _mapping(page.get("absence_near_miss_gap_comparison"))
    if absence.get("absence_status") not in ABSENCE_STATUSES:
        errors.append("absence_near_miss_gap_comparison.absence_status is not allowed.")
    if absence.get("global_absence_claimed") is not False:
        errors.append("absence_near_miss_gap_comparison.global_absence_claimed must be false.")
    for index, gap_value in enumerate(_list(absence.get("gaps_compared"))):
        if _mapping(gap_value).get("gap_type") not in GAP_TYPES:
            errors.append(f"absence_near_miss_gap_comparison.gaps_compared[{index}].gap_type is not allowed.")

    projection = _mapping(page.get("result_card_object_source_projection"))
    if projection.get("projection_status") not in PROJECTION_STATUSES:
        errors.append("result_card_object_source_projection.projection_status is not allowed.")
    api = _mapping(page.get("api_projection"))
    if api.get("response_kind") != "comparison_page_response":
        errors.append("api_projection.response_kind must be comparison_page_response.")
    if api.get("implemented_now") is not False:
        errors.append("api_projection.implemented_now must be false.")
    static = _mapping(page.get("static_projection"))
    if static.get("generated_static_artifact") is not False:
        errors.append("static_projection.generated_static_artifact must be false for P81 examples.")

    privacy = _mapping(page.get("privacy"))
    if privacy.get("privacy_classification") not in PRIVACY_CLASSIFICATIONS:
        errors.append("privacy.privacy_classification is not allowed.")
    for key in ("contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query"):
        if privacy.get(key) is not False:
            errors.append(f"privacy.{key} must be false.")
    if privacy.get("publishable") is not True:
        errors.append("privacy.publishable must be true for public-safe examples.")


def _validate_checksums(root: Path, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.is_file():
        errors.append("CHECKSUMS.SHA256 is missing.")
        return
    lines = [line.strip() for line in checksum_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        errors.append("CHECKSUMS.SHA256 has no entries.")
        return
    for line in lines:
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"CHECKSUMS.SHA256 entry is malformed: {line!r}")
            continue
        expected, rel = parts
        target = root / rel
        if not target.is_file():
            errors.append(f"CHECKSUMS.SHA256 references missing file: {rel}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"CHECKSUMS.SHA256 mismatch for {rel}.")


def _scan_sensitive_values(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{path}.{key_text}: forbidden key for public comparison page examples.")
            _scan_sensitive_values(nested, errors, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan_sensitive_values(nested, errors, f"{path}[{index}]")
    elif isinstance(value, str):
        if PRIVATE_PATH_RE.search(value):
            errors.append(f"{path}: contains private or absolute path-like value.")
        if SECRET_RE.search(value):
            errors.append(f"{path}: contains credential-like value.")
        if IP_RE.search(value):
            errors.append(f"{path}: contains IP-address-like value.")
        if ACCOUNT_RE.search(value):
            errors.append(f"{path}: contains account/user identifier-like value.")


def _read_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _emit(report: Mapping[str, Any], *, json_mode: bool, stream: TextIO) -> None:
    if json_mode:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
        return
    stream.write(f"status: {report['status']}\n")
    if "example_count" in report:
        stream.write(f"example_count: {report['example_count']}\n")
    if report.get("errors"):
        stream.write("errors:\n")
        for error in report["errors"]:
            stream.write(f"- {error}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Comparison Page v0 examples.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--page", type=Path, help="Validate one COMPARISON_PAGE.json file.")
    group.add_argument("--page-root", type=Path, help="Validate one example root containing COMPARISON_PAGE.json and CHECKSUMS.SHA256.")
    group.add_argument("--all-examples", action="store_true", help="Validate all examples/comparison_pages roots.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation metadata in output.")
    return parser


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    if args.page:
        report = validate_page(args.page, strict=args.strict)
    elif args.page_root:
        report = validate_page_root(args.page_root, strict=args.strict)
    else:
        report = validate_all_examples(strict=args.strict)
    _emit(report, json_mode=args.json, stream=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
