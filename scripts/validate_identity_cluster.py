#!/usr/bin/env python3
"""Validate Cross-Source Identity Cluster v0 examples.

This validator is stdlib-only and local-only. It validates provisional identity
cluster artifacts without creating stores, merging records, or mutating indexes,
source cache, evidence ledger, or candidate state.
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
    "identity_cluster_id",
    "identity_cluster_kind",
    "status",
    "created_by_tool",
    "cluster_identity",
    "cluster_members",
    "cluster_relations",
    "canonicalization_policy",
    "conflicts",
    "confidence",
    "review",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_identity_cluster_implemented",
    "persistent_cluster_store_implemented",
    "cluster_accepted_as_truth",
    "records_merged",
    "destructive_merge_performed",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "telemetry_exported",
}
CLUSTER_STATUSES = {"draft_example", "synthetic_example", "candidate_cluster", "review_required", "conflicted", "rejected_by_policy", "runtime_future"}
MEMBER_STATUSES = {"fixture_backed", "recorded_fixture_backed", "candidate", "review_required", "placeholder", "future", "conflicted", "unknown"}
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
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}

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


def validate_sensitive_content(cluster: Mapping[str, Any], errors: list[str]) -> None:
    for key_path, key in iter_keys(cluster):
        if key in FORBIDDEN_KEYS:
            errors.append(f"{key_path}: forbidden key {key!r}")
    for key_path, text in iter_strings(cluster):
        if PRIVATE_PATH_RE.search(text):
            errors.append(f"{key_path}: contains private absolute path or file URL")
        if SECRET_RE.search(text):
            errors.append(f"{key_path}: contains credential-like text")
        if IP_RE.search(text):
            errors.append(f"{key_path}: contains IP address")
        if ACCOUNT_RE.search(text):
            errors.append(f"{key_path}: contains account/user identifier")


def validate_cluster(cluster: Mapping[str, Any], *, source: str = "<memory>") -> list[str]:
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_REQUIRED - cluster.keys())
    if missing:
        errors.append(f"{source}: missing required fields: {', '.join(missing)}")

    if cluster.get("schema_version") != "0.1.0":
        errors.append(f"{source}: schema_version must be 0.1.0")
    if cluster.get("identity_cluster_kind") != "identity_cluster":
        errors.append(f"{source}: identity_cluster_kind must be identity_cluster")
    check_enum(errors, "status", cluster.get("status"), CLUSTER_STATUSES)
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, cluster.get(key))

    cluster_identity = cluster.get("cluster_identity", {})
    if isinstance(cluster_identity, Mapping):
        if cluster_identity.get("cluster_claim_not_truth") is not True:
            errors.append("cluster_identity.cluster_claim_not_truth must be true")
    else:
        errors.append("cluster_identity must be an object")

    members = cluster.get("cluster_members", [])
    if not isinstance(members, list) or len(members) < 2:
        errors.append("cluster_members must contain at least two members")
    else:
        for index, member in enumerate(members):
            if not isinstance(member, Mapping):
                errors.append(f"cluster_members[{index}] must be an object")
                continue
            if not member.get("member_ref"):
                errors.append(f"cluster_members[{index}].member_ref is required")
            check_enum(errors, f"cluster_members[{index}].member_status", member.get("member_status"), MEMBER_STATUSES)
            check_enum(errors, f"cluster_members[{index}].relation_to_cluster", member.get("relation_to_cluster"), RELATION_TYPES)

    relations = cluster.get("cluster_relations", [])
    if not isinstance(relations, list) or not relations:
        errors.append("cluster_relations must be present")
    else:
        for index, relation in enumerate(relations):
            if not isinstance(relation, Mapping):
                errors.append(f"cluster_relations[{index}] must be an object")
                continue
            check_enum(errors, f"cluster_relations[{index}].relation_type", relation.get("relation_type"), RELATION_TYPES)
            if relation.get("relation_claim_not_truth") is not True:
                errors.append(f"cluster_relations[{index}].relation_claim_not_truth must be true")
            check_false(errors, f"cluster_relations[{index}].global_merge_allowed", relation.get("global_merge_allowed"))

    canonical = cluster.get("canonicalization_policy", {})
    if isinstance(canonical, Mapping):
        check_false(errors, "canonicalization_policy.canonicalization_allowed_now", canonical.get("canonicalization_allowed_now"))
        check_false(errors, "canonicalization_policy.canonical_label_selected_now", canonical.get("canonical_label_selected_now"))
        if canonical.get("canonicalization_review_required") is not True:
            errors.append("canonicalization_policy.canonicalization_review_required must be true")
    else:
        errors.append("canonicalization_policy must be an object")

    conflicts = cluster.get("conflicts", {})
    if isinstance(conflicts, Mapping):
        check_enum(errors, "conflicts.conflict_status", conflicts.get("conflict_status"), CONFLICT_STATUSES)
        if conflicts.get("disagreement_preserved") is not True:
            errors.append("conflicts.disagreement_preserved must be true")
        check_false(errors, "conflicts.destructive_merge_allowed", conflicts.get("destructive_merge_allowed"))
    else:
        errors.append("conflicts must be an object")

    confidence = cluster.get("confidence", {})
    if isinstance(confidence, Mapping):
        check_enum(errors, "confidence.confidence_class", confidence.get("confidence_class"), CONFIDENCE_CLASSES)
        check_enum(errors, "confidence.confidence_basis", confidence.get("confidence_basis"), CONFIDENCE_BASES)
        if confidence.get("confidence_not_truth") is not True:
            errors.append("confidence.confidence_not_truth must be true")
        check_false(errors, "confidence.confidence_sufficient_for_merge_now", confidence.get("confidence_sufficient_for_merge_now"))
    else:
        errors.append("confidence must be an object")

    review = cluster.get("review", {})
    if isinstance(review, Mapping):
        check_enum(errors, "review.review_status", review.get("review_status"), REVIEW_STATUSES)
        if review.get("promotion_policy_required") is not True:
            errors.append("review.promotion_policy_required must be true")
        if review.get("destructive_merge_forbidden") is not True:
            errors.append("review.destructive_merge_forbidden must be true")
    else:
        errors.append("review must be an object")

    privacy = cluster.get("privacy", {})
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

    validate_sensitive_content(cluster, errors)
    return [f"{source}: {error}" for error in errors]


def discover_example_clusters() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(EXAMPLES_ROOT.glob("*/IDENTITY_CLUSTER.json"))


def validate_path(path: Path) -> list[str]:
    try:
        cluster = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive CLI path
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(cluster, Mapping):
        return [f"{path}: cluster must be a JSON object"]
    return validate_cluster(cluster, source=str(path))


def validate_example_root(root: Path) -> list[str]:
    cluster_path = root / "IDENTITY_CLUSTER.json"
    if not cluster_path.exists():
        return [f"{root}: missing IDENTITY_CLUSTER.json"]
    errors = validate_path(cluster_path)
    errors.extend(validate_checksum_file(root))
    return errors


def validate_all_examples() -> Mapping[str, Any]:
    paths = discover_example_clusters()
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
    if args.cluster:
        targets.append(Path(args.cluster))
    if args.cluster_root:
        targets.append(Path(args.cluster_root) / "IDENTITY_CLUSTER.json")
    if not targets:
        targets = discover_example_clusters()
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
    parser.add_argument("--cluster", help="Validate a single identity cluster JSON path.")
    parser.add_argument("--cluster-root", help="Validate IDENTITY_CLUSTER.json under a root.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all identity cluster examples.")
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
