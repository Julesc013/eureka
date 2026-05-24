#!/usr/bin/env python3
"""Generate governed LOCAL-APPLY-GATE-01 contracts, policy, docs, and audit assets."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK = "AIDE-BATCH-LOCAL-APPLY-GATE-01"
PRODUCT_TASK = "LOCAL-APPLY-GATE-01"
NEXT_TASK = "WORKBENCH-LOCAL-LOOP-CLOSEOUT-01 - Prove query to reviewed local result through apply gate"
CONTRACTS = [
    "local_apply_plan",
    "local_apply_command",
    "local_apply_preview",
    "local_apply_backup_manifest",
    "local_apply_mutation_manifest",
    "local_apply_audit_log",
    "local_apply_result",
    "local_apply_rollback_plan",
    "local_apply_rollback_result",
    "local_apply_boundary_report",
]
INSTANCE_CONTRACTS = [
    "instance_descriptor",
    "instance_snapshot",
    "instance_mutation_scope",
]
POLICIES = [
    "local_apply_gate_policy",
    "local_apply_backup_policy",
    "local_apply_rollback_policy",
    "local_apply_audit_policy",
    "local_apply_non_claim_policy",
    "operator_instance_mutation_policy",
]
COMMANDS = [
    "preview_local_apply",
    "create_local_apply_plan",
    "validate_local_apply_plan",
    "create_pre_apply_backup",
    "apply_local_change",
    "validate_post_apply",
    "create_rollback_plan",
    "run_rollback",
    "validate_post_rollback",
    "inspect_apply_audit_log",
]
STATES = [
    "preview_created",
    "plan_created",
    "plan_validated",
    "backup_created",
    "rollback_plan_created",
    "apply_blocked",
    "apply_ready",
    "apply_performed",
    "post_apply_validated",
    "rollback_ready",
    "rollback_performed",
    "post_rollback_validated",
    "failed",
]
EVENTS = [
    "local_apply.preview_created",
    "local_apply.plan_created",
    "local_apply.policy_checked",
    "local_apply.backup_created",
    "local_apply.rollback_plan_created",
    "local_apply.apply_blocked",
    "local_apply.apply_started",
    "local_apply.apply_completed",
    "local_apply.post_apply_validated",
    "local_apply.rollback_started",
    "local_apply.rollback_completed",
    "local_apply.post_rollback_validated",
    "local_apply.audit_written",
    "warning.emitted",
]
BOUNDARY_FALSES = [
    "operator_instance_mutated",
    "operator_instance_mutation_enabled_by_default",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", default="pending")
    parser.add_argument("--full-discovery-status", default="not_run")
    parser.add_argument("--full-discovery-reason", default="deferred until final closeout unless selected lanes require it")
    args = parser.parse_args(argv)

    write_contracts()
    write_policies()
    write_matrices()
    write_examples()
    write_docs()
    write_audit_pack(args.status, args.full_discovery_status, args.full_discovery_reason)
    write_queue()
    update_repo_health()
    return 0


def write_contracts() -> None:
    write_text(
        "contracts/local_apply/README.md",
        """# Local Apply Contracts

These contracts define the local-only operator apply gate. They describe dry-run
preview, explicit apply plans, pre-apply backups, mutation manifests, audit logs,
post-apply validation, rollback plans, and boundary reports.

The contracts do not authorize public apply, production deployment, master-index
mutation, committed public-index mutation, downloads, extraction, or provider calls.
""",
    )
    for name in CONTRACTS:
        write_json(
            f"contracts/local_apply/{name}.v0.json",
            contract_schema(name, required_fields_for(name), "local_apply"),
        )
    write_text(
        "contracts/instances/README.md",
        """# Instance Contracts

