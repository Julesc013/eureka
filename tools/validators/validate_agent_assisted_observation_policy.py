"""Validate OBS agent-assisted observation policy files.

The validator is local and read-only. It checks governance files for the
review-gated OBS workflow without authorizing source access or performing
observations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_POLICY_PATH = "control/inventory/observations/agent_assisted_observation_policy.json"
REVIEW_POLICY_PATH = "control/inventory/observations/observation_candidate_review_policy.json"
PARALLEL_POLICY_PATH = "control/inventory/observations/obs_parallel_development_policy.json"
SOURCE_MODES_PATH = "control/inventory/observations/observation_source_access_modes.json"
AUDIT_REPORT_PATH = "control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json"
DOC_PATHS = (
    "docs/operations/AGENT_ASSISTED_OBSERVATION_WORKFLOW.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW.md",
    "docs/operations/OBSERVATION_SOURCE_ACCESS_POLICY.md",
    "docs/operations/OBS_PARALLEL_DEVELOPMENT_POLICY.md",
)

ALLOWED_AGENT_ACTIONS = {
    "run_repo_local_tests",
    "run_repo_local_evals",
    "run_search_usefulness_audits",
    "mine_local_failure_reports",
    "inspect_committed_fixtures",
    "summarize_local_source_gaps",
    "produce_observation_candidates",
    "produce_source_lead_candidates",
    "produce_work_unit_candidates",
    "prepare_review_packets",
    "prepare_source_policy_decision_packets",
    "prepare_approved_source_fixture_normalizers",
}
FORBIDDEN_AGENT_ACTIONS = {
    "scrape_google_search_results",
    "browser_automation",
    "browser_opening",
    "unapproved_forum_crawling",
    "bulk_reddit_ingestion",
    "external_api_call_without_explicit_source_approval",
    "live_source_probe_without_explicit_approval",
    "automatic_binary_download",
    "claim_rights_clearance",
    "claim_malware_safety",
    "treat_ai_summary_as_evidence",
    "treat_source_lead_as_accepted_truth",
    "treat_observation_candidate_as_observed_baseline",
    "mutate_master_index",
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
REVIEW_STATES = {
    "proposed",
    "needs_human_review",
    "approved_for_manual_observation",
    "approved_as_source_lead",
    "approved_as_work_unit_seed",
    "rejected",
    "duplicate",
    "policy_blocked",
    "needs_more_evidence",
    "deferred",
}
DECISIONS = {
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
FORBIDDEN_AUTHORIZATION_MARKERS = (
    "scraping_allowed",
    "live_probes_enabled",
    "downloads_enabled",
    "accounts_enabled",
    "telemetry_enabled",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent-assisted observation governance policy.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_agent_assisted_observation_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_agent_assisted_observation_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    agent_policy = _load_json(root / AGENT_POLICY_PATH, errors)
    review_policy = _load_json(root / REVIEW_POLICY_PATH, errors)
    parallel_policy = _load_json(root / PARALLEL_POLICY_PATH, errors)
    source_modes = _load_json(root / SOURCE_MODES_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_docs(root, DOC_PATHS))
    errors.extend(validate_agent_policy(agent_policy, AGENT_POLICY_PATH))
    errors.extend(validate_review_policy(review_policy, REVIEW_POLICY_PATH))
    errors.extend(validate_parallel_policy(parallel_policy, PARALLEL_POLICY_PATH))
    errors.extend(validate_source_access_modes(source_modes, SOURCE_MODES_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    return {
        "schema_version": "agent_assisted_observation_policy_validation.v0",
        "status": "valid" if not errors else "invalid",
        "policy_files": [
            AGENT_POLICY_PATH,
            REVIEW_POLICY_PATH,
            PARALLEL_POLICY_PATH,
            SOURCE_MODES_PATH,
        ],
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_docs(repo_root: Path, paths: Sequence[str]) -> list[str]:
    errors: list[str] = []
    required_phrases = ("manual", "agent", "review")
    for path in paths:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{path}: missing phrase {phrase!r}")
    return errors


def validate_agent_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "agent_assisted_observation_policy.v0":
        errors.append(f"{source}: schema_version must be agent_assisted_observation_policy.v0")
    errors.extend(_missing_items(data.get("allowed_agent_actions"), ALLOWED_AGENT_ACTIONS, f"{source}: allowed_agent_actions"))
    errors.extend(_missing_items(data.get("forbidden_agent_actions"), FORBIDDEN_AGENT_ACTIONS, f"{source}: forbidden_agent_actions"))
    errors.extend(_missing_items(data.get("source_access_modes"), SOURCE_ACCESS_MODES, f"{source}: source_access_modes"))
    errors.extend(_missing_items(data.get("required_review_states"), REVIEW_STATES, f"{source}: required_review_states"))
    if data.get("source_access_modes_ref") != SOURCE_MODES_PATH:
        errors.append(f"{source}: source_access_modes_ref must be {SOURCE_MODES_PATH}")
    truth = set(_string_items(data.get("forbidden_truth_conversions")))
    for item in (
        "candidate_to_observed_baseline_without_manual_observation",
        "agent_summary_to_evidence_truth",
        "source_lead_to_source_validation",
        "google_scrape_to_approved_source",
        "candidate_to_master_index_mutation",
    ):
        if item not in truth:
            errors.append(f"{source}: forbidden_truth_conversions missing {item}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_forbidden_marker_errors(data, source))
    return errors


def validate_review_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_candidate_review_policy.v0":
        errors.append(f"{source}: schema_version must be observation_candidate_review_policy.v0")
    errors.extend(_missing_items(data.get("review_states"), REVIEW_STATES, f"{source}: review_states"))
    errors.extend(_missing_items(data.get("decisions"), DECISIONS, f"{source}: decisions"))
    for field in ("accepted_as_observed_baseline", "accepted_as_evidence_truth", "master_index_mutation_allowed"):
        if field not in _string_items(data.get("required_false_booleans")):
            errors.append(f"{source}: required_false_booleans missing {field}")
    for action in ("mark_observed_baseline", "mark_evidence_truth", "mutate_master_index", "scrape_google_results"):
        if action not in _string_items(data.get("forbidden_next_actions")):
            errors.append(f"{source}: forbidden_next_actions missing {action}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_forbidden_marker_errors(data, source))
    return errors


def validate_parallel_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_parallel_development_policy.v0":
        errors.append(f"{source}: schema_version must be obs_parallel_development_policy.v0")
    if data.get("main_track_can_continue_in_parallel") is not True:
        errors.append(f"{source}: main_track_can_continue_in_parallel must be true")
    if data.get("manual_observation_blocks_all_development") is not False:
        errors.append(f"{source}: manual_observation_blocks_all_development must be false")
    if data.get("human_review_required") is not True:
        errors.append(f"{source}: human_review_required must be true")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_source_access_modes(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "observation_source_access_modes.v0":
        errors.append(f"{source}: schema_version must be observation_source_access_modes.v0")
    modes = data.get("modes")
    if not isinstance(modes, list):
        return errors + [f"{source}: modes must be a list"]
    found: set[str] = set()
    for index, mode in enumerate(modes):
        item = _mapping(mode)
        mode_id = item.get("mode_id")
        if not isinstance(mode_id, str):
            errors.append(f"{source}: modes[{index}] missing mode_id")
            continue
        found.add(mode_id)
        if mode_id not in {"repo_local_only", "approved_fixture_only"} and item.get("current_agent_access_allowed") is not False:
            errors.append(f"{source}: {mode_id} must not allow current agent source access")
    for mode in sorted(SOURCE_ACCESS_MODES):
        if mode not in found:
            errors.append(f"{source}: missing source access mode {mode}")
    requirements = set(_string_items(data.get("source_policy_approval_requirements")))
    for field in ("source_id", "rate_limit", "user_agent_contact_policy", "kill_switch", "operator_approval", "review_requirement"):
        if field not in requirements:
            errors.append(f"{source}: source_policy_approval_requirements missing {field}")
    if data.get("google_web_search_posture") != "manual_human_only_without_approved_api":
        errors.append(f"{source}: google_web_search_posture must remain manual_human_only_without_approved_api")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_replan_01_report.v0":
        errors.append(f"{source}: schema_version must be obs_replan_01_report.v0")
    workflow = _mapping(data.get("workflow_decision"))
    if workflow.get("manual_observation_remains_gold_standard") is not True:
        errors.append(f"{source}: manual_observation_remains_gold_standard must be true")
    if workflow.get("human_review_required") is not True:
        errors.append(f"{source}: human_review_required must be true")
    if workflow.get("main_track_can_continue_in_parallel") is not True:
        errors.append(f"{source}: main_track_can_continue_in_parallel must be true")
    truth = _mapping(data.get("truth_boundary"))
    for field in ("candidate_is_observed_baseline", "agent_summary_is_evidence_truth", "source_lead_is_source_validation", "master_index_mutation_allowed"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("review_required_before_downstream_use") is not True:
        errors.append(f"{source}: truth_boundary.review_required_before_downstream_use must be true")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def _boundary_false_errors(boundary: Mapping[str, Any], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(PRODUCT_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _forbidden_marker_errors(payload: Any, source: str) -> list[str]:
    text = json.dumps(payload, sort_keys=True).lower()
    errors: list[str] = []
    for marker in FORBIDDEN_AUTHORIZATION_MARKERS:
        if marker in text and f'"{marker}": false' not in text:
            errors.append(f"{source}: contains unsafe authorization marker {marker}")
    return errors


def _missing_items(value: Any, required: set[str], source: str) -> list[str]:
    found = set(_string_items(value))
    return [f"{source} missing {item}" for item in sorted(required - found)]


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
        f"validate_agent_assisted_observation_policy: {report['status']}",
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
