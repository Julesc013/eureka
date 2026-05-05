from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = ROOT / "examples" / "search_result_explanations"

STATUSES = {
    "draft_example",
    "dry_run_validated",
    "synthetic_example",
    "public_safe_example",
    "fixture_explanation",
    "recorded_fixture_explanation",
    "candidate_explanation",
    "review_required",
    "runtime_future",
    "rejected_by_policy",
}
SCOPE_KINDS = {
    "public_search_result",
    "result_merge_group",
    "object_page_result",
    "source_page_result",
    "comparison_page_result",
    "known_absence_result",
    "extraction_gap_result",
    "synthetic_example",
    "unknown",
}
SEARCH_MODES = {"local_index_only", "static_demo", "fixture_example", "runtime_future", "unknown"}
EXPLANATION_BASES = {
    "synthetic_example",
    "fixture_backed",
    "recorded_fixture_backed",
    "public_index_document",
    "source_cache_future",
    "evidence_ledger_future",
    "candidate_index_future",
    "ranking_contract_future",
    "unknown",
}
RESULT_KINDS = {
    "software",
    "software_version",
    "driver",
    "package",
    "source_record",
    "web_capture",
    "documentation",
    "object_page",
    "source_page",
    "comparison_page",
    "known_absence",
    "extraction_gap",
    "synthetic_example",
    "unknown",
}
RESULT_STATUSES = {
    "fixture_backed",
    "recorded_fixture_backed",
    "public_index_backed",
    "candidate",
    "review_required",
    "conflicted",
    "placeholder",
    "future",
    "unknown",
}
RESULT_LANES = {"official", "preservation", "community", "candidate", "absence", "conflicted", "demo", "unknown"}
COMPONENT_TYPES = {
    "query_interpretation",
    "lexical_match",
    "phrase_match",
    "identifier_match",
    "alias_match",
    "source_match",
    "metadata_field_match",
    "compatibility_match",
    "representation_match",
    "member_match",
    "evidence_strength",
    "provenance_strength",
    "source_coverage",
    "ranking_reason",
    "grouping_reason",
    "identity_reason",
    "conflict_warning",
    "candidate_warning",
    "absence_explanation",
    "near_miss_explanation",
    "gap_explanation",
    "action_safety",
    "rights_risk_caution",
    "privacy_redaction_notice",
    "not_checked_notice",
    "unknown",
}
REQUIRED_COMPONENTS = {"query_interpretation", "source_coverage", "evidence_strength", "action_safety", "rights_risk_caution"}
INTENTS = {
    "find_software",
    "find_version",
    "find_driver",
    "find_documentation",
    "find_source_code",
    "find_package",
    "find_capture",
    "find_compatibility",
    "find_member",
    "compare",
    "unknown",
}
CONFIDENCE = {"low", "medium", "high", "unknown"}
RECALL_SCOPES = {"public_index_only", "static_demo", "fixture_only", "source_cache_future", "live_sources_not_checked", "unknown"}
STRENGTHS = {"none", "weak", "medium", "strong", "conflicting", "unknown"}
SOURCE_COVERAGE_STATUSES = {"public_index_only", "fixture_backed", "recorded_fixture_backed", "source_cache_future", "live_sources_disabled", "unknown"}
REASONS_NOT_CHECKED = {"live_connector_disabled", "approval_required", "source_policy_missing", "not_in_public_index", "not_requested", "unknown"}
DUP_STATUSES = {"not_grouped", "exact_duplicate_future", "near_duplicate_future", "variant_future", "conflict_preserving_group_future", "unknown"}
NUMERIC_SCORE_POLICIES = {"no_numeric_score_v0", "categorical_future", "full_explanation_future"}
COMPATIBILITY_STATUSES = {"known_supported", "likely_supported", "unknown", "likely_unsupported", "unsupported", "conflicting", "not_applicable"}
ABSENCE_STATUSES = {"not_absent", "scoped_absence", "no_verified_result", "near_miss_only", "gap_only", "unknown"}
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
SAFE_ACTIONS = {"inspect_metadata", "view_sources", "view_evidence", "compare", "cite"}
DISABLED_ACTIONS = {"download", "install", "execute", "upload", "mirror", "arbitrary_url_fetch", "package_manager_invoke", "emulator_launch", "VM_launch"}
ACTION_STATUSES = {"inspect_only", "metadata_actions_only", "risky_actions_disabled", "action_policy_required", "unknown"}
RIGHTS_CLASSIFICATIONS = {"public_metadata_only", "source_terms_apply", "review_required", "restricted", "unknown"}
RISK_CLASSIFICATIONS = {"metadata_only", "executable_reference", "private_data_risk", "credential_risk", "malware_review_required", "unknown"}
PRIVACY_CLASSIFICATIONS = {"public_safe_example", "public_safe_metadata", "local_private", "rejected_sensitive", "redacted", "unknown"}