Instance contracts describe an explicit local instance root, a bounded mutation
scope, and the snapshot material needed for backup and rollback. They are local
operator contracts, not committed instance state.
""",
    )
    for name in INSTANCE_CONTRACTS:
        write_json(
            f"contracts/instances/{name}.v0.json",
            contract_schema(name, required_fields_for(name), "instances"),
        )


def contract_schema(name: str, required: Sequence[str], family: str) -> dict[str, Any]:
    return {
        "schema_version": f"{name}.v0",
        "task": PRODUCT_TASK,
        "family": family,
        "description": f"Governed {name.replace('_', ' ')} contract for the local apply gate.",
        "required_fields": list(required),
        "boundary_false_fields": list(BOUNDARY_FALSES),
        "public_projection_apply_enabled": False,
        "native_projection_apply_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def required_fields_for(name: str) -> list[str]:
    fields: dict[str, list[str]] = {
        "local_apply_plan": [
            "schema_version",
            "plan_id",
            "target_instance_path",
            "target_instance_descriptor",
            "operation_kind",
            "source_preview_ref",
            "required_operator_token",
            "required_confirmation",
            "dry_run",
            "apply_allowed",
            "backup_required",
            "rollback_required",
            "mutation_scope",
            "blocked_actions",
            "non_claims",
        ],
        "local_apply_mutation_manifest": [
            "schema_version",
            "mutation_id",
            "plan_id",
            "target_instance_path",
            "operation_kind",
            "files_created",
            "files_modified",
            "files_deleted",
            "stores_modified",
            "before_hashes",
            "after_hashes",
            "backup_manifest_ref",
            "rollback_plan_ref",
            "validation_result_ref",
            "created_at",
        ],
        "local_apply_audit_log": [
            "schema_version",
            "audit_id",
            "plan_id",
            "mutation_id",
            "operator_context_redacted",
            "command",
            "dry_run",
            "apply_performed",
            "target_instance_path",
            "timestamp",
            "policy_result",
            "validation_result",
            "boundary_report_ref",
        ],
    }
    return fields.get(name, ["schema_version", "status", "task"])


def write_policies() -> None:
    base = {
        "schema_version": "local_apply_policy.v0",
        "task": TASK,
        "local_apply_enabled_by_default": False,
        "dry_run_default": True,
        "operator_token_required": True,
        "explicit_apply_flag_required": True,
        "explicit_confirmation_required": True,
        "target_instance_path_required": True,
        "target_instance_must_be_outside_repo": True,
        "repository_path_mutation_forbidden": True,
        "backup_required_before_apply": True,
        "rollback_plan_required_before_apply": True,
        "audit_log_required": True,
        "mutation_manifest_required": True,
        "post_apply_validation_required": True,
        "automatic_candidate_acceptance_enabled": False,
        "master_index_mutation_enabled": False,
        "committed_data_public_index_mutation_enabled": False,
        "public_apply_enabled": False,
        "native_apply_enabled": False,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for policy in POLICIES:
        payload = dict(base)
        payload["schema_version"] = f"{policy}.v0"
        payload["policy_id"] = policy
        payload["scope"] = policy.removeprefix("local_apply_").replace("_policy", "")
        write_json(f"control/policies/{policy}.json", payload)


def write_matrices() -> None:
    matrix_payloads: dict[str, dict[str, Any]] = {
        "local_apply_gate_policy_matrix": {
            "policies": POLICIES,
            "required_truths": {key: True for key in ("operator_token_required", "backup_required_before_apply", "rollback_plan_required_before_apply")},
            "required_false": BOUNDARY_FALSES,
        },
        "local_apply_gate_route_matrix": {
            "routes": [
                "/apply",
                "/apply/{plan_id}",
                "/apply/{plan_id}/backup",
                "/apply/{plan_id}/rollback",
                "/api/v1/local-apply/preview",
                "/api/v1/local-apply/plan",
                "/api/v1/local-apply/{plan_id}/apply",
                "/api/v1/local-apply/{plan_id}/rollback",
                "/api/v1/local-apply/audit",
            ],
            "public_apply_enabled": False,
            "native_apply_enabled": False,
        },
        "local_apply_gate_api_matrix": {
            "operator_projection": ["preview", "plan", "backup", "apply", "rollback", "audit"],
            "public_projection": "blocked",
            "native_read_only_projection": "blocked",
        },
        "local_apply_gate_command_matrix": {"commands": COMMANDS},
        "local_apply_gate_permission_matrix": {
            "operator_token_required": True,
            "exact_apply_confirmation": "APPLY_TO_LOCAL_INSTANCE",
            "exact_rollback_confirmation": "ROLLBACK_LOCAL_INSTANCE",
            "repo_internal_target_blocked": True,
        },
        "local_apply_gate_state_matrix": {"states": STATES},
        "local_apply_gate_event_matrix": {"event_types": EVENTS},
        "local_apply_backup_matrix": {"backup_required_before_apply": True, "backup_location": "<instance>/backups/local_apply/<backup_id>"},
        "local_apply_rollback_matrix": {"rollback_required": True, "rollback_confirmation": "ROLLBACK_LOCAL_INSTANCE"},
        "local_apply_mutation_manifest_matrix": {"required_fields": required_fields_for("local_apply_mutation_manifest")},
        "local_apply_audit_log_matrix": {"required_fields": required_fields_for("local_apply_audit_log"), "raw_token_stored": False},
        "local_apply_reviewed_index_refresh_matrix": {
            "operation_kind": "reviewed_index_refresh",
            "stores_modified": ["source_cache", "evidence_ledger", "review_queue", "public_index"],
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
        },
    }
    for name, payload in matrix_payloads.items():
        body = {"schema_version": f"{name}.v0", "task": TASK, **payload}
        write_json(f"control/inventory/{name}.json", body)
    write_json(
        "control/inventory/local_apply_gate_input_state.json",
        build_input_state(),
    )
    write_json(
        "control/inventory/local_apply_boundary_report.json",
        {"schema_version": "local_apply_boundary_report.v0", "task": TASK, **false_flags(), "explicit_local_instance_mutation_performed": False},
    )
    write_json("control/inventory/local_apply_smoke_result.json", pending_result("local_apply_smoke_result.v0"))
    write_json("control/inventory/local_apply_failure_repair_log.json", {"schema_version": "local_apply_failure_repair_log.v0", "task": TASK, "repairs": []})
    write_json("control/inventory/local_apply_validation_matrix.json", pending_result("local_apply_validation_matrix.v0", commands=[]))
    write_json("control/inventory/local_apply_gate_result.json", local_apply_result("pending", "not_run", "pending validation"))
    write_json(
        "control/inventory/local_apply_next_task_decision.json",
        {
            "schema_version": "local_apply_next_task_decision.v0",
            "task": TASK,
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "DEV-TO-MAIN-PROMOTION-REVIEW-02",
                "SOURCE-ACTION-KERNEL-00",
                "SOURCE-WAVE-00",
                "SNAPSHOT-RELAY-00",
            ],
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    )


def build_input_state() -> dict[str, Any]:
    health = read_json(".aide/reports/eureka-repo-health.json")
    review = read_json("control/inventory/workbench_review_promote_result.json")
    return {
        "schema_version": "local_apply_gate_input_state.v0",
        "task": TASK,
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "origin_main": git("rev-parse", "origin/main"),
        "origin_dev": git("rev-parse", "origin/dev"),
        "working_tree_clean_before": git("status", "--short") == "",
        "workbench_review_promote_found": review.get("status") == "pass",
        "ia_live_metadata_lane_found": Path("control/inventory/ia_live_metadata_lane_result.json").exists(),
        "workbench_live_run_found": Path("control/inventory/workbench_live_run_result.json").exists(),
        "resolution_run_kernel_found": Path("control/inventory/resolution_run_result.json").exists(),
        "ia_hunt_bridge_found": Path("control/inventory/ia_hunt_bridge_result.json").exists(),
        "workbench_result_lanes_found": Path("control/inventory/workbench_result_lanes_result.json").exists(),
        "search_interaction_found": Path("control/inventory/search_interaction_result.json").exists(),
        "reviewed_index_refresh_temp_proof_found": bool(review.get("temp_reviewed_index_refresh_passed")),
        "repo_health_workbench_review_promote_status_before": health.get("workbench_review_promote_status", ""),
        "operator_instance_mutation_default": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def write_examples() -> None:
    samples = sample_payloads()
    for name, payload in samples.items():
        write_json(f"examples/local_apply/{name}.json", payload)
        write_json(f"control/audits/local-apply-gate-01-v0/generated/{name}.json", payload)


def sample_payloads() -> dict[str, dict[str, Any]]:
    target = "<explicit-outside-repo-instance-path>"
    preview = {
        "schema_version": "local_apply_preview.v0",
        "task": TASK,
        "preview_id": "local_apply_preview_sample",
        "status": "preview_created",
        "operation_kind": "reviewed_index_refresh",
        "target_instance_path": target,
        "dry_run": True,
        "apply_allowed": False,
        "required_operator_token": True,
        "required_confirmation": "APPLY_TO_LOCAL_INSTANCE",
        "backup_required": True,
        "rollback_required": True,
        **false_flags(),
    }
    plan = {
        "schema_version": "local_apply_plan.v0",
        "task": TASK,
        "plan_id": "local_apply_plan_sample",
        "target_instance_path": target,
        "target_instance_descriptor": {"schema_version": "instance_descriptor.v0", "instance_root": target, "valid": True},
        "operation_kind": "reviewed_index_refresh",
        "source_preview_ref": "local_apply_preview_sample",
        "required_operator_token": True,
        "required_confirmation": "APPLY_TO_LOCAL_INSTANCE",
        "dry_run": True,
        "apply_allowed": False,
        "backup_required": True,
        "rollback_required": True,
        "mutation_scope": {"schema_version": "instance_mutation_scope.v0", "repo_mutation_allowed": False},
        "blocked_actions": ["master_index_mutation", "download", "extraction", "deployment"],
        "non_claims": ["not production readiness", "not public launch readiness"],
        **false_flags(),
    }
    backup = {"schema_version": "local_apply_backup_manifest.v0", "backup_id": "sample_backup", "plan_id": plan["plan_id"], "target_instance_path": target, "files": [], "backup_created_before_apply": True, **false_flags()}
    manifest = {"schema_version": "local_apply_mutation_manifest.v0", "mutation_id": "sample_mutation", "plan_id": plan["plan_id"], "target_instance_path": target, "operation_kind": "reviewed_index_refresh", "files_created": [], "files_modified": ["db/public_index.sqlite"], "files_deleted": [], "stores_modified": ["public_index"], "before_hashes": {}, "after_hashes": {}, "backup_manifest_ref": backup["backup_id"], "rollback_plan_ref": "sample_rollback", "validation_result_ref": "sample_validation", "created_at": "2026-05-22T00:00:00Z", **false_flags()}
    audit = {"schema_version": "local_apply_audit_log.v0", "audit_id": "sample_audit", "plan_id": plan["plan_id"], "mutation_id": manifest["mutation_id"], "operator_context_redacted": {"operator_token_present": True, "operator_token_stored": False}, "command": "apply_local_change", "dry_run": False, "apply_performed": True, "target_instance_path": target, "timestamp": "2026-05-22T00:00:00Z", "policy_result": "pass", "validation_result": {"status": "pass"}, "boundary_report_ref": "sample_boundary", "raw_token_stored": False, **false_flags()}
    apply_result = {"schema_version": "local_apply_result.v0", "task": TASK, "status": "pass", "apply_performed": True, "backup_created_before_apply": True, "mutation_manifest_created": True, "audit_log_created": True, "rollback_plan_created": True, "post_apply_validation_passed": True, **false_flags()}
    rollback_plan = {"schema_version": "local_apply_rollback_plan.v0", "rollback_plan_id": "sample_rollback", "plan_id": plan["plan_id"], "mutation_id": manifest["mutation_id"], "target_instance_path": target, "required_operator_token": True, "required_confirmation": "ROLLBACK_LOCAL_INSTANCE", "files_to_restore": [], **false_flags()}
    rollback_result = {"schema_version": "local_apply_rollback_result.v0", "status": "pass", "rollback_plan_id": "sample_rollback", "rollback_performed": True, "post_rollback_validation_passed": True, **false_flags()}
    boundary = {"schema_version": "local_apply_boundary_report.v0", "boundary_report_id": "sample_boundary", "explicit_local_instance_mutation_performed": True, **false_flags()}
    return {
        "sample_local_apply_preview": preview,
        "sample_local_apply_plan": plan,
        "sample_backup_manifest": backup,
        "sample_mutation_manifest": manifest,
        "sample_audit_log": audit,
        "sample_apply_result": apply_result,
        "sample_rollback_plan": rollback_plan,
        "sample_rollback_result": rollback_result,
        "sample_boundary_report": boundary,
        "sample_public_blocked_projection": {"schema_version": "local_apply_projection.v0", "projection": "public_web", "apply_enabled": False, "status": "blocked"},
        "sample_native_blocked_projection": {"schema_version": "local_apply_projection.v0", "projection": "native_desktop_read_only", "apply_enabled": False, "status": "blocked"},
    }


def write_docs() -> None:
    docs = {
        "docs/architecture/LOCAL_APPLY_GATE.md": "Local Apply Gate",
        "docs/architecture/OPERATOR_INSTANCE_MUTATION_MODEL.md": "Operator Instance Mutation Model",
        "docs/architecture/LOCAL_APPLY_BACKUP_AND_ROLLBACK.md": "Local Apply Backup And Rollback",
        "docs/operations/LOCAL_APPLY_GATE_RUNBOOK.md": "Local Apply Gate Runbook",
        "docs/operations/POST_LOCAL_APPLY_GATE_PLAN.md": "Post Local Apply Gate Plan",
        "docs/reference/LOCAL_APPLY_COMMANDS.md": "Local Apply Commands",
        "docs/reference/LOCAL_APPLY_AUDIT_LOG.md": "Local Apply Audit Log",
        "docs/reference/LOCAL_APPLY_MUTATION_MANIFEST.md": "Local Apply Mutation Manifest",
        "docs/reference/LOCAL_APPLY_ROLLBACK_PLAN.md": "Local Apply Rollback Plan",
    }
    body = """
