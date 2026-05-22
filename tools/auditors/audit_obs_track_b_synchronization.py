"""Audit OBS side-lane artifacts against local Track B state.

This script is intentionally repo-local and read-only by default. It inspects
committed OBS audit artifacts plus Track B contracts/audit reports and emits a
deterministic synchronization matrix. It does not call external tools, network
services, browsers, models, providers, or APIs.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

POLICY_PATH = "control/inventory/observations/obs_track_b_sync_policy.json"
MATRIX_PATH = "control/inventory/observations/obs_track_b_sync_matrix.json"
READINESS_PATH = "control/inventory/observations/obs_track_b_handoff_readiness.json"

OBS_REPORT_PATHS = {
    "OBS-REPLAN-01": "control/audits/obs-replan-01-agent-assisted-observation-workflow-v0/obs_replan_01_report.json",
    "OBS-AGENT-01": "control/audits/obs-agent-01-local-eval-failure-mining-v0/obs_agent_01_report.json",
    "OBS-AGENT-02": "control/audits/obs-agent-02-source-gap-candidate-generation-v0/obs_agent_02_report.json",
    "OBS-AGENT-03": "control/audits/obs-agent-03-observation-candidate-review-queue-v0/obs_agent_03_report.json",
    "OBS-AGENT-04": "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/obs_agent_04_report.json",
    "OBS-AGENT-05": "control/audits/obs-agent-05-candidate-to-workunit-seeds-v0/obs_agent_05_report.json",
}

OBS_INPUT_PATHS = (
    "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json",
    "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json",
    "control/inventory/observations/observation_candidate_review_queue.json",
    "control/inventory/observations/search_need_seed_manifest.json",
    "control/inventory/observations/workunit_seed_manifest.json",
    "control/audits/obs-agent-01-local-eval-failure-mining-v0/local_eval_candidate_manifest.json",
    "control/audits/obs-agent-02-source-gap-candidate-generation-v0/source_gap_candidate_manifest.json",
    "control/audits/obs-agent-03-observation-candidate-review-queue-v0/observation_candidate_review_queue.json",
    "control/audits/obs-agent-04-candidate-to-search-need-seeds-v0/search_need_seed_manifest.json",
    "control/audits/obs-agent-05-candidate-to-workunit-seeds-v0/workunit_seed_manifest.json",
)

TRACK_B_CONTRACT_PATHS = (
    "contracts/node/eureka_node_manifest.v0.json",
    "contracts/node/node_policy.v0.json",
    "contracts/control_schemas/policies/node/node_capability.v0.json",
    "contracts/control_schemas/policies/node/work_unit.v0.json",
    "contracts/control_schemas/policies/node/work_unit_result.v0.json",
    "contracts/control_schemas/policies/node/local_foundry_state.v0.json",
)

TRACK_B_INVENTORY_PATHS = (
    "control/inventory/nodes/eureka_node_manifest_policy.json",
    "control/inventory/nodes/node_policy_registry.json",
    "control/inventory/nodes/node_capability_registry.json",
    "control/inventory/nodes/workunit_policy.json",
    "control/inventory/nodes/workunit_result_policy.json",
    "control/inventory/nodes/node_source_access_policy.json",
)

TRACK_B_DOC_PATHS = (
    "docs/reference/EUREKA_NODE_MANIFEST_CONTRACT.md",
    "docs/reference/NODE_POLICY_CONTRACT.md",
    "docs/reference/NODE_CAPABILITY_CONTRACT.md",
    "docs/reference/WORK_UNIT_CONTRACT.md",
    "docs/reference/WORK_UNIT_RESULT_CONTRACT.md",
    "docs/reference/LOCAL_FOUNDRY_STATE_CONTRACT.md",
)

PRIMARY_INPUT_PATHS = (
    POLICY_PATH,
    READINESS_PATH,
    *OBS_REPORT_PATHS.values(),
    *OBS_INPUT_PATHS,
    *TRACK_B_CONTRACT_PATHS,
    *TRACK_B_INVENTORY_PATHS,
    *TRACK_B_DOC_PATHS,
    "scripts/validate_eureka_node_manifest.py",
    "scripts/validate_eureka_node_policy.py",
    "scripts/validate_eureka_node_capability.py",
    "scripts/validate_local_foundry_state.py",
)

PRODUCT_BOUNDARY = {
    "performed_observations": False,
    "automated_external_search": False,
    "scraped_external_systems": False,
    "crawled_external_systems": False,
    "called_external_apis": False,
    "opened_browsers": False,
    "fabricated_results": False,
    "marked_pending_as_observed": False,
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "mutated_master_index": False,
    "approved_source_access": False,
    "executed_workunits": False,
    "modified_track_b_files": False,
    "created_runtime_search_needs": False,
    "created_runtime_workunits": False,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit OBS and Track B synchronization state.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--list-inputs", action="store_true", help="List deterministic repo-local inputs and exit.")
    parser.add_argument("--check", action="store_true", help="Validate that the synchronization matrix can be built.")
    parser.add_argument("--json-output", help="Explicit path for generated sync matrix JSON.")
    parser.add_argument("--markdown-output", help="Explicit path for generated handoff summary Markdown.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.repo_root).resolve()
    output = stdout or sys.stdout

    if args.list_inputs:
        for path in list_input_paths(root):
            output.write(f"{path}\n")
        return 0

    matrix = build_sync_matrix(root)
    errors = validate_built_matrix(matrix)

    if args.check:
        if errors:
            output.write("audit_obs_track_b_synchronization: fail\n")
            for error in errors:
                output.write(f"- {error}\n")
            return 1
        output.write("audit_obs_track_b_synchronization: pass\n")
        output.write(f"sync_mapping_count: {len(matrix['mappings'])}\n")

    if args.json_output:
        _write_text(root, args.json_output, json.dumps(matrix, indent=2, sort_keys=True) + "\n")

    if args.markdown_output:
        _write_text(root, args.markdown_output, format_markdown_summary(matrix))

    if not args.check and not args.json_output and not args.markdown_output:
        output.write(format_plain_summary(matrix))
    return 0 if not errors else 1


def list_input_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    paths = list(PRIMARY_INPUT_PATHS)
    paths.extend(_track_b_report_paths(repo_root))
    return sorted(path for path in paths if (repo_root / path).exists())


def build_sync_matrix(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    track_b_state = detect_track_b_state(root)
    obs_state = detect_obs_state(root)
    mappings = build_mappings(root)
    ready_items = [mapping["mapping_id"] for mapping in mappings if mapping["current_handoff_state"].startswith("ready_")]
    blocked_items = [
        mapping["mapping_id"]
        for mapping in mappings
        if mapping["current_handoff_state"].startswith("blocked_")
        or mapping["current_handoff_state"] in {"insufficient_local_evidence", "deferred"}
    ]
    human_review_items = [mapping["mapping_id"] for mapping in mappings if mapping["human_review_required"] is True]
    source_policy_items = [mapping["mapping_id"] for mapping in mappings if mapping["source_policy_approval_required"] is True]
    dependency_counts = Counter(mapping["track_b_artifact_family"] for mapping in mappings)

    return {
        "schema_version": "obs_track_b_sync_matrix.v0",
        "matrix_id": "obs_track_b_sync_matrix_v0",
        "label": "OBS to Track B synchronization matrix",
        "description": "Read-only alignment of OBS side-lane draft artifacts with current local Track B contracts and audit reports.",
        "generated_from": list_input_paths(root),
        "observed_track_b_state": track_b_state,
        "observed_obs_state": obs_state,
        "mappings": mappings,
        "ready_items": ready_items,
        "blocked_items": blocked_items,
        "human_review_items": human_review_items,
        "source_policy_items": source_policy_items,
        "track_b_dependency_items": [
            {"track_b_artifact_family": family, "mapping_count": count}
            for family, count in sorted(dependency_counts.items())
        ],
        "next_actions": [
            "Continue OBS and Track B in parallel without mutating Track B files from the OBS lane.",
            "Route OBS candidates, SearchNeed seeds, and WorkUnit seeds into human review before any downstream conversion.",
            "Treat source policy items as decision packets only; do not approve live source access from this sync audit.",
            "Let Track B proceed to TRACK-B-07 before any runtime consumption decision.",
            "Keep AIDE queue/context updates deferred while the local latest task packet is stale relative to the OBS side lane."
        ],
        "truth_boundary": {
            "read_only": True,
            "human_review_required": True,
            "runtime_activation_allowed_now": False,
            "accepted_as_observed_baseline": False,
            "accepted_as_evidence_truth": False,
            "creates_runtime_search_need": False,
            "creates_runtime_workunit": False,
            "executes_workunit": False,
            "source_access_approved": False,
            "master_index_mutation_allowed": False
        },
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "notes": [
            "Synchronization is audit evidence only.",
            "Track B contracts through TRACK-B-06 are present locally, but OBS outputs remain draft inputs.",
            "Runtime consumption, public index effects, source approval, and evidence acceptance remain blocked."
        ]
    }


def detect_track_b_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    reports = _track_b_report_paths(repo_root)
    task_numbers = [_track_b_number(path) for path in reports]
    task_numbers = sorted(number for number in task_numbers if number is not None)
    latest_number = task_numbers[-1] if task_numbers else None
    latest_task = f"TRACK-B-{latest_number:02d}" if latest_number is not None else None
    next_task = f"TRACK-B-{latest_number + 1:02d}" if latest_number is not None else "TRACK-B-01"
    return {
        "track_b_01_seen": 1 in task_numbers,
        "track_b_02_seen": 2 in task_numbers,
        "track_b_03_seen": 3 in task_numbers,
        "track_b_04_seen": 4 in task_numbers,
        "track_b_05_seen": 5 in task_numbers,
        "track_b_06_seen": 6 in task_numbers,
        "track_b_03_or_later_seen": any(number >= 3 for number in task_numbers),
        "latest_track_b_task_seen": latest_task,
        "next_track_b_task_expected": next_task,
        "audit_reports_seen": reports,
        "contracts_present": {
            "node_manifest": (repo_root / "contracts/node/eureka_node_manifest.v0.json").is_file(),
            "node_policy": (repo_root / "contracts/node/node_policy.v0.json").is_file(),
            "node_capability": (repo_root / "contracts/control_schemas/policies/node/node_capability.v0.json").is_file(),
            "workunit_contract": (repo_root / "contracts/control_schemas/policies/node/work_unit.v0.json").is_file(),
            "workunit_result_contract": (repo_root / "contracts/control_schemas/policies/node/work_unit_result.v0.json").is_file(),
            "local_foundry_state_contract": (repo_root / "contracts/control_schemas/policies/node/local_foundry_state.v0.json").is_file()
        },
        "runtime_consumption_enabled": False,
        "notes": [
            "Track B state is inferred from local audit directories and contracts only.",
            "Presence of a Track B contract is not runtime activation."
        ]
    }


def detect_obs_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    reports_seen = sorted(task for task, path in OBS_REPORT_PATHS.items() if (repo_root / path).is_file())
    queue = _load_json(repo_root / "control/inventory/observations/observation_candidate_review_queue.json")
    search_need = _load_json(repo_root / "control/inventory/observations/search_need_seed_manifest.json")
    workunit = _load_json(repo_root / "control/inventory/observations/workunit_seed_manifest.json")
    source_gap = _load_json(repo_root / "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json")
    local_eval = _load_json(repo_root / "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json")
    return {
        "obs_replan_seen": "OBS-REPLAN-01" in reports_seen,
        "obs_agent_01_seen": "OBS-AGENT-01" in reports_seen,
        "obs_agent_02_seen": "OBS-AGENT-02" in reports_seen,
        "obs_agent_03_seen": "OBS-AGENT-03" in reports_seen,
        "obs_agent_04_seen": "OBS-AGENT-04" in reports_seen,
        "obs_agent_05_seen": "OBS-AGENT-05" in reports_seen,
        "latest_obs_task_seen": "OBS-AGENT-05" if "OBS-AGENT-05" in reports_seen else (reports_seen[-1] if reports_seen else None),
        "audit_reports_seen": [OBS_REPORT_PATHS[task] for task in reports_seen],
        "local_eval_candidate_count": _int_value(local_eval.get("candidate_count")),
        "source_gap_candidate_count": _int_value(source_gap.get("source_gap_candidate_count")),
        "review_queue_entry_count": len(_sequence_items(queue.get("queue_entries"))),
        "search_need_seed_count": _int_value(search_need.get("seed_count")),
        "workunit_seed_count": _int_value(workunit.get("seed_count")),
        "runtime_consumption_enabled": False,
        "notes": [
            "OBS outputs are draft or queued records only.",
            "Human review remains required before downstream use."
        ]
    }


def build_mappings(repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    base = [
        _mapping_record(
            "obs_candidates_to_human_review",
            "observation_candidate",
            "control/inventory/observations/obs_agent_candidate_batch_0_local_eval_manifest.json",
            "review_queue_future",
            "control/inventory/observations/observation_candidate_review_queue.json",
            "ready_for_human_review",
            "ready_for_human_review",
            "Human review should triage local eval and candidate records before any downstream use.",
            True,
            False,
            ["OBS candidates are review items, not observed baselines or evidence truth."]
        ),
        _mapping_record(
            "source_gaps_to_source_policy_decisions",
            "source_gap_candidate",
            "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json",
            "node_policy",
            "control/inventory/nodes/node_source_access_policy.json",
            "blocked_until_source_policy_approval",
            "source_policy_review_required",
            "Prepare human source policy decision items; do not approve source access from OBS sync.",
            True,
            True,
            ["Source leads remain blocked until reviewed source policy decisions exist."]
        ),
        _mapping_record(
            "review_queue_to_track_b_candidate_store",
            "observation_review_queue",
            "control/inventory/observations/observation_candidate_review_queue.json",
            "candidate_store_future",
            "control/inventory/observations/observation_candidate_review_queue.json",
            "ready_for_human_review",
            "ready_for_human_review",
            "Use the OBS queue as a human review packet only until Track B defines a candidate store.",
            True,
            False,
            ["The OBS queue records recommended actions but no approval decisions."]
        ),
        _mapping_record(
            "search_need_seeds_to_track_b_future",
            "search_need_seed",
            "control/inventory/observations/search_need_seed_manifest.json",
            "candidate_store_future",
            "contracts/query/search_need_seed.v0.json",
            "ready_for_track_b_after_contracts",
            "ready_for_track_b_after_contracts",
            "Keep SearchNeed seeds as drafts until Track B defines acceptance and runtime semantics.",
            True,
            False,
            ["SearchNeed seeds are not runtime SearchNeeds."]
        ),
        _mapping_record(
            "workunit_seeds_to_workunit_contract",
            "workunit_seed",
            "control/inventory/observations/workunit_seed_manifest.json",
            "workunit_contract_future",
            "contracts/control_schemas/policies/node/work_unit.v0.json",
            "ready_for_track_b_after_contracts",
            "track_b_dependency_present_read_only",
            "Track B WorkUnit contract is present; OBS WorkUnit seeds still require review and future runtime acceptance.",
            True,
            False,
            ["Contract presence is not WorkUnit execution permission."]
        ),
        _mapping_record(
            "workunit_seeds_to_workunit_result_contract",
            "workunit_seed",
            "control/inventory/observations/workunit_seed_manifest.json",
            "workunit_result_contract_future",
            "contracts/control_schemas/policies/node/work_unit_result.v0.json",
            "ready_for_track_b_after_contracts",
            "track_b_dependency_present_read_only",
            "Track B WorkUnit result contract is present; OBS seeds still cannot create results.",
            True,
            False,
            ["WorkUnit result contracts do not create accepted evidence."]
        ),
        _mapping_record(
            "workunit_seeds_to_local_foundry_state",
            "workunit_seed",
            "control/inventory/observations/workunit_seed_manifest.json",
            "local_foundry_state_future",
            "contracts/control_schemas/policies/node/local_foundry_state.v0.json",
            "ready_for_track_b_after_contracts",
            "track_b_dependency_present_read_only",
            "Local foundry state contract can later host private draft state, but this audit writes no runtime state.",
            True,
            False,
            ["Local foundry state remains contract-only for this handoff."]
        ),
        _mapping_record(
            "manual_pending_slots_to_future_observed_records",
            "manual_observation_pending_slot",
            "control/inventory/observations/manual_observation_batch_0_slot_manifest.json",
            "evidence_ledger_future",
            "docs/reference/EVIDENCE_LEDGER_CONTRACT.md",
            "blocked_until_manual_observation",
            "manual_observation_required",
            "Manual pending slots must stay pending until an approved human observation is performed.",
            True,
            False,
            ["No pending slot is marked observed by this audit."]
        ),
        _mapping_record(
            "policy_blocked_items_to_node_policy",
            "source_gap_candidate",
            "control/inventory/observations/obs_agent_source_gap_candidate_manifest.json",
            "node_policy",
            "contracts/node/node_policy.v0.json",
            "blocked_by_policy",
            "blocked_by_policy",
            "Keep broad web, forum, and live-source ideas blocked until explicit source policy review.",
            True,
            True,
            ["Policy-blocked items are not source approvals."]
        ),
    ]
    return sorted(base, key=lambda item: item["mapping_id"])


def validate_built_matrix(matrix: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if matrix.get("schema_version") != "obs_track_b_sync_matrix.v0":
        errors.append("schema_version must be obs_track_b_sync_matrix.v0")
    mappings = [_mapping(item) for item in _sequence_items(matrix.get("mappings"))]
    if not mappings:
        errors.append("mappings must be non-empty")
    for mapping in mappings:
        mapping_id = str(mapping.get("mapping_id", "<missing>"))
        if mapping.get("runtime_activation_allowed_now") is not False:
            errors.append(f"{mapping_id}: runtime_activation_allowed_now must be false")
        if mapping.get("accepted_as_evidence_truth") is not False:
            errors.append(f"{mapping_id}: accepted_as_evidence_truth must be false")
        if mapping.get("master_index_mutation_allowed") is not False:
            errors.append(f"{mapping_id}: master_index_mutation_allowed must be false")
    for field, value in _mapping(matrix.get("product_boundary")).items():
        if value is not False:
            errors.append(f"product_boundary.{field} must be false")
    return sorted(set(errors))


def format_plain_summary(matrix: Mapping[str, Any]) -> str:
    lines = [
        "audit_obs_track_b_synchronization:",
        f"- sync_mapping_count: {len(_sequence_items(matrix.get('mappings')))}",
        f"- ready_item_count: {len(_sequence_items(matrix.get('ready_items')))}",
        f"- blocked_item_count: {len(_sequence_items(matrix.get('blocked_items')))}",
        f"- latest_track_b_task_seen: {_mapping(matrix.get('observed_track_b_state')).get('latest_track_b_task_seen')}",
    ]
    return "\n".join(lines) + "\n"


def format_markdown_summary(matrix: Mapping[str, Any]) -> str:
    mappings = [_mapping(mapping) for mapping in _sequence_items(matrix.get("mappings"))]
    track_b_state = _mapping(matrix.get("observed_track_b_state"))
    obs_state = _mapping(matrix.get("observed_obs_state"))
    lines = [
        "# OBS to Track B Handoff Summary",
        "",
        "This summary is generated from repo-local OBS and Track B artifacts. It is audit evidence only and does not activate runtime behavior.",
        "",
        "## Latest State",
        "",
        f"- Latest OBS state observed: `{obs_state.get('latest_obs_task_seen')}`.",
        f"- Latest Track B state observed: `{track_b_state.get('latest_track_b_task_seen')}`.",
        f"- Next Track B task expected: `{track_b_state.get('next_track_b_task_expected')}`.",
        "",
        "## Handoff Matrix",
        "",
        "| Mapping | OBS artifact | Track B dependency | Handoff state | Readiness |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mapping in mappings:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                mapping.get("mapping_id"),
                mapping.get("obs_artifact_family"),
                mapping.get("track_b_artifact_family"),
                mapping.get("current_handoff_state"),
                mapping.get("readiness_state"),
            )
        )
    lines.extend(
        [
            "",
            "## Ready For Human Review",
            "",
            *_mapping_lines(mappings, lambda item: item.get("current_handoff_state") == "ready_for_human_review"),
            "",
            "## Blocked By Track B Or Policy",
            "",
            *_mapping_lines(mappings, lambda item: str(item.get("current_handoff_state", "")).startswith("blocked_")),
            "",
            "## Source Policy Items",
            "",
            *_mapping_lines(mappings, lambda item: item.get("source_policy_approval_required") is True),
            "",
            "## Not Yet Consumable",
            "",
            "- Runtime SearchNeeds are not created by this audit.",
            "- Runtime WorkUnits are not created or executed by this audit.",
            "- Source access remains unapproved.",
            "- Public index effects remain disallowed.",
            "",
        ]
    )
    return "\n".join(lines)


def _mapping_record(
    mapping_id: str,
    obs_family: str,
    obs_ref: str,
    track_b_family: str,
    track_b_ref: str,
    handoff_state: str,
    readiness_state: str,
    next_action: str,
    human_review: bool,
    source_policy: bool,
    notes: Sequence[str],
) -> dict[str, Any]:
    return {
        "mapping_id": mapping_id,
        "obs_artifact_family": obs_family,
        "obs_artifact_ref": obs_ref,
        "track_b_artifact_family": track_b_family,
        "track_b_dependency_ref": track_b_ref,
        "current_handoff_state": handoff_state,
        "readiness_state": readiness_state,
        "required_next_action": next_action,
        "human_review_required": human_review,
        "source_policy_approval_required": source_policy,
        "runtime_activation_allowed_now": False,
        "accepted_as_observed_baseline": False,
        "accepted_as_evidence_truth": False,
        "creates_runtime_search_need": False,
        "creates_runtime_workunit": False,
        "executes_workunit": False,
        "master_index_mutation_allowed": False,
        "notes": list(notes),
    }


def _track_b_report_paths(repo_root: Path) -> list[str]:
    audit_root = repo_root / "control/audits"
    if not audit_root.is_dir():
        return []
    paths = []
    for directory in sorted(audit_root.glob("track-b-*")):
        number = _track_b_number(directory.name)
        if number is None:
            continue
        report = directory / f"track_b_{number:02d}_report.json"
        if report.is_file():
            paths.append(report.relative_to(repo_root).as_posix())
    return sorted(paths)


def _track_b_number(value: str) -> int | None:
    match = re.search(r"track[-_]b[-_](\d+)", value.lower())
    return int(match.group(1)) if match else None


def _mapping_lines(mappings: Sequence[Mapping[str, Any]], predicate: Any) -> list[str]:
    lines = [
        f"- `{mapping.get('mapping_id')}`: `{mapping.get('required_next_action')}`"
        for mapping in mappings
        if predicate(mapping)
    ]
    return lines or ["- None."]


def _write_text(repo_root: Path, output_arg: str, text: str) -> None:
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _int_value(value: Any) -> int:
    return value if isinstance(value, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
