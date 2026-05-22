"""Validate observation candidate contracts and examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_CONTRACT = "contracts/control_schemas/previews/query/observation_candidate.v0.json"
REVIEW_CONTRACT = "contracts/query/observation_review_decision.v0.json"
CANDIDATE_EXAMPLES = (
    "examples/observation_candidates/local_eval_extraction_gap_candidate_v0.json",
    "examples/observation_candidates/local_eval_failure_mining_batch_0_v0.json",
    "examples/observation_candidates/local_eval_failure_observation_candidate_v0.json",
    "examples/observation_candidates/local_eval_policy_blocked_candidate_v0.json",
    "examples/observation_candidates/local_eval_ranking_gap_candidate_v0.json",
    "examples/observation_candidates/local_eval_source_gap_candidate_v0.json",
    "examples/observation_candidates/minimal_observation_candidate_v0.json",
    "examples/observation_candidates/policy_blocked_observation_candidate_v0.json",
    "examples/observation_candidates/source_gap_github_releases_candidate_v0.json",
    "examples/observation_candidates/source_gap_internet_archive_metadata_candidate_v0.json",
    "examples/observation_candidates/source_gap_manual_only_forum_candidate_v0.json",
    "examples/observation_candidates/source_gap_package_registry_candidate_v0.json",
    "examples/observation_candidates/source_gap_policy_blocked_candidate_v0.json",
    "examples/observation_candidates/source_gap_wayback_metadata_candidate_v0.json",
    "examples/observation_candidates/source_lead_observation_candidate_v0.json",
)
REVIEW_EXAMPLES = (
    "examples/observation_reviews/approve_observation_candidate_review_v0.json",
    "examples/observation_reviews/reject_observation_candidate_review_v0.json",
    "examples/observation_reviews/request_more_evidence_review_v0.json",
)
CANDIDATE_TYPES = {
    "local_eval_failure",
    "source_lead",
    "search_need_seed",
    "work_unit_seed",
    "manual_slot_suggestion",
    "approved_api_result_future",
    "approved_metadata_probe_result_future",
    "policy_blocked_candidate",
    "not_evaluable_candidate",
}
ORIGINS = {
    "local_eval",
    "static_demo",
    "search_usefulness_audit",
    "committed_fixture",
    "manual_pending_slot",
    "approved_api_future",
    "approved_metadata_probe_future",
    "human_note_future",
    "ai_summary_future",
}
SOURCE_ACCESS_MODES = {
    "repo_local_only",
    "manual_human_only",
    "approved_api_future",
    "approved_metadata_probe_future",
    "approved_fixture_only",
    "approved_static_dump_future",
    "permission_needed",
    "robots_blocked",
    "terms_blocked",
    "restricted_demand_signal_only",
    "no_autonomous_access",
}
REVIEW_DECISIONS = {
    "approve_as_source_lead",
    "approve_as_work_unit_seed",
    "approve_for_manual_observation",
    "reject",
    "request_more_evidence",
    "mark_duplicate",
    "mark_policy_blocked",
    "defer",
    "not_evaluable",
}
PRODUCT_BOUNDARY_FIELDS = {
    "performed_observations",
    "automated_external_search",
    "scraped_external_systems",
    "crawled_external_systems",
    "called_external_apis",
    "opened_browsers",
    "fabricated_results",
    "marked_pending_as_observed",
    "changed_product_behavior",
    "changed_public_routes",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "mutated_master_index",
}
FORBIDDEN_TEXT_MARKERS = (
    "scraped google result",
    "scrape_google",
    "unapproved live source",
    "live source observed",
    "downloaded binary",
    "rights clearance confirmed",
    "malware safe",
    "master index mutation",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate observation candidate and review examples.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--candidate-file", help="Validate one candidate JSON file.")
    parser.add_argument("--review-file", help="Validate one review decision JSON file.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root)
    if args.candidate_file:
        payload = _load_json(Path(args.candidate_file), [])
        errors = validate_candidate_record(payload, args.candidate_file)
        report = _single_report("candidate", args.candidate_file, errors)
    elif args.review_file:
        payload = _load_json(Path(args.review_file), [])
        errors = validate_review_record(payload, args.review_file)
        report = _single_report("review", args.review_file, errors)
    else:
        report = validate_observation_candidates(root)

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_observation_candidates(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    for path in (CANDIDATE_CONTRACT, REVIEW_CONTRACT):
        payload = _load_json(root / path, errors)
        if not isinstance(payload, Mapping):
            errors.append(f"{path}: contract must be a JSON object")
    for path in CANDIDATE_EXAMPLES:
        payload = _load_json(root / path, errors)
        errors.extend(validate_candidate_record(payload, path))
    for path in REVIEW_EXAMPLES:
        payload = _load_json(root / path, errors)
        errors.extend(validate_review_record(payload, path))
    return {
        "schema_version": "observation_candidate_validation.v0",
        "status": "valid" if not errors else "invalid",
        "candidate_examples": list(CANDIDATE_EXAMPLES),
        "review_examples": list(REVIEW_EXAMPLES),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_candidate_record(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_candidate.v0":
        errors.append(f"{source}: schema_version must be observation_candidate.v0")
    for field in ("observation_candidate_id", "candidate_type", "candidate_status", "origin", "source_access_mode", "source_policy_status", "candidate_summary", "limitations"):
        if field not in data:
            errors.append(f"{source}: missing {field}")
    if data.get("candidate_type") not in CANDIDATE_TYPES:
        errors.append(f"{source}: invalid candidate_type {data.get('candidate_type')!r}")
    if data.get("origin") not in ORIGINS:
        errors.append(f"{source}: invalid origin {data.get('origin')!r}")
    if data.get("source_access_mode") not in SOURCE_ACCESS_MODES:
        errors.append(f"{source}: invalid source_access_mode {data.get('source_access_mode')!r}")
    if data.get("required_human_review") is not True:
        errors.append(f"{source}: required_human_review must be true")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_forbidden_text_errors(data, source))
    mode = data.get("source_access_mode")
    policy_status = str(data.get("source_policy_status", "")).lower()
    if mode in {"approved_api_future", "approved_metadata_probe_future", "approved_static_dump_future"}:
        if "future" not in policy_status and "deferred" not in policy_status and "required" not in policy_status:
            errors.append(f"{source}: future source access modes must remain future/deferred or policy-required")
    if data.get("candidate_type") == "policy_blocked_candidate" and "block" not in policy_status:
        errors.append(f"{source}: policy_blocked_candidate must remain blocked")
    if data.get("origin") == "ai_summary_future" and data.get("accepted_as_evidence_truth") is not False:
        errors.append(f"{source}: AI summary must not be evidence truth")
    return errors


def validate_review_record(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_review_decision.v0":
        errors.append(f"{source}: schema_version must be observation_review_decision.v0")
    for field in ("review_decision_id", "observation_candidate_id", "reviewer", "reviewed_at", "decision", "decision_scope", "approved_next_actions", "rejected_next_actions", "rationale"):
        if field not in data:
            errors.append(f"{source}: missing {field}")
    if data.get("decision") not in REVIEW_DECISIONS:
        errors.append(f"{source}: invalid decision {data.get('decision')!r}")
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    rejected = set(_string_items(data.get("rejected_next_actions")))
    for action in ("mark_evidence_truth", "mutate_master_index"):
        if action not in rejected and data.get("decision") not in {"reject", "mark_policy_blocked", "not_evaluable"}:
            errors.append(f"{source}: rejected_next_actions should include {action}")
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def _single_report(kind: str, source: str, errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "observation_candidate_validation.v0",
        "status": "valid" if not errors else "invalid",
        "kind": kind,
        "source": source,
        "errors": sorted(set(errors)),
        "warnings": [],
    }


def _boundary_false_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(PRODUCT_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _forbidden_text_errors(payload: Any, source: str) -> list[str]:
    text = json.dumps(payload, sort_keys=True).lower()
    return [f"{source}: forbidden claim marker {marker}" for marker in FORBIDDEN_TEXT_MARKERS if marker in text]


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_observation_candidate: {report['status']}",
        f"schema_version: {report['schema_version']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