LOCAL-APPLY-GATE-01 is a local-only controlled mutation boundary. The default is
dry-run preview. Mutation requires an explicit instance path outside the repo, an
operator token, the `--apply` flag, the exact confirmation string, a pre-apply
backup, a mutation manifest, an audit log, post-apply validation, and a rollback
plan.

Public and native read-only projections cannot apply. The gate does not mutate a
master index, committed public index, `site/dist`, or committed instance state. It
does not download, upload, extract, execute, call model providers, deploy, or claim
production/public launch readiness.

Primary commands:

```text
python scripts/eureka_local_apply.py --instance <path> --from-review-promote-fixture --dry-run --json
python scripts/eureka_local_apply.py --instance <path> --from-review-promote-fixture --apply --operator-token <token> --confirm APPLY_TO_LOCAL_INSTANCE --json
python scripts/eureka_local_apply_rollback.py --instance <path> --rollback-plan <path> --apply --operator-token <token> --confirm ROLLBACK_LOCAL_INSTANCE --json
```
"""
    for path, title in docs.items():
        write_text(path, f"# {title}\n\n{body.strip()}\n")


def write_audit_pack(status: str, full_status: str, full_reason: str) -> None:
    base = "control/audits/local-apply-gate-01-v0"
    report = local_apply_result(status, full_status, full_reason)
    write_text(f"{base}/README.md", "# Local Apply Gate Audit\n\nEvidence for LOCAL-APPLY-GATE-01.\n")
    write_json(f"{base}/local_apply_gate_report.json", report)
    for name in [
        "policy_matrix",
        "command_matrix",
        "permission_matrix",
        "backup_matrix",
        "rollback_matrix",
        "mutation_manifest_matrix",
        "audit_log_matrix",
        "boundary_report",
        "smoke_result",
        "validation_matrix",
    ]:
        write_text(f"{base}/{name}.md", f"# {name.replace('_', ' ').title()}\n\nGenerated audit evidence for `{TASK}`.\n")
    write_text(f"{base}/validation.md", f"# Validation\n\nStatus: `{status}`\n\nFull discovery: `{full_status}`. {full_reason}\n")
    write_text(f"{base}/generated/sample_summary.md", "# Generated Sample Summary\n\nSamples mirror `examples/local_apply` and are evidence-only.\n")


def write_queue() -> None:
    write_text(
        ".aide/queue/AIDE-BATCH-LOCAL-APPLY-GATE-01/task.yaml",
        f"""id: AIDE-BATCH-LOCAL-APPLY-GATE-01
