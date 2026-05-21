#!/usr/bin/env python3
"""Validate the LOCAL-00 Local Appliance planning track."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

try:
    from local_queue_progress import (
        current_recommended_task,
        latest_packet_current_or_advanced,
        queue_current_or_advanced,
        queue_task_available,
        queue_task_completed,
    )
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports in tests.
    from scripts.local_queue_progress import (
        current_recommended_task,
        latest_packet_current_or_advanced,
        queue_current_or_advanced,
        queue_task_available,
        queue_task_completed,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "LOCAL-00"
NEXT_TASK = "LOCAL-01"
ADVANCED_NEXT_TASK = "LOCAL-02"
F0_TASK = "F0-BUNDLE-01"
LOCAL_CLOSEOUT = "LOCAL-14"

POLICIES = {
    "control/policies/local_appliance_policy.json": "local_appliance_policy.v0",
    "control/policies/local_network_safety_policy.json": "local_network_safety_policy.v0",
    "control/policies/local_agent_workunit_policy.json": "local_agent_workunit_policy.v0",
    "control/policies/future_task_behavior_gate_policy.json": "future_task_behavior_gate_policy.v0",
    "control/policies/local_track_completion_policy.json": "local_track_completion_policy.v0",
}

INVENTORIES = {
    "control/inventory/local_appliance_track_plan.json": "local_appliance_track_plan.v0",
    "control/inventory/local_appliance_readiness_matrix.json": "local_appliance_readiness_matrix.v0",
    "control/inventory/local_appliance_next_task_decision.json": "local_appliance_next_task_decision.v0",
    "control/inventory/f0_deferral_for_local_appliance.json": "f0_deferral_for_local_appliance.v0",
    "control/inventory/future_track_local_appliance_dependency_matrix.json": "future_track_local_appliance_dependency_matrix.v0",
}

DOCS = (
    "docs/architecture/LOCAL_APPLIANCE_MODEL.md",
    "docs/architecture/LOCAL_WORKBENCH_RUNTIME.md",
    "docs/architecture/LOCAL_SERVICE_STORE_WORKER_BOUNDARY.md",
    "docs/operations/LOCAL_APPLIANCE_TRACK.md",
    "docs/operations/LOCAL_NETWORK_SAFETY_POLICY.md",
    "docs/operations/F0_DEFERRAL_FOR_LOCAL_APPLIANCE.md",
    "docs/operations/FUTURE_TASK_BEHAVIOR_GATE.md",
    "docs/operations/LOCAL_TRACK_COMPLETION_STANDARD.md",
)

AUDIT_FILES = (
    "README.md",
    "local_00_report.json",
    "track_plan.md",
    "readiness_matrix.md",
    "f0_deferral.md",
    "future_task_gate.md",
    "validation.md",
    "generated/sample_local_appliance_track_plan.json",
    "generated/sample_readiness_matrix.json",
    "generated/sample_summary.md",
)

AUDIT_ROOT = Path("control/audits/local-00-local-appliance-track-v0")
QUEUE_INDEX = Path(".aide/queue/index.yaml")
TASK_PACKET = Path(".aide/context/latest-task-packet.md")
HEALTH_JSON = Path(".aide/reports/eureka-repo-health.json")

FORBIDDEN_CHANGED_ROOTS = (
    "runtime/",
    "contracts/",
    "surfaces/",
    "site/",
    "native/",
    "crates/",
    "examples/",
    "control/prototypes/",
)

TRACK_SEQUENCE = [
    "LOCAL-00",
    "LOCAL-01",
    "LOCAL-02",
    "LOCAL-03",
    "LOCAL-04",
    "LOCAL-05",
    "LOCAL-06",
    "LOCAL-07",
    "LOCAL-08",
    "LOCAL-09",
    "LOCAL-10",
    "LOCAL-11",
    "LOCAL-12",
    "LOCAL-13",
    "LOCAL-14",
]

CAPABILITIES = {
    "explicit_instance_root",
    "instance_config_schema",
    "runtime_composition_boundary",
    "localhost_read_only_service",
    "html_workbench",
    "object_source_absence_pages",
    "workunit_queue",
    "review_rebuild_ui",
    "deterministic_worker_runner",
    "auto_search_eval_harness",
    "lan_safety_policy",
    "lan_read_only_smoke_test",
    "clean_machine_bootstrap",
    "local_appliance_closeout",
}

FUTURE_TRACKS = {"HUNT", "SYN", "F", "G", "H", "I", "J", "K", "D", "C", "E", "L"}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-00 Local Appliance track validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel, schema in {**POLICIES, **INVENTORIES}.items():
        payloads[rel] = load_json(root / rel, schema, errors)
    report = load_json(root / AUDIT_ROOT / "local_00_report.json", "local_00_report.v0", errors)
    validate_audit_pack(root, errors)
    validate_track_plan(payloads.get("control/inventory/local_appliance_track_plan.json", {}), errors)
    validate_readiness(payloads.get("control/inventory/local_appliance_readiness_matrix.json", {}), errors)
    validate_f0_deferral(payloads.get("control/inventory/f0_deferral_for_local_appliance.json", {}), errors)
    validate_dependency_matrix(payloads.get("control/inventory/future_track_local_appliance_dependency_matrix.json", {}), errors)
    validate_policies(payloads, errors)
    validate_report(report, errors)
    validate_queue_and_context(root, errors)
    validate_health(root, errors)
    validate_git_alignment(root, report, errors, warnings)
    validate_scope(root, errors)
    return {
        "schema_version": "local_appliance_track_validation.v0",
        "task": TASK_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "main_dev_aligned": report.get("main_dev_aligned"),
        "current_queue_item": report.get("current_queue_item"),
        "f0_deferred": report.get("f0_deferred"),
        "lan_enabled": report.get("lan_enabled"),
        "server_implemented": report.get("server_implemented"),
        "html_workbench_implemented": report.get("html_workbench_implemented"),
        "deployment_performed": report.get("deployment_performed"),
        "production_readiness_claimed": report.get("production_readiness_claimed"),
        "public_launch_readiness_claimed": report.get("public_launch_readiness_claimed"),
    }


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {relpath(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {relpath(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain an object: {relpath(path)}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema_version mismatch for {relpath(path)}")
    return payload


def validate_audit_pack(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_ROOT / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_ROOT / rel).as_posix()}")
        elif path.stat().st_size == 0:
            errors.append(f"empty audit file: {(AUDIT_ROOT / rel).as_posix()}")


def validate_track_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    entries = plan.get("track")
    if not isinstance(entries, list):
        errors.append("track plan must contain a track list")
        return
    ids = [entry.get("task_id") for entry in entries if isinstance(entry, Mapping)]
    if ids != TRACK_SEQUENCE:
        errors.append("Local Appliance task sequence is not exact")
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"track entry {index} must be an object")
            continue
        for key in ("task_id", "purpose", "proof_level_required", "required_runtime_behavior", "required_tests", "forbidden_side_effects", "next_task"):
            if key not in entry:
                errors.append(f"track entry {entry.get('task_id', index)} missing {key}")


def validate_readiness(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("capabilities")
    if not isinstance(rows, list):
        errors.append("readiness matrix must contain capabilities list")
        return
    seen = set()
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("readiness row must be an object")
            continue
        capability = row.get("capability")
        seen.add(capability)
        if row.get("status") not in {"missing", "planned", "implemented", "tested", "blocked"}:
            errors.append(f"invalid readiness status for {capability}")
        for key in ("required_before_f0", "required_before_lan", "required_before_public_hosting"):
            if not isinstance(row.get(key), bool):
                errors.append(f"readiness row {capability} missing boolean {key}")
    missing = CAPABILITIES - seen
    if missing:
        errors.append(f"readiness matrix missing capabilities: {sorted(missing)}")


def validate_f0_deferral(deferral: Mapping[str, Any], errors: list[str]) -> None:
    if deferral.get("f0_previous_status") != "resume_allowed":
        errors.append("F0 previous status must be resume_allowed")
    if deferral.get("f0_current_status") != "deferred":
        errors.append("F0 current status must be deferred")
    if deferral.get("deferred_until") != LOCAL_CLOSEOUT:
        errors.append("F0 must be deferred until LOCAL-14")
    if deferral.get("f0_must_use_local_appliance") is not True:
        errors.append("F0 must use local appliance")
    if deferral.get("f0_must_not_create_scaffold_only_work") is not True:
        errors.append("F0 scaffold-only guard missing")
    validate_false_claims(deferral, "F0 deferral", errors)


def validate_dependency_matrix(matrix: Mapping[str, Any], errors: list[str]) -> None:
    rows = matrix.get("tracks")
    if not isinstance(rows, list):
        errors.append("dependency matrix must contain tracks list")
        return
    seen = {row.get("track") for row in rows if isinstance(row, Mapping)}
    missing = FUTURE_TRACKS - seen
    if missing:
        errors.append(f"dependency matrix missing tracks: {sorted(missing)}")
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("dependency matrix row must be an object")
            continue
        for key in (
            "local_appliance_dependency",
            "required_workbench_capabilities",
            "required_store_capabilities",
            "required_worker_capabilities",
            "required_eval_capabilities",
            "can_start_before_LOCAL_14",
            "notes",
        ):
            if key not in row:
                errors.append(f"dependency row {row.get('track')} missing {key}")


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    appliance = payloads.get("control/policies/local_appliance_policy.json", {})
    network = payloads.get("control/policies/local_network_safety_policy.json", {})
    agent = payloads.get("control/policies/local_agent_workunit_policy.json", {})
    future = payloads.get("control/policies/future_task_behavior_gate_policy.json", {})
    completion = payloads.get("control/policies/local_track_completion_policy.json", {})
    expected_true = {
        "localhost_default": appliance,
        "read_only_default": appliance,
        "explicit_instance_path_required": appliance,
        "hidden_state_roots_forbidden": appliance,
        "committed_instance_state_forbidden": appliance,
        "no_deployment": appliance,
        "no_production_readiness_claim": appliance,
        "no_public_launch_readiness_claim": appliance,
        "lan_requires_explicit_flag": network,
        "agents_execute_workunits_only": agent,
        "agent_effects_must_be_typed_store_outputs": agent,
        "product_tasks_must_prove_runtime_behavior": future,
        "future_tracks_must_integrate_local_appliance_where_applicable": future,
        "warning_debt_must_be_disposed_before_advancing": future,
    }
    for key, payload in expected_true.items():
        if payload.get(key) is not True:
            errors.append(f"policy flag must be true: {key}")
    expected_false = {
        "lan_binding_default": appliance,
        "agents_may_accept_truth": agent,
        "agents_may_mutate_public_index_directly": agent,
        "agents_may_mutate_master_index": agent,
        "agents_may_broad_crawl_by_default": agent,
        "agents_may_download_packages": agent,
        "agents_may_install_packages": agent,
        "agents_may_execute_packages": agent,
        "model_provider_agents_enabled": agent,
        "contracts_policies_examples_alone_are_sufficient": future,
        "validators_alone_are_sufficient": future,
        "scaffold_only_product_completion_allowed": future,
    }
    for key, payload in expected_false.items():
        if payload.get(key) is not False:
            errors.append(f"policy flag must be false: {key}")
    if network.get("read_only_default") is not True or network.get("lan_binding_default") is not False:
        errors.append("LAN policy must default to read-only and disabled")
    required_levels = completion.get("required_task_levels", {})
    for task in ("LOCAL-01", "LOCAL-02", "LOCAL-03", "LOCAL-04", "LOCAL-05", "LOCAL-07", "LOCAL-08", "LOCAL-10", "LOCAL-12", "LOCAL-13", "LOCAL-14"):
        if task not in required_levels:
            errors.append(f"missing proof level for {task}")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("status") not in {"pass", "pass_with_warnings", "partial", "blocked", "fail"}:
        errors.append("LOCAL-00 report status is invalid")
    if report.get("main_dev_aligned") is not True:
        errors.append("main/dev alignment must be recorded true")
    if report.get("f0_deferred") is not True or report.get("f0_deferred_until") != LOCAL_CLOSEOUT:
        errors.append("LOCAL-00 report must defer F0 until LOCAL-14")
    if report.get("current_queue_item") != NEXT_TASK:
        errors.append("LOCAL-00 report current queue item must be LOCAL-01")
    for key in (
        "runtime_modified",
        "contracts_modified",
        "server_implemented",
        "html_workbench_implemented",
        "workunit_runtime_implemented",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            errors.append(f"LOCAL-00 report must set {key}=false")


def validate_queue_and_context(root: Path, errors: list[str]) -> None:
    queue_text = read_text(root / QUEUE_INDEX, errors)
    packet_text = read_text(root / TASK_PACKET, errors)
    queue_current = current_recommended_task(root)
    queue_points_to_local_01 = queue_current == NEXT_TASK
    queue_points_to_local_02 = queue_current == ADVANCED_NEXT_TASK
    queue_points_to_later_handoff = local_track_handoff_queue(queue_current)
    if not (
        queue_points_to_local_01
        or queue_points_to_local_02
        or queue_points_to_later_handoff
        or queue_current_or_advanced(root, TASK_ID, NEXT_TASK)
    ):
        errors.append("queue index must point to LOCAL-01 or the completed LOCAL-01 successor LOCAL-02")
    if not queue_task_completed(root, TASK_ID) or not queue_task_available(root, NEXT_TASK) or not queue_task_available(root, ADVANCED_NEXT_TASK):
        errors.append("queue index must include LOCAL-00, LOCAL-01, and LOCAL-02")
    if queue_points_to_local_02 and "id: LOCAL-01" in queue_text and "status: completed" not in queue_text:
        errors.append("queue index must mark LOCAL-01 completed before pointing to LOCAL-02")
    if F0_TASK not in queue_text or "deferred_until: LOCAL-14" not in queue_text:
        errors.append("queue index must record F0 deferral until LOCAL-14")
    if queue_points_to_local_01 and NEXT_TASK not in packet_text:
        errors.append("latest task packet must point to LOCAL-01")
    if queue_points_to_local_02 and ADVANCED_NEXT_TASK not in packet_text:
        errors.append("latest task packet must point to LOCAL-02 after LOCAL-01 completes")
    if (
        not (queue_points_to_local_01 or queue_points_to_local_02)
        and not (queue_points_to_later_handoff and latest_packet_is_later_control_or_handoff(packet_text))
        and not latest_packet_current_or_advanced(root, TASK_ID, NEXT_TASK)
    ):
        errors.append("latest task packet must point to the active advanced queue item")
    if "<fill from the next reviewed queue packet>" in packet_text:
        errors.append("latest task packet still contains placeholder allowed paths")


def validate_health(root: Path, errors: list[str]) -> None:
    health = load_json(root / HEALTH_JSON, "eureka_repo_health.v0", errors)
    health_current = health.get("current_queue_item")
    health_recommended = (
        health.get("current_recommended_queue_item")
        or health.get("next_recommended_queue_item")
        or health.get("current_recommended_task")
    )
    queue_current = current_recommended_task(root)
    if health_current not in {NEXT_TASK, ADVANCED_NEXT_TASK} and not (health_recommended == queue_current and queue_task_completed(root, TASK_ID)):
        errors.append("repo health current_queue_item must be LOCAL-01 or completed successor LOCAL-02")
    f0_status = health.get("f0_current_status")
    if f0_status is None and health.get("f0_can_resume") is True:
        f0_status = "resumable_through_local_appliance"
    if f0_status not in {"deferred", "resumable_through_local_appliance", "implemented_pending_full_closeout", "completed"}:
        errors.append("repo health must record F0 deferred")
    if health.get("f0_deferred_until") not in {LOCAL_CLOSEOUT, None} and f0_status not in {
        "resumable_through_local_appliance",
        "implemented_pending_full_closeout",
        "completed",
    }:
        errors.append("repo health must record F0 deferred until LOCAL-14")
    false_keys = {
        "production_readiness": health.get("production_readiness", health.get("production_readiness_claimed")),
        "public_launch_readiness": health.get("public_launch_readiness", health.get("public_launch_readiness_claimed")),
        "deployment_performed": health.get("deployment_performed"),
        "lan_enabled": health.get("lan_enabled", False),
    }
    for key, value in false_keys.items():
        if value is not False:
            errors.append(f"repo health must set {key}=false")


def local_track_handoff_queue(queue_current: str | None) -> bool:
    if not queue_current:
        return False
    if queue_current.startswith("AIDE-"):
        return True
    handoff_tasks = {
        "SYN-00",
        "DOMAIN-00",
        "SCOUT-SCHEMA-00",
        "F0-00",
        "G0",
        "HUNT-REMEDIATION",
        "HUNT-REMEDIATION-CONTINUE",
        "HUNT-TO-MAIN-PROMOTION-REVIEW",
        "DEV-AND-IA-PROMOTION-BLOCKER-01",
        "DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW",
        "IA-HUNT-BRIDGE-00",
        "SOURCE-WAVE-00",
        "SNAPSHOT-RELAY-00",
    }
    return any(queue_current == task or queue_current.startswith(f"{task} ") for task in handoff_tasks)


def latest_packet_is_later_control_or_handoff(packet_text: str) -> bool:
    markers = (
        "AIDE-",
        "HUNT-",
        "DEV-AND-IA-",
        "IA-HUNT-",
        "SYN-",
        "DOMAIN-",
        "SCOUT-",
        "F0-",
        "G0",
        "SOURCE-WAVE-",
        "SNAPSHOT-RELAY-",
    )
    return any(marker in packet_text for marker in markers)


def validate_git_alignment(root: Path, report: Mapping[str, Any], errors: list[str], warnings: list[str]) -> None:
    if local_track_handoff_queue(current_recommended_task(root)):
        return
    main = git(root, "rev-parse", "origin/main")
    dev = git(root, "rev-parse", "origin/dev")
    if main and dev:
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "origin/main", "origin/dev"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if ancestor.returncode != 0:
            errors.append("origin/dev must contain origin/main")
        elif main != dev and current_recommended_task(root) not in {
            "SYN-00",
            "DOMAIN-00",
            "SCOUT-SCHEMA-00",
            "F0-00",
            "G0",
            "HUNT-REMEDIATION",
            "HUNT-TO-MAIN-PROMOTION-REVIEW",
            "DEV-AND-IA-PROMOTION-BLOCKER-01",
            "DEV-AND-IA-TO-MAIN-PROMOTION-REVIEW",
            "IA-HUNT-BRIDGE-00",
            "SOURCE-WAVE-00",
            "SNAPSHOT-RELAY-00",
        }:
            warnings.append("origin/dev is ahead of origin/main after Local Appliance queue work")
    else:
        warnings.append("could not verify origin/main and origin/dev alignment")
    if report.get("main_dev_aligned") is not True:
        errors.append("report does not record main/dev alignment")


def validate_scope(root: Path, errors: list[str]) -> None:
    if local_track_handoff_queue(current_recommended_task(root)):
        return
    status = git(root, "status", "--porcelain=v1")
    for path in parse_status_paths(status.splitlines() if status else []):
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in FORBIDDEN_CHANGED_ROOTS):
            errors.append(f"forbidden product path changed: {path}")


def validate_false_claims(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    for key in ("production_readiness_claimed", "public_launch_readiness_claimed"):
        if payload.get(key) is not False:
            errors.append(f"{label} must set {key}=false")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing text file: {relpath(path)}")
        return ""


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def parse_status_paths(lines: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        if " -> " in raw:
            paths.extend(part.strip('"') for part in raw.split(" -> "))
        else:
            paths.append(raw)
    return paths


def relpath(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
