#!/usr/bin/env python3
"""Validate WORKBENCH-RESULT-LANES-01 artifacts and projections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "WORKBENCH-RESULT-LANES-01"

REQUIRED_LANES = {
    "reviewed_local_results",
    "local_candidate_results",
    "source_cache_hits",
    "ia_metadata_candidates",
    "review_queue_items",
    "known_absence",
    "near_misses",
    "blocked_actions",
    "running_workunits",
    "deferred_deepening",
    "future_extraction_work",
}

REQUIRED_VIEW_MODELS = {
    "ResultLaneView",
    "ResultItemView",
    "ReviewedResultItemView",
    "CandidateResultItemView",
    "SourceCacheHitView",
    "IAMetadataCandidateView",
    "ReviewQueueItemView",
    "AbsenceLaneView",
    "NearMissLaneView",
    "BlockedActionLaneView",
    "WorkUnitLaneView",
    "DeferredDeepeningLaneView",
    "FutureExtractionLaneView",
    "ResultLanePageView",
}

REQUIRED_JSON = {
    "control/policies/workbench_result_lane_policy.json": "workbench_result_lane_policy.v0",
    "control/policies/workbench_lane_projection_policy.json": "workbench_lane_projection_policy.v0",
    "control/policies/workbench_lane_non_claim_policy.json": "workbench_lane_non_claim_policy.v0",
    "control/inventory/workbench_result_lanes_input_state.json": "workbench_result_lanes_input_state.v0",
    "control/inventory/workbench_result_lane_schema_matrix.json": "workbench_result_lane_schema_matrix.v0",
    "control/inventory/workbench_result_lane_view_model_matrix.json": "workbench_result_lane_view_model_matrix.v0",
    "control/inventory/workbench_result_lane_projection_matrix.json": "workbench_result_lane_projection_matrix.v0",
    "control/inventory/workbench_result_lane_source_mapping.json": "workbench_result_lane_source_mapping.v0",
    "control/inventory/workbench_result_lane_action_posture_matrix.json": "workbench_result_lane_action_posture_matrix.v0",
    "control/inventory/workbench_result_lane_boundary_report.json": "workbench_result_lane_boundary_report.v0",
    "control/inventory/workbench_result_lanes_validator_matrix.json": "workbench_result_lanes_validator_matrix.v0",
    "control/inventory/workbench_result_lanes_result.json": "workbench_result_lanes_result.v0",
    "control/inventory/workbench_result_lanes_next_task_decision.json": "workbench_result_lanes_next_task_decision.v0",
    "control/audits/workbench-result-lanes-01-v0/workbench_result_lanes_report.json": "workbench_result_lanes_report.v0",
}

REQUIRED_DOCS = [
    "docs/architecture/WORKBENCH_RESULT_LANES.md",
    "docs/architecture/RESULT_LANE_VIEW_MODEL.md",
    "docs/operations/WORKBENCH_RESULT_LANES_RUNBOOK.md",
    "docs/operations/POST_RESULT_LANES_PLAN.md",
    "docs/reference/WORKBENCH_RESULT_LANE_PACKET.md",
]

REQUIRED_EXAMPLES = [
    "examples/workbench/result_lanes/expected_lane_packet.json",
    "examples/workbench/result_lanes/expected_operator_projection.json",
    "examples/workbench/result_lanes/expected_public_projection.json",
    "examples/workbench/result_lanes/expected_boundary_report.json",
]

OPERATOR_ONLY_FIELDS = {
    "operator_notes",
    "source_record_ids",
    "source_cache_entry_ids",
    "evidence_refs",
    "candidate_refs",
    "review_refs",
    "workunit_refs",
    "private_local_path_refs",
    "debug",
}

UNSAFE_FLAGS = {
    "can_download",
    "can_extract",
    "can_execute",
    "can_call_model",
    "can_deploy",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("Workbench result lanes validation", file=stdout)
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
    for rel in REQUIRED_EXAMPLES:
        if not (root / rel).is_file():
            errors.append(f"missing example: {rel}")
    for rel in (
        "runtime/local_service/workbench_result_lanes.py",
        "surfaces/web/workbench/project_result_lanes.py",
        "scripts/eureka_workbench_result_lanes.py",
    ):
        if not (root / rel).is_file():
            errors.append(f"missing implementation file: {rel}")

    lanes = {item.get("lane_kind"): item for item in payloads["control/inventory/workbench_result_lane_schema_matrix.json"].get("lanes", [])}
    if REQUIRED_LANES - set(lanes):
        errors.append(f"lane schema matrix missing lanes: {sorted(REQUIRED_LANES - set(lanes))}")
    for lane_kind, row in lanes.items():
        if not row.get("truth_level"):
            errors.append(f"{lane_kind} missing truth_level")
        if "can_download" not in " ".join(row.get("blocked_actions", [])):
            pass
        for action in ("download", "extract", "call_model_provider"):
            if action not in row.get("blocked_actions", []):
                errors.append(f"{lane_kind} must block {action}")

    view_models = {
        item.get("view_model_id")
        for item in payloads["control/inventory/workbench_result_lane_view_model_matrix.json"].get("view_models", [])
    }
    if REQUIRED_VIEW_MODELS - view_models:
        errors.append(f"view-model matrix missing: {sorted(REQUIRED_VIEW_MODELS - view_models)}")

    projections = payloads["control/inventory/workbench_result_lane_projection_matrix.json"].get("projections", [])
    public_source_probe = [
        row for row in projections if row.get("projection_profile") == "public_web" and row.get("can_run_source_probe") is not False
    ]
    if public_source_probe:
        errors.append("public projection can run source probe")
    native_mutating = [
        row for row in projections if row.get("projection_profile") == "native_desktop_read_only" and row.get("can_mutate_store") is not False
    ]
    if native_mutating:
        errors.append("native read-only projection can mutate store")

    source_mapping = {item.get("lane_kind") for item in payloads["control/inventory/workbench_result_lane_source_mapping.json"].get("mappings", [])}
    if REQUIRED_LANES - source_mapping:
        errors.append(f"source mapping missing lanes: {sorted(REQUIRED_LANES - source_mapping)}")

    for row in payloads["control/inventory/workbench_result_lane_action_posture_matrix.json"].get("postures", []):
        for flag in UNSAFE_FLAGS:
            if row.get(flag) is not False:
                errors.append(f"{row.get('lane_kind')} unsafe flag {flag} must be false")

    policy = payloads["control/policies/workbench_lane_non_claim_policy.json"]
    for key in (
        "source_probe_executed",
        "live_ia_call_performed",
        "source_cache_write_performed",
        "evidence_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "operator_instance_mutated",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "marketplace_or_app_store_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"non-claim policy {key} must be false")

    cli_reports = run_cli_checks(root, errors)
    for profile, page in cli_reports.items():
        if page.get("boundary_report", {}).get("unsafe_actions_blocked") is not True:
            errors.append(f"{profile} did not block unsafe actions")
        for lane in page.get("lanes", []):
            posture = lane.get("action_posture", {})
            for flag in UNSAFE_FLAGS:
                if posture.get(flag) is not False:
                    errors.append(f"{profile}/{lane.get('lane_kind')} {flag} must be false")
        if profile in {"public_web", "native_desktop_read_only"} and contains_operator_field(page):
            errors.append(f"{profile} projection exposes operator-only fields")

    public_page = cli_reports.get("public_web", {})
    if public_page and not public_page.get("boundary_report", {}).get("operator_fields_hidden"):
        errors.append("public projection must hide operator fields")

    result = payloads["control/inventory/workbench_result_lanes_result.json"]
    for key in (
        "lane_policy_added",
        "projection_policy_added",
        "non_claim_policy_added",
        "lane_schema_matrix_added",
        "view_model_matrix_added",
        "projection_matrix_added",
        "source_mapping_added",
        "action_posture_matrix_added",
        "lane_view_builder_added",
        "lane_cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "operator_projection_passed",
        "public_projection_passed",
        "native_read_only_projection_passed",
        "public_projection_hides_operator_fields",
        "unsafe_actions_blocked",
    ):
        require_true(result, key, errors)
    for key in (
        "html_ui_implemented",
        "ia_hunt_bridge_implemented",
        "source_probe_executed",
        "live_ia_call_performed",
        "source_cache_write_performed",
        "evidence_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "operator_instance_mutated",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
        "marketplace_or_app_store_readiness_claimed",
    ):
        require_false(result, key, errors)
    if result.get("runtime_behavior_changed") is not True:
        errors.append("runtime_behavior_changed should be true because view-model builder code was added")
    if not str(result.get("recommended_next_task", "")).startswith("IA-HUNT-BRIDGE-00"):
        errors.append("recommended next task must be IA-HUNT-BRIDGE-00")

    return {
        "schema_version": "workbench_result_lanes_validation.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "operator_projection_passed": "operator_workbench" in cli_reports and not contains_operator_field(cli_reports.get("public_web", {})),
        "public_projection_hides_operator_fields": "public_web" in cli_reports and not contains_operator_field(cli_reports["public_web"]),
        "native_read_only_projection_passed": "native_desktop_read_only" in cli_reports and not contains_operator_field(cli_reports["native_desktop_read_only"]),
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def run_cli_checks(root: Path, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    script = root / "scripts" / "eureka_workbench_result_lanes.py"
    help_result = subprocess.run([sys.executable, str(script), "--help"], cwd=root, capture_output=True, text=True)
    if help_result.returncode != 0:
        errors.append(f"CLI help failed: {help_result.stderr.strip()}")
    reports: dict[str, Mapping[str, Any]] = {}
    for profile in ("operator_workbench", "public_web", "native_desktop_read_only"):
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--query",
                "sampleproject",
                "--projection",
                profile,
                "--from-play-demo",
                "--from-ia-examples",
                "--json",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"CLI {profile} failed: {result.stderr.strip()}")
            continue
        try:
            reports[profile] = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"CLI {profile} emitted malformed JSON: {exc}")
    return reports


def contains_operator_field(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(key in OPERATOR_ONLY_FIELDS or contains_operator_field(inner) for key, inner in value.items())
    if isinstance(value, list):
        return any(contains_operator_field(item) for item in value)
    return False


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON file {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema_version:
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