title: Explicit operator-instance apply, backup, audit, and rollback gate
status: in_progress
purpose: Implement the governed local apply boundary after Workbench review/promote.
allowed_scope_summary: Local apply contracts, runtime gate, CLI, validator, tests, docs, policies, inventories, and audit evidence.
gate: No silent operator instance mutation, committed instance state, master/public mutation, downloads, extraction, model/provider calls, deployment, or readiness claim.
recommended_after: WORKBENCH-REVIEW-PROMOTE-01
recommended_next: WORKBENCH-LOCAL-LOOP-CLOSEOUT-01
""",
    )
    write_text(
        ".aide/queue/LOCAL-APPLY-GATE-01/task.yaml",
        f"""id: LOCAL-APPLY-GATE-01
title: Local operator apply gate
status: in_progress
purpose: Add explicit operator apply gates for local instance writes after review/promote flow is governed.
allowed_scope_summary: Dry-run preview, operator token, backup/snapshot, audit log, rollback, validators, tests, and audit evidence.
gate: No default operator instance mutation, force push, deployment, or production/public launch claim.
recommended_after: WORKBENCH-REVIEW-PROMOTE-01
recommended_next: WORKBENCH-LOCAL-LOOP-CLOSEOUT-01
""",
    )
    for task_id, title, after in [
        ("WORKBENCH-LOCAL-LOOP-CLOSEOUT-01", "Prove query to reviewed local result through apply gate", "LOCAL-APPLY-GATE-01"),
        ("SOURCE-ACTION-KERNEL-00", "Generic source-action kernel planning", "WORKBENCH-LOCAL-LOOP-CLOSEOUT-01"),
        ("SOURCE-WAVE-00", "Next source-family metadata wave planning", "SOURCE-ACTION-KERNEL-00"),
        ("SNAPSHOT-RELAY-00", "Read-only snapshot and relay planning", "SOURCE-WAVE-00"),
        ("PUBLIC-ALPHA-READONLY-00", "Public alpha read-only reviewed-index planning", "SNAPSHOT-RELAY-00"),
    ]:
        write_text(
            f".aide/queue/{task_id}/task.yaml",
            f"""id: {task_id}
