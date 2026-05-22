"""Validate Track B Eureka Node policy governance artifacts.

This validator is local and read-only. It checks policy contracts, registries,
examples, and audit evidence without creating node runtime state or authorizing
source access.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = "contracts/node/node_policy.v0.json"
POLICY_REGISTRY_PATH = "control/inventory/nodes/node_policy_registry.json"
ACTION_POLICY_PATH = "control/inventory/nodes/node_action_policy.json"
SOURCE_ACCESS_POLICY_PATH = "control/inventory/nodes/node_source_access_policy.json"
OUTPUT_POLICY_PATH = "control/inventory/nodes/node_output_policy.json"
REVIEW_GATE_POLICY_PATH = "control/inventory/nodes/node_review_gate_policy.json"
AUDIT_REPORT_PATH = "control/audits/track-b-02-node-policy-contract-v0/track_b_02_report.json"
EXAMPLE_ROOT = "examples/nodes/policies"
DOC_PATHS = (
    "docs/reference/NODE_POLICY_CONTRACT.md",
    "docs/architecture/EUREKA_NODE_POLICY.md",
    "docs/operations/NODE_POLICY_REVIEW.md",
)

REQUIRED_STATUSES = {
    "example_only",
    "contract_only",
    "disabled",
    "dry_run_only",
    "review_required",
    "approval_gated",
    "operator_gated",
    "human_operated",
    "deferred",
    "blocked",
    "active_future",
}
CURRENT_EXAMPLE_STATUSES = REQUIRED_STATUSES - {"active_future"}
FUTURE_OR_GATED_STATUSES = {"deferred", "approval_gated", "operator_gated", "blocked"}
ALLOWED_MODES = {
    "local_private",
    "local_pack_builder",
    "local_autonomous_dry_run",
    "community_node_future",
    "institution_node_future",
    "hosted_worker_future",
}
ALLOWED_INPUTS = {
    "repo_local_fixture",
    "committed_pack_example",
    "committed_static_artifact",
    "committed_eval_report",
    "committed_audit_report",
    "manual_pending_slot",
    "observation_candidate",
    "observation_review_decision",
    "source_lead_candidate",
    "search_need_seed_future",
    "workunit_future",
    "node_manifest",
    "node_policy",
    "source_policy_future",
    "local_private_state_future",
}
FORBIDDEN_INPUTS = {
    "unapproved_live_source_result",
    "scraped_search_result",
    "scraped_forum_thread",
    "bulk_reddit_content",
    "private_user_file",
    "secret_or_credential",
    "executable_download",
    "installer_payload",
    "raw_browser_profile",
    "account_session_data",
    "telemetry_stream",
    "unreviewed_external_api_payload",
}
ALLOWED_ACTIONS = {
    "inspect_repo_local_artifact",
    "validate_contract",
    "validate_pack",
    "run_local_eval",
    "summarize_local_gap",
    "prepare_observation_candidate",
    "prepare_source_lead",
    "prepare_search_need_seed_future",
    "prepare_workunit_seed_future",
    "draft_evidence_candidate_future",
    "draft_candidate_record_future",
    "draft_pack_future",
    "produce_dry_run_report",
    "produce_review_packet",
    "request_human_review",
    "request_source_policy_approval_future",
}
FORBIDDEN_ACTIONS = {
    "mutate_master_index",
    "mark_candidate_accepted",
    "mark_evidence_accepted",
    "mark_observation_observed_without_human",
    "mark_agent_output_as_truth",
    "enable_live_probe",
    "scrape_external_site",
    "crawl_external_site",
    "browser_automation",
    "call_unapproved_api",
    "download_binary",
    "run_installer",
    "execute_downloaded_artifact",
    "store_credentials",
    "upload_to_hosted_backend",
    "create_account_or_user_data",
    "emit_telemetry",
    "claim_rights_clearance",
    "claim_malware_safety",
    "claim_verified_installability",
    "claim_exhaustive_global_search",
    "claim_production_readiness",
}
SOURCE_ACCESS_MODES = {
    "repo_local_only",
    "committed_fixture_only",
    "manual_human_only",
    "approved_api_future",
    "approved_metadata_probe_future",
    "approved_static_dump_future",
    "approved_common_crawl_or_archive_future",
    "permission_needed",
    "robots_blocked",
    "terms_blocked",
    "restricted_demand_signal_only",
    "no_autonomous_access",
}
CURRENT_SOURCE_ACCESS_MODES = {
    "repo_local_only",
    "committed_fixture_only",
    "manual_human_only",
    "no_autonomous_access",
}
ALLOWED_OUTPUTS = {
    "node_report",
    "dry_run_report",
    "observation_candidate",
    "observation_candidate_summary",
    "source_lead_candidate",
    "search_need_seed_future",
    "workunit_seed_future",
    "evidence_draft_future",
    "candidate_record_future",
    "contribution_pack_draft_future",
    "review_item_future",
    "pack_export_future",
}
FORBIDDEN_OUTPUTS = {
    "observed_baseline_truth",
    "accepted_evidence_truth",
    "accepted_public_record",
    "master_index_mutation",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search_proof",
    "production_readiness_claim",
}
REVIEW_GATES = {
    "human_review_required",
    "source_policy_review_required",
    "evidence_review_required",
    "candidate_review_required",
    "pack_review_required",
    "master_index_review_required",
    "rights_review_required",
    "risk_review_required",
    "privacy_review_required",
    "operator_approval_required_for_network",
    "operator_approval_required_for_hosted_behavior",
    "legal_or_rights_decision_stop_required",
}
REVIEW_OUTCOMES = {
    "approve_for_local_dry_run",
    "approve_as_source_lead",
    "approve_as_workunit_seed",
    "approve_for_manual_observation",
    "request_more_evidence",
    "reject",
    "mark_duplicate",
    "policy_block",
    "rights_block",
    "risk_block",
    "defer",
    "not_evaluable",
}
PRODUCT_BOUNDARY_FIELDS = {
    "implemented_node_runtime",
    "created_local_state",
    "enabled_network_access",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}
SOURCE_ACCESS_REQUIRED_FIELDS = {
    "source_id",
    "allowed_mode",
    "operator_approval_required",
    "human_review_required",
    "rate_limit_policy_future",
    "cache_ttl_policy_future",
    "User_Agent_contact_policy_future",
    "kill_switch_policy_future",
    "terms_robots_posture",
    "privacy_posture",
    "rights_risk_posture",
    "notes",
}
OUTPUT_TRUTH_FALSE_FIELDS = {
    "outputs_are_public_truth",
    "outputs_are_accepted_evidence",
    "outputs_may_mutate_master_index",
    "outputs_may_mark_observed_baselines",
}
PACK_FALSE_FIELDS = {
    "automatic_acceptance_allowed",
    "import_runtime_enabled",
    "upload_runtime_enabled",
    "hosted_submission_enabled",
}
EVIDENCE_CANDIDATE_FALSE_FIELDS = {
    "evidence_truth_allowed",
    "candidate_truth_allowed",
    "accepted_public_status_allowed",
    "master_index_mutation_allowed",
}
OBSERVATION_FALSE_FIELDS = {
    "may_mark_observed_baseline",
    "accepted_observation_truth_allowed",
}
FORBIDDEN_NETWORK_MODES = {
    "unapproved_live_probe",
    "arbitrary_url_fetch",
    "scraping",
    "crawling",
    "browser_automation",
    "bulk_forum_ingestion",
    "bulk_reddit_ingestion",
    "download_binary",
    "installer_execution",
    "api_without_approval",
}
SENSITIVE_KEY_NAMES = {"api_key", "password", "secret", "credential", "credentials", "token"}
PRIVATE_PATH_MARKERS = ("c:\\", "\\users\\", "/users/", "/home/")
FORBIDDEN_TEXT_CLAIMS = (
    "production ready",
    "production-ready",
    "rights clearance confirmed",
    "rights cleared",
    "malware safe",
    "malware-safe",
    "verified installability",
    "verified installable",
    "exhaustive global search proof",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka Node policy contract files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_eureka_node_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_eureka_node_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    schema = _load_json(root / SCHEMA_PATH, errors)
    policy_registry = _load_json(root / POLICY_REGISTRY_PATH, errors)
    action_policy = _load_json(root / ACTION_POLICY_PATH, errors)
    source_policy = _load_json(root / SOURCE_ACCESS_POLICY_PATH, errors)
    output_policy = _load_json(root / OUTPUT_POLICY_PATH, errors)
    review_policy = _load_json(root / REVIEW_GATE_POLICY_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_docs(root))
    errors.extend(validate_schema(schema, SCHEMA_PATH))
    errors.extend(validate_policy_registry(policy_registry, POLICY_REGISTRY_PATH))
    errors.extend(validate_action_policy(action_policy, ACTION_POLICY_PATH))
    errors.extend(validate_source_access_registry(source_policy, SOURCE_ACCESS_POLICY_PATH))
    errors.extend(validate_output_policy(output_policy, OUTPUT_POLICY_PATH))
    errors.extend(validate_review_gate_policy(review_policy, REVIEW_GATE_POLICY_PATH))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    example_paths = list_example_policy_paths(root)
    if len(example_paths) != 7:
        errors.append(f"{EXAMPLE_ROOT}: expected 7 example policies, found {len(example_paths)}")
    seen_ids: set[str] = set()
    for path in example_paths:
        payload = _load_json(path, errors)
        source = _relative(root, path)
        policy_id = _mapping(payload).get("node_policy_id")
        if isinstance(policy_id, str):
            if policy_id in seen_ids:
                errors.append(f"{source}: duplicate node_policy_id {policy_id}")
            seen_ids.add(policy_id)
        errors.extend(validate_node_policy_record(payload, source))

    return {
        "schema_version": "eureka_node_policy_validation.v0",
        "status": "valid" if not errors else "invalid",
        "validated_files": sorted(
            [
                SCHEMA_PATH,
                POLICY_REGISTRY_PATH,
                ACTION_POLICY_PATH,
                SOURCE_ACCESS_POLICY_PATH,
                OUTPUT_POLICY_PATH,
                REVIEW_GATE_POLICY_PATH,
                AUDIT_REPORT_PATH,
                *DOC_PATHS,
                *[_relative(root, path) for path in example_paths],
            ]
        ),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def list_example_policy_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    return sorted((repo_root.resolve() / EXAMPLE_ROOT).glob("*.json"))


def validate_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in DOC_PATHS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in ("node policy", "review", "source", "master index"):
            if phrase not in text:
                errors.append(f"{path}: missing required phrase {phrase!r}")
    return errors


def validate_schema(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("title") != "EurekaNodePolicyV0":
        errors.append(f"{source}: title must be EurekaNodePolicyV0")
    properties = _mapping(data.get("properties"))
    schema_version = _mapping(properties.get("schema_version"))
    if schema_version.get("const") != "node_policy.v0":
        errors.append(f"{source}: schema_version const must be node_policy.v0")
    errors.extend(_missing_items(data.get("required"), _required_fields(), f"{source}: required"))
    for key in (
        "x-node-runtime-implemented",
        "x-network-access-enabled",
        "x-local-state-created",
        "x-master-index-mutation-allowed",
    ):
        if data.get(key) is not False:
            errors.append(f"{source}: {key} must be false")
    return errors


def validate_policy_registry(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_policy_registry.v0":
        errors.append(f"{source}: schema_version must be node_policy_registry.v0")
    errors.extend(_missing_items(data.get("required_fields"), _required_fields(), f"{source}: required_fields"))
    errors.extend(_missing_items(data.get("allowed_policy_statuses"), REQUIRED_STATUSES, f"{source}: allowed_policy_statuses"))
    errors.extend(_missing_items(data.get("current_example_statuses"), CURRENT_EXAMPLE_STATUSES, f"{source}: current_example_statuses"))
    if len(_string_items(data.get("policy_refs"))) != 7:
        errors.append(f"{source}: policy_refs must contain 7 examples")
    errors.extend(_missing_items(data.get("product_boundary_false_fields"), PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary_false_fields"))
    return errors


def validate_action_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_action_policy.v0":
        errors.append(f"{source}: schema_version must be node_action_policy.v0")
    errors.extend(_missing_items(data.get("allowed_actions"), ALLOWED_ACTIONS, f"{source}: allowed_actions"))
    errors.extend(_missing_items(data.get("forbidden_actions"), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_source_access_registry(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_source_access_policy.v0":
        errors.append(f"{source}: schema_version must be node_source_access_policy.v0")
    errors.extend(_missing_items(data.get("source_access_modes"), SOURCE_ACCESS_MODES, f"{source}: source_access_modes"))
    errors.extend(_missing_items(data.get("current_allowed_modes"), CURRENT_SOURCE_ACCESS_MODES, f"{source}: current_allowed_modes"))
    errors.extend(_missing_items(data.get("required_source_access_fields"), SOURCE_ACCESS_REQUIRED_FIELDS, f"{source}: required_source_access_fields"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_output_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_output_policy.v0":
        errors.append(f"{source}: schema_version must be node_output_policy.v0")
    errors.extend(_missing_items(data.get("allowed_outputs"), ALLOWED_OUTPUTS, f"{source}: allowed_outputs"))
    errors.extend(_missing_items(data.get("forbidden_outputs"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))
    errors.extend(_missing_items(data.get("truth_boundary_false_fields"), OUTPUT_TRUTH_FALSE_FIELDS, f"{source}: truth_boundary_false_fields"))
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_review_gate_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_review_gate_policy.v0":
        errors.append(f"{source}: schema_version must be node_review_gate_policy.v0")
    errors.extend(_missing_items(data.get("review_gates"), REVIEW_GATES, f"{source}: review_gates"))
    errors.extend(_missing_items(data.get("review_outcomes"), REVIEW_OUTCOMES, f"{source}: review_outcomes"))
    approval = _mapping(data.get("approval_boundary"))
    for field in ("approval_is_public_truth", "approval_is_accepted_evidence", "approval_mutates_master_index"):
        if approval.get(field) is not False:
            errors.append(f"{source}: approval_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "track_b_02_report.v0":
        errors.append(f"{source}: schema_version must be track_b_02_report.v0")
    if data.get("task") != "TRACK-B-02":
        errors.append(f"{source}: task must be TRACK-B-02")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    truth = _mapping(data.get("truth_boundary"))
    for field in (
        "node_output_is_public_truth",
        "node_output_is_accepted_evidence",
        "node_can_mutate_master_index",
        "node_can_mark_observations_observed",
    ):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    return errors


def validate_node_policy_record(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "node_policy.v0":
        errors.append(f"{source}: schema_version must be node_policy.v0")
    errors.extend(_missing_items(data, _required_fields(), f"{source}: top-level"))

    status = str(data.get("policy_status", ""))
    if status not in REQUIRED_STATUSES:
        errors.append(f"{source}: policy_status {status!r} is not allowed")
    if status not in CURRENT_EXAMPLE_STATUSES:
        errors.append(f"{source}: current example policy_status {status!r} is not allowed")

    modes = set(_string_items(data.get("applies_to_node_modes")))
    errors.extend(_unknown_items(modes, ALLOWED_MODES, f"{source}: applies_to_node_modes"))
    for ref in _string_items(data.get("applies_to_node_manifest_refs")):
        if not (REPO_ROOT / ref).is_file():
            errors.append(f"{source}: manifest ref does not exist: {ref}")

    errors.extend(_unknown_items(set(_string_items(data.get("allowed_inputs"))), ALLOWED_INPUTS, f"{source}: allowed_inputs"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_inputs"))), FORBIDDEN_INPUTS, f"{source}: forbidden_inputs"))
    errors.extend(_missing_items(data.get("forbidden_inputs"), FORBIDDEN_INPUTS, f"{source}: forbidden_inputs"))
    errors.extend(_unknown_items(set(_string_items(data.get("allowed_actions"))), ALLOWED_ACTIONS, f"{source}: allowed_actions"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_actions"))), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))
    errors.extend(_missing_items(data.get("forbidden_actions"), FORBIDDEN_ACTIONS, f"{source}: forbidden_actions"))

    outputs = _mapping(data.get("allowed_outputs"))
    errors.extend(_unknown_items(set(_string_items(outputs.get("categories"))), ALLOWED_OUTPUTS, f"{source}: allowed_outputs.categories"))
    errors.extend(_false_field_errors(outputs, OUTPUT_TRUTH_FALSE_FIELDS, f"{source}: allowed_outputs"))
    errors.extend(_unknown_items(set(_string_items(data.get("forbidden_outputs"))), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))
    errors.extend(_missing_items(data.get("forbidden_outputs"), FORBIDDEN_OUTPUTS, f"{source}: forbidden_outputs"))

    source_access = _mapping(data.get("source_access_policy"))
    errors.extend(_missing_items(source_access, SOURCE_ACCESS_REQUIRED_FIELDS, f"{source}: source_access_policy"))
    mode = str(source_access.get("allowed_mode", ""))
    if mode not in SOURCE_ACCESS_MODES:
        errors.append(f"{source}: source_access_policy.allowed_mode {mode!r} is not allowed")
    if mode not in CURRENT_SOURCE_ACCESS_MODES and status not in FUTURE_OR_GATED_STATUSES:
        errors.append(f"{source}: future source access mode {mode!r} requires deferred or approval-gated status")
    if source_access.get("operator_approval_required") is not True:
        errors.append(f"{source}: source_access_policy.operator_approval_required must be true")
    if source_access.get("human_review_required") is not True:
        errors.append(f"{source}: source_access_policy.human_review_required must be true")

    network = _mapping(data.get("network_policy"))
    if network.get("network_enabled") is not False:
        errors.append(f"{source}: network_policy.network_enabled must be false")
    if _string_items(network.get("allowed_network_modes")):
        errors.append(f"{source}: network_policy.allowed_network_modes must be empty for current examples")
    errors.extend(_missing_items(network.get("forbidden_network_modes"), FORBIDDEN_NETWORK_MODES, f"{source}: network_policy.forbidden_network_modes"))
    for field in ("requires_operator_approval", "requires_source_policy", "requires_kill_switch", "requires_rate_limit"):
        if network.get(field) is not True:
            errors.append(f"{source}: network_policy.{field} must be true")

    local_state = _mapping(data.get("local_state_policy"))
    if local_state.get("local_state_enabled") is not False:
        errors.append(f"{source}: local_state_policy.local_state_enabled must be false")
    if local_state.get("local_state_root_future") is not None:
        errors.append(f"{source}: local_state_policy.local_state_root_future must be null")
    if local_state.get("public_export_requires_review") is not True:
        errors.append(f"{source}: local_state_policy.public_export_requires_review must be true")

    review = _mapping(data.get("review_gate_policy"))
    for gate in sorted(REVIEW_GATES):
        if review.get(gate) is not True:
            errors.append(f"{source}: review_gate_policy.{gate} must be true")
    errors.extend(_missing_items(review.get("allowed_review_outcomes"), REVIEW_OUTCOMES, f"{source}: review_gate_policy.allowed_review_outcomes"))
    if review.get("approval_is_public_truth") is not False:
        errors.append(f"{source}: review_gate_policy.approval_is_public_truth must be false")

    pack = _mapping(data.get("pack_policy"))
    errors.extend(_false_field_errors(pack, PACK_FALSE_FIELDS, f"{source}: pack_policy"))
    if pack.get("review_required_before_submission") is not True:
        errors.append(f"{source}: pack_policy.review_required_before_submission must be true")

    evidence = _mapping(data.get("evidence_policy"))
    errors.extend(_false_field_errors(evidence, {"evidence_truth_allowed", "accepted_public_status_allowed", "master_index_mutation_allowed"}, f"{source}: evidence_policy"))
    if evidence.get("review_required") is not True:
        errors.append(f"{source}: evidence_policy.review_required must be true")

    candidate = _mapping(data.get("candidate_policy"))
    errors.extend(_false_field_errors(candidate, {"candidate_truth_allowed", "accepted_public_status_allowed", "master_index_mutation_allowed"}, f"{source}: candidate_policy"))
    if candidate.get("review_required") is not True:
        errors.append(f"{source}: candidate_policy.review_required must be true")

    observation = _mapping(data.get("observation_policy"))
    errors.extend(_false_field_errors(observation, OBSERVATION_FALSE_FIELDS, f"{source}: observation_policy"))
    if observation.get("human_observation_required") is not True:
        errors.append(f"{source}: observation_policy.human_observation_required must be true")

    privacy = _mapping(data.get("privacy_policy"))
    for field in ("private_user_data_allowed", "account_session_data_allowed", "raw_query_telemetry_allowed"):
        if privacy.get(field) is not False:
            errors.append(f"{source}: privacy_policy.{field} must be false")
    if privacy.get("no_private_data_publication") is not True:
        errors.append(f"{source}: privacy_policy.no_private_data_publication must be true")

    rights = _mapping(data.get("rights_policy"))
    if rights.get("may_claim_rights_clearance") is not False:
        errors.append(f"{source}: rights_policy.may_claim_rights_clearance must be false")
    if rights.get("rights_review_required") is not True:
        errors.append(f"{source}: rights_policy.rights_review_required must be true")

    risk = _mapping(data.get("risk_policy"))
    if risk.get("may_claim_malware_safety") is not False:
        errors.append(f"{source}: risk_policy.may_claim_malware_safety must be false")
    if risk.get("may_claim_verified_installability") is not False:
        errors.append(f"{source}: risk_policy.may_claim_verified_installability must be false")
    if risk.get("risk_review_required") is not True:
        errors.append(f"{source}: risk_policy.risk_review_required must be true")

    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    errors.extend(_sensitive_key_errors(data, source))
    errors.extend(_private_path_errors(data, source))
    errors.extend(_forbidden_text_claim_errors(data, source))
    return errors


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [f"validate_eureka_node_policy: {report['status']}"]
    lines.append(f"schema_version: {report['schema_version']}")
    lines.append(f"validated_files: {len(report.get('validated_files', []))}")
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_relative(REPO_ROOT, path)}: missing file")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_relative(REPO_ROOT, path)}: invalid JSON: {exc}")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _missing_items(value: Any, required: set[str], label: str) -> list[str]:
    if isinstance(value, Mapping):
        present = set(str(key) for key in value)
    elif isinstance(value, set):
        present = set(value)
    else:
        present = set(_string_items(value))
    return [f"{label} missing {item}" for item in sorted(required - present)]


def _unknown_items(value: set[str], allowed: set[str], label: str) -> list[str]:
    return [f"{label} unknown {item}" for item in sorted(value - allowed)]


def _boundary_false_errors(payload: Mapping[str, Any], source: str) -> list[str]:
    return _false_field_errors(payload, PRODUCT_BOUNDARY_FIELDS, f"{source}: product_boundary")


def _false_field_errors(payload: Mapping[str, Any], fields: set[str], label: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if payload.get(field) is not False:
            errors.append(f"{label}.{field} must be false")
    return errors


def _sensitive_key_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in SENSITIVE_KEY_NAMES:
                errors.append(f"{source}: sensitive key {path}.{key_text} is not allowed")
            errors.extend(_sensitive_key_errors(child, source, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_key_errors(child, source, f"{path}[{index}]"))
    return errors


def _private_path_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            errors.append(f"{source}: private/local user path marker at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_private_path_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_private_path_errors(child, source, f"{path}[{index}]"))
    return errors


def _forbidden_text_claim_errors(value: Any, source: str, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, str):
        lowered = value.lower()
        for marker in FORBIDDEN_TEXT_CLAIMS:
            if marker in lowered:
                errors.append(f"{source}: forbidden product claim marker {marker!r} at {path}")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_text_claim_errors(child, source, f"{path}[{index}]"))
    return errors


def _required_fields() -> set[str]:
    return {
        "schema_version",
        "node_policy_id",
        "policy_label",
        "policy_status",
        "applies_to_node_modes",
        "applies_to_node_manifest_refs",
        "allowed_inputs",
        "forbidden_inputs",
        "allowed_actions",
        "forbidden_actions",
        "allowed_outputs",
        "forbidden_outputs",
        "source_access_policy",
        "network_policy",
        "local_state_policy",
        "privacy_policy",
        "rights_policy",
        "risk_policy",
        "review_gate_policy",
        "pack_policy",
        "evidence_policy",
        "candidate_policy",
        "observation_policy",
        "workunit_policy_future",
        "budget_policy_future",
        "audit_policy",
        "product_boundary",
        "no_goals",
        "notes",
    }


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
