#!/usr/bin/env python3
"""Validate Result Merge Group v0 examples.

The validator is stdlib-only and local-only. It performs no network calls,
does not execute connectors, does not group live search results, and mutates no
source cache, evidence ledger, candidate index, public index, local index, or
master index state.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "result_merge"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "result_merge_group_id",
    "result_merge_group_kind",
    "status",
    "created_by_tool",
    "merge_group_identity",
    "group_relation",
    "grouped_results",
    "canonical_display_record",
    "collapsed_results",
    "transparency",
    "grouping_criteria",
    "identity_resolution_refs",
    "source_evidence_provenance",
    "conflicts",
    "user_facing_behavior",
    "result_card_projection",
    "api_projection",
    "privacy",
    "limitations",
    "no_destructive_merge_guarantees",
    "no_ranking_promotion_mutation_guarantees",
    "no_runtime_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_result_merge_implemented",
    "persistent_merge_group_store_implemented",
    "public_search_runtime_grouping_enabled",
    "public_search_ranking_changed",
    "records_merged",
    "duplicates_deleted",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "canonical_record_claimed_as_truth",
    "candidate_promotion_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_exported",
}
GROUP_STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "exact_duplicate_group",
    "near_duplicate_group",
    "variant_group",
    "conflict_preserving_group",
    "review_required",
    "runtime_future",
    "rejected_by_policy",
}
RELATION_TYPES = {
    "exact_duplicate_result",
    "near_duplicate_result",
    "variant_result",
    "same_object_different_source",
    "same_object_different_representation",
    "same_version_different_representation",
    "same_source_duplicate",
    "parent_child_result",
    "member_of_result",
    "source_mirror_result",
    "conflicting_duplicate_claim",
    "not_duplicate",
    "unknown",
}
RELATION_STATUSES = {"asserted_example", "candidate", "review_required", "conflicted", "rejected", "future"}
RESULT_KINDS = {"public_search_result", "public_index_document", "object_page", "source_page", "source_cache_record", "evidence_ledger_record", "candidate_index_record", "synthetic_example", "unknown"}
RESULT_STATUSES = {"fixture_backed", "recorded_fixture_backed", "candidate", "review_required", "placeholder", "future", "conflicted", "unknown"}
SELECTION_POLICIES = {"first_result_example", "strongest_identifier_future", "strongest_evidence_future", "preferred_lane_future", "user_selected_future", "review_required", "no_canonical_selected"}
CRITERION_TYPES = {
    "exact_identifier_match",
    "checksum_match",
    "source_native_id_match",
    "package_url_match",
    "SWHID_match",
    "archive_identifier_match",
    "same_object_identity_ref",
    "same_version_ref",
    "same_representation_ref",
    "same_member_ref",
    "normalized_title_match",
    "alias_match",
    "source_family_match",
    "weak_text_similarity",
    "parent_child_relation",
    "manual_review_future",
    "unknown",
}
STRENGTHS = {"strong", "medium", "weak", "insufficient", "unknown"}
STRONG_CRITERIA = {"exact_identifier_match", "checksum_match", "source_native_id_match", "package_url_match", "SWHID_match", "archive_identifier_match", "same_object_identity_ref"}
WEAK_CRITERIA = {"normalized_title_match", "alias_match", "weak_text_similarity", "source_family_match"}
CONFLICT_STATUSES = {
    "none_known",
    "possible_duplicate",
    "conflicting_duplicate_claim",
    "identity_conflict",
    "version_conflict",
    "representation_conflict",
    "member_conflict",
    "source_conflict",
    "evidence_conflict",
    "rights_or_access_conflict",
    "unresolved",
    "unknown",
}
DISPLAY_MODES = {"ungrouped_example", "grouped_future", "expandable_group_future", "conflict_group_future"}
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "result_merge_path",
    "deduplication_path",
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
    "download_url",
    "install_url",
    "execute_url",
    "raw_source_payload",
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


def validate_sensitive_content(group: Mapping[str, Any], errors: list[str]) -> None:
    for key_path, key in iter_keys(group):
        if key in FORBIDDEN_KEYS:
            errors.append(f"{key_path}: forbidden key {key!r}")
    for key_path, text in iter_strings(group):
        if PRIVATE_PATH_RE.search(text):
            errors.append(f"{key_path}: contains private absolute path or file URL")
        if SECRET_RE.search(text):
            errors.append(f"{key_path}: contains credential-like text")
        if IP_RE.search(text):
            errors.append(f"{key_path}: contains IP address")
        if ACCOUNT_RE.search(text):
            errors.append(f"{key_path}: contains account/user identifier")


def has_strong_grouping_evidence(group: Mapping[str, Any]) -> bool:
    for item in group.get("grouping_criteria", []):
        if not isinstance(item, Mapping):
            continue
        if item.get("passed") is True and item.get("strength") == "strong" and item.get("criterion_type") in STRONG_CRITERIA:
            return True
    return False


def weak_only(group: Mapping[str, Any]) -> bool:
    criteria = [item for item in group.get("grouping_criteria", []) if isinstance(item, Mapping) and item.get("passed") is True]
    return bool(criteria) and all(item.get("criterion_type") in WEAK_CRITERIA or item.get("strength") in {"weak", "insufficient"} for item in criteria)


def validate_group(group: Mapping[str, Any], *, source: str = "<memory>") -> list[str]:
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_REQUIRED - group.keys())
    if missing:
        errors.append(f"{source}: missing required fields: {', '.join(missing)}")
    if group.get("schema_version") != "0.1.0":
        errors.append(f"{source}: schema_version must be 0.1.0")
    if group.get("result_merge_group_kind") != "result_merge_group":
        errors.append(f"{source}: result_merge_group_kind must be result_merge_group")
    check_enum(errors, "status", group.get("status"), GROUP_STATUSES)
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, group.get(key))

    identity = group.get("merge_group_identity", {})
    if isinstance(identity, Mapping):
        if identity.get("group_label_not_truth") is not True:
            errors.append("merge_group_identity.group_label_not_truth must be true")
        fingerprint = identity.get("merge_group_fingerprint", {})
        if isinstance(fingerprint, Mapping):
            if fingerprint.get("algorithm") != "sha256":
                errors.append("merge_group_identity.merge_group_fingerprint.algorithm must be sha256")
            check_false(errors, "merge_group_identity.merge_group_fingerprint.reversible", fingerprint.get("reversible"))
    else:
        errors.append("merge_group_identity must be an object")

    relation = group.get("group_relation", {})
    relation_type = None
    if isinstance(relation, Mapping):
        relation_type = relation.get("relation_type")
        check_enum(errors, "group_relation.relation_type", relation_type, RELATION_TYPES)
        check_enum(errors, "group_relation.relation_status", relation.get("relation_status"), RELATION_STATUSES)
        if relation.get("relation_claim_not_truth") is not True:
            errors.append("group_relation.relation_claim_not_truth must be true")
        check_false(errors, "group_relation.destructive_merge_allowed", relation.get("destructive_merge_allowed"))
        if relation_type == "exact_duplicate_result" and not has_strong_grouping_evidence(group):
            errors.append("exact_duplicate_result requires strong grouping evidence")
    else:
        errors.append("group_relation must be an object")

    results = group.get("grouped_results", [])
    if not isinstance(results, list) or len(results) < 2:
        errors.append("grouped_results must contain at least two results")
    else:
        for index, result in enumerate(results):
            if not isinstance(result, Mapping):
                errors.append(f"grouped_results[{index}] must be an object")
                continue
            check_enum(errors, f"grouped_results[{index}].result_kind", result.get("result_kind"), RESULT_KINDS)
            check_enum(errors, f"grouped_results[{index}].result_status", result.get("result_status"), RESULT_STATUSES)
            if not result.get("result_ref") or not result.get("result_title"):
                errors.append(f"grouped_results[{index}] requires result_ref and result_title")

    canonical = group.get("canonical_display_record", {})
    if isinstance(canonical, Mapping):
        check_enum(errors, "canonical_display_record.selection_policy", canonical.get("selection_policy"), SELECTION_POLICIES)
        check_false(errors, "canonical_display_record.canonical_record_claimed_as_truth", canonical.get("canonical_record_claimed_as_truth"))
        if canonical.get("alternative_results_preserved") is not True:
            errors.append("canonical_display_record.alternative_results_preserved must be true")
    else:
        errors.append("canonical_display_record must be an object")

    collapsed = group.get("collapsed_results", {})
    if isinstance(collapsed, Mapping):
        check_false(errors, "collapsed_results.collapse_applied_now", collapsed.get("collapse_applied_now"))
        check_false(errors, "collapsed_results.hidden_without_explanation", collapsed.get("hidden_without_explanation"))
        if collapsed.get("explanation_required") is not True:
            errors.append("collapsed_results.explanation_required must be true")
        if collapsed.get("conflict_results_must_not_be_hidden") is not True:
            errors.append("collapsed_results.conflict_results_must_not_be_hidden must be true")
    else:
        errors.append("collapsed_results must be an object")

    criteria = group.get("grouping_criteria", [])
    if not isinstance(criteria, list) or not criteria:
        errors.append("grouping_criteria must be present")
    else:
        for index, item in enumerate(criteria):
            if not isinstance(item, Mapping):
                errors.append(f"grouping_criteria[{index}] must be an object")
                continue
            check_enum(errors, f"grouping_criteria[{index}].criterion_type", item.get("criterion_type"), CRITERION_TYPES)
            check_enum(errors, f"grouping_criteria[{index}].strength", item.get("strength"), STRENGTHS)
            if not isinstance(item.get("passed"), bool):
                errors.append(f"grouping_criteria[{index}].passed must be boolean")
    if weak_only(group) and relation_type == "exact_duplicate_result":
        errors.append("weak name/alias/text-only evidence cannot support exact_duplicate_result")

    for index, identity_ref in enumerate(group.get("identity_resolution_refs", [])):
        if not isinstance(identity_ref, Mapping):
            errors.append(f"identity_resolution_refs[{index}] must be an object")
            continue
        if identity_ref.get("confidence_not_truth") is not True:
            errors.append(f"identity_resolution_refs[{index}].confidence_not_truth must be true")
        check_false(errors, f"identity_resolution_refs[{index}].destructive_merge_allowed", identity_ref.get("destructive_merge_allowed"))

    preservation = group.get("source_evidence_provenance", {})
    if isinstance(preservation, Mapping):
        if not preservation.get("source_refs") or not preservation.get("evidence_refs"):
            errors.append("source_evidence_provenance must preserve source_refs and evidence_refs")
        if preservation.get("conflicts_preserved") is not True:
            errors.append("source_evidence_provenance.conflicts_preserved must be true")
        check_false(errors, "source_evidence_provenance.source_trust_claimed", preservation.get("source_trust_claimed"))
        check_false(errors, "source_evidence_provenance.accepted_as_truth", preservation.get("accepted_as_truth"))
    else:
        errors.append("source_evidence_provenance must be an object")

    conflicts = group.get("conflicts", {})
    if isinstance(conflicts, Mapping):
        check_enum(errors, "conflicts.conflict_status", conflicts.get("conflict_status"), CONFLICT_STATUSES)
        if conflicts.get("disagreement_preserved") is not True:
            errors.append("conflicts.disagreement_preserved must be true")
        if conflicts.get("conflict_results_must_remain_expandable") is not True:
            errors.append("conflicts.conflict_results_must_remain_expandable must be true")
        check_false(errors, "conflicts.destructive_merge_allowed", conflicts.get("destructive_merge_allowed"))
    else:
        errors.append("conflicts must be an object")

    behavior = group.get("user_facing_behavior", {})
    if isinstance(behavior, Mapping):
        check_enum(errors, "user_facing_behavior.display_mode", behavior.get("display_mode"), DISPLAY_MODES)
        for key in ("user_can_expand_group_future", "user_can_view_all_sources_future", "user_can_view_grouping_reason_future", "user_can_disable_grouping_future", "uncertainty_notice_required"):
            if behavior.get(key) is not True:
                errors.append(f"user_facing_behavior.{key} must be true")
    else:
        errors.append("user_facing_behavior must be an object")

    api = group.get("api_projection", {})
    if isinstance(api, Mapping) and api.get("implemented_now") is not False:
        errors.append("api_projection.implemented_now must be false")

    privacy = group.get("privacy", {})
    if isinstance(privacy, Mapping):
        check_enum(errors, "privacy.privacy_classification", privacy.get("privacy_classification"), PRIVACY_CLASSIFICATIONS)
        for key in ("contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query"):
            check_false(errors, f"privacy.{key}", privacy.get(key))
    else:
        errors.append("privacy must be an object")

    validate_sensitive_content(group, errors)
    return [f"{source}: {error}" for error in errors]


def discover_example_groups() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(EXAMPLES_ROOT.glob("*/RESULT_MERGE_GROUP.json"))


def validate_path(path: Path) -> list[str]:
    try:
        group = load_json(path)
    except Exception as exc:
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(group, Mapping):
        return [f"{path}: group must be a JSON object"]
    return validate_group(group, source=str(path))


def validate_example_root(root: Path) -> list[str]:
    group_path = root / "RESULT_MERGE_GROUP.json"
    if not group_path.exists():
        return [f"{root}: missing RESULT_MERGE_GROUP.json"]
    errors = validate_path(group_path)
    errors.extend(validate_checksum_file(root))
    return errors


def validate_all_examples() -> Mapping[str, Any]:
    paths = discover_example_groups()
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
    if args.group:
        targets.append(Path(args.group))
    if args.group_root:
        targets.append(Path(args.group_root) / "RESULT_MERGE_GROUP.json")
    if not targets:
        targets = discover_example_groups()
    errors: list[str] = []
    validated: list[str] = []
    for target in targets:
        target = target if target.is_absolute() else (REPO_ROOT / target)
        errors.extend(validate_path(target))
        validated.append(str(target))
    return {"status": "valid" if not errors else "invalid", "example_count": len(validated), "validated_paths": validated, "errors": errors}


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
    parser.add_argument("--group", help="Validate a single RESULT_MERGE_GROUP.json path.")
    parser.add_argument("--group-root", help="Validate RESULT_MERGE_GROUP.json under a root.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all examples.")
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