HARD_FALSE = [
    "runtime_explanation_implemented",
    "explanation_generated_by_runtime",
    "explanation_applied_to_live_search",
    "public_search_response_changed",
    "public_search_order_changed",
    "hidden_score_used",
    "hidden_suppression_performed",
    "result_suppressed",
    "model_call_performed",
    "AI_generated_answer",
    "candidate_promotion_performed",
    "ranking_applied_to_live_search",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "live_source_called",
    "external_calls_performed",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
    "telemetry_exported",
]
REQUIRED_FIELDS = [
    "schema_version",
    "search_result_explanation_id",
    "search_result_explanation_kind",
    "status",
    "created_by_tool",
    "explanation_scope",
    "explained_result",
    "query_interpretation",
    "match_and_recall",
    "source_coverage",
    "evidence_and_provenance",
    "identity_grouping_deduplication",
    "ranking_relationship",
    "compatibility",
    "absence_near_miss_gaps",
    "action_safety",
    "rights_risk",
    "user_facing_summary",
    "detailed_components",
    "api_projection",
    "static_lite_text_projection",
    "privacy",
    "limitations",
    "no_truth_guarantees",
    "no_runtime_guarantees",
    "no_mutation_guarantees",
    "notes",
] + HARD_FALSE


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def require(data: dict[str, Any], fields: list[str], path: Path) -> None:
    for field in fields:
        if field not in data:
            raise ValidationError(f"{path}: missing required field {field}")


def expect_false(data: dict[str, Any], fields: list[str], path: Path) -> None:
    for field in fields:
        if data.get(field) is not False:
            raise ValidationError(f"{path}: {field} must be false")


def expect_true(data: dict[str, Any], field: str, path: Path) -> None:
    if data.get(field) is not True:
        raise ValidationError(f"{path}: {field} must be true")


def expect_enum(value: str, allowed: set[str], label: str, path: Path) -> None:
    if value not in allowed:
        raise ValidationError(f"{path}: {label} has unsupported value {value!r}")


def walk_strings(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)
    elif isinstance(value, str):
        yield value


def public_safe_path(value: str) -> bool:
    if not value:
        return True
    if value.startswith("/api/"):
        return True
    lower = value.lower()
    if "://" in value or lower.startswith(("file:", "data:", "javascript:")):
        return False
    if value.startswith(("/", "\\")) or "\\" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    parts = value.replace("\\", "/").split("/")
    if any(part in {"..", "~"} for part in parts):
        return False
    if any(part.lower() in {"users", "home", "private", "secrets", ".ssh", ".env"} for part in parts):
        return False
    return True


SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b\d{10,}\b"),
]


