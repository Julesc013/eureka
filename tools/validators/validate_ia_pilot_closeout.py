#!/usr/bin/env python3
"""Validate Internet Archive metadata pilot closeout evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_ia_candidate_index_integration import validate_ia_candidate_index_integration  # noqa: E402
from scripts.validate_ia_evidence_ledger_integration import validate_ia_evidence_ledger_integration  # noqa: E402
from scripts.validate_ia_fixture_replay import validate_ia_fixture_replay  # noqa: E402
from scripts.validate_ia_live_metadata_probe import validate_ia_live_metadata_probe  # noqa: E402
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy  # noqa: E402
from scripts.validate_ia_review_promotion_dry_run import validate_ia_review_promotion_dry_run  # noqa: E402
from scripts.validate_ia_reviewed_index_rebuild import validate_ia_reviewed_index_rebuild  # noqa: E402
from scripts.validate_ia_source_cache_write import validate_ia_source_cache_write  # noqa: E402


REQUIRED_STAGE_RESULTS = (
    "control/inventory/ia_00_result.json",
    "control/inventory/ia_01_result.json",
    "control/inventory/ia_02_result.json",
    "control/inventory/ia_03_result.json",
    "control/inventory/ia_04_result.json",
    "control/inventory/ia_05_result.json",
    "control/inventory/ia_06_result.json",
    "control/inventory/ia_07_result.json",
)

REQUIRED_FILES = REQUIRED_STAGE_RESULTS + (
    "control/inventory/ia_pilot_closeout_input_state.json",
    "control/inventory/ia_pilot_capability_matrix.json",
    "control/inventory/ia_pilot_validation_matrix.json",
    "control/inventory/ia_pilot_boundary_matrix.json",
    "control/inventory/ia_pilot_reuse_matrix.json",
    "control/inventory/ia_pilot_warning_disposition.json",
    "control/inventory/ia_pilot_blocker_register.json",
    "control/inventory/ia_pilot_closeout_result.json",
    "control/inventory/ia_pilot_next_task_decision.json",
    "docs/operations/IA_METADATA_PILOT_CLOSEOUT.md",
    "docs/operations/POST_IA_SYN_ENTRY_PLAN.md",
    "scripts/summarize_ia_pilot.py",
    "scripts/validate_ia_pilot_closeout.py",
)

REQUIRED_CAPABILITIES = {
    "ia_00_policy_approval",
    "ia_01_fixture_replay",
    "ia_02_bounded_live_metadata_probe",
    "ia_02_tls_trust_diagnosis_repair",
    "ia_03_source_cache_write_path",
    "ia_04_evidence_ledger_integration",
    "ia_05_candidate_index_integration",
    "ia_06_review_queue_promotion_dry_run",
    "ia_07_reviewed_local_index_rebuild",
    "search_result_proof",
    "object_packet_proof",
    "absence_packet_proof",
    "play_integration_readiness",
    "syn_handoff_readiness",
}

REQUIRED_VALIDATIONS = {
    "policy_validator",
    "fixture_replay_validator",
    "live_probe_validator",
    "tls_validator",
    "source_cache_validator",
    "evidence_validator",
    "candidate_validator",
    "review_promotion_validator",
    "reviewed_index_validator",
    "architecture_boundaries",
    "generated_artifact_cleanliness",
    "aide_doctor",
    "aide_validate",
    "aide_test",
    "aide_selftest",
    "aide_verify",
    "aide_review_pack",
    "aide_commit_check",
    "focused_ia_tests",
    "full_unittest_discovery",
}

REQUIRED_REUSE = {
    "source_policy_gate",
    "fixture_replay",
    "bounded_live_metadata_probe",
    "tls_diagnostics",
    "redaction_policy",
    "source_cache_write_path",
    "evidence_candidate_generation",
    "provisional_candidate_generation",
    "review_queue_integration",
    "promotion_dry_run",
    "reviewed_local_index_rebuild",
    "search_object_absence_proof",
    "temp_instance_proof_pattern",
    "non_claim_policy",
    "boundary_report_pattern",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_pilot_closeout(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_pilot_closeout(repo_root: Path = REPO_ROOT, *, run_stage_validators: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    stage_results = validate_stage_results(repo_root)
    errors.extend(stage_results)

    stage_validator_status = _stage_validator_status(repo_root) if run_stage_validators else {}
    for name, status in stage_validator_status.items():
        if status != "pass":
            errors.append(f"{name}_failed")

    capability = _load_json(repo_root / "control/inventory/ia_pilot_capability_matrix.json", errors)
    validation = _load_json(repo_root / "control/inventory/ia_pilot_validation_matrix.json", errors)
    boundary = _load_json(repo_root / "control/inventory/ia_pilot_boundary_matrix.json", errors)
    reuse = _load_json(repo_root / "control/inventory/ia_pilot_reuse_matrix.json", errors)
    warnings_doc = _load_json(repo_root / "control/inventory/ia_pilot_warning_disposition.json", errors)
    blockers = _load_json(repo_root / "control/inventory/ia_pilot_blocker_register.json", errors)
    result = _load_json(repo_root / "control/inventory/ia_pilot_closeout_result.json", errors)
    decision = _load_json(repo_root / "control/inventory/ia_pilot_next_task_decision.json", errors)

    errors.extend(validate_capability_matrix(capability))
    errors.extend(validate_validation_matrix(validation))
    errors.extend(validate_boundary_matrix(boundary))
    errors.extend(validate_reuse_matrix(reuse))
    errors.extend(validate_warning_and_blocker_disposition(warnings_doc, blockers))
    errors.extend(validate_closeout_result(result))
    errors.extend(validate_next_task_decision(decision))
    errors.extend(validate_non_claim_docs(repo_root))
    errors.extend(validate_no_raw_response_commit(repo_root))
    errors.extend(validate_no_forbidden_git_state(repo_root))

    return {
        "schema_version": "ia_pilot_closeout_validation.v0",
        "task": "IA-PILOT-CLOSEOUT-01",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "ia_00_policy_validated": stage_validator_status.get("ia_00_policy", "pass") == "pass",
        "ia_01_fixture_replay_validated": stage_validator_status.get("ia_01_fixture_replay", "pass") == "pass",
        "ia_02_live_probe_validated": stage_validator_status.get("ia_02_live_probe", "pass") == "pass",
        "ia_03_source_cache_validated": stage_validator_status.get("ia_03_source_cache", "pass") == "pass",
        "ia_04_evidence_ledger_validated": stage_validator_status.get("ia_04_evidence", "pass") == "pass",
        "ia_05_candidate_index_validated": stage_validator_status.get("ia_05_candidate", "pass") == "pass",
        "ia_06_review_promotion_validated": stage_validator_status.get("ia_06_review_promotion", "pass") == "pass",
        "ia_07_reviewed_index_validated": stage_validator_status.get("ia_07_reviewed_index", "pass") == "pass",
        "capability_matrix_complete": not validate_capability_matrix(capability),
        "validation_matrix_complete": not validate_validation_matrix(validation),
        "boundary_matrix_complete": not validate_boundary_matrix(boundary),
        "reuse_matrix_complete": not validate_reuse_matrix(reuse),
        "hard_blockers_remaining": blockers.get("hard_blockers_remaining"),
        "warnings_remaining": warnings_doc.get("warnings_remaining"),
        "full_ia_metadata_vertical_slice_complete": result.get("full_ia_metadata_vertical_slice_complete") is True,
        "full_archive_org_integration_claimed": result.get("full_archive_org_integration_claimed") is True,
        "syn_can_start": decision.get("syn_can_start") is True,
        "raw_response_committed": False,
        "operator_instance_mutated": False,
        "committed_data_public_index_mutated": False,
        "master_index_mutated": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_stage_results(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_STAGE_RESULTS:
        payload = _load_json(repo_root / rel_path, errors)
        if payload.get("status") != "pass":
            errors.append(f"stage_result_not_pass:{rel_path}")
    ia07 = _load_json(repo_root / "control/inventory/ia_07_result.json", errors)
    if ia07.get("search_result_proof_passed") is not True:
        errors.append("ia07_search_result_proof_missing")
    if ia07.get("object_packet_proof_passed") is not True:
        errors.append("ia07_object_packet_proof_missing")
    if ia07.get("absence_packet_proof_passed") is not True:
        errors.append("ia07_absence_packet_proof_missing")
    return errors


def validate_capability_matrix(matrix: Mapping[str, Any]) -> list[str]:
    rows = matrix.get("rows", [])
    ids = {row.get("capability_id") for row in rows if isinstance(row, Mapping)}
    errors = [f"missing_capability:{item}" for item in sorted(REQUIRED_CAPABILITIES - ids)]
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            continue
        for key in ("capability_id", "stage", "implemented", "tested", "writes_instance_state", "write_scope", "validates_with", "audit_evidence", "limitations", "reusable_for_future_sources"):
            if key not in row:
                errors.append(f"capability_missing_field:{row.get('capability_id')}:{key}")
    return errors


def validate_validation_matrix(matrix: Mapping[str, Any]) -> list[str]:
    rows = matrix.get("rows", [])
    ids = {row.get("validation_id") for row in rows if isinstance(row, Mapping)}
    errors = [f"missing_validation:{item}" for item in sorted(REQUIRED_VALIDATIONS - ids)]
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            continue
        if row.get("status") not in {"pass", "warn", "fail", "not_run"}:
            errors.append(f"validation_bad_status:{row.get('validation_id')}")
        if row.get("blocks_closeout") is True and row.get("status") != "pass":
            errors.append(f"blocking_validation_not_pass:{row.get('validation_id')}")
        for key in ("command", "status", "blocks_closeout", "notes", "evidence_path"):
            if key not in row:
                errors.append(f"validation_missing_field:{row.get('validation_id')}:{key}")
    return errors


def validate_boundary_matrix(matrix: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    forbidden = matrix.get("forbidden_boundaries", {})
    for key in (
        "raw_response_committed",
        "operator_instance_mutated",
        "instance_state_committed",
        "committed_data_public_index_mutated",
        "master_index_mutated",
        "hosted_public_search_mutated",
        "public_search_fanout_enabled",
        "downloads_performed",
        "uploads_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if forbidden.get(key) is not False:
            errors.append(f"forbidden_boundary_not_false:{key}")
    allowed = matrix.get("intentionally_allowed_actions", {})
    for key in (
        "live_metadata_probe_performed",
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "candidate_index_mutated",
        "review_queue_mutated",
        "reviewed_index_mutated",
    ):
        if allowed.get(key) is not True:
            errors.append(f"allowed_action_not_true:{key}")
    if allowed.get("total_http_requests") != 2:
        errors.append("total_http_requests_not_two")
    for key in ("source_cache_write_scope", "evidence_ledger_write_scope", "candidate_index_write_scope", "review_queue_write_scope", "reviewed_index_write_scope"):
        if allowed.get(key) != "temp_explicit_instance_only":
            errors.append(f"write_scope_not_temp:{key}")
    return errors


def validate_reuse_matrix(matrix: Mapping[str, Any]) -> list[str]:
    rows = matrix.get("rows", [])
    ids = {row.get("pattern_id") for row in rows if isinstance(row, Mapping)}
    errors = [f"missing_reuse_pattern:{item}" for item in sorted(REQUIRED_REUSE - ids)]
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            continue
        reusable_for = row.get("reusable_for", [])
        if not isinstance(reusable_for, list) or "future source packs" not in reusable_for:
            errors.append(f"reuse_pattern_missing_future_source_packs:{row.get('pattern_id')}")
    return errors


def validate_warning_and_blocker_disposition(warnings_doc: Mapping[str, Any], blockers: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if warnings_doc.get("warnings_remaining") != 0:
        errors.append("warnings_remaining_not_zero")
    if blockers.get("hard_blockers_remaining") != 0:
        errors.append("hard_blockers_remaining_not_zero")
    return errors


def validate_closeout_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required_true = (
        "ia_00_policy_validated",
        "ia_01_fixture_replay_validated",
        "ia_02_live_probe_validated",
        "ia_03_source_cache_validated",
        "ia_04_evidence_ledger_validated",
        "ia_05_candidate_index_validated",
        "ia_06_review_promotion_validated",
        "ia_07_reviewed_index_validated",
        "full_ia_metadata_vertical_slice_complete",
        "live_metadata_probe_performed",
        "syn_can_start",
    )
    for key in required_true:
        if result.get(key) is not True:
            errors.append(f"closeout_result_expected_true:{key}")
    required_false = (
        "full_archive_org_integration_claimed",
        "raw_response_committed",
        "operator_instance_mutated",
        "instance_state_committed",
        "committed_data_public_index_mutated",
        "master_index_mutated",
        "public_search_fanout_enabled",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for key in required_false:
        if result.get(key) is not False:
            errors.append(f"closeout_result_expected_false:{key}")
    if result.get("total_http_requests") != 2:
        errors.append("closeout_total_http_requests_not_two")
    return errors


def validate_next_task_decision(decision: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if "SYN-00" not in str(decision.get("recommended_next_task", "")):
        errors.append("syn_not_recommended_next")
    if "IA-TO-MAIN-PROMOTION-REVIEW" not in str(decision.get("alternative_next_task", "")):
        errors.append("promotion_review_not_alternative")
    if decision.get("syn_can_start") is not True:
        errors.append("syn_can_start_not_true")
    return errors


def validate_non_claim_docs(repo_root: Path) -> list[str]:
    errors: list[str] = []
    closeout_doc = repo_root / "docs/operations/IA_METADATA_PILOT_CLOSEOUT.md"
    if not closeout_doc.exists():
        return ["missing_closeout_doc"]
    text = closeout_doc.read_text(encoding="utf-8").lower()
    forbidden_phrases = (
        "full archive.org integration is complete",
        "production ready",
        "public launch ready",
        "rights clearance is established",
        "malware safety is established",
    )
    for phrase in forbidden_phrases:
        if phrase in text:
            errors.append(f"forbidden_closeout_claim:{phrase}")
    required_phrases = ("does not prove full archive.org integration", "syn-00", "temp explicit instance")
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"missing_closeout_non_claim:{phrase}")
    return errors


def validate_no_raw_response_commit(repo_root: Path) -> list[str]:
    errors: list[str] = []
    paths = list((repo_root / "control/inventory").glob("ia*.json")) + list((repo_root / "control/audits").glob("ia*/**/*.json"))
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        text = json.dumps(payload, sort_keys=True).lower()
        if "raw_response_body" in text or "\"response_body\"" in text:
            errors.append(f"raw_response_body_committed:{path.relative_to(repo_root).as_posix()}")
    return errors


def validate_no_forbidden_git_state(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--",
            "eureka-instance",
            "instances",
            ".aide.local",
            "secrets",
            ".env",
            "site/dist/data/public_index",
            "runtime/connectors",
            "runtime/extraction",
            "runtime/search_quality",
            "native",
            "crates",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return ["git_status_forbidden_paths_failed"]
    return ["forbidden_path_modified:" + completed.stdout.strip().replace("\n", ";")] if completed.stdout.strip() else []


def _stage_validator_status(repo_root: Path) -> dict[str, str]:
    validators = {
        "ia_00_policy": validate_ia_metadata_policy,
        "ia_01_fixture_replay": validate_ia_fixture_replay,
        "ia_02_live_probe": validate_ia_live_metadata_probe,
        "ia_03_source_cache": validate_ia_source_cache_write,
        "ia_04_evidence": validate_ia_evidence_ledger_integration,
        "ia_05_candidate": validate_ia_candidate_index_integration,
        "ia_06_review_promotion": validate_ia_review_promotion_dry_run,
        "ia_07_reviewed_index": validate_ia_reviewed_index_rebuild,
    }
    return {name: validator(repo_root).get("status", "fail") for name, validator in validators.items()}


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.exists():
        errors.append(f"missing_json:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


if __name__ == "__main__":
    raise SystemExit(main())
