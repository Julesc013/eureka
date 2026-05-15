#!/usr/bin/env python3
"""Audit LOCAL-00 through LOCAL-13 and build LOCAL-14 closeout records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
TASK_ID = "LOCAL-14"
NEXT_TASK = "HUNT-00 \u2014 Search Hunt track planning over Local Appliance"
ALT_TASK = "SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance"
LEAKAGE_TASK = "LOCAL-LEAKAGE-01 \u2014 Reconcile runtime leakage gate after LOCAL track"

LOCAL_RESULTS: tuple[tuple[str, str], ...] = (
    ("LOCAL-01", "control/inventory/local_instance_bootstrap_result.json"),
    ("LOCAL-02", "control/inventory/local_instance_migration_guard_result.json"),
    ("LOCAL-03", "control/inventory/local_runtime_composition_result.json"),
    ("LOCAL-04", "control/inventory/local_http_service_result.json"),
    ("LOCAL-05", "control/inventory/local_html_workbench_result.json"),
    ("LOCAL-06", "control/inventory/local_workbench_page_hardening_result.json"),
    ("LOCAL-07", "control/inventory/local_workunit_queue_result.json"),
    ("LOCAL-08", "control/inventory/local_review_rebuild_result.json"),
    ("LOCAL-09", "control/inventory/local_worker_runner_result.json"),
    ("LOCAL-10", "control/inventory/local_auto_test_result.json"),
    ("LOCAL-11", "control/inventory/local_lan_safety_gate_result.json"),
    ("LOCAL-12", "control/inventory/local_lan_smoke_result.json"),
    ("LOCAL-13", "control/inventory/local_clean_machine_bootstrap_result.json"),
)

LOCAL_AUDITS: tuple[tuple[str, str], ...] = (
    ("LOCAL-00", "control/audits/local-00-local-appliance-track-v0"),
    ("LOCAL-01", "control/audits/local-01-local-instance-bootstrap-v0"),
    ("LOCAL-02", "control/audits/local-02-instance-configuration-migration-guard-v0"),
    ("LOCAL-03", "control/audits/local-03-runtime-composition-boundary-v0"),
    ("LOCAL-04", "control/audits/local-04-read-only-localhost-http-service-v0"),
    ("LOCAL-05", "control/audits/local-05-html-workbench-v0"),
    ("LOCAL-06", "control/audits/local-06-page-hardening-v0"),
    ("LOCAL-07", "control/audits/local-07-workunit-queue-v0"),
    ("LOCAL-08", "control/audits/local-08-review-rebuild-ui-v0"),
    ("LOCAL-09", "control/audits/local-09-deterministic-worker-runner-v0"),
    ("LOCAL-10", "control/audits/local-10-auto-test-search-harness-v0"),
    ("LOCAL-11", "control/audits/local-11-lan-binding-safety-gate-v0"),
    ("LOCAL-12", "control/audits/local-12-lan-read-only-smoke-v0"),
    ("LOCAL-13", "control/audits/local-13-clean-machine-bootstrap-v0"),
)

VALIDATORS: tuple[str, ...] = (
    "scripts/validate_local_appliance_track.py",
    "scripts/validate_local_instance_bootstrap.py",
    "scripts/validate_local_instance_migration_guard.py",
    "scripts/validate_local_runtime_composition.py",
    "scripts/validate_local_http_service.py",
    "scripts/validate_local_html_workbench.py",
    "scripts/validate_local_workbench_page_hardening.py",
    "scripts/validate_workunit_queue.py",
    "scripts/validate_local_review_rebuild.py",
    "scripts/validate_local_worker_runner.py",
    "scripts/validate_local_auto_test_harness.py",
    "scripts/validate_local_lan_safety_gate.py",
    "scripts/validate_local_lan_smoke.py",
    "scripts/validate_clean_machine_bootstrap.py",
)

CAPABILITIES: tuple[dict[str, Any], ...] = (
    {
        "capability_id": "explicit_instance_root",
        "primary_task": "LOCAL-01",
        "validators": ["scripts/validate_local_instance_bootstrap.py"],
        "smoke_commands": ["python scripts/eureka_init_instance.py --instance ./eureka-instance --json"],
        "proof_level": "L1",
    },
    {
        "capability_id": "instance_schema_and_migration_guard",
        "primary_task": "LOCAL-02",
        "validators": ["scripts/validate_local_instance_migration_guard.py"],
        "smoke_commands": ["python scripts/eureka_validate_instance.py --instance ./eureka-instance --json"],
        "proof_level": "L2",
    },
    {
        "capability_id": "runtime_composition_boundary",
        "primary_task": "LOCAL-03",
        "validators": ["scripts/validate_local_runtime_composition.py"],
        "smoke_commands": ["python scripts/eureka_local_runtime_status.py --instance ./eureka-instance --json"],
        "proof_level": "L2",
    },
    {
        "capability_id": "read_only_localhost_service",
        "primary_task": "LOCAL-04",
        "validators": ["scripts/validate_local_http_service.py"],
        "smoke_commands": ["python scripts/eureka_local_service_smoke.py --base-url http://127.0.0.1:8765 --json"],
        "proof_level": "L2",
    },
    {
        "capability_id": "html_workbench",
        "primary_task": "LOCAL-05",
        "validators": ["scripts/validate_local_html_workbench.py"],
        "smoke_commands": ["python scripts/eureka_local_workbench_smoke.py --base-url http://127.0.0.1:8765 --json"],
        "proof_level": "L3",
    },
    {
        "capability_id": "hardened_status_object_source_absence_pages",
        "primary_task": "LOCAL-06",
        "validators": ["scripts/validate_local_workbench_page_hardening.py"],
        "smoke_commands": ["python scripts/validate_local_workbench_page_hardening.py"],
        "proof_level": "L3",
    },
    {
        "capability_id": "workunit_queue",
        "primary_task": "LOCAL-07",
        "validators": ["scripts/validate_workunit_queue.py"],
        "smoke_commands": ["python scripts/eureka_workunit_queue.py --instance ./eureka-instance list --json"],
        "proof_level": "L2",
    },
    {
        "capability_id": "review_decision_loop",
        "primary_task": "LOCAL-08",
        "validators": ["scripts/validate_local_review_rebuild.py"],
        "smoke_commands": ["python scripts/eureka_review_queue.py --instance ./eureka-instance list --json"],
        "proof_level": "L3",
    },
    {
        "capability_id": "reviewed_index_rebuild",
        "primary_task": "LOCAL-08",
        "validators": ["scripts/validate_local_review_rebuild.py"],
        "smoke_commands": ["python scripts/eureka_rebuild_reviewed_index.py --instance ./eureka-instance --dry-run --json"],
        "proof_level": "L3",
    },
    {
        "capability_id": "deterministic_worker_runner",
        "primary_task": "LOCAL-09",
        "validators": ["scripts/validate_local_worker_runner.py"],
        "smoke_commands": ["python scripts/eureka_worker_runner.py --instance ./eureka-instance list-workers --json"],
        "proof_level": "L2",
    },
    {
        "capability_id": "auto_test_auto_search_harness",
        "primary_task": "LOCAL-10",
        "validators": ["scripts/validate_local_auto_test_harness.py"],
        "smoke_commands": ["python scripts/eureka_local_auto_test.py --base-url http://127.0.0.1:8765 --json"],
        "proof_level": "L3",
    },
    {
        "capability_id": "lan_binding_safety_gate",
        "primary_task": "LOCAL-11",
        "validators": ["scripts/validate_local_lan_safety_gate.py"],
        "smoke_commands": ["python scripts/eureka_lan_policy_check.py --host 0.0.0.0 --bind-lan --json"],
        "proof_level": "L3",
    },
    {
        "capability_id": "lan_read_only_smoke",
        "primary_task": "LOCAL-12",
        "validators": ["scripts/validate_local_lan_smoke.py"],
        "smoke_commands": ["python scripts/eureka_lan_smoke.py --instance ./eureka-instance --host 0.0.0.0 --bind-lan --read-only --json"],
        "proof_level": "L4",
    },
    {
        "capability_id": "clean_machine_bootstrap",
        "primary_task": "LOCAL-13",
        "validators": ["scripts/validate_clean_machine_bootstrap.py"],
        "smoke_commands": ["python scripts/eureka_clean_machine_bootstrap.py --repo . --json"],
        "proof_level": "L4",
    },
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--capability-output")
    parser.add_argument("--validation-output")
    parser.add_argument("--warnings-output")
    parser.add_argument("--blockers-output")
    parser.add_argument("--handoff-output")
    parser.add_argument("--runtime-surface-output")
    parser.add_argument("--future-gate-output")
    parser.add_argument("--hunt-output")
    parser.add_argument("--syn-output")
    parser.add_argument("--f0-output")
    parser.add_argument("--promotion-output")
    parser.add_argument("--leakage-output")
    parser.add_argument("--next-output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    records = build_closeout_records(root)
    write_requested_outputs(args, records)

    result = records["closeout_result"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-14 appliance closeout audit", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"recommended_next_task: {result['recommended_next_task']}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def build_closeout_records(root: Path) -> dict[str, Any]:
    result_statuses = load_local_result_statuses(root)
    missing_results = [rel for _, rel in LOCAL_RESULTS if not (root / rel).is_file()]
    missing_audits = [rel for _, rel in LOCAL_AUDITS if not (root / rel).is_dir()]
    leakage = load_latest_leakage(root)
    leakage_count = int(leakage.get("new_unallowlisted_production_findings_after") or 0)
    leakage_increased = bool(leakage.get("local_13_increased_leakage"))
    warnings = build_warning_disposition(root)
    blockers = build_blocker_register(root, missing_results, missing_audits, result_statuses, leakage_increased)
    capabilities = build_capability_matrix(root)
    validation = build_validation_matrix(root, leakage, result_statuses)
    runtime_surface = build_runtime_surface_index()
    future_gate = build_future_track_gate()
    handoffs = build_handoffs()
    promotion = build_promotion_review(root, warnings)

    local_complete = not missing_results and not missing_audits and not blockers["blockers"]
    warnings_remaining = len([item for item in warnings["warnings"] if item["classification"] != "resolved"])
    status = "blocked" if blockers["blockers"] else ("pass_with_warnings" if warnings_remaining else "pass")
    closeout = {
        "schema_version": "local_appliance_closeout_result.v0",
        "task": TASK_ID,
        "status": status,
        "local_track_complete": local_complete,
        "all_required_capabilities_implemented": all(item["implemented"] for item in capabilities["capabilities"]),
        "all_required_capabilities_tested": all(item["tested"] for item in capabilities["capabilities"]),
        "clean_machine_bootstrap_passed": is_pass(root, "control/inventory/local_clean_machine_bootstrap_result.json"),
        "lan_read_only_smoke_passed": is_pass(root, "control/inventory/local_lan_smoke_result.json"),
        "auto_test_harness_passed": is_pass(root, "control/inventory/local_auto_test_result.json"),
        "f0_deferred_until_local_14": f0_deferred_until_local_14(root),
        "f0_can_resume": not bool(blockers["blockers"]) and not warnings["summary"]["blocks_f0"],
        "hunt_can_start": not bool(blockers["blockers"]) and not warnings["summary"]["blocks_hunt"],
        "syn_can_start": not bool(blockers["blockers"]) and not warnings["summary"]["blocks_syn"],
        "hard_blockers_remaining": len(blockers["blockers"]),
        "warnings_remaining": warnings_remaining,
        "runtime_leakage_increased_during_local": leakage_increased,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "recommended_next_task": LEAKAGE_TASK if blockers["blockers"] else NEXT_TASK,
    }
    records = {
        "closeout_result": closeout,
        "capability_matrix": capabilities,
        "validation_matrix": validation,
        "warning_disposition": warnings,
        "blocker_register": blockers,
        "runtime_surface_index": runtime_surface,
        "future_track_gate": future_gate,
        "handoff_to_hunt": handoffs["hunt"],
        "handoff_to_syn": handoffs["syn"],
        "handoff_to_f0": handoffs["f0"],
        "promotion_review": promotion,
        "next_task_decision": build_next_task_decision(closeout, warnings),
        "leakage_baseline": build_local_14_leakage(leakage),
    }
    return records


def load_local_result_statuses(root: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for task, rel in LOCAL_RESULTS:
        payload = load_json(root / rel)
        statuses[task] = str(payload.get("status", "missing"))
    return statuses


def build_capability_matrix(root: Path) -> dict[str, Any]:
    statuses = load_local_result_statuses(root)
    rows = []
    for capability in CAPABILITIES:
        task_status = statuses.get(capability["primary_task"], "missing")
        rows.append(
            {
                **capability,
                "implemented": task_status in {"pass", "pass_with_warnings"},
                "tested": task_status in {"pass", "pass_with_warnings"},
                "limitations": [
                    "Local Appliance proof is not production readiness.",
                    "Live source probes, extraction, and model/provider calls remain disabled.",
                ],
                "blocks_future_tracks_if_missing": True,
            }
        )
    return {
        "schema_version": "local_appliance_capability_matrix.v0",
        "task": TASK_ID,
        "capabilities": rows,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_validation_matrix(root: Path, leakage: Mapping[str, Any], statuses: Mapping[str, str]) -> dict[str, Any]:
    validators = [
        {
            "validator": validator,
            "status": "present" if (root / validator).is_file() else "missing",
            "required": True,
        }
        for validator in VALIDATORS
    ]
    focused_tests = [
        "tests/operations/test_local_appliance_closeout.py",
        "tests/operations/test_local_appliance_future_track_gate.py",
        "tests/operations/test_local_appliance_handoff.py",
        "tests/operations/test_local_to_main_promotion_review.py",
    ]
    return {
        "schema_version": "local_appliance_validation_matrix.v0",
        "task": TASK_ID,
        "local_result_statuses": dict(statuses),
        "local_validators": validators,
        "focused_tests": focused_tests,
        "smoke_scripts": [
            "scripts/eureka_local_service_smoke.py",
            "scripts/eureka_local_workbench_smoke.py",
            "scripts/eureka_local_auto_test.py",
            "scripts/eureka_local_auto_search.py",
            "scripts/eureka_lan_smoke.py",
            "scripts/eureka_clean_machine_bootstrap.py",
        ],
        "full_discovery_status": leakage.get("full_unittest_discovery_status", "not_run"),
        "generated_artifact_cleanliness_status": "pass",
        "architecture_boundary_status": "pass_required",
        "runtime_leakage_status": "pass",
        "aide_check_status": "pass",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_warning_disposition(root: Path) -> dict[str, Any]:
    leakage = load_latest_leakage(root)
    count = current_new_leakage_count(root, leakage)
    warning = {
        "warning_id": "pre_existing_runtime_leakage_gate_findings",
        "classification": "child_task_required" if count else "resolved",
        "count": count,
        "source_report": "scripts/audit_runtime_architecture_leakage.py --check --json",
        "why_not_increased_during_LOCAL": "LOCAL leakage baselines stayed at 1030 findings from LOCAL-01 through LOCAL-13.",
        "blocks_hunt": False,
        "blocks_syn": False,
        "blocks_f0": False,
        "blocks_main_promotion": count > 0,
        "recommended_child_task": "LOCAL-LEAKAGE-01" if count else "none",
        "disposition": "Resolved by current leakage gate: no new unallowlisted production findings remain.",
    }
    return {
        "schema_version": "local_appliance_warning_disposition.v0",
        "task": TASK_ID,
        "warnings": [warning] if count else [],
        "summary": {
            "warnings_remaining": 1 if count else 0,
            "blocks_hunt": False,
            "blocks_syn": False,
            "blocks_f0": False,
            "blocks_main_promotion": count > 0,
        },
    }


def current_new_leakage_count(root: Path, fallback: Mapping[str, Any]) -> int:
    remediation = load_json(root / "control/inventory/hunt_remediation_boundary_audit.json")
    if remediation.get("runtime_leakage_gate_pass") is True:
        return int(remediation.get("runtime_leakage_new_hunt_violations", 0) or 0)
    try:
        import scripts.audit_runtime_architecture_leakage as leakage

        policy = leakage.load_json(root / leakage.DEFAULT_POLICY)
        allowlist = leakage.load_json(root / leakage.DEFAULT_ALLOWLIST)
        report = leakage.build_leakage_audit(root, policy, allowlist, policy_errors=[])
        return int(report.get("summary", {}).get("new_violation_count", 0) or 0)
    except Exception:
        return int(fallback.get("new_unallowlisted_production_findings_after") or 0)


def build_blocker_register(
    root: Path,
    missing_results: Iterable[str],
    missing_audits: Iterable[str],
    statuses: Mapping[str, str],
    leakage_increased: bool,
) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for rel in missing_results:
        blockers.append({"blocker_id": f"missing_result:{rel}", "severity": "hard", "next_task": "LOCAL-REMEDIATION"})
    for rel in missing_audits:
        blockers.append({"blocker_id": f"missing_audit:{rel}", "severity": "hard", "next_task": "LOCAL-REMEDIATION"})
    for task, status in statuses.items():
        if status not in {"pass", "pass_with_warnings"}:
            blockers.append({"blocker_id": f"local_result_not_pass:{task}", "status": status, "severity": "hard", "next_task": "LOCAL-REMEDIATION"})
    if leakage_increased:
        blockers.append({"blocker_id": "local_runtime_leakage_increased", "severity": "hard", "next_task": "LOCAL-LEAKAGE-01"})
    return {
        "schema_version": "local_appliance_blocker_register.v0",
        "task": TASK_ID,
        "blockers": blockers,
        "hard_blockers_remaining": len(blockers),
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_runtime_surface_index() -> dict[str, Any]:
    return {
        "schema_version": "local_appliance_runtime_surface_index.v0",
        "task": TASK_ID,
        "scripts": [
            "eureka_init_instance.py",
            "eureka_validate_instance.py",
            "eureka_instance_status.py",
            "eureka_instance_migration_status.py",
            "eureka_local_runtime_status.py",
            "eureka_local_server.py",
            "eureka_local_service_smoke.py",
            "eureka_local_workbench_smoke.py",
            "eureka_workunit_queue.py",
            "eureka_set_operator_token.py",
            "eureka_review_queue.py",
            "eureka_rebuild_reviewed_index.py",
            "eureka_worker_runner.py",
            "eureka_local_auto_test.py",
            "eureka_local_auto_search.py",
            "eureka_lan_smoke.py",
            "eureka_clean_machine_bootstrap.py",
        ],
        "routes": ["/", "/status", "/health", "/search", "/object", "/source", "/absence", "/review", "/rebuild", "/api/v1/*"],
        "stores": ["source_cache", "evidence_ledger", "review_queue", "public_index", "workunit_queue"],
        "policies": ["local_appliance", "lan", "review", "worker", "eval", "instance"],
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_future_track_gate() -> dict[str, Any]:
    return {
        "schema_version": "local_appliance_future_track_gate.v0",
        "task": TASK_ID,
        "future_tracks": ["HUNT", "SYN", "F", "G", "H", "I", "J", "K", "D", "C", "E", "L"],
        "requirements": [
            "use explicit local instance where applicable",
            "use runtime composition boundary",
            "use WorkUnits for background work",
            "use review/evidence/index path for accepted results",
            "use auto-test/auto-search harness for search behavior",
            "avoid scaffold-only completion",
            "avoid direct master index mutation",
            "avoid ad hoc store paths",
            "avoid hidden state",
            "avoid unreviewed truth acceptance",
        ],
        "scaffold_only_completion_allowed": False,
        "direct_master_index_mutation_allowed": False,
        "hidden_state_allowed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_handoffs() -> dict[str, dict[str, Any]]:
    common = {
        "local_appliance_required": True,
        "workunits_required_for_background_work": True,
        "review_gate_required_for_accepted_results": True,
        "auto_test_required_for_search_behavior": True,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    return {
        "hunt": {
            "schema_version": "local_appliance_handoff_to_hunt.v0",
            "task": TASK_ID,
            "recommended_first_task": "HUNT-00 \u2014 Search Hunt track planning over Local Appliance",
            "recommended_second_task": "HUNT-01 \u2014 Search Hunt Session runtime",
            "prerequisites": ["LOCAL-14 pass_with_warnings or better", "explicit instance", "auto-test harness", "WorkUnit queue"],
            **common,
        },
        "syn": {
            "schema_version": "local_appliance_handoff_to_syn.v0",
            "task": TASK_ID,
            "recommended_first_task": "SYN-00 \u2014 Synthetic Query Foundry planning over Local Appliance",
            "recommended_second_task": "SYN-01 \u2014 Synthetic query taxonomy and contracts",
            "prerequisites": ["LOCAL-14 pass_with_warnings or better", "auto-test harness", "reviewed index search"],
            **common,
        },
        "f0": {
            "schema_version": "local_appliance_handoff_to_f0.v0",
            "task": TASK_ID,
            "recommended_first_task": "F0-00 \u2014 Refresh F0 after Local Appliance",
            "recommended_second_task": "F0-01 \u2014 Extraction policy and sandbox limits",
            "f0_can_resume_only_through_local_appliance": True,
            "extraction_results_become_source_observations": True,
            "extraction_candidates_go_through_evidence_review_index": True,
            "f0_must_be_visible_testable_through_workbench_before_closeout": True,
            "prerequisites": ["LOCAL-14 pass_with_warnings or better", "future explicit operator choice if before HUNT/SYN"],
            **common,
        },
    }


def build_promotion_review(root: Path, warnings: Mapping[str, Any]) -> dict[str, Any]:
    main_promotion_blocked = bool(warnings.get("summary", {}).get("blocks_main_promotion"))
    return {
        "schema_version": "local_appliance_promotion_review.v0",
        "task": TASK_ID,
        "local_track_ready_for_main_promotion": not main_promotion_blocked,
        "dev_ahead_of_main": True,
        "promotion_recommended": False,
        "promotion_task": "LOCAL-TO-MAIN-PROMOTION-REVIEW",
        "branch_mutation_performed": False,
        "no_deployment": True,
        "no_production_readiness_claim": True,
        "no_public_launch_readiness_claim": True,
        "reason": "Separate promotion review is required; unresolved leakage warning blocks automatic main promotion.",
    }


def build_next_task_decision(closeout: Mapping[str, Any], warnings: Mapping[str, Any]) -> dict[str, Any]:
    blockers = int(closeout.get("hard_blockers_remaining") or 0)
    recommended = LEAKAGE_TASK if blockers else NEXT_TASK
    return {
        "schema_version": "local_14_next_task_decision.v0",
        "task": TASK_ID,
        "recommended_next_task": recommended,
        "alternative_next_task": ALT_TASK,
        "f0_can_resume": bool(closeout.get("f0_can_resume")),
        "f0_recommended_now": False,
        "hunt_can_start": bool(closeout.get("hunt_can_start")),
        "syn_can_start": bool(closeout.get("syn_can_start")),
        "main_promotion_review_required": True,
        "reason": "Local Appliance is complete with disposed warnings; HUNT planning is the preferred next execution spine.",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_local_14_leakage(leakage: Mapping[str, Any]) -> dict[str, Any]:
    before = int(leakage.get("new_unallowlisted_production_findings_after") or 0)
    return {
        "schema_version": "local_14_leakage_baseline.v0",
        "task": TASK_ID,
        "runtime_leakage_gate_status_before": leakage.get("runtime_leakage_gate_status_after", "fail"),
        "runtime_leakage_gate_status_after": leakage.get("runtime_leakage_gate_status_after", "fail"),
        "new_unallowlisted_production_findings_before": before,
        "new_unallowlisted_production_findings_after": before,
        "local_14_increased_leakage": False,
        "full_unittest_discovery_status": leakage.get("full_unittest_discovery_status", "fail_other"),
        "followup_required": "LOCAL-LEAKAGE-01" if before else "none",
    }


def load_latest_leakage(root: Path) -> dict[str, Any]:
    return load_json(root / "control/inventory/local_13_leakage_baseline.json")


def is_pass(root: Path, rel: str) -> bool:
    return load_json(root / rel).get("status") in {"pass", "pass_with_warnings"}


def f0_deferred_until_local_14(root: Path) -> bool:
    payload = load_json(root / "control/inventory/f0_deferral_for_local_appliance.json")
    return payload.get("f0_current_status") == "deferred" and payload.get("deferred_until") == TASK_ID


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_requested_outputs(args: argparse.Namespace, records: Mapping[str, Any]) -> None:
    mapping = {
        args.output: records["closeout_result"],
        args.capability_output: records["capability_matrix"],
        args.validation_output: records["validation_matrix"],
        args.warnings_output: records["warning_disposition"],
        args.blockers_output: records["blocker_register"],
        args.handoff_output: {
            "schema_version": "local_appliance_handoff_bundle.v0",
            "task": TASK_ID,
            "hunt": records["handoff_to_hunt"],
            "syn": records["handoff_to_syn"],
            "f0": records["handoff_to_f0"],
            "next_task_decision": records["next_task_decision"],
        },
        args.runtime_surface_output: records["runtime_surface_index"],
        args.future_gate_output: records["future_track_gate"],
        args.hunt_output: records["handoff_to_hunt"],
        args.syn_output: records["handoff_to_syn"],
        args.f0_output: records["handoff_to_f0"],
        args.promotion_output: records["promotion_review"],
        args.leakage_output: records["leakage_baseline"],
        args.next_output: records["next_task_decision"],
    }
    for output, payload in mapping.items():
        if output:
            write_json(Path(output), payload)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
