#!/usr/bin/env python3
"""Validate Cross-Source Identity Resolution Assessment v0 examples.

This validator is stdlib-only and local-only. It performs no external calls,
does not execute connectors, and does not mutate source cache, evidence ledger,
candidate index, public index, local index, or master index state.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "identity_resolution"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "assessment_id",
    "assessment_kind",
    "status",
    "created_by_tool",
    "assessment_scope",
    "subjects",
    "asserted_relation",
    "relation_evidence",
    "identifier_evidence",
    "alias_name_evidence",
    "version_platform_architecture_evidence",
    "source_provenance_evidence",
    "hash_checksum_intrinsic_id_model",
    "package_repository_archive_capture_identity",
    "representation_member_evidence",
    "conflicts",
    "confidence",
    "review",
    "promotion_and_merge_boundary",
    "public_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_identity_resolution_implemented",
    "persistent_identity_store_implemented",
    "identity_cluster_created",
    "records_merged",
    "destructive_merge_performed",
    "candidate_promotion_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
}
ASSESSMENT_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "candidate_relation",
    "review_required",
    "conflicted",
    "rejected_by_policy",
    "runtime_future",
}
SCOPE_KINDS = {
    "object_identity",
    "version_identity",
    "representation_identity",
    "member_identity",
    "source_identity",
    "package_identity",
    "repository_identity",
    "archive_capture_identity",
    "compatibility_claim_identity",
    "candidate_identity",
    "mixed",
    "unknown",
}
ASSESSMENT_BASES = {
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
RELATION_GOALS = {
    "determine_same",
    "determine_variant",
    "determine_version_relation",
    "determine_representation_relation",
    "determine_member_relation",
    "determine_conflict",
    "preserve_uncertainty",
    "unknown",
}
SUBJECT_KINDS = {
    "object_page",
    "source_page",
    "comparison_page",
    "public_search_result",
    "public_index_document",
    "source_cache_record",
    "evidence_ledger_record",
    "candidate_index_record",
    "source_pack_record",
    "evidence_pack_record",
    "synthetic_example",
    "unknown",
}
SUBJECT_STATUSES = {
    "fixture_backed",
    "recorded_fixture_backed",
    "candidate",
    "review_required",
    "placeholder",
    "future",
    "conflicted",
    "unknown",
}
RELATION_TYPES = {
    "exact_same_object",
    "likely_same_object",
    "possible_same_object",
    "variant_of",
    "version_of",
    "release_of",
    "representation_of",
    "member_of",
    "source_record_for",
    "package_record_for",
    "repository_record_for",
    "capture_of",
    "alias_of",
    "near_match",
    "different_object",
    "conflicting_identity",
    "unknown",
}
RELATION_STATUSES = {"asserted_example", "candidate", "review_required", "conflicted", "rejected", "future"}
IDENTIFIER_KINDS = {
    "sha256",
    "sha1",
    "md5",
    "checksum",
    "DOI",
    "ISBN",
    "package_url",
    "SWHID",
    "GitHub_owner_repo",
    "package_name",
    "version_string",
    "archive_item_identifier",
    "wayback_uri_r",
    "file_name",
    "member_path",
    "source_native_id",
    "unknown",
}
IDENTIFIER_STATUSES = {"exact_match", "normalized_match", "conflicting", "missing", "not_applicable", "review_required"}
IDENTIFIER_STRENGTHS = {"intrinsic_strong", "strong", "medium", "weak", "unknown"}
NAME_SIMILARITY_STATUSES = {
    "exact_name_match",
    "normalized_name_match",
    "alias_match",
    "weak_similarity",
    "conflicting_names",
    "insufficient",
}
NAME_MATCH_STRENGTHS = {"weak", "medium", "strong", "unknown"}
VERSION_RELATIONS = {"same_version", "different_version", "version_range_overlap", "one_newer", "one_older", "unknown", "conflicting"}
PLATFORM_RELATIONS = {"same_platform", "overlapping_platforms", "different_platforms", "unknown", "conflicting"}
ARCHITECTURE_RELATIONS = {"same_architecture", "overlapping_architectures", "different_architectures", "unknown", "conflicting"}
SOURCE_RELATIONS = {
    "same_source_record",
    "different_sources_same_identifier",
    "different_sources_conflict",
    "source_only_match",
    "source_missing",
    "unknown",
}
PROVENANCE_STATUSES = {"fixture", "recorded_fixture", "source_cache_future", "evidence_ledger_future", "candidate", "review_required", "insufficient"}
REPRESENTATION_RELATIONS = {"same_representation", "different_representation", "variant_representation", "parent_child_representation", "unknown", "conflicting"}
MEMBER_RELATIONS = {"same_member", "different_member", "member_of_same_container", "parent_child_member", "unknown", "conflicting"}
CONTAINER_RELATIONS = {"same_container", "different_container", "unknown", "conflicting"}
CONFLICT_STATUSES = {
    "none_known",
    "possible_duplicate",
    "identity_conflict",
    "version_conflict",
    "source_conflict",
    "representation_conflict",
    "member_conflict",
    "package_conflict",
    "repository_conflict",
    "capture_conflict",
    "evidence_conflict",
    "rights_or_access_conflict",
    "unresolved",
    "unknown",
}
CONFIDENCE_CLASSES = {"low", "medium", "high", "unknown"}
CONFIDENCE_BASES = {
    "exact_intrinsic_identifier",
    "exact_hash_match",
    "package_url_match",
    "SWHID_match",
    "source_native_id_match",
    "alias_name_match",
    "version_platform_match",
    "source_provenance_match",
    "manual_review_future",
    "insufficient",
    "conflicting",
    "unknown",
}
REVIEW_STATUSES = {
    "unreviewed",
    "structurally_valid",
    "evidence_required",
    "human_review_required",
    "policy_review_required",
    "conflict_review_required",
    "duplicate_review_required",
    "promotion_review_required",
    "rejected_future",
    "accepted_future",
}
PUBLIC_VISIBILITIES = {"public_safe_example", "local_private", "review_required", "restricted"}
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}
STRONG_IDENTIFIER_KINDS = {"sha256", "checksum", "DOI", "ISBN", "package_url", "SWHID", "GitHub_owner_repo", "archive_item_identifier", "source_native_id"}
STRONG_IDENTIFIER_STRENGTHS = {"intrinsic_strong", "strong"}

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "identity_resolution_path",
    "identity_cluster_path",
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
    "private_local_path",
    "raw_source_payload",
    "download_url",
    "install_url",
    "execute_url",
    "source_credentials",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_strings(value: Any, key_path: str = ""):
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield from iter_strings(item, f"{key_path}.{key}" if key_path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{key_path}[{index}]")
    elif isinstance(value, str):
        yield key_path, value


def iter_keys(value: Any, key_path: str = ""):
    if isinstance(value, Mapping):
        for key, item in value.items():
            path = f"{key_path}.{key}" if key_path else str(key)
            yield path, str(key)
            yield from iter_keys(item, path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_keys(item, f"{key_path}[{index}]")


def validate_checksum_file(example_root: Path) -> list[str]:
    errors: list[str] = []
    checksum_path = example_root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        return [f"{example_root}: missing CHECKSUMS.SHA256"]
    for line_number, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            errors.append(f"{checksum_path}:{line_number}: invalid checksum line")
            continue
        expected, rel = parts
        file_path = example_root / rel.strip()
        if not file_path.exists():
            errors.append(f"{checksum_path}:{line_number}: missing checksummed file {rel}")
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"{checksum_path}:{line_number}: checksum mismatch for {rel}")
    return errors


def check_enum(errors: list[str], path: str, value: Any, allowed: set[str]) -> None:
    if value not in allowed:
        errors.append(f"{path} must be one of {sorted(allowed)}, got {value!r}")


def check_false(errors: list[str], path: str, value: Any) -> None:
    if value is not False:
        errors.append(f"{path} must be false")


def validate_sensitive_content(page: Mapping[str, Any], errors: list[str]) -> None:
    for key_path, key in iter_keys(page):
        if key in FORBIDDEN_KEYS:
            errors.append(f"{key_path}: forbidden key {key!r}")
    for key_path, text in iter_strings(page):
        if PRIVATE_PATH_RE.search(text):
            errors.append(f"{key_path}: contains private absolute path or file URL")
        if SECRET_RE.search(text):
            errors.append(f"{key_path}: contains credential-like text")
        if IP_RE.search(text):
            errors.append(f"{key_path}: contains IP address")
        if ACCOUNT_RE.search(text):
            errors.append(f"{key_path}: contains account/user identifier")


def has_strong_identifier(page: Mapping[str, Any]) -> bool:
    hash_model = page.get("hash_checksum_intrinsic_id_model", {})
    if isinstance(hash_model, Mapping) and hash_model.get("exact_hash_match_present") is True:
        return True
    for item in page.get("identifier_evidence", []):
        if not isinstance(item, Mapping):
            continue
        if item.get("identifier_status") != "exact_match":
            continue
        if item.get("strength") not in STRONG_IDENTIFIER_STRENGTHS:
            continue
        if item.get("identifier_kind") in STRONG_IDENTIFIER_KINDS:
            return True
    return False


def validate_assessment(page: Mapping[str, Any], *, source: str = "<memory>") -> list[str]:
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_REQUIRED - page.keys())
    if missing:
        errors.append(f"{source}: missing required fields: {', '.join(missing)}")

    if page.get("schema_version") != "0.1.0":
        errors.append(f"{source}: schema_version must be 0.1.0")
    if page.get("assessment_kind") != "identity_resolution_assessment":
        errors.append(f"{source}: assessment_kind must be identity_resolution_assessment")
    check_enum(errors, "status", page.get("status"), ASSESSMENT_STATUSES)
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, page.get(key))

    scope = page.get("assessment_scope", {})
    if isinstance(scope, Mapping):
        check_enum(errors, "assessment_scope.scope_kind", scope.get("scope_kind"), SCOPE_KINDS)
        check_enum(errors, "assessment_scope.assessment_basis", scope.get("assessment_basis"), ASSESSMENT_BASES)
        check_enum(errors, "assessment_scope.relation_goal", scope.get("relation_goal"), RELATION_GOALS)
    else:
        errors.append("assessment_scope must be an object")

    subjects = page.get("subjects", [])
    if not isinstance(subjects, list) or len(subjects) < 2:
        errors.append("subjects must contain at least two subjects")
    else:
        for index, subject in enumerate(subjects):
            if not isinstance(subject, Mapping):
                errors.append(f"subjects[{index}] must be an object")
                continue
            check_enum(errors, f"subjects[{index}].subject_kind", subject.get("subject_kind"), SUBJECT_KINDS)
            check_enum(errors, f"subjects[{index}].subject_status", subject.get("subject_status"), SUBJECT_STATUSES)
            if not subject.get("subject_ref"):
                errors.append(f"subjects[{index}].subject_ref is required")

    relation = page.get("asserted_relation", {})
    if isinstance(relation, Mapping):
        check_enum(errors, "asserted_relation.relation_type", relation.get("relation_type"), RELATION_TYPES)
        check_enum(errors, "asserted_relation.relation_status", relation.get("relation_status"), RELATION_STATUSES)
        if relation.get("relation_claim_not_truth") is not True:
            errors.append("asserted_relation.relation_claim_not_truth must be true")
        check_false(errors, "asserted_relation.global_merge_allowed", relation.get("global_merge_allowed"))
        if relation.get("relation_type") == "exact_same_object" and not has_strong_identifier(page):
            errors.append("exact_same_object requires exact strong identifier evidence")
    else:
        errors.append("asserted_relation must be an object")

    identifiers = page.get("identifier_evidence", [])
    if not isinstance(identifiers, list):
        errors.append("identifier_evidence must be a list")
    else:
        for index, item in enumerate(identifiers):
            if not isinstance(item, Mapping):
                errors.append(f"identifier_evidence[{index}] must be an object")
                continue
            check_enum(errors, f"identifier_evidence[{index}].identifier_kind", item.get("identifier_kind"), IDENTIFIER_KINDS)
            check_enum(errors, f"identifier_evidence[{index}].identifier_status", item.get("identifier_status"), IDENTIFIER_STATUSES)
            check_enum(errors, f"identifier_evidence[{index}].strength", item.get("strength"), IDENTIFIER_STRENGTHS)
            if item.get("identifier_value_public_safe") is not True:
                errors.append(f"identifier_evidence[{index}].identifier_value_public_safe must be true")

    alias = page.get("alias_name_evidence", {})
    if isinstance(alias, Mapping):
        check_enum(errors, "alias_name_evidence.name_similarity_status", alias.get("name_similarity_status"), NAME_SIMILARITY_STATUSES)
        check_enum(errors, "alias_name_evidence.name_match_strength", alias.get("name_match_strength"), NAME_MATCH_STRENGTHS)
        if alias.get("name_match_not_sufficient_alone") is not True:
            errors.append("alias_name_evidence.name_match_not_sufficient_alone must be true")
    else:
        errors.append("alias_name_evidence must be an object")

    vpa = page.get("version_platform_architecture_evidence", {})
    if isinstance(vpa, Mapping):
        check_enum(errors, "version_platform_architecture_evidence.version_relation", vpa.get("version_relation"), VERSION_RELATIONS)
        check_enum(errors, "version_platform_architecture_evidence.platform_relation", vpa.get("platform_relation"), PLATFORM_RELATIONS)
        check_enum(errors, "version_platform_architecture_evidence.architecture_relation", vpa.get("architecture_relation"), ARCHITECTURE_RELATIONS)
    else:
        errors.append("version_platform_architecture_evidence must be an object")

    source_provenance = page.get("source_provenance_evidence", {})
    if isinstance(source_provenance, Mapping):
        check_enum(errors, "source_provenance_evidence.source_relation", source_provenance.get("source_relation"), SOURCE_RELATIONS)
        check_enum(errors, "source_provenance_evidence.provenance_status", source_provenance.get("provenance_status"), PROVENANCE_STATUSES)
        check_false(errors, "source_provenance_evidence.source_trust_claimed", source_provenance.get("source_trust_claimed"))
        if source_provenance.get("provenance_not_truth") is not True:
            errors.append("source_provenance_evidence.provenance_not_truth must be true")
    else:
        errors.append("source_provenance_evidence must be an object")

    representation = page.get("representation_member_evidence", {})
    if isinstance(representation, Mapping):
        check_enum(errors, "representation_member_evidence.representation_relation", representation.get("representation_relation"), REPRESENTATION_RELATIONS)
        check_enum(errors, "representation_member_evidence.member_relation", representation.get("member_relation"), MEMBER_RELATIONS)
        check_enum(errors, "representation_member_evidence.container_relation", representation.get("container_relation"), CONTAINER_RELATIONS)
        check_false(errors, "representation_member_evidence.payload_included", representation.get("payload_included"))
        check_false(errors, "representation_member_evidence.downloads_enabled", representation.get("downloads_enabled"))
    else:
        errors.append("representation_member_evidence must be an object")

    conflicts = page.get("conflicts", {})
    if isinstance(conflicts, Mapping):
        check_enum(errors, "conflicts.conflict_status", conflicts.get("conflict_status"), CONFLICT_STATUSES)
        check_false(errors, "conflicts.destructive_merge_allowed", conflicts.get("destructive_merge_allowed"))
        conflict_items = conflicts.get("conflicts", [])
        if conflict_items and conflicts.get("disagreement_preserved") is not True:
            errors.append("conflicts.disagreement_preserved must be true when conflicts exist")
    else:
        errors.append("conflicts must be an object")

    confidence = page.get("confidence", {})
    if isinstance(confidence, Mapping):
        check_enum(errors, "confidence.confidence_class", confidence.get("confidence_class"), CONFIDENCE_CLASSES)
        check_enum(errors, "confidence.confidence_basis", confidence.get("confidence_basis"), CONFIDENCE_BASES)
        if confidence.get("confidence_not_truth") is not True:
            errors.append("confidence.confidence_not_truth must be true")
        check_false(errors, "confidence.confidence_sufficient_for_merge_now", confidence.get("confidence_sufficient_for_merge_now"))
    else:
        errors.append("confidence must be an object")

    review = page.get("review", {})
    if isinstance(review, Mapping):
        check_enum(errors, "review.review_status", review.get("review_status"), REVIEW_STATUSES)
        if review.get("promotion_policy_required") is not True:
            errors.append("review.promotion_policy_required must be true")
        if review.get("destructive_merge_forbidden") is not True:
            errors.append("review.destructive_merge_forbidden must be true")
    else:
        errors.append("review must be an object")

    boundary = page.get("promotion_and_merge_boundary", {})
    if isinstance(boundary, Mapping):
        for key in (
            "merge_runtime_implemented",
            "merge_allowed_now",
            "destructive_merge_allowed",
            "canonicalization_allowed_now",
            "public_index_update_allowed_now",
        ):
            check_false(errors, f"promotion_and_merge_boundary.{key}", boundary.get(key))
    else:
        errors.append("promotion_and_merge_boundary must be an object")

    public_projection = page.get("public_projection", {})
    if isinstance(public_projection, Mapping):
        check_enum(errors, "public_projection.public_visibility", public_projection.get("public_visibility"), PUBLIC_VISIBILITIES)
    else:
        errors.append("public_projection must be an object")

    privacy = page.get("privacy", {})
    if isinstance(privacy, Mapping):
        check_enum(errors, "privacy.privacy_classification", privacy.get("privacy_classification"), PRIVACY_CLASSIFICATIONS)
        for key in (
            "contains_private_path",
            "contains_secret",
            "contains_private_url",
            "contains_user_identifier",
            "contains_ip_address",
            "contains_raw_private_query",
            "contains_private_repository",
            "contains_private_package",
        ):
            check_false(errors, f"privacy.{key}", privacy.get(key))
    else:
        errors.append("privacy must be an object")

    validate_sensitive_content(page, errors)
    return [f"{source}: {error}" for error in errors]


def discover_example_assessments() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(EXAMPLES_ROOT.glob("*/IDENTITY_RESOLUTION_ASSESSMENT.json"))


def validate_path(path: Path) -> list[str]:
    try:
        page = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive CLI path
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{path}: assessment must be a JSON object"]
    errors = validate_assessment(page, source=str(path))
    return errors


def validate_example_root(root: Path) -> list[str]:
    page_path = root / "IDENTITY_RESOLUTION_ASSESSMENT.json"
    if not page_path.exists():
        return [f"{root}: missing IDENTITY_RESOLUTION_ASSESSMENT.json"]
    errors = validate_path(page_path)
    errors.extend(validate_checksum_file(root))
    return errors


def validate_all_examples() -> Mapping[str, Any]:
    paths = discover_example_assessments()
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_example_root(path.parent))
    return {
        "status": "valid" if not errors else "invalid",
        "example_count": len(paths),
        "validated_paths": [str(path.relative_to(REPO_ROOT)) for path in paths],
        "errors": errors,
    }


def build_report(args: argparse.Namespace) -> Mapping[str, Any]:
    if args.all_examples:
        return validate_all_examples()
    targets: list[Path] = []
    if args.assessment:
        targets.append(Path(args.assessment))
    if args.assessment_root:
        targets.append(Path(args.assessment_root) / "IDENTITY_RESOLUTION_ASSESSMENT.json")
    if not targets:
        targets = discover_example_assessments()
    errors: list[str] = []
    validated: list[str] = []
    for target in targets:
        target = target if target.is_absolute() else (REPO_ROOT / target)
        errors.extend(validate_path(target))
        validated.append(str(target))
    return {
        "status": "valid" if not errors else "invalid",
        "example_count": len(validated),
        "validated_paths": validated,
        "errors": errors,
    }


def emit_report(report: Mapping[str, Any], *, json_output: bool, stream: TextIO) -> None:
    if json_output:
        stream.write(json.dumps(report, indent=2) + "\n")
        return
    stream.write(f"status: {report['status']}\n")
    stream.write(f"example_count: {report['example_count']}\n")
    for path in report.get("validated_paths", []):
        stream.write(f"validated: {path}\n")
    for error in report.get("errors", []):
        stream.write(f"error: {error}\n")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", help="Validate a single assessment JSON path.")
    parser.add_argument("--assessment-root", help="Validate IDENTITY_RESOLUTION_ASSESSMENT.json under a root.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all identity resolution examples.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Kept for command compatibility; validation is strict by default.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_report(args)
    emit_report(report, json_output=args.json, stream=sys.stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
