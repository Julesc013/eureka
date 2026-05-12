"""Validate OBS and Track B synchronization audit artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

POLICY_PATH = "control/inventory/observations/obs_track_b_sync_policy.json"
MATRIX_PATH = "control/inventory/observations/obs_track_b_sync_matrix.json"
READINESS_PATH = "control/inventory/observations/obs_track_b_handoff_readiness.json"
AUDIT_REPORT_PATH = "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_agent_06_report.json"
AUDIT_MATRIX_PATH = "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_track_b_sync_matrix.json"
AUDIT_SUMMARY_PATH = "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_track_b_handoff_summary.md"
GAP_REGISTER_PATH = "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_track_b_gap_register.md"
NEXT_ACTIONS_PATH = "control/audits/obs-agent-06-obs-track-b-synchronization-v0/obs_track_b_next_actions.md"

REQUIRED_DOCS = (
    "docs/operations/OBS_TRACK_B_SYNCHRONIZATION.md",
    "docs/operations/OBS_TO_TRACK_B_HANDOFF_GUIDE.md",
    "docs/operations/OBS_PARALLEL_DEVELOPMENT_POLICY.md",
    "docs/operations/OBSERVATION_CANDIDATE_REVIEW_QUEUE.md",
    "docs/operations/OBS_CANDIDATE_TO_SEARCH_NEED_SEEDS.md",
    "docs/operations/OBS_CANDIDATE_TO_WORKUNIT_SEEDS.md",
)

PENDING_BATCH_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST_PATH = "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
OBSERVATION_DIRS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    "evals/search_usefulness/external_baselines/observations",
)

OBS_FAMILIES = {
    "observation_candidate",
    "observation_review_queue",
    "source_gap_candidate",
    "search_need_seed",
    "workunit_seed",
    "manual_observation_pending_slot",
    "manual_observation_observed_record_future",
}
TRACK_B_FAMILIES = {
    "node_manifest",
    "node_policy",
    "node_capability_future",
    "workunit_contract_future",
    "workunit_result_contract_future",
    "local_foundry_state_future",
    "node_policy_evaluator_future",
    "workunit_dry_run_runner_future",
    "candidate_store_future",
    "source_cache_future",
    "evidence_ledger_future",
    "review_queue_future",
}
HANDOFF_STATES = {
    "ready_for_human_review",
    "ready_for_track_b_after_contracts",
    "blocked_until_node_capability",
    "blocked_until_workunit_contract",
    "blocked_until_workunit_result_contract",
    "blocked_until_local_foundry_state",
    "blocked_until_review_queue",
    "blocked_until_source_policy_approval",
    "blocked_until_manual_observation",
    "blocked_by_policy",
    "insufficient_local_evidence",
    "duplicate_or_superseded",
    "deferred",
}
READINESS_STATES = {
    "ready_for_parallel_continuation",
    "ready_for_human_review",
    "ready_for_track_b_after_contracts",
    "track_b_dependency_present_read_only",
    "track_b_dependency_missing_future",
    "source_policy_review_required",
    "manual_observation_required",
    "blocked_by_policy",
    "not_ready_for_runtime_consumption",
    "insufficient_local_evidence",
    "deferred",
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
    "approved_source_access",
    "executed_workunits",
    "modified_track_b_files",
    "created_runtime_search_needs",
    "created_runtime_workunits",
}

TRACK_B_PREFIXES = (
    "contracts/node/",
    "control/inventory/nodes/",
    "control/audits/track-b-",
    "docs/reference/EUREKA_NODE",
    "docs/reference/NODE_",
    "docs/reference/WORK_UNIT",
    "docs/reference/LOCAL_FOUNDRY",
    "runtime/",
)

HISTORICAL_PATH_ALIASES = {
    "contracts/node/local_foundry_state.v0.json": "control/schemas/policies/node/local_foundry_state.v0.json",
    "contracts/node/node_capability.v0.json": "control/schemas/policies/node/node_capability.v0.json",
}

FORBIDDEN_MATRIX_MARKERS = (
    "live source observed",
    "external observation performed",
    "accepted evidence truth",
    "mark_observation_observed",
    "mark_candidate_accepted",
    "mark_evidence_accepted",
    "create_runtime_search_need",
    "create_runtime_workunit",
    "execute_workunit",
    "executed workunit",
    "source access approved",
    "source approval granted",
    "approved live source access",
    "live probe completed",
    "api call completed",
    "browser opened",
    "scraped google result",
    "google " + "scrape",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OBS/Track B synchronization artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--matrix-file", default=MATRIX_PATH, help="Sync matrix path relative to repo root.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_obs_track_b_synchronization(Path(args.repo_root), args.matrix_file)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_obs_track_b_synchronization(
    repo_root: Path = REPO_ROOT,
    matrix_file: str = MATRIX_PATH,
) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    policy = _load_json(root / POLICY_PATH, errors)
    matrix = _load_json(root / matrix_file, errors)
    readiness = _load_json(root / READINESS_PATH, errors)
    audit_matrix = _load_json(root / AUDIT_MATRIX_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_policy_payload(policy, POLICY_PATH))
    errors.extend(validate_matrix_payload(matrix, matrix_file, root))
    errors.extend(validate_readiness_payload(readiness, READINESS_PATH))
    errors.extend(validate_matrix_payload(audit_matrix, AUDIT_MATRIX_PATH, root))
    errors.extend(validate_audit_report_payload(audit_report, AUDIT_REPORT_PATH))
    errors.extend(_validate_required_docs(root))
    errors.extend(_validate_pending_slots(root))
    errors.extend(_validate_no_observed_files(root))

    return {
        "schema_version": "obs_track_b_sync_validation.v0",
        "status": "valid" if not errors else "invalid",
        "policy_file": POLICY_PATH,
        "matrix_file": matrix_file,
        "readiness_file": READINESS_PATH,
        "audit_matrix_file": AUDIT_MATRIX_PATH,
        "audit_report_file": AUDIT_REPORT_PATH,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_policy_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_track_b_sync_policy.v0":
        errors.append(f"{source}: schema_version must be obs_track_b_sync_policy.v0")
    errors.extend(_missing_items(_string_items(data.get("obs_artifact_families")), OBS_FAMILIES, f"{source}: obs_artifact_families"))
    errors.extend(_missing_items(_string_items(data.get("track_b_artifact_families")), TRACK_B_FAMILIES, f"{source}: track_b_artifact_families"))
    errors.extend(_missing_items(_string_items(data.get("handoff_states")), HANDOFF_STATES, f"{source}: handoff_states"))
    errors.extend(_missing_items(_string_items(data.get("readiness_states")), READINESS_STATES, f"{source}: readiness_states"))
    for action in (
        "mutate_track_b_files",
        "execute_workunits",
        "approve_source_access",
        "mark_observation_observed",
        "mark_candidate_accepted",
        "mark_evidence_accepted",
        "create_runtime_search_need",
        "create_runtime_workunit",
        "mutate_master_index",
        "call_external_api",
        "scrape_external_source",
        "enable_live_probe",
    ):
        if action not in _string_items(data.get("forbidden_sync_actions")):
            errors.append(f"{source}: forbidden_sync_actions missing {action}")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("read_only") is not True or truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary must be read-only and human-review-required")
    for field in ("runtime_activation_allowed_now", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit", "source_access_approved", "master_index_mutation_allowed"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_matrix_payload(payload: Any, source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_track_b_sync_matrix.v0":
        errors.append(f"{source}: schema_version must be obs_track_b_sync_matrix.v0")
    mappings = [_mapping(item) for item in _sequence_items(data.get("mappings"))]
    if not mappings:
        errors.append(f"{source}: mappings must be non-empty")
    if data.get("ready_items") != [mapping["mapping_id"] for mapping in mappings if str(mapping.get("current_handoff_state", "")).startswith("ready_")]:
        errors.append(f"{source}: ready_items must match mappings")
    expected_blocked = [
        mapping["mapping_id"]
        for mapping in mappings
        if str(mapping.get("current_handoff_state", "")).startswith("blocked_")
        or mapping.get("current_handoff_state") in {"insufficient_local_evidence", "deferred"}
    ]
    if data.get("blocked_items") != expected_blocked:
        errors.append(f"{source}: blocked_items must match mappings")
    if data.get("human_review_items") != [mapping["mapping_id"] for mapping in mappings if mapping.get("human_review_required") is True]:
        errors.append(f"{source}: human_review_items must match mappings")
    if data.get("source_policy_items") != [mapping["mapping_id"] for mapping in mappings if mapping.get("source_policy_approval_required") is True]:
        errors.append(f"{source}: source_policy_items must match mappings")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("read_only") is not True or truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary must be read-only and human-review-required")
    for field in ("runtime_activation_allowed_now", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit", "source_access_approved", "master_index_mutation_allowed"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    for mapping in mappings:
        errors.extend(validate_mapping_payload(mapping, source, repo_root))
    errors.extend(_forbidden_text_errors(data, source))
    return errors


def validate_mapping_payload(mapping: Mapping[str, Any], source: str, repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    mapping_id = str(mapping.get("mapping_id", "<missing>"))
    for field in (
        "mapping_id",
        "obs_artifact_family",
        "obs_artifact_ref",
        "track_b_artifact_family",
        "track_b_dependency_ref",
        "current_handoff_state",
        "readiness_state",
        "required_next_action",
        "human_review_required",
        "source_policy_approval_required",
        "runtime_activation_allowed_now",
        "accepted_as_observed_baseline",
        "accepted_as_evidence_truth",
        "creates_runtime_search_need",
        "creates_runtime_workunit",
        "executes_workunit",
        "master_index_mutation_allowed",
        "notes",
    ):
        if field not in mapping:
            errors.append(f"{source}: {mapping_id}: missing {field}")
    if mapping.get("obs_artifact_family") not in OBS_FAMILIES:
        errors.append(f"{source}: {mapping_id}: invalid obs_artifact_family {mapping.get('obs_artifact_family')!r}")
    if mapping.get("track_b_artifact_family") not in TRACK_B_FAMILIES:
        errors.append(f"{source}: {mapping_id}: invalid track_b_artifact_family {mapping.get('track_b_artifact_family')!r}")
    if mapping.get("current_handoff_state") not in HANDOFF_STATES:
        errors.append(f"{source}: {mapping_id}: invalid current_handoff_state {mapping.get('current_handoff_state')!r}")
    if mapping.get("readiness_state") not in READINESS_STATES:
        errors.append(f"{source}: {mapping_id}: invalid readiness_state {mapping.get('readiness_state')!r}")
    if mapping.get("human_review_required") is not True:
        errors.append(f"{source}: {mapping_id}: human_review_required must be true")
    for field in ("runtime_activation_allowed_now", "accepted_as_observed_baseline", "accepted_as_evidence_truth", "creates_runtime_search_need", "creates_runtime_workunit", "executes_workunit", "master_index_mutation_allowed"):
        if mapping.get(field) is not False:
            errors.append(f"{source}: {mapping_id}: {field} must be false")
    if mapping.get("source_access_approved") is True:
        errors.append(f"{source}: {mapping_id}: source_access_approved must not be true")
    obs_ref = mapping.get("obs_artifact_ref")
    if isinstance(obs_ref, str) and not (repo_root / obs_ref).exists():
        errors.append(f"{source}: {mapping_id}: obs_artifact_ref missing {obs_ref}")
    dependency_ref = mapping.get("track_b_dependency_ref")
    if isinstance(dependency_ref, str) and not dependency_ref.endswith("_future") and not (repo_root / dependency_ref).exists():
        alias = HISTORICAL_PATH_ALIASES.get(dependency_ref)
        historical_source = source.replace("\\", "/").startswith("control/audits/")
        if not (historical_source and alias and (repo_root / alias).exists()):
            errors.append(f"{source}: {mapping_id}: track_b_dependency_ref missing {dependency_ref}")
    errors.extend(_forbidden_text_errors(mapping, f"{source}: {mapping_id}"))
    return errors


def validate_readiness_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_track_b_handoff_readiness.v0":
        errors.append(f"{source}: schema_version must be obs_track_b_handoff_readiness.v0")
    if data.get("ready_for_parallel_continuation") is not True:
        errors.append(f"{source}: ready_for_parallel_continuation must be true")
    for field in ("ready_for_runtime_consumption", "ready_for_workunit_runtime", "ready_for_public_index_effect"):
        if data.get(field) is not False:
            errors.append(f"{source}: {field} must be false")
    if data.get("ready_for_source_policy_decision") not in {"partial_review_required", "review_required", "maybe", False}:
        errors.append(f"{source}: ready_for_source_policy_decision must be review-gated")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    return errors


def validate_audit_report_payload(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "obs_agent_06_report.v0":
        errors.append(f"{source}: schema_version must be obs_agent_06_report.v0")
    if data.get("track") != "Observation":
        errors.append(f"{source}: track must be Observation")
    if data.get("task") != "OBS-AGENT-06":
        errors.append(f"{source}: task must be OBS-AGENT-06")
    truth = _mapping(data.get("truth_boundary"))
    if truth.get("human_review_required") is not True:
        errors.append(f"{source}: truth_boundary.human_review_required must be true")
    for field in ("sync_outputs_are_observed_baselines", "sync_outputs_are_evidence_truth", "sync_outputs_create_runtime_search_needs", "sync_outputs_create_runtime_workunits", "sync_outputs_execute_workunits", "sync_outputs_can_mutate_master_index"):
        if truth.get(field) is not False:
            errors.append(f"{source}: truth_boundary.{field} must be false")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), source))
    for section in ("added_docs", "added_inventories", "added_scripts", "added_tests"):
        for path in _string_items(data.get(section)):
            normalized = path.replace("\\", "/")
            if any(normalized.startswith(prefix) for prefix in TRACK_B_PREFIXES):
                errors.append(f"{source}: {section} contains Track B path {path}")
    return errors


def _validate_required_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_DOCS:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"docs: missing {path}")
            continue
        if path in {"docs/operations/OBS_TRACK_B_SYNCHRONIZATION.md", "docs/operations/OBS_TO_TRACK_B_HANDOFF_GUIDE.md"}:
            text = full_path.read_text(encoding="utf-8").lower()
            for phrase in ("track b", "human review", "runtime", "no-goals"):
                if phrase not in text:
                    errors.append(f"{path}: missing phrase {phrase!r}")
    for path in (AUDIT_SUMMARY_PATH, GAP_REGISTER_PATH, NEXT_ACTIONS_PATH):
        if not (repo_root / path).is_file():
            errors.append(f"audit: missing {path}")
    return errors


def _validate_pending_slots(repo_root: Path) -> list[str]:
    errors: list[str] = []
    pending = _mapping(_load_json(repo_root / PENDING_BATCH_PATH, errors))
    if pending.get("observation_status") != "pending_manual_observation":
        errors.append(f"{PENDING_BATCH_PATH}: observation_status must remain pending_manual_observation")
    for record in _sequence_items(pending.get("observations")):
        item = _mapping(record)
        observation_id = item.get("observation_id", "<missing>")
        if item.get("observation_status") != "pending_manual_observation":
            errors.append(f"{PENDING_BATCH_PATH}: {observation_id}: observation_status must remain pending_manual_observation")
        if item.get("top_results") != []:
            errors.append(f"{PENDING_BATCH_PATH}: {observation_id}: top_results must remain empty")
    slot_manifest = _mapping(_load_json(repo_root / SLOT_MANIFEST_PATH, errors))
    for slot in _sequence_items(slot_manifest.get("slots")):
        item = _mapping(slot)
        slot_id = item.get("slot_id", "<missing>")
        if item.get("slot_status") != "pending_manual_observation":
            errors.append(f"{SLOT_MANIFEST_PATH}: {slot_id}: slot_status must remain pending_manual_observation")
        if item.get("observed_file_path_if_any") is not None:
            errors.append(f"{SLOT_MANIFEST_PATH}: {slot_id}: observed_file_path_if_any must remain null")
    return errors


def _validate_no_observed_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for relative_dir in OBSERVATION_DIRS:
        directory = repo_root / relative_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            name = path.name.lower()
            if name.startswith("observed") or name.startswith("accepted"):
                errors.append(f"{relative_dir}: observed/accepted result file is not allowed: {path.name}")
    return errors


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
    return [f"{source}: forbidden claim marker {marker}" for marker in FORBIDDEN_MATRIX_MARKERS if marker in text]


def _missing_items(found_items: Sequence[str], required_items: set[str], source: str) -> list[str]:
    found = set(found_items)
    return [f"{source} missing {item}" for item in sorted(required_items - found)]


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _string_items(value: Any) -> list[str]:
    return [item for item in _sequence_items(value) if isinstance(item, str)]


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_obs_track_b_synchronization: {report['status']}",
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
