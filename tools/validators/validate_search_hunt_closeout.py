#!/usr/bin/env python3
"""Validate HUNT-12 Search Hunt closeout and handoff evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.audit_search_hunt_closeout import audit_closeout
from scripts.hunt_queue_progress import current_recommended_task_id, post_hunt_current_allowed


PASS_STATUSES = {"pass", "pass_with_warnings"}
TASK_ID = "HUNT-12"

INVENTORIES = {
    "control/inventory/search_hunt_closeout_result.json": "search_hunt_closeout_result.v0",
    "control/inventory/search_hunt_capability_matrix.json": "search_hunt_capability_matrix.v0",
    "control/inventory/search_hunt_validation_matrix.json": "search_hunt_validation_matrix.v0",
    "control/inventory/search_hunt_warning_disposition.json": "search_hunt_warning_disposition.v0",
    "control/inventory/search_hunt_blocker_register.json": "search_hunt_blocker_register.v0",
    "control/inventory/search_hunt_runtime_surface_index.json": "search_hunt_runtime_surface_index.v0",
    "control/inventory/search_hunt_future_track_gate_final.json": "search_hunt_future_track_gate_final.v0",
    "control/inventory/search_hunt_handoff_to_syn.json": "search_hunt_handoff_to_syn.v0",
    "control/inventory/search_hunt_handoff_to_f0.json": "search_hunt_handoff_to_f0.v0",
    "control/inventory/search_hunt_handoff_to_g_h_k.json": "search_hunt_handoff_to_g_h_k.v0",
    "control/inventory/search_hunt_promotion_review.json": "search_hunt_promotion_review.v0",
    "control/inventory/hunt_12_next_task_decision.json": "hunt_12_next_task_decision.v0",
}

SCRIPTS = (
    "scripts/audit_search_hunt_closeout.py",
    "scripts/validate_search_hunt_closeout.py",
    "scripts/summarize_search_hunt_capabilities.py",
    "scripts/prepare_hunt_to_syn_f0_handoff.py",
    "scripts/prepare_hunt_to_main_promotion_review.py",
)
DOCS = (
    "docs/architecture/SEARCH_HUNT_PRODUCT_SPINE.md",
    "docs/architecture/SEARCH_HUNT_CAPABILITY_MAP.md",
    "docs/operations/SEARCH_HUNT_CLOSEOUT.md",
    "docs/operations/HUNT_TO_SYN_F0_HANDOFF.md",
    "docs/operations/SEARCH_HUNT_FUTURE_TASK_GATE.md",
    "docs/operations/SEARCH_HUNT_REMAINING_WARNINGS.md",
    "docs/operations/HUNT_TO_MAIN_PROMOTION_REVIEW.md",
    "docs/operations/POST_HUNT_EXECUTION_SPINE.md",
)
TESTS = (
    "tests/operations/test_search_hunt_closeout.py",
    "tests/operations/test_search_hunt_future_track_gate.py",
    "tests/operations/test_search_hunt_handoff.py",
    "tests/operations/test_hunt_to_main_promotion_review.py",
)
AUDIT_ROOT = Path("control/audits/hunt-12-search-hunt-closeout-v0")
AUDIT_FILES = (
    "README.md",
    "hunt_12_report.json",
    "capability_matrix.md",
    "validation_matrix.md",
    "warning_disposition.md",
    "blocker_register.md",
    "runtime_surface_index.md",
    "future_track_gate.md",
    "syn_handoff.md",
    "f0_handoff.md",
    "g_h_k_handoff.md",
    "promotion_review.md",
    "validation.md",
    "generated/sample_hunt_closeout_result.json",
    "generated/sample_capability_matrix.json",
    "generated/sample_future_track_gate.json",
    "generated/sample_next_task_decision.json",
    "generated/sample_summary.md",
)
HUNT_VALIDATORS = (
    "python scripts/validate_ai_escalation_gate.py",
    "python scripts/validate_hunt_replay.py",
    "python scripts/validate_agent_research_task_contract.py",
    "python scripts/validate_search_hunt_workbench_integration.py",
    "python scripts/validate_background_hunt_runner.py",
    "python scripts/validate_hunt_to_workunits.py",
    "python scripts/validate_hunt_to_search_need.py",
    "python scripts/validate_search_hunt_exhaustion.py",
    "python scripts/validate_search_hunt_commands.py",
    "python scripts/validate_search_hunt_ui.py",
    "python scripts/validate_search_hunt_runtime.py",
    "python scripts/validate_search_hunt_track.py",
)
LOCAL_VALIDATORS = (
    "python scripts/validate_local_appliance_closeout.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--run-full-discovery", action="store_true")
    parser.add_argument("--run-local-closeout", action="store_true")
    args = parser.parse_args(argv)

    result = validate(
        Path(args.repo_root).resolve(),
        run_full_discovery=args.run_full_discovery,
        run_local_closeout=args.run_local_closeout,
    )
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("HUNT-12 Search Hunt closeout validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in PASS_STATUSES else 1


def validate(root: Path = REPO_ROOT, *, run_full_discovery: bool = False, run_local_closeout: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in INVENTORIES.items()}
    report = load_json(root / AUDIT_ROOT / "hunt_12_report.json", "hunt_12_report.v0", errors)
    validate_files(root, errors)
    validate_closeout_payload(payloads, report, errors, warnings)
    validate_future_gate(payloads, errors)
    validate_handoffs(payloads, errors)
    validate_queue(root, errors)
    audit = audit_closeout(root)
    if audit["closeout_result"]["hard_blockers_remaining"]:
        errors.extend(audit["errors"])
    run_validation_commands(root, warnings, errors, run_full_discovery=run_full_discovery, run_local_closeout=run_local_closeout)
    status = "fail" if errors else ("pass_with_warnings" if warnings or payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("warnings_remaining", 0) else "pass")
    return {
        "schema_version": "search_hunt_closeout_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "audit_status": audit["status"],
        "hunt_track_complete": payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("hunt_track_complete") is True,
        "hard_blockers_remaining": payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("hard_blockers_remaining", 0),
        "warnings_remaining": payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("warnings_remaining", 0),
        "syn_can_start": payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("syn_can_start") is True,
        "f0_can_resume": payloads.get("control/inventory/search_hunt_closeout_result.json", {}).get("f0_can_resume") is True,
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "download_install_execute_performed": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in (*SCRIPTS, *DOCS, *TESTS):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty file: {rel}")
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_closeout_payload(payloads: Mapping[str, Mapping[str, Any]], report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    closeout = payloads.get("control/inventory/search_hunt_closeout_result.json", {})
    for key in (
        "hunt_track_complete",
        "all_required_capabilities_implemented",
        "all_required_capabilities_tested",
        "workbench_workflow_smoke_passed",
        "api_smoke_passed",
        "deterministic_replay_passed",
        "ai_escalation_gate_disabled",
        "syn_can_start",
        "f0_can_resume",
        "main_promotion_review_required",
    ):
        if closeout.get(key) is not True:
            errors.append(f"closeout {key} must be true")
    for key in (
        "provider_calls_performed",
        "source_probes_executed",
        "extraction_executed",
        "master_index_mutated",
        "site_dist_mutated",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if closeout.get(key) is not False:
            errors.append(f"closeout {key} must be false")
    if closeout.get("hard_blockers_remaining") != 0:
        errors.append("hard blockers must be zero for closeout")
    if int(closeout.get("warnings_remaining", 0) or 0) > 0 and closeout.get("status") != "pass_with_warnings":
        errors.append("closeout with warnings must use pass_with_warnings")
    if closeout.get("f0_recommended_now") is not False:
        errors.append("F0 must not be recommended now by default")
    if not hunt_closeout_next_task_allowed(closeout.get("recommended_next_task", "")):
        errors.append("closeout next task must be SYN-00 or gated HUNT-TO-MAIN-PROMOTION-REVIEW")
    if report.get("schema_version") != "hunt_12_report.v0":
        errors.append("hunt_12_report schema mismatch")
    if report.get("status") not in PASS_STATUSES:
        errors.append("hunt_12_report status must pass or pass_with_warnings")
    for key in ("source_probe_executed", "extraction_executed", "model_provider_used", "deployment_performed"):
        if report.get(key) is not False:
            errors.append(f"hunt_12_report {key} must be false")
    warnings_payload = payloads.get("control/inventory/search_hunt_warning_disposition.json", {})
    if warnings_payload.get("all_warnings_disposed") is not True:
        errors.append("all warnings must be disposed")
    if int(warnings_payload.get("warnings_blocking_syn", 0) or 0):
        errors.append("warnings must not block SYN")
    if int(warnings_payload.get("warnings_blocking_f0", 0) or 0):
        errors.append("warnings must not block F0")
    if int(warnings_payload.get("warnings_blocking_main_promotion", 0) or 0):
        warnings.append("main promotion review must resolve warning(s) before merge")
    blockers = payloads.get("control/inventory/search_hunt_blocker_register.json", {})
    if blockers.get("blockers") != []:
        errors.append("blocker register must be empty")
    capabilities = payloads.get("control/inventory/search_hunt_capability_matrix.json", {}).get("capabilities", [])
    required = {
        "hunt_track_plan",
        "search_hunt_session_runtime",
        "hunt_ui_state",
        "hunt_commands_and_steering",
        "exhaustion_reports",
        "search_need_runtime",
        "hunt_to_search_need",
        "hunt_to_workunit",
        "background_hunt_runner",
        "workbench_api_cli_smoke",
        "agent_research_task_contract_provider_disabled",
        "deterministic_replay",
        "ai_escalation_gate_disabled_by_default",
    }
    seen = {row.get("capability_id") for row in capabilities}
    missing = sorted(required - seen)
    if missing:
        errors.append("missing capabilities: " + ", ".join(missing))
    for row in capabilities:
        if row.get("implemented") is not True or row.get("tested") is not True:
            errors.append(f"capability not implemented/tested: {row.get('capability_id')}")


def validate_future_gate(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    gate = payloads.get("control/inventory/search_hunt_future_track_gate_final.json", {})
    required_true = (
        "syn_must_use_hunt_and_local_appliance_for_query_pressure",
        "f0_extraction_tasks_must_be_generated_as_workunits_where_applicable",
        "f0_outputs_are_candidates_not_direct_truth",
        "g_must_consume_hunt_exhaustion_near_miss_and_absence_state",
        "h_source_expansion_starts_from_policy_gated_source_probe_workunits",
        "k_ai_assist_must_use_ai_escalation_gate_candidate_only",
        "future_tracks_may_not_bypass_hunt_workunit_review_index_without_exception",
    )
    for key in required_true:
        if gate.get(key) is not True:
            errors.append(f"future gate {key} must be true")


def validate_handoffs(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    syn = payloads.get("control/inventory/search_hunt_handoff_to_syn.json", {})
    f0 = payloads.get("control/inventory/search_hunt_handoff_to_f0.json", {})
    ghk = payloads.get("control/inventory/search_hunt_handoff_to_g_h_k.json", {})
    if "SYN-00" not in str(syn.get("next_task", "")) or syn.get("syn_must_not_generate_fake_evidence") is not True:
        errors.append("SYN handoff must point to SYN-00 and forbid fake evidence")
    if "F0-00" not in str(f0.get("next_task", "")) or f0.get("f0_should_use_workunits_for_extraction_tasks") is not True:
        errors.append("F0 handoff must point to F0-00 and use WorkUnits")
    if ghk.get("g_consumes_hunt_explanations_exhaustion_absence") is not True or ghk.get("k_consumes_ai_escalation_gate_and_agent_research_task_contract") is not True:
        errors.append("G/H/K handoff must bind later tracks to HUNT surfaces")
    promotion = payloads.get("control/inventory/search_hunt_promotion_review.json", {})
    if promotion.get("branch_mutation_performed") is not False or promotion.get("merge_performed") is not False:
        errors.append("promotion review must not merge or mutate branches")
    decision = payloads.get("control/inventory/hunt_12_next_task_decision.json", {})
    if not hunt_closeout_next_task_allowed(decision.get("recommended_next_task", "")):
        errors.append("HUNT-12 next decision must recommend SYN-00 or gated HUNT-TO-MAIN-PROMOTION-REVIEW")
    if decision.get("f0_recommended_now") is not False:
        errors.append("HUNT-12 decision must defer F0 by default")


def validate_queue(root: Path, errors: list[str]) -> None:
    index = root / ".aide/queue/index.yaml"
    text = index.read_text(encoding="utf-8") if index.is_file() else ""
    if not queue_preserves_hunt_handoff(root, text):
        errors.append(
            "queue current_recommended_task must be SYN-00, DOMAIN-00, gated HUNT-TO-MAIN-PROMOTION-REVIEW, "
            "or an accepted post-HUNT Workbench/IA bridge handoff"
        )
    for rel in (
        ".aide/queue/SYN-00/task.yaml",
        ".aide/queue/F0-00/task.yaml",
        ".aide/queue/HUNT-PROMOTION-REVIEW/task.yaml",
        ".aide/queue/HUNT-REMEDIATION/task.yaml",
    ):
        if not (root / rel).is_file():
            errors.append(f"missing queue task stub: {rel}")


def queue_preserves_hunt_handoff(root: Path, queue_text: str) -> bool:
    if post_hunt_current_allowed(root):
        return True
    if "current_recommended_task: SYN-00" in queue_text:
        return True
    if "current_recommended_task: DOMAIN-00" in queue_text:
        return True
    if "current_recommended_task: SCOUT-SCHEMA-00" in queue_text:
        return True
    if (
        "current_recommended_task: DEV-AND-IA-" in queue_text
        or "current_recommended_task: REPO-LAYOUT-" in queue_text
        or "current_recommended_task: WORKBENCH-" in queue_text
        or "current_recommended_task: SEARCH-INTERACTION-" in queue_text
        or "current_recommended_task: IA-HUNT-BRIDGE-00" in queue_text
    ):
        closeout = load_json(root / "control/inventory/search_hunt_closeout_result.json", "search_hunt_closeout_result.v0", [])
        return (
            "id: SYN-00" in queue_text
            and "id: HUNT-TO-MAIN-PROMOTION-REVIEW" in queue_text
            and closeout.get("syn_can_start") is True
            and closeout.get("hard_blockers_remaining") == 0
        )
    if "current_recommended_task: HUNT-TO-MAIN-PROMOTION-REVIEW" not in queue_text:
        return False
    aide = load_json(root / "control/inventory/aide_eval_green_result.json", "aide_eval_green_result.v0", [])
    closeout = load_json(root / "control/inventory/search_hunt_closeout_result.json", "search_hunt_closeout_result.v0", [])
    return (
        aide.get("aide_eval_green") is True
        and aide.get("eval_fail_count_after") == 0
        and aide.get("product_behavior_changed") is False
        and closeout.get("syn_can_start") is True
        and closeout.get("hard_blockers_remaining") == 0
    )


def hunt_closeout_next_task_allowed(value: object) -> bool:
    text = str(value)
    return "SYN-00" in text or "HUNT-TO-MAIN-PROMOTION-REVIEW" in text


def run_validation_commands(root: Path, warnings: list[str], errors: list[str], *, run_full_discovery: bool, run_local_closeout: bool) -> None:
    for command in HUNT_VALIDATORS:
        outcome = run_command(root, command, timeout=90)
        classify_command(command, outcome, warnings, errors)
    if run_local_closeout:
        for command in LOCAL_VALIDATORS:
            outcome = run_command(root, command, timeout=1800)
            classify_command(command, outcome, warnings, errors)
    for command in (
        "python scripts/check_generated_artifact_cleanliness.py --check --json",
        "python scripts/check_architecture_boundaries.py",
    ):
        outcome = run_command(root, command, timeout=120)
        classify_command(command, outcome, warnings, errors, cleanliness_is_warning=True)
    if run_full_discovery:
        outcome = run_command(root, "python -m unittest discover -s tests -t .", timeout=300)
        classify_command("python -m unittest discover -s tests -t .", outcome, warnings, errors, timeout_is_warning=True)


def run_command(root: Path, command: str, *, timeout: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(command.split(), cwd=root, text=True, capture_output=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return {"status": "timeout", "returncode": None, "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
    return {"status": "completed", "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def classify_command(command: str, outcome: Mapping[str, Any], warnings: list[str], errors: list[str], *, timeout_is_warning: bool = False, cleanliness_is_warning: bool = False) -> None:
    text = f"{outcome.get('stdout', '')}\n{outcome.get('stderr', '')}"
    if outcome.get("status") == "timeout":
        if timeout_is_warning:
            warnings.append(f"{command}: WARN timeout in closeout lane")
        else:
            errors.append(f"{command}: timed out")
        return
    if outcome.get("returncode") == 0:
        return
    lower = text.lower()
    if "queue" in lower or "current_recommended_task" in lower or "next task" in lower or "must point to" in lower:
        warnings.append(f"{command}: WARN historical queue-sensitive validator after HUNT closeout")
        return
    if cleanliness_is_warning and ("generated_drift_paths" in text or "forbidden_untracked_generated_outputs" in text):
        warnings.append(f"{command}: WARN generated-artifact drift expected before commit")
        return
    errors.append(f"{command}: failed with exit {outcome.get('returncode')}")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.as_posix()}")
        return {}
    if payload.get("schema_version") != schema_version:
        errors.append(f"{path.as_posix()} schema_version must be {schema_version}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
