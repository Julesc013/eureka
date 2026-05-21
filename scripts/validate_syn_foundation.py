#!/usr/bin/env python3
"""Validate SYN-00 Synthetic Query Foundry foundation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "SYN-00"

REQUIRED_JSON: dict[str, str] = {
    "contracts/query/synthetic_query_case.v0.json": "synthetic_query_case.v0",
    "contracts/query/synthetic_query_set.v0.json": "synthetic_query_set.v0",
    "control/policies/syn_foundation_policy.json": "syn_foundation_policy.v0",
    "control/inventory/syn_foundation_input_state.json": "syn_foundation_input_state.v0",
    "control/inventory/syn_query_taxonomy.json": "syn_query_taxonomy.v0",
    "control/inventory/syn_eval_contract_matrix.json": "syn_eval_contract_matrix.v0",
    "control/inventory/syn_query_set_matrix.json": "syn_query_set_matrix.v0",
    "control/inventory/syn_seed_bridge_matrix.json": "syn_seed_bridge_matrix.v0",
    "examples/syn_foundation/query_sets/demo_query_set_v0.json": "synthetic_query_set.v0",
    "examples/syn_foundation/query_sets/hard_query_set_v0.json": "synthetic_query_set.v0",
    "examples/syn_foundation/query_sets/adversarial_query_set_v0.json": "synthetic_query_set.v0",
    "examples/syn_foundation/synthetic_to_search_need_seeds_v0.json": "syn_search_need_seed_bridge.v0",
    "examples/syn_foundation/synthetic_to_workunit_seeds_v0.json": "syn_workunit_seed_bridge.v0",
    "examples/syn_foundation/sample_foundry_plan.json": "syn_foundry_plan.v0",
}

OPTIONAL_RESULT_JSON: dict[str, str] = {
    "control/inventory/syn_validation_matrix.json": "syn_validation_matrix.v0",
    "control/inventory/syn_foundation_result.json": "syn_foundation_result.v0",
    "control/inventory/syn_next_task_decision.json": "syn_next_task_decision.v0",
    "control/audits/syn-foundation-01-v0/syn_foundation_report.json": "syn_foundation_report.v0",
}

REQUIRED_DOCS = (
    "docs/architecture/SYNTHETIC_QUERY_FOUNDRY.md",
    "docs/operations/SYN_FOUNDATION_RUNBOOK.md",
    "docs/operations/POST_SYN_FOUNDATION_PLAN.md",
)

REQUIRED_SPLITS = {"demo", "hard", "adversarial"}
REQUIRED_STACK = {
    "LOCAL",
    "HUNT",
    "PLAY",
    "IA_METADATA_PILOT",
    "WORKBENCH_RESULT_LANES",
    "IA_HUNT_BRIDGE",
}
REQUIRED_LANES = {
    "reviewed_local_results",
    "ia_metadata_candidates",
    "source_cache_hits",
    "review_queue_items",
    "known_absence",
    "blocked_actions",
    "running_workunits",
    "deferred_deepening",
    "future_extraction_work",
}
FALSE_BOUNDARY_FLAGS = (
    "runtime_query_logged",
    "runtime_search_need_created",
    "runtime_workunit_created",
    "source_probe_executed",
    "live_ia_call_performed",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "master_index_mutated",
    "operator_instance_mutated",
    "public_search_behavior_changed",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)
FORBIDDEN_TEXT = (
    "production-ready",
    "public launch ready",
    "live ia call completed",
    "source probe completed",
    "download completed",
    "extraction completed",
    "model call completed",
    "accepted evidence truth",
    "master index updated",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_syn_foundation(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("SYN foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_syn_foundation(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for rel_path, schema_version in {**REQUIRED_JSON, **OPTIONAL_RESULT_JSON}.items():
        path = root / rel_path
        if rel_path in OPTIONAL_RESULT_JSON and not path.exists():
            continue
        payload = _load_json(path, errors)
        if isinstance(payload, Mapping):
            payloads[rel_path] = payload
            if payload.get("schema_version") != schema_version:
                errors.append(f"{rel_path}: schema_version must be {schema_version}.")

    for rel_path in REQUIRED_DOCS:
        path = root / rel_path
        if not path.is_file():
            errors.append(f"{rel_path}: required doc is missing.")

    _validate_policy(payloads.get("control/policies/syn_foundation_policy.json", {}), errors)
    query_cases = _validate_query_sets(payloads, errors)
    _validate_seed_bridge(
        query_cases,
        payloads.get("examples/syn_foundation/synthetic_to_search_need_seeds_v0.json", {}),
        payloads.get("examples/syn_foundation/synthetic_to_workunit_seeds_v0.json", {}),
        errors,
    )
    _validate_text_claims(root, errors)

    return {
        "schema_version": "syn_foundation_validation_report.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "required_json_count": len(REQUIRED_JSON),
        "optional_result_json_present": sorted(path for path in OPTIONAL_RESULT_JSON if (root / path).exists()),
        "query_case_count": len(query_cases),
        "split_labels": sorted({str(case.get("difficulty_band")) for case in query_cases}),
        "stack_targets": sorted({target for case in query_cases for target in _string_list(case.get("stack_targets"))}),
        "errors": errors,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_false = (
        "synthetic_generation_runtime_enabled",
        "runtime_search_need_creation_allowed",
        "runtime_workunit_creation_allowed",
        "accepted_evidence_creation_allowed",
        "source_probe_enabled",
        "live_ia_call_enabled",
        "download_enabled",
        "upload_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "operator_instance_mutation_allowed",
        "master_index_mutation_allowed",
        "public_search_behavior_change_allowed",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for flag in required_false:
        if policy.get(flag) is not False:
            errors.append(f"control/policies/syn_foundation_policy.json: {flag} must be false.")
    for flag in ("fixture_query_sets_allowed", "search_need_seed_drafts_allowed", "workunit_seed_drafts_allowed"):
        if policy.get(flag) is not True:
            errors.append(f"control/policies/syn_foundation_policy.json: {flag} must be true.")


def _validate_query_sets(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> list[Mapping[str, Any]]:
    query_set_paths = [
        "examples/syn_foundation/query_sets/demo_query_set_v0.json",
        "examples/syn_foundation/query_sets/hard_query_set_v0.json",
        "examples/syn_foundation/query_sets/adversarial_query_set_v0.json",
    ]
    cases: list[Mapping[str, Any]] = []
    splits: set[str] = set()
    stack_targets: set[str] = set()
    lane_kinds: set[str] = set()

    for rel_path in query_set_paths:
        payload = payloads.get(rel_path, {})
        split = str(payload.get("split_label", ""))
        splits.add(split)
        if payload.get("query_set_status") != "example_only":
            errors.append(f"{rel_path}: query_set_status must be example_only.")
        if not _string_list(payload.get("query_cases")):
            errors.append(f"{rel_path}: query_cases must not be empty.")
        _validate_false_map(rel_path, _mapping(payload.get("runtime_capability_boundary")), FALSE_BOUNDARY_FLAGS, errors)
        no_claims = _mapping(payload.get("no_claims"))
        for flag in ("production_search_quality", "user_demand_observed", "result_truth_created"):
            if no_claims.get(flag) is not False:
                errors.append(f"{rel_path}: no_claims.{flag} must be false.")
        for case in _list(payload.get("query_cases")):
            if not isinstance(case, Mapping):
                errors.append(f"{rel_path}: query_cases entries must be objects.")
                continue
            cases.append(case)
            stack_targets.update(_string_list(case.get("stack_targets")))
            lane_kinds.update(_string_list(case.get("expected_lanes")))
            if case.get("schema_version") != "synthetic_query_case.v0":
                errors.append(f"{rel_path}: {case.get('query_case_id')} schema_version must be synthetic_query_case.v0.")
            if case.get("difficulty_band") != split:
                errors.append(f"{rel_path}: {case.get('query_case_id')} difficulty_band must match split_label.")
            if case.get("review_required") is not True:
                errors.append(f"{rel_path}: {case.get('query_case_id')} review_required must be true.")
            if not _string_list(case.get("expected_search_need_seed_refs")):
                errors.append(f"{rel_path}: {case.get('query_case_id')} must list expected_search_need_seed_refs.")
            if not _string_list(case.get("expected_workunit_seed_refs")):
                errors.append(f"{rel_path}: {case.get('query_case_id')} must list expected_workunit_seed_refs.")

    if splits != REQUIRED_SPLITS:
        errors.append(f"SYN query sets must include splits {sorted(REQUIRED_SPLITS)}.")
    missing_stack = REQUIRED_STACK - stack_targets
    if missing_stack:
        errors.append(f"SYN query cases are missing stack targets: {sorted(missing_stack)}.")
    missing_lanes = REQUIRED_LANES - lane_kinds
    if missing_lanes:
        errors.append(f"SYN query cases are missing expected lanes: {sorted(missing_lanes)}.")
    if len(cases) < 9:
        errors.append("SYN query cases must include at least nine pressure cases.")
    return cases


def _validate_seed_bridge(
    query_cases: list[Mapping[str, Any]],
    search_need_bridge: Mapping[str, Any],
    workunit_bridge: Mapping[str, Any],
    errors: list[str],
) -> None:
    case_ids = {str(case.get("query_case_id")) for case in query_cases}
    need_map = {str(item.get("query_case_id")): item for item in _list(search_need_bridge.get("mappings")) if isinstance(item, Mapping)}
    workunit_map = {str(item.get("query_case_id")): item for item in _list(workunit_bridge.get("mappings")) if isinstance(item, Mapping)}
    if set(need_map) != case_ids:
        errors.append("SearchNeed seed bridge must map every synthetic query case exactly once.")
    if set(workunit_map) != case_ids:
        errors.append("WorkUnit seed bridge must map every synthetic query case exactly once.")
    _validate_false_map(
        "examples/syn_foundation/synthetic_to_search_need_seeds_v0.json",
        _mapping(search_need_bridge.get("runtime_capability_boundary")),
        (
            "runtime_search_need_created",
            "accepted_runtime_search_need",
            "source_probe_executed",
            "live_ia_call_performed",
            "extraction_executed",
            "model_provider_used",
            "master_index_mutated",
        ),
        errors,
    )
    _validate_false_map(
        "examples/syn_foundation/synthetic_to_workunit_seeds_v0.json",
        _mapping(workunit_bridge.get("runtime_capability_boundary")),
        (
            "runtime_workunit_created",
            "accepted_runtime_workunit",
            "workunit_executed",
            "source_probe_executed",
            "live_ia_call_performed",
            "download_performed",
            "upload_performed",
            "extraction_executed",
            "model_provider_used",
            "master_index_mutated",
        ),
        errors,
    )


def _validate_text_claims(root: Path, errors: list[str]) -> None:
    paths = [
        root / "docs" / "architecture" / "SYNTHETIC_QUERY_FOUNDRY.md",
        root / "docs" / "operations" / "SYN_FOUNDATION_RUNBOOK.md",
        root / "docs" / "operations" / "POST_SYN_FOUNDATION_PLAN.md",
    ]
    paths.extend((root / "examples" / "syn_foundation").rglob("*.json"))
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_TEXT:
            if marker in text:
                errors.append(f"{_rel(path, root)}: forbidden claim marker {marker!r}.")


def _validate_false_map(rel_path: str, payload: Mapping[str, Any], flags: Sequence[str], errors: list[str]) -> None:
    for flag in flags:
        if payload.get(flag) is not False:
            errors.append(f"{rel_path}: runtime_capability_boundary.{flag} must be false.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_rel(path, REPO_ROOT)}: required JSON file is missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, REPO_ROOT)}: invalid JSON: {exc}")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in _list(value)]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