def validate_no_private_strings(data: Any, path: Path) -> None:
    for value in walk_strings(data):
        if "://" in value or value.lower().startswith(("file:", "data:", "javascript:")):
            raise ValidationError(f"{path}: arbitrary URL-like value is not allowed: {value!r}")
        if not public_safe_path(value) and ("/" in value or "\\" in value or re.match(r"^[A-Za-z]:", value)):
            raise ValidationError(f"{path}: private or unsafe path value is not allowed: {value!r}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                raise ValidationError(f"{path}: secret, contact, IP, or account-like value is not allowed")


def validate_checksums(root: Path) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        raise ValidationError(f"{root}: missing CHECKSUMS.SHA256")
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, name = line.split(None, 1)
        except ValueError as exc:
            raise ValidationError(f"{checksum_path}: malformed checksum line") from exc
        expected[name.strip()] = digest.strip()
    if not expected:
        raise ValidationError(f"{checksum_path}: no checksum entries")
    for name, digest in expected.items():
        candidate = root / name
        if not candidate.exists():
            raise ValidationError(f"{checksum_path}: listed file missing: {name}")
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != digest:
            raise ValidationError(f"{checksum_path}: checksum mismatch for {name}")


def example_roots() -> list[Path]:
    if not EXAMPLES_ROOT.exists():
        return []
    return sorted(path for path in EXAMPLES_ROOT.iterdir() if path.is_dir())


def validate_component(component: dict[str, Any], path: Path) -> str:
    require(
        component,
        [
            "schema_version",
            "component_id",
            "component_kind",
            "component_type",
            "status",
            "public_user_text",
            "audit_text",
            "evidence_refs",
            "source_refs",
            "confidence",
            "uncertainty",
            "limitations",
            "privacy",
            "no_truth_guarantees",
            "component_claimed_as_truth",
            "hidden_from_user",
            "private_data_included",
            "raw_payload_included",
        ],
        path,
    )
    if component["component_kind"] != "search_result_explanation_component":
        raise ValidationError(f"{path}: component_kind must be search_result_explanation_component")
    expect_enum(component["component_type"], COMPONENT_TYPES, "component_type", path)
    expect_false(component, ["component_claimed_as_truth", "hidden_from_user", "private_data_included", "raw_payload_included"], path)
    if not component["public_user_text"] or not component["audit_text"]:
        raise ValidationError(f"{path}: component public_user_text and audit_text must be present")
    return component["component_type"]


def validate_explanation(path: Path, check_checksum: bool = False) -> None:
    data = load_json(path)
    require(data, REQUIRED_FIELDS, path)
    if data["search_result_explanation_kind"] != "search_result_explanation":
        raise ValidationError(f"{path}: search_result_explanation_kind must be search_result_explanation")
    expect_enum(data["status"], STATUSES, "status", path)
    expect_false(data, HARD_FALSE, path)

    scope = data["explanation_scope"]
    require(scope, ["scope_kind", "search_mode", "explanation_basis", "limitations"], path)
    expect_enum(scope["scope_kind"], SCOPE_KINDS, "explanation_scope.scope_kind", path)
    expect_enum(scope["search_mode"], SEARCH_MODES, "explanation_scope.search_mode", path)
    expect_enum(scope["explanation_basis"], EXPLANATION_BASES, "explanation_scope.explanation_basis", path)

    result = data["explained_result"]
    require(result, ["result_ref", "result_title", "result_kind", "result_status", "result_lane", "limitations"], path)
    expect_enum(result["result_kind"], RESULT_KINDS, "explained_result.result_kind", path)
    expect_enum(result["result_status"], RESULT_STATUSES, "explained_result.result_status", path)
    expect_enum(result["result_lane"], RESULT_LANES, "explained_result.result_lane", path)

    query = data["query_interpretation"]
    if query.get("raw_query_included") is not False:
        raise ValidationError(f"{path}: query_interpretation.raw_query_included must be false")
    expect_enum(query.get("interpreted_intent"), INTENTS, "query_interpretation.interpreted_intent", path)
    expect_enum(query.get("interpretation_confidence"), CONFIDENCE, "query_interpretation.interpretation_confidence", path)
    expect_true(query, "interpretation_not_truth", path)

    match = data["match_and_recall"]
    expect_enum(match.get("recall_scope"), RECALL_SCOPES, "match_and_recall.recall_scope", path)
    expect_enum(match.get("match_strength"), STRENGTHS, "match_and_recall.match_strength", path)
    expect_true(match, "match_strength_not_truth", path)

    coverage = data["source_coverage"]
    expect_enum(coverage.get("source_coverage_status"), SOURCE_COVERAGE_STATUSES, "source_coverage.source_coverage_status", path)
    expect_true(coverage, "source_coverage_not_exhaustive", path)
    for item in coverage.get("not_checked_sources", []):
        expect_enum(item.get("reason_not_checked"), REASONS_NOT_CHECKED, "not_checked_sources.reason_not_checked", path)

    evidence = data["evidence_and_provenance"]
    expect_enum(evidence.get("evidence_strength"), STRENGTHS, "evidence_and_provenance.evidence_strength", path)
    expect_enum(evidence.get("provenance_strength"), STRENGTHS, "evidence_and_provenance.provenance_strength", path)
    expect_true(evidence, "evidence_not_truth", path)
    expect_true(evidence, "provenance_not_truth", path)
    if evidence.get("accepted_as_truth") is not False:
        raise ValidationError(f"{path}: evidence_and_provenance.accepted_as_truth must be false")

    identity = data["identity_grouping_deduplication"]
    expect_enum(identity.get("duplicate_or_variant_status"), DUP_STATUSES, "identity_grouping_deduplication.duplicate_or_variant_status", path)
    if identity.get("conflicts_hidden") is not False:
        raise ValidationError(f"{path}: conflicts_hidden must be false")
    if identity.get("destructive_merge_performed") is not False:
        raise ValidationError(f"{path}: destructive_merge_performed must be false")

    ranking = data["ranking_relationship"]
    if ranking.get("ranking_applied_to_live_search") is not False:
        raise ValidationError(f"{path}: ranking_applied_to_live_search must be false")
    if ranking.get("public_search_order_changed") is not False:
        raise ValidationError(f"{path}: public_search_order_changed must be false")
    if ranking.get("hidden_score_used") is not False:
        raise ValidationError(f"{path}: hidden_score_used must be false")
    expect_enum(ranking.get("numeric_score_publication_policy"), NUMERIC_SCORE_POLICIES, "numeric_score_publication_policy", path)
    expect_true(ranking, "ranking_not_truth", path)

    compatibility = data["compatibility"]
    expect_enum(compatibility.get("compatibility_status"), COMPATIBILITY_STATUSES, "compatibility.compatibility_status", path)
    expect_enum(compatibility.get("compatibility_evidence_strength"), STRENGTHS, "compatibility.compatibility_evidence_strength", path)
    expect_true(compatibility, "compatibility_not_truth", path)
    expect_false(compatibility, ["installability_claimed", "dependency_safety_claimed"], path)

    gaps = data["absence_near_miss_gaps"]
    expect_enum(gaps.get("absence_status"), ABSENCE_STATUSES, "absence_status", path)
    if gaps.get("global_absence_claimed") is not False:
        raise ValidationError(f"{path}: global_absence_claimed must be false")
    expect_true(gaps, "absence_not_truth", path)
    for gap in gaps.get("gaps", []):
        expect_enum(gap.get("gap_type"), GAP_TYPES, "gap_type", path)

    actions = data["action_safety"]
    if not set(actions.get("safe_actions", [])).issubset(SAFE_ACTIONS):
        raise ValidationError(f"{path}: unsupported safe action")
    if not set(actions.get("disabled_actions", [])).issubset(DISABLED_ACTIONS):
        raise ValidationError(f"{path}: unsupported disabled action")
    expect_enum(actions.get("action_safety_status"), ACTION_STATUSES, "action_safety_status", path)
    expect_false(actions, ["downloads_enabled", "installs_enabled", "execution_enabled", "package_manager_invoked", "emulator_vm_launch_enabled"], path)

    rights = data["rights_risk"]
    expect_enum(rights.get("rights_classification"), RIGHTS_CLASSIFICATIONS, "rights_classification", path)
    expect_enum(rights.get("risk_classification"), RISK_CLASSIFICATIONS, "risk_classification", path)
    expect_false(rights, ["rights_clearance_claimed", "malware_safety_claimed", "dependency_safety_claimed", "installability_claimed"], path)

    summary = data["user_facing_summary"]
    for field in ["summary_text", "why_this_result", "evidence_caveat", "source_caveat", "compatibility_caveat", "action_caveat", "gap_caveat"]:
        if not summary.get(field):
            raise ValidationError(f"{path}: user_facing_summary.{field} must be present")
    expect_true(summary, "plain_language_required", path)
    expect_true(summary, "no_marketing_claims", path)
    expect_true(summary, "no_unscoped_superiority_claims", path)

    api = data["api_projection"]
    if api.get("response_kind") != "search_result_explanation_response":
        raise ValidationError(f"{path}: api_projection.response_kind must be search_result_explanation_response")
    if api.get("route_future") not in {"/api/v1/search", "/api/v1/result/{result_id}/explanation", "/api/v1/result-group/{group_id}/explanation"}:
        raise ValidationError(f"{path}: unsupported api_projection.route_future")
    if api.get("implemented_now") is not False:
        raise ValidationError(f"{path}: api_projection.implemented_now must be false")

    static = data["static_lite_text_projection"]
    if static.get("generated_static_artifact") is not False:
        raise ValidationError(f"{path}: generated_static_artifact must be false")

    privacy = data["privacy"]
    expect_enum(privacy.get("privacy_classification"), PRIVACY_CLASSIFICATIONS, "privacy.privacy_classification", path)
    for field in ["raw_query_included", "contains_private_path", "contains_secret", "contains_private_url", "contains_user_identifier", "contains_ip_address", "contains_raw_private_query", "contains_local_machine_fingerprint"]:
        if privacy.get(field) is not False:
            raise ValidationError(f"{path}: privacy.{field} must be false")
    if privacy.get("publishable") is not True:
        raise ValidationError(f"{path}: privacy.publishable must be true")

    component_types = {validate_component(item, path) for item in data["detailed_components"]}
    missing = REQUIRED_COMPONENTS - component_types
    if missing:
        raise ValidationError(f"{path}: missing required component types {sorted(missing)}")
    if not (component_types & {"lexical_match", "identifier_match", "phrase_match", "alias_match", "source_match", "metadata_field_match", "compatibility_match", "member_match", "gap_explanation", "absence_explanation"}):
        raise ValidationError(f"{path}: missing match or gap component")
    validate_no_private_strings(data, path)
    if check_checksum:
        validate_checksums(path.parent)


def paths_from_args(args: argparse.Namespace) -> list[tuple[Path, bool]]:
    if args.explanation:
        return [(Path(args.explanation), False)]
    if args.explanation_root:
        return [(Path(args.explanation_root) / "SEARCH_RESULT_EXPLANATION.json", True)]
    return [(root / "SEARCH_RESULT_EXPLANATION.json", True) for root in example_roots()]


def emit(ok: bool, checked: list[str], errors: list[str], json_mode: bool) -> int:
    if json_mode:
        print(json.dumps({"ok": ok, "checked": checked, "error_count": len(errors), "errors": errors}, indent=2, sort_keys=True))
    elif ok:
        print(f"search result explanation validation passed: {len(checked)} item(s)")
    else:
        for error in errors:
            print(error, file=sys.stderr)
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka Search Result Explanation v0 examples.")
    parser.add_argument("--explanation")
    parser.add_argument("--explanation-root")
    parser.add_argument("--all-examples", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    checked: list[str] = []
    errors: list[str] = []
    for path, checksum in paths_from_args(args):
        try:
            validate_explanation(path, checksum)
            checked.append(str(path.relative_to(ROOT) if path.is_absolute() and path.is_relative_to(ROOT) else path))
        except Exception as exc:
            errors.append(str(exc))
    if not checked and not errors:
        errors.append("no search result explanation examples found")
    return emit(not errors, checked, errors, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