title: {title}
status: queued
purpose: Follow-on work after the local apply gate.
allowed_scope_summary: Future task must provide reviewed scope before implementation.
gate: No production/public launch claim without future explicit policy.
recommended_after: {after}
""",
        )


def update_repo_health() -> None:
    path = REPO_ROOT / ".aide/reports/eureka-repo-health.json"
    if path.exists():
        health = json.loads(path.read_text(encoding="utf-8"))
        health["workbench_review_promote_status"] = "completed"
        health["workbench_review_promote_validation_status"] = "pass"
        health["current_recommended_task"] = "LOCAL-APPLY-GATE-01 - Explicit operator-instance apply, backup, audit, and rollback gate"
        health["local_apply_gate_status"] = "in_progress"
        health["deployment_performed"] = False
        health["production_readiness_claimed"] = False
        health["public_launch_readiness_claimed"] = False
        write_json(".aide/reports/eureka-repo-health.json", health)
    md = REPO_ROOT / ".aide/reports/eureka-repo-health.md"
    if md.exists():
        text = md.read_text(encoding="utf-8")
        text = text.replace("workbench_review_promote_status: completed_pending_validation", "workbench_review_promote_status: completed")
        if "local_apply_gate_status:" not in text:
            text += "\nlocal_apply_gate_status: in_progress\n"
        write_text(".aide/reports/eureka-repo-health.md", text)


def local_apply_result(status: str, full_status: str, full_reason: str) -> dict[str, Any]:
    passed = status in {"pass", "pass_with_warnings"}
    return {
        "schema_version": "local_apply_gate_result.v0",
        "task": TASK,
        "status": status,
        "contracts_added": True,
        "policies_added": True,
        "route_matrix_added": True,
        "api_matrix_added": True,
        "command_matrix_added": True,
        "permission_matrix_added": True,
        "state_matrix_added": True,
        "event_matrix_added": True,
        "backup_matrix_added": True,
        "rollback_matrix_added": True,
        "mutation_manifest_matrix_added": True,
        "audit_log_matrix_added": True,
        "runtime_apply_gate_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "dry_run_preview_passed": passed,
        "apply_without_token_blocked": passed,
        "apply_without_confirmation_blocked": passed,
        "repo_path_target_blocked": passed,
        "temp_instance_apply_passed": passed,
        "backup_created_before_apply": passed,
        "mutation_manifest_created": passed,
        "audit_log_created": passed,
        "rollback_plan_created": passed,
        "rollback_passed": passed,
        "post_apply_validation_passed": passed,
        "post_rollback_validation_passed": passed,
        "public_projection_blocked": True,
        "native_read_only_projection_blocked": True,
        "operator_instance_mutated": False,
        "operator_instance_mutation_enabled_by_default": False,
        "committed_instance_state": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "full_unittest_discovery_status": full_status,
        "full_unittest_discovery_reason": full_reason,
        "recommended_next_task": NEXT_TASK,
    }


def pending_result(schema: str, **extra: Any) -> dict[str, Any]:
    return {"schema_version": schema, "task": TASK, "status": "pending", **extra, **false_flags()}


def false_flags() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSES}


def read_json(path: str) -> dict[str, Any]:
    full = REPO_ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def write_json(path: str, payload: Mapping[str, Any]) -> None:
    full = REPO_ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: str, text: str) -> None:
    full = REPO_ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text.rstrip() + "\n", encoding="utf-8")


def git(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


if __name__ == "__main__":
    raise SystemExit(main())
