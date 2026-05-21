#!/usr/bin/env python3
"""Validate SEARCH-INTERACTION-00 contract artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "SEARCH-INTERACTION-00"

REQUIRED_PACKETS = {
    "SearchRequestPacket": "search_request_packet.v0.json",
    "CompiledQueryPacket": "compiled_query_packet.v0.json",
    "ResolutionRunPacket": "resolution_run_packet.v0.json",
    "ResultLanePacket": "result_lane_packet.v0.json",
    "PartialResultPacket": "partial_result_packet.v0.json",
    "CandidateClusterPacket": "candidate_cluster_packet.v0.json",
    "ActionPosturePacket": "action_posture_packet.v0.json",
    "SearchControlCommand": "search_control_command.v0.json",
    "UserFeedbackEvent": "user_feedback_event.v0.json",
    "SearchPlanPatch": "search_plan_patch.v0.json",
    "AbsencePacket": "absence_packet.v0.json",
    "CoverageReportPacket": "coverage_report_packet.v0.json",
    "DiscoveryTrailPacket": "discovery_trail_packet.v0.json",
}
REQUIRED_STATES = {
    "accepted", "compiled", "local_index_running", "local_results_available", "candidate_index_running",
    "candidate_results_available", "source_cache_running", "source_cache_results_available", "hunt_planning",
    "hunt_running", "source_workunit_queued", "source_workunit_running", "source_candidates_available",
    "review_items_available", "index_rebuild_available", "paused", "resumed", "cancelled", "completed", "failed",
}
REQUIRED_CONTROLS = {
    "pause", "resume", "cancel", "deepen", "narrow", "broaden", "refine_query", "add_constraint",
    "remove_constraint", "include_source", "exclude_source", "prefer_source", "suppress_source",
    "inspect_candidate", "accept_candidate_for_review", "reject_candidate", "mark_near_miss",
    "mark_duplicate", "mark_policy_blocked", "request_more_evidence", "export_resolution_packet",
    "save_search", "watch_need",
}
REQUIRED_FEEDBACK = {
    "right_app_wrong_version", "right_era_wrong_platform", "wrong_object_family", "ignore_isos",
    "only_portable_apps", "search_deeper_inside_bundles", "source_relevant", "source_not_relevant",
    "file_path_promising", "needs_manual_review",
}
REQUIRED_LANES = {
    "reviewed_local_results", "local_candidate_results", "source_cache_hits", "IA_metadata_candidates",
    "review_queue_items", "known_absence", "near_misses", "blocked_actions", "running_workunits",
    "deferred_deepening", "future_extraction_work",
}
REQUIRED_JSON = {
    "control/inventory/search_interaction_input_state.json": "search_interaction_input_state.v0",
    "control/inventory/search_interaction_packet_inventory.json": "search_interaction_packet_inventory.v0",
    "control/inventory/search_interaction_state_machine.json": "search_interaction_state_machine.v0",
    "control/inventory/search_interaction_control_command_matrix.json": "search_interaction_control_command_matrix.v0",
    "control/inventory/search_interaction_feedback_event_matrix.json": "search_interaction_feedback_event_matrix.v0",
    "control/inventory/search_interaction_query_compilation_matrix.json": "search_interaction_query_compilation_matrix.v0",
    "control/inventory/search_interaction_result_lane_contract_matrix.json": "search_interaction_result_lane_contract_matrix.v0",
    "control/inventory/search_interaction_projection_matrix.json": "search_interaction_projection_matrix.v0",
    "control/inventory/search_interaction_permission_matrix.json": "search_interaction_permission_matrix.v0",
    "control/inventory/search_interaction_handoff_matrix.json": "search_interaction_handoff_matrix.v0",
    "control/inventory/search_interaction_validator_matrix.json": "search_interaction_validator_matrix.v0",
    "control/inventory/search_interaction_result.json": "search_interaction_result.v0",
    "control/inventory/search_interaction_next_task_decision.json": "search_interaction_next_task_decision.v0",
    "control/policies/search_interaction_policy.json": "search_interaction_policy.v0",
    "control/policies/search_interaction_control_policy.json": "search_interaction_control_policy.v0",
    "control/policies/search_interaction_feedback_policy.json": "search_interaction_feedback_policy.v0",
    "control/policies/search_interaction_non_claim_policy.json": "search_interaction_non_claim_policy.v0",
    "control/policies/search_interaction_future_ai_policy.json": "search_interaction_future_ai_policy.v0",
    "control/audits/search-interaction-00-v0/search_interaction_report.json": "search_interaction_report.v0",
}
REQUIRED_DOCS = [
    "docs/architecture/SEARCH_INTERACTION_CONTRACT.md",
    "docs/architecture/SEARCH_RESOLUTION_RUN_MODEL.md",
    "docs/architecture/QUERY_COMPILATION_MODEL.md",
    "docs/architecture/SEARCH_CONTROL_AND_FEEDBACK_MODEL.md",
    "docs/operations/SEARCH_INTERACTION_PLAN.md",
    "docs/operations/POST_SEARCH_INTERACTION_PLAN.md",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("Search Interaction contract validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")
    for packet_id, filename in REQUIRED_PACKETS.items():
        path = root / "contracts/search_interaction" / filename
        packet = load_json(path, "", errors, require_schema=False)
        if packet.get("properties", {}).get("packet_type", {}).get("const") != packet_id:
            errors.append(f"{filename} packet_type must be {packet_id}")
        for field in ("schema_version", "packet_type"):
            if field not in packet.get("required", []):
                errors.append(f"{filename} missing required {field}")

    inventory_packets = {item.get("packet_id") for item in payloads["control/inventory/search_interaction_packet_inventory.json"].get("packets", [])}
    if set(REQUIRED_PACKETS) - inventory_packets:
        errors.append(f"packet inventory missing packets: {sorted(set(REQUIRED_PACKETS) - inventory_packets)}")

    state = payloads["control/inventory/search_interaction_state_machine.json"]
    if REQUIRED_STATES - set(state.get("states", [])):
        errors.append(f"state machine missing states: {sorted(REQUIRED_STATES - set(state.get('states', [])))}")
    for illegal in (["completed", "hunt_running"], ["cancelled", "hunt_running"], ["failed", "completed"]):
        if illegal not in state.get("illegal_transitions", []):
            errors.append(f"state machine must reject {illegal}")

    commands = {item.get("command_type"): item for item in payloads["control/inventory/search_interaction_control_command_matrix.json"].get("commands", [])}
    if REQUIRED_CONTROLS - set(commands):
        errors.append(f"control matrix missing controls: {sorted(REQUIRED_CONTROLS - set(commands))}")
    for command in ("accept_candidate_for_review", "request_more_evidence"):
        if commands.get(command, {}).get("allowed_public") is not False:
            errors.append(f"{command} must not be public-allowed")

    feedback = {item.get("feedback_type"): item for item in payloads["control/inventory/search_interaction_feedback_event_matrix.json"].get("feedback_events", [])}
    if REQUIRED_FEEDBACK - set(feedback):
        errors.append(f"feedback matrix missing events: {sorted(REQUIRED_FEEDBACK - set(feedback))}")
    for item in feedback.values():
        if item.get("creates_plan_patch") is not True:
            errors.append("feedback must create plan patch")

    lanes = {item.get("lane_kind"): item for item in payloads["control/inventory/search_interaction_result_lane_contract_matrix.json"].get("lanes", [])}
    if REQUIRED_LANES - set(lanes):
        errors.append(f"result lane matrix missing lanes: {sorted(REQUIRED_LANES - set(lanes))}")
    for lane_id, lane in lanes.items():
        if not lane.get("truth_level"):
            errors.append(f"{lane_id} missing truth_level")

    projections = {item.get("projection_profile"): item for item in payloads["control/inventory/search_interaction_projection_matrix.json"].get("profiles", [])}
    public = projections.get("public_web", {})
    native = projections.get("native_desktop_read_only", {})
    if public.get("can_run_source_probe") is not False:
        errors.append("public_web cannot run source probes")
    if public.get("can_review_promote") is not False:
        errors.append("public_web cannot review/promote")
    if native.get("can_mutate") is not False:
        errors.append("native read-only cannot mutate")

    permissions = {item.get("permission_id"): item for item in payloads["control/inventory/search_interaction_permission_matrix.json"].get("permissions", [])}
    if permissions.get("run_source_probe", {}).get("public_web") is not False:
        errors.append("permission matrix must block public source probes")
    if permissions.get("review_promote", {}).get("public_web") is not False:
        errors.append("permission matrix must block public review/promote")

    policy = payloads["control/policies/search_interaction_non_claim_policy.json"]
    for key in ("live_sources_enabled", "extraction_enabled", "model_provider_calls_enabled", "downloads_enabled", "deployment_enabled", "production_readiness_claimed", "public_launch_readiness_claimed", "marketplace_or_app_store_readiness_claimed"):
        if policy.get(key) is not False:
            errors.append(f"non-claim policy {key} must be false")

    result = payloads["control/inventory/search_interaction_result.json"]
    for key in (
        "packet_contracts_added", "search_request_packet_added", "compiled_query_packet_added", "resolution_run_packet_added",
        "result_lane_packet_added", "partial_result_packet_added", "candidate_cluster_packet_added", "action_posture_packet_added",
        "search_control_command_added", "user_feedback_event_added", "search_plan_patch_added", "absence_packet_added",
        "coverage_report_packet_added", "discovery_trail_packet_added", "state_machine_added", "control_command_matrix_added",
        "feedback_event_matrix_added", "query_compilation_matrix_added", "result_lane_contract_matrix_added", "projection_matrix_added",
        "permission_matrix_added", "handoff_matrix_added", "policies_added", "validator_added", "tests_added",
    ):
        require_true(result, key, errors)
    for key in ("runtime_behavior_changed", "html_ui_implemented", "workbench_result_lanes_implemented", "ia_hunt_bridge_implemented", "source_probe_executed", "extraction_executed", "model_provider_used", "deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed", "marketplace_or_app_store_readiness_claimed"):
        require_false(result, key, errors)
    if not str(result.get("recommended_next_task", "")).startswith("WORKBENCH-RESULT-LANES-01"):
        errors.append("recommended next task must be WORKBENCH-RESULT-LANES-01")

    return {
        "schema_version": "search_interaction_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "runtime_behavior_changed": False,
        "html_ui_implemented": False,
        "source_probe_executed": False,
        "model_provider_calls_made": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def load_json(path: Path, schema_version: str, errors: list[str], *, require_schema: bool = True) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON file {path}: {exc}")
        return {}
    if require_schema and payload.get("schema_version") != schema_version:
        errors.append(f"{path} schema_version must be {schema_version}")
    return payload


def require_true(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not True:
        errors.append(f"{key} must be true")


def require_false(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if payload.get(key) is not False:
        errors.append(f"{key} must be false")


if __name__ == "__main__":
    raise SystemExit(main())
