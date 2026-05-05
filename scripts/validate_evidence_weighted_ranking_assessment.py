#!/usr/bin/env python3
"""Validate Evidence-Weighted Ranking Assessment v0 examples.

The validator is stdlib-only and local-only. It performs no network calls,
does not rank live search results, does not suppress results, uses no telemetry
or popularity signals, and mutates no index/cache/ledger state.
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
EXAMPLES_ROOT = REPO_ROOT / "examples" / "evidence_weighted_ranking"

TOP_LEVEL_REQUIRED = {
    "schema_version",
    "ranking_assessment_id",
    "ranking_assessment_kind",
    "status",
    "created_by_tool",
    "ranking_scope",
    "ranked_items",
    "ranking_factors",
    "evidence_strength",
    "provenance_strength",
    "source_posture",
    "freshness",
    "conflicts_and_uncertainty",
    "candidate_status",
    "absence_and_gaps",
    "action_safety",
    "rights_risk",
    "tie_breaks",
    "ranking_explanation_ref",
    "public_projection",
    "privacy",
    "limitations",
    "no_runtime_guarantees",
    "no_ranking_change_guarantees",
    "no_mutation_guarantees",
    "notes",
}
HARD_FALSE_FIELDS = {
    "runtime_ranking_implemented",
    "persistent_ranking_store_implemented",
    "ranking_applied_to_live_search",
    "public_search_order_changed",
    "result_suppressed",
    "hidden_suppression_performed",
    "candidate_promotion_performed",
    "records_merged",
    "master_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "telemetry_exported",
    "popularity_signal_used",
    "user_profile_signal_used",
    "ad_signal_used",
    "model_call_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
}
STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "review_required",
    "ranking_policy_candidate",
    "runtime_future",
    "rejected_by_policy",
}
SCOPE_KINDS = {
    "public_search_results",
    "result_merge_group",
    "object_page_candidates",
    "source_page_candidates",
    "comparison_page_candidates",
    "known_absence_candidates",
    "synthetic_example",
    "unknown",
}
RANKING_MODES = {"evidence_weighted_future", "dry_run_example", "contract_only"}
ITEM_KINDS = {
    "public_search_result",
    "result_merge_group",
    "object_page",
    "source_page",
    "comparison_page",
    "source_cache_record",
    "evidence_ledger_record",
    "candidate_index_record",
    "known_absence_page",
    "synthetic_example",
    "unknown",
}
ITEM_STATUSES = {
    "fixture_backed",
    "recorded_fixture_backed",
    "evidence_backed",
    "candidate",
    "review_required",
    "conflicted",
    "placeholder",
    "future",
    "unknown",
}
FACTOR_TYPES = {
    "evidence_strength",
    "provenance_strength",
    "source_posture",
    "intrinsic_identifier_match",
    "compatibility_evidence",
    "representation_availability",
    "member_access",
    "freshness",
    "conflict_penalty",
    "uncertainty_penalty",
    "candidate_penalty",
    "rights_risk_caution",
    "action_safety",
    "absence_transparency",
    "gap_transparency",
    "result_merge_group_quality",
    "identity_resolution_strength",
    "manual_review_status",
    "unknown",
}
DIRECTIONS = {"positive", "negative", "neutral", "informational"}
WEIGHT_POLICIES = {"descriptive_only", "future_weighted", "not_weighted_v0"}
EVIDENCE_CLASSES = {"none", "weak", "medium", "strong", "conflicting", "unknown"}
EVIDENCE_BASES = {
    "no_evidence",
    "name_match_only",
    "fixture_record",
    "recorded_fixture",
    "source_cache_future",
    "evidence_ledger_future",
    "source_backed_metadata",
    "intrinsic_identifier",
    "checksum",
    "compatibility_evidence",
    "manual_review_future",
    "multiple_independent_sources_future",
    "unknown",
}
COUNT_POLICIES = {"example_count", "future_runtime_count", "unavailable"}
PROVENANCE_CLASSES = {"none", "weak", "medium", "strong", "conflicting", "unknown"}
PROVENANCE_BASES = {
    "missing",
    "fixture",
    "recorded_fixture",
    "source_pack",
    "evidence_pack",
    "source_cache_future",
    "evidence_ledger_future",
    "manual_review_future",
    "unknown",
}
SOURCE_CLASSES = {
    "active_fixture",
    "active_recorded_fixture",
    "source_cache_future",
    "approval_required",
    "placeholder",
    "disabled",
    "unknown",
}
FRESHNESS_CLASSES = {"current_fixture", "recorded_fixture_static", "fresh_future", "stale_future", "unknown"}
CONFLICT_STATUSES = {
    "none_known",
    "possible_conflict",
    "identity_conflict",
    "version_conflict",
    "source_conflict",
    "compatibility_conflict",
    "evidence_conflict",
    "rights_or_access_conflict",
    "unresolved",
    "unknown",
}
UNCERTAINTY_STATUSES = {"low", "medium", "high", "unknown"}
PENALTY_POLICIES = {"descriptive_only", "future_penalty", "no_penalty_v0"}
CANDIDATE_CLASSES = {
    "accepted_fixture",
    "evidence_backed",
    "candidate_only",
    "review_required",
    "promotion_required",
    "rejected",
    "unknown",
}
ABSENCE_STATUSES = {"not_absent", "scoped_absence", "no_verified_result", "gap_only", "unknown"}
GAP_TYPES = {
    "source_coverage_gap",
    "capability_gap",
    "compatibility_evidence_gap",
    "member_access_gap",
    "representation_gap",
    "query_interpretation_gap",
    "live_probe_disabled",
    "external_baseline_pending",
    "source_cache_missing",
    "evidence_ledger_missing",
    "unknown",
}
ACTION_CLASSES = {"inspect_only", "safe_metadata_actions_only", "risky_action_disabled", "action_policy_required", "unknown"}
RIGHTS_CLASSES = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
RISK_CLASSES = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
TIE_POLICIES = {"deterministic_stable_order", "preserve_current_order_v0", "future_evidence_tie_break", "review_required"}
TIE_FACTORS = {
    "stable_id",
    "source_order",
    "evidence_count_future",
    "provenance_strength_future",
    "freshness_future",
    "none",
}
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}

PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:[\\/]|\\\\|file://|/(?:home|users|tmp|var|etc)/)", re.IGNORECASE)
SECRET_RE = re.compile(r"(api[_-]?key\s*=|auth[_-]?token\s*=|password\s*=|secret\s*=|token\s*=)", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|user)[_-]?id\s*[:=]", re.IGNORECASE)
FORBIDDEN_KEYS = {
    "ranking_path",
    "scoring_path",
    "evidence_weight_path",
    "result_merge_path",
    "identity_resolution_path",
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


def checksum_errors(example_root: Path) -> list[str]:
    checksum_path = example_root / "CHECKSUMS.SHA256"
    errors: list[str] = []
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


def check_true(errors: list[str], path: str, value: Any) -> None:
    if value is not True:
        errors.append(f"{path} must be true")


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
    if page.get("ranking_assessment_kind") != "evidence_weighted_ranking_assessment":
        errors.append(f"{source}: ranking_assessment_kind must be evidence_weighted_ranking_assessment")
    check_enum(errors, "status", page.get("status"), STATUSES)
    for key in HARD_FALSE_FIELDS:
        check_false(errors, key, page.get(key))

    scope = page.get("ranking_scope", {})
    if isinstance(scope, Mapping):
        check_enum(errors, "ranking_scope.scope_kind", scope.get("scope_kind"), SCOPE_KINDS)
        check_enum(errors, "ranking_scope.ranking_mode", scope.get("ranking_mode"), RANKING_MODES)
        check_true(errors, "ranking_scope.current_runtime_order_preserved", scope.get("current_runtime_order_preserved"))
        check_false(errors, "ranking_scope.live_runtime_changed", scope.get("live_runtime_changed"))
    else:
        errors.append("ranking_scope must be an object")

    ranked_items = page.get("ranked_items", [])
    if not isinstance(ranked_items, list) or len(ranked_items) < 2:
        errors.append("ranked_items must contain at least two items")
    else:
        ranks = []
        for index, item in enumerate(ranked_items):
            if not isinstance(item, Mapping):
                errors.append(f"ranked_items[{index}] must be an object")
                continue
            check_enum(errors, f"ranked_items[{index}].item_kind", item.get("item_kind"), ITEM_KINDS)
            check_enum(errors, f"ranked_items[{index}].item_status", item.get("item_status"), ITEM_STATUSES)
            check_false(errors, f"ranked_items[{index}].rank_changed_now", item.get("rank_changed_now"))
            if isinstance(item.get("proposed_rank"), int):
                ranks.append(item["proposed_rank"])
        if ranks and sorted(ranks) != list(range(1, len(ranks) + 1)):
            errors.append("ranked_items proposed_rank values must be deterministic 1..n examples")

    factors = page.get("ranking_factors", [])
    if not isinstance(factors, list) or not factors:
        errors.append("ranking_factors must be a non-empty list")
    else:
        for index, item in enumerate(factors):
            if not isinstance(item, Mapping):
                errors.append(f"ranking_factors[{index}] must be an object")
                continue
            check_enum(errors, f"ranking_factors[{index}].factor_type", item.get("factor_type"), FACTOR_TYPES)
            check_enum(errors, f"ranking_factors[{index}].direction", item.get("direction"), DIRECTIONS)
            check_enum(errors, f"ranking_factors[{index}].weight_policy", item.get("weight_policy"), WEIGHT_POLICIES)
            check_false(errors, f"ranking_factors[{index}].score_applied_now", item.get("score_applied_now"))

    evidence = page.get("evidence_strength", {})
    if isinstance(evidence, Mapping):
        check_enum(errors, "evidence_strength.evidence_strength_class", evidence.get("evidence_strength_class"), EVIDENCE_CLASSES)
        check_enum(errors, "evidence_strength.evidence_basis", evidence.get("evidence_basis"), EVIDENCE_BASES)
        check_enum(errors, "evidence_strength.evidence_count_policy", evidence.get("evidence_count_policy"), COUNT_POLICIES)
        check_true(errors, "evidence_strength.evidence_strength_not_truth", evidence.get("evidence_strength_not_truth"))
    else:
        errors.append("evidence_strength must be an object")

    provenance = page.get("provenance_strength", {})
    if isinstance(provenance, Mapping):
        check_enum(errors, "provenance_strength.provenance_strength_class", provenance.get("provenance_strength_class"), PROVENANCE_CLASSES)
        check_enum(errors, "provenance_strength.provenance_basis", provenance.get("provenance_basis"), PROVENANCE_BASES)
        check_true(errors, "provenance_strength.provenance_not_truth", provenance.get("provenance_not_truth"))
    else:
        errors.append("provenance_strength must be an object")

    source_posture = page.get("source_posture", {})
    if isinstance(source_posture, Mapping):
        check_enum(errors, "source_posture.source_posture_class", source_posture.get("source_posture_class"), SOURCE_CLASSES)
        check_false(errors, "source_posture.live_enabled", source_posture.get("live_enabled"))
        check_false(errors, "source_posture.source_trust_claimed", source_posture.get("source_trust_claimed"))
    else:
        errors.append("source_posture must be an object")

    freshness = page.get("freshness", {})
    if isinstance(freshness, Mapping):
        check_enum(errors, "freshness.freshness_class", freshness.get("freshness_class"), FRESHNESS_CLASSES)
        check_false(errors, "freshness.freshness_score_applied_now", freshness.get("freshness_score_applied_now"))

    conflicts = page.get("conflicts_and_uncertainty", {})
    if isinstance(conflicts, Mapping):
        check_enum(errors, "conflicts_and_uncertainty.conflict_status", conflicts.get("conflict_status"), CONFLICT_STATUSES)
        check_enum(errors, "conflicts_and_uncertainty.uncertainty_status", conflicts.get("uncertainty_status"), UNCERTAINTY_STATUSES)
        check_enum(errors, "conflicts_and_uncertainty.penalty_policy", conflicts.get("penalty_policy"), PENALTY_POLICIES)
        check_false(errors, "conflicts_and_uncertainty.conflict_hidden", conflicts.get("conflict_hidden"))
        check_false(errors, "conflicts_and_uncertainty.conflict_suppresses_result_now", conflicts.get("conflict_suppresses_result_now"))
        check_true(errors, "conflicts_and_uncertainty.uncertainty_explanation_required", conflicts.get("uncertainty_explanation_required"))
    else:
        errors.append("conflicts_and_uncertainty must be an object")

    candidate = page.get("candidate_status", {})
    if isinstance(candidate, Mapping):
        check_enum(errors, "candidate_status.candidate_class", candidate.get("candidate_class"), CANDIDATE_CLASSES)
        check_false(errors, "candidate_status.candidate_promotion_performed", candidate.get("candidate_promotion_performed"))
        check_true(errors, "candidate_status.candidate_confidence_not_truth", candidate.get("candidate_confidence_not_truth"))

    absence = page.get("absence_and_gaps", {})
    if isinstance(absence, Mapping):
        check_enum(errors, "absence_and_gaps.absence_status", absence.get("absence_status"), ABSENCE_STATUSES)
        check_false(errors, "absence_and_gaps.global_absence_claimed", absence.get("global_absence_claimed"))
        check_true(errors, "absence_and_gaps.gap_transparency_required", absence.get("gap_transparency_required"))
        check_false(errors, "absence_and_gaps.absence_or_gap_suppresses_result_now", absence.get("absence_or_gap_suppresses_result_now"))
        for index, gap in enumerate(absence.get("gaps", [])):
            if isinstance(gap, Mapping):
                check_enum(errors, f"absence_and_gaps.gaps[{index}].gap_type", gap.get("gap_type"), GAP_TYPES)

    action = page.get("action_safety", {})
    if isinstance(action, Mapping):
        check_enum(errors, "action_safety.action_safety_class", action.get("action_safety_class"), ACTION_CLASSES)
        check_false(errors, "action_safety.risky_action_bonus_allowed", action.get("risky_action_bonus_allowed"))
        for key in ("downloads_enabled", "installs_enabled", "execution_enabled"):
            check_false(errors, f"action_safety.{key}", action.get(key))

    rights = page.get("rights_risk", {})
    if isinstance(rights, Mapping):
        check_enum(errors, "rights_risk.rights_classification", rights.get("rights_classification"), RIGHTS_CLASSES)
        check_enum(errors, "rights_risk.risk_classification", rights.get("risk_classification"), RISK_CLASSES)
        check_false(errors, "rights_risk.rights_clearance_claimed", rights.get("rights_clearance_claimed"))
        check_false(errors, "rights_risk.malware_safety_claimed", rights.get("malware_safety_claimed"))
        check_false(errors, "rights_risk.rights_risk_score_applied_now", rights.get("rights_risk_score_applied_now"))

    tie_breaks = page.get("tie_breaks", {})
    if isinstance(tie_breaks, Mapping):
        check_enum(errors, "tie_breaks.tie_break_policy", tie_breaks.get("tie_break_policy"), TIE_POLICIES)
        for item in tie_breaks.get("tie_break_factors", []):
            check_enum(errors, "tie_breaks.tie_break_factors[]", item, TIE_FACTORS)
        check_false(errors, "tie_breaks.tie_break_applied_now", tie_breaks.get("tie_break_applied_now"))
        check_false(errors, "tie_breaks.random_tie_break_allowed", tie_breaks.get("random_tie_break_allowed"))

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
        ):
            check_false(errors, f"privacy.{key}", privacy.get(key))

    validate_sensitive_content(page, errors)
    return errors


def validate_path(path: Path, *, check_checksums: bool = True) -> list[str]:
    try:
        page = load_json(path)
    except Exception as exc:
        return [f"{path}: failed to parse JSON: {exc}"]
    if not isinstance(page, Mapping):
        return [f"{path}: assessment must be an object"]
    errors = validate_assessment(page, source=str(path))
    if check_checksums and path.name == "EVIDENCE_WEIGHTED_RANKING_ASSESSMENT.json" and path.parent.parent == EXAMPLES_ROOT:
        errors.extend(checksum_errors(path.parent))
    return errors


def example_paths() -> list[Path]:
    return sorted(EXAMPLES_ROOT.glob("*/EVIDENCE_WEIGHTED_RANKING_ASSESSMENT.json"))


def validate_all_examples() -> tuple[list[Path], list[str]]:
    paths = example_paths()
    errors: list[str] = []
    if not paths:
        errors.append("no evidence-weighted ranking examples found")
    for path in paths:
        errors.extend(validate_path(path))
    return paths, errors


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def emit(status: str, paths: Sequence[Path], errors: Sequence[str], *, as_json: bool, stream: TextIO) -> None:
    if as_json:
        print(
            json.dumps(
                {
                    "status": status,
                    "example_count": len(paths),
                    "validated_paths": [display_path(path) for path in paths],
                    "errors": list(errors),
                },
                indent=2,
            ),
            file=stream,
        )
    else:
        print(f"status: {status}", file=stream)
        print(f"example_count: {len(paths)}", file=stream)
        for error in errors:
            print(f"error: {error}", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", type=Path)
    parser.add_argument("--assessment-root", type=Path)
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    paths: list[Path] = []
    errors: list[str] = []
    if args.all_examples:
        paths, errors = validate_all_examples()
    elif args.assessment:
        paths = [args.assessment]
        errors = validate_path(args.assessment, check_checksums=False)
    elif args.assessment_root:
        path = args.assessment_root / "EVIDENCE_WEIGHTED_RANKING_ASSESSMENT.json"
        paths = [path]
        errors = validate_path(path, check_checksums=False)
    else:
        errors.append("provide --assessment, --assessment-root, or --all-examples")

    status = "valid" if not errors else "invalid"
    emit(status, paths, errors, as_json=args.json, stream=sys.stdout)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
