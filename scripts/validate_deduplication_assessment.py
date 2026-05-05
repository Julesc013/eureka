#!/usr/bin/env python3
"""Validate Deduplication Assessment v0 examples.

The validator is stdlib-only and local-only. It applies no deduplication to live
search, suppresses no results, changes no ranking, and mutates no index/cache or
ledger state.
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
    "deduplication_assessment_id",
    "deduplication_assessment_kind",
    "status",
    "created_by_tool",
    "assessment_scope",
    "assessed_results",
    "asserted_relation",
    "relation_evidence",
    "grouping_decision",
    "display_decision",
    "conflict_review",
    "confidence",
    "review",
    "privacy",
    "limitations",
    "no_destructive_merge_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_deduplication_implemented",
    "deduplication_applied_to_live_search",
    "records_merged",
    "results_suppressed",
    "results_hidden_without_explanation",
    "destructive_merge_performed",
    "ranking_changed",
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
ASSESSMENT_STATUSES = {"draft_example", "dry_run_validated", "synthetic_example", "public_safe_example", "possible_duplicate", "near_duplicate", "variant", "conflict", "not_duplicate", "review_required", "runtime_future"}
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


def validate_assessment(page: Mapping[str, Any], *, source: str = "<memory>") -> list[str]:
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_REQUIRED - page.keys())
    if missing:
        errors.append(f"{source}: missing required fields: {', '.join(missing)}")
    if page.get("schema_version") != "0.1.0":
        errors.append(f"{source}: schema_version must be 0.1.0")
    if page.get("deduplication_assessment_kind") != "deduplication_assessment":
        errors.append(f"{source}: deduplication_assessment_kind must be deduplication_assessment")
    check_enum(errors, "status", page.get("status"), ASSESSMENT_STATUSES)
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, page.get(key))

    assessed = page.get("assessed_results", [])
    if not isinstance(assessed, list) or len(assessed) < 2:
        errors.append("assessed_results must contain at least two results")

    relation = page.get("asserted_relation", {})
    if isinstance(relation, Mapping):
        check_enum(errors, "asserted_relation.relation_type", relation.get("relation_type"), RELATION_TYPES)
        check_enum(errors, "asserted_relation.relation_status", relation.get("relation_status"), RELATION_STATUSES)
        if relation.get("relation_claim_not_truth") is not True:
            errors.append("asserted_relation.relation_claim_not_truth must be true")
        check_false(errors, "asserted_relation.destructive_merge_allowed", relation.get("destructive_merge_allowed"))
    else:
        errors.append("asserted_relation must be an object")

    grouping = page.get("grouping_decision", {})
    if isinstance(grouping, Mapping):
        check_false(errors, "grouping_decision.grouping_applied_now", grouping.get("grouping_applied_now"))
        if grouping.get("decision_not_truth") is not True:
            errors.append("grouping_decision.decision_not_truth must be true")
    else:
        errors.append("grouping_decision must be an object")

    display = page.get("display_decision", {})
    if isinstance(display, Mapping):
        check_false(errors, "display_decision.canonical_record_claimed_as_truth", display.get("canonical_record_claimed_as_truth"))
        check_false(errors, "display_decision.results_hidden_without_explanation", display.get("results_hidden_without_explanation"))
        if display.get("alternative_results_preserved") is not True:
            errors.append("display_decision.alternative_results_preserved must be true")
    else:
        errors.append("display_decision must be an object")

    conflict_review = page.get("conflict_review", {})
    if isinstance(conflict_review, Mapping):
        if conflict_review.get("disagreement_preserved") is not True:
            errors.append("conflict_review.disagreement_preserved must be true")
        if conflict_review.get("conflict_results_must_remain_expandable") is not True:
            errors.append("conflict_review.conflict_results_must_remain_expandable must be true")
    else:
        errors.append("conflict_review must be an object")

    confidence = page.get("confidence", {})
    if isinstance(confidence, Mapping):
        if confidence.get("confidence_not_truth") is not True:
            errors.append("confidence.confidence_not_truth must be true")
        check_false(errors, "confidence.confidence_sufficient_for_merge_now", confidence.get("confidence_sufficient_for_merge_now"))
    else:
        errors.append("confidence must be an object")

    review = page.get("review", {})
    if isinstance(review, Mapping):
        if review.get("destructive_merge_forbidden") is not True:
            errors.append("review.destructive_merge_forbidden must be true")
        if review.get("ranking_change_forbidden") is not True:
            errors.append("review.ranking_change_forbidden must be true")
    else:
        errors.append("review must be an object")

    privacy = page.get("privacy", {})
    if isinstance(privacy, Mapping):
        check_enum(errors, "privacy.privacy_classification", privacy.get("privacy_classification"), PRIVACY_CLASSIFICATIONS)
        for key in ("contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query"):
            check_false(errors, f"privacy.{key}", privacy.get(key))
    else:
        errors.append("privacy must be an object")

    validate_sensitive_content(page, errors)
    return [f"{source}: {error}" for error in errors]


def discover_example_assessments() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(EXAMPLES_ROOT.glob("*/DEDUPLICATION_ASSESSMENT.json"))


def validate_path(path: Path) -> list[str]:
    try:
        page = load_json(path)
    except Exception as exc:
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{path}: assessment must be a JSON object"]
    return validate_assessment(page, source=str(path))


def validate_example_root(root: Path) -> list[str]:
    page_path = root / "DEDUPLICATION_ASSESSMENT.json"
    if not page_path.exists():
        return [f"{root}: missing DEDUPLICATION_ASSESSMENT.json"]
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
        targets.append(Path(args.assessment_root) / "DEDUPLICATION_ASSESSMENT.json")
    if not targets:
        targets = discover_example_assessments()
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
    parser.add_argument("--assessment", help="Validate a single DEDUPLICATION_ASSESSMENT.json path.")
    parser.add_argument("--assessment-root", help="Validate DEDUPLICATION_ASSESSMENT.json under a root.")
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
