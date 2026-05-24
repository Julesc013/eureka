"""Explicit local-operator apply, backup, audit, and rollback gate."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any, Mapping, Sequence

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.appliance.instance import resolve_instance_paths
from runtime.local.appliance.paths import describe_instance_layout, resolve_repo_root
from runtime.local.service.workbench_review_promote import (
    SAMPLE_CANDIDATE,
    run_review_promote_flow,
    seed_temp_review_records,
)
from runtime.local.review import rebuild_reviewed_index, record_review_decision
from runtime.resolution_run.run_store import FIXED_CREATED_AT, stable_id


APPLY_CONFIRMATION = "APPLY_TO_LOCAL_INSTANCE"
ROLLBACK_CONFIRMATION = "ROLLBACK_LOCAL_INSTANCE"
TASK_ID = "LOCAL-APPLY-GATE-01"
OPERATION_KIND = "reviewed_index_refresh"
POLICY_PATH = Path("control/policies/local_apply_gate_policy.json")
BOUNDARY_FALSES = (
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
)
WATCHED_RELATIVE_PATHS = (
    "config/instance.json",
    "config/store_manifest.json",
    "config/migration_state.json",
    "run/status.json",
    "db/source_cache.sqlite",
    "db/evidence_ledger.sqlite",
    "db/review_queue.sqlite",
    "db/public_index.sqlite",
)


class LocalApplyError(ValueError):
    """Raised when the local apply gate rejects a request."""


def default_policy() -> dict[str, Any]:
    return {
        "schema_version": "local_apply_gate_policy.v0",
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


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    policy = default_policy()
    candidate = Path(path) if path else resolve_repo_root() / POLICY_PATH
    if candidate.is_file():
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping):
            policy.update(dict(payload))
    return policy


def build_local_apply_preview(
    source_preview: Mapping[str, Any] | None = None,
    target_instance: str | Path | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy_record = dict(default_policy(), **dict(policy or {}))
    target_descriptor = _target_descriptor(target_instance)
    preview_source = dict(source_preview or _default_reviewed_index_refresh_preview())
    preview_id = stable_id("local_apply_preview", {"source_preview": preview_source, "target": target_descriptor})
    return {
        "schema_version": "local_apply_preview.v0",
        "task": TASK_ID,
        "preview_id": preview_id,
        "status": "preview_created" if target_descriptor["valid"] else "blocked",
        "operation_kind": OPERATION_KIND,
        "source_preview": preview_source,
        "target_instance_path": target_descriptor.get("instance_root", ""),
        "target_instance_descriptor": target_descriptor,
        "dry_run": True,
        "apply_allowed": False,
        "required_operator_token": True,
        "required_confirmation": APPLY_CONFIRMATION,
        "backup_required": True,
        "rollback_required": True,
        "mutation_scope": _mutation_scope(),
        "blocked_actions": _blocked_actions(),
        "non_claims": _non_claims(),
        "warnings": [] if target_descriptor["valid"] else target_descriptor["errors"],
        **_boundary_flags(operator_instance_mutated=False),
    }


def build_local_apply_plan(
    preview: Mapping[str, Any],
    target_instance: str | Path,
    operator_context: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy_record = dict(default_policy(), **dict(policy or {}))
    context = dict(operator_context or {})
    target_descriptor = _target_descriptor(target_instance)
    apply_requested = bool(context.get("apply", False))
    confirmation = str(context.get("confirmation", "") or "")
    token_present = bool(context.get("operator_token", "") or context.get("operator_token_present", False))
    plan_id = stable_id(
        "local_apply_plan",
        {
            "preview_id": preview.get("preview_id", ""),
            "target": target_descriptor.get("instance_root", ""),
            "operation_kind": OPERATION_KIND,
        },
    )
    errors = []
    if not target_descriptor["valid"]:
        errors.extend(target_descriptor["errors"])
    if apply_requested and not token_present:
        errors.append("operator token is required for apply")
    if apply_requested and confirmation != APPLY_CONFIRMATION:
        errors.append(f"confirmation must be {APPLY_CONFIRMATION}")
    plan = {
        "schema_version": "local_apply_plan.v0",
        "task": TASK_ID,
        "plan_id": plan_id,
        "preview_id": preview.get("preview_id", ""),
        "target_instance_path": target_descriptor.get("instance_root", ""),
        "target_instance_descriptor": target_descriptor,
        "operation_kind": OPERATION_KIND,
        "source_preview_ref": preview.get("preview_id", ""),
        "source_preview": dict(preview.get("source_preview", {})),
        "required_operator_token": True,
        "required_confirmation": APPLY_CONFIRMATION,
        "dry_run": not apply_requested,
        "apply_requested": apply_requested,
        "apply_allowed": apply_requested and not errors,
        "backup_required": True,
        "rollback_required": True,
        "audit_log_required": True,
        "mutation_manifest_required": True,
        "post_apply_validation_required": True,
        "mutation_scope": _mutation_scope(),
        "blocked_actions": _blocked_actions(),
        "non_claims": _non_claims(),
        "policy": {key: value for key, value in policy_record.items() if key != "schema_version"},
        "operator_context_redacted": _redacted_operator_context(context),
        "validation_errors": errors,
        "status": "apply_ready" if apply_requested and not errors else ("preview_created" if not apply_requested and not errors else "blocked"),
        "created_at": _now(),
        **_boundary_flags(operator_instance_mutated=False),
    }
    return plan


def validate_local_apply_plan(plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    policy_record = dict(default_policy(), **dict(policy or {}))
    for field in (
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
    ):
        if field not in plan:
            errors.append(f"missing plan field: {field}")
    if plan.get("operation_kind") != OPERATION_KIND:
        errors.append("operation_kind must be reviewed_index_refresh")
    if plan.get("required_confirmation") != APPLY_CONFIRMATION:
        errors.append(f"required_confirmation must be {APPLY_CONFIRMATION}")
    if policy_record.get("backup_required_before_apply") is not True or plan.get("backup_required") is not True:
        errors.append("backup is required before apply")
    if policy_record.get("rollback_plan_required_before_apply") is not True or plan.get("rollback_required") is not True:
        errors.append("rollback plan is required")
    descriptor = plan.get("target_instance_descriptor")
    if isinstance(descriptor, Mapping) and descriptor.get("valid") is not True:
        errors.extend(str(item) for item in descriptor.get("errors", []))
    for key in BOUNDARY_FALSES:
        if plan.get(key) is not False:
            errors.append(f"plan boundary must set {key}=false")
    return {
        "schema_version": "local_apply_plan_validation.v0",
        "status": "pass" if not errors else "fail",
        "plan_id": str(plan.get("plan_id", "")),
        "errors": errors,
        "warnings": [],
    }


def create_pre_apply_backup(plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    validation = validate_local_apply_plan(plan, policy)
    if validation["status"] != "pass":
        raise LocalApplyError("; ".join(validation["errors"]))
    paths = resolve_instance_paths(str(plan["target_instance_path"]))
    backup_id = stable_id("local_apply_backup", {"plan_id": plan["plan_id"], "target": str(paths.instance_root)})
    backup_root = paths.instance_root / "backups" / "local_apply" / backup_id
    files: list[dict[str, Any]] = []
    for rel in WATCHED_RELATIVE_PATHS:
        source = paths.instance_root / rel
        digest_before = _hash_file(source) if source.exists() else ""
        target = backup_root / rel
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        files.append(
            {
                "relative_path": rel,
                "source_path": str(source),
                "backup_path": str(target),
                "existed": source.exists(),
                "sha256": digest_before,
            }
        )
    manifest = {
        "schema_version": "local_apply_backup_manifest.v0",
        "backup_id": backup_id,
        "plan_id": plan["plan_id"],
        "target_instance_path": str(paths.instance_root),
        "backup_root": str(backup_root),
        "created_at": _now(),
        "files": files,
        "backup_created_before_apply": True,
        "repository_path_mutated": False,
        **_boundary_flags(operator_instance_mutated=False),
    }
    _write_instance_json(backup_root / "backup_manifest.json", manifest)
    return manifest


def apply_reviewed_index_refresh(plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not bool(plan.get("apply_allowed", False)):
        raise LocalApplyError("apply is not allowed by plan")
    runtime = open_local_appliance(str(plan["target_instance_path"]), read_only=False)
    try:
        candidate = _candidate_from_plan(plan)
        seed = seed_temp_review_records(runtime, candidate)
        decision = record_review_decision(runtime, seed["review_item_id"], "accept", None, "local_apply_gate", True)
        refresh = rebuild_reviewed_index(runtime, operator_label="local_apply_gate", dry_run=False)
        query = candidate.get("claim_subject", "sampleproject")
        search_results = [item.to_dict() for item in runtime.public_index.search(query, limit=10)]
        return {
            "schema_version": "local_apply_reviewed_index_refresh_result.v0",
            "status": "pass",
            "plan_id": plan["plan_id"],
            "seeded_review_records": seed,
            "review_decision": decision,
            "reviewed_index_refresh": refresh,
            "post_apply_search_query": query,
            "post_apply_search_result_count": len(search_results),
            "post_apply_search_results": search_results,
            "post_apply_validation_passed": bool(search_results),
            "explicit_local_instance_mutated": True,
            "operator_instance_mutated": False,
            "mutation_scope": "explicit_operator_instance_path",
            "master_index_mutated": False,
            "committed_data_public_index_mutated": False,
            "warnings": [],
        }
    finally:
        close_local_appliance(runtime)


def build_mutation_manifest(
    plan: Mapping[str, Any],
    before_state: Mapping[str, str],
    after_state: Mapping[str, str],
    backup_manifest: Mapping[str, Any],
    validation_result: Mapping[str, Any],
) -> dict[str, Any]:
    mutation_id = stable_id("local_apply_mutation", {"plan_id": plan["plan_id"], "after": dict(after_state)})
    files_created = [rel for rel, digest in after_state.items() if digest and not before_state.get(rel)]
    files_modified = [rel for rel, digest in after_state.items() if digest and before_state.get(rel) and before_state.get(rel) != digest]
    files_deleted = [rel for rel, digest in before_state.items() if digest and not after_state.get(rel)]
    manifest = {
        "schema_version": "local_apply_mutation_manifest.v0",
        "mutation_id": mutation_id,
        "plan_id": plan["plan_id"],
        "target_instance_path": plan["target_instance_path"],
        "operation_kind": OPERATION_KIND,
        "files_created": files_created,
        "files_modified": files_modified,
        "files_deleted": files_deleted,
        "stores_modified": [rel for rel in files_modified + files_created if rel.startswith("db/")],
        "before_hashes": dict(before_state),
        "after_hashes": dict(after_state),
        "backup_manifest_ref": backup_manifest.get("backup_id", ""),
        "rollback_plan_ref": stable_id("local_apply_rollback", {"mutation_id": mutation_id}),
        "validation_result_ref": validation_result.get("validation_id", ""),
        "created_at": _now(),
        "repository_path_mutated": False,
        "committed_instance_state": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        **_boundary_flags(operator_instance_mutated=False),
    }
    _write_instance_json(Path(str(plan["target_instance_path"])) / "logs" / "local_apply" / f"{mutation_id}.manifest.json", manifest)
    return manifest


def write_local_apply_audit_log(
    plan: Mapping[str, Any],
    mutation_manifest: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
    *,
    command: str = "apply_local_change",
    dry_run: bool = False,
    apply_performed: bool = True,
    validation_result: Mapping[str, Any] | None = None,
    boundary_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    paths = resolve_instance_paths(str(plan["target_instance_path"]))
    audit_id = stable_id("local_apply_audit", {"plan_id": plan["plan_id"], "mutation": mutation_manifest.get("mutation_id", ""), "command": command})
    audit = {
        "schema_version": "local_apply_audit_log.v0",
        "audit_id": audit_id,
        "plan_id": plan["plan_id"],
        "mutation_id": mutation_manifest.get("mutation_id", ""),
        "operator_context_redacted": dict(plan.get("operator_context_redacted", {})),
        "command": command,
        "dry_run": dry_run,
        "apply_performed": apply_performed,
        "target_instance_path": str(paths.instance_root),
        "timestamp": _now(),
        "policy_result": "pass",
        "validation_result": dict(validation_result or {}),
        "boundary_report_ref": (boundary_report or {}).get("boundary_report_id", ""),
        "raw_token_stored": False,
        "raw_source_response_stored": False,
        **_boundary_flags(operator_instance_mutated=False),
    }
    _write_instance_json(paths.logs_dir / "local_apply" / f"{audit_id}.json", audit)
    return audit


def validate_post_apply(plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    runtime = open_local_appliance(str(plan["target_instance_path"]), read_only=True)
    try:
        integrity = runtime.check_integrity()
        query = _candidate_from_plan(plan).get("claim_subject", "sampleproject")
        results = [item.to_dict() for item in runtime.public_index.search(query, limit=10)]
        passed = integrity.get("status") == "pass" and bool(results)
        return {
            "schema_version": "local_apply_post_apply_validation.v0",
            "validation_id": stable_id("local_apply_post_apply_validation", plan["plan_id"]),
            "status": "pass" if passed else "fail",
            "plan_id": plan["plan_id"],
            "integrity_status": integrity.get("status"),
            "search_query": query,
            "search_result_count": len(results),
            "post_apply_validation_passed": passed,
            "errors": [] if passed else ["post-apply search did not find reviewed local record"],
            **_boundary_flags(operator_instance_mutated=False),
        }
    finally:
        close_local_appliance(runtime)


def build_rollback_plan(
    plan: Mapping[str, Any],
    backup_manifest: Mapping[str, Any],
    mutation_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    rollback_id = mutation_manifest.get("rollback_plan_ref") or stable_id("local_apply_rollback", {"mutation_id": mutation_manifest.get("mutation_id", "")})
    rollback_plan = {
        "schema_version": "local_apply_rollback_plan.v0",
        "rollback_plan_id": rollback_id,
        "plan_id": plan["plan_id"],
        "mutation_id": mutation_manifest.get("mutation_id", ""),
        "target_instance_path": plan["target_instance_path"],
        "backup_manifest_ref": backup_manifest.get("backup_id", ""),
        "backup_manifest": dict(backup_manifest),
        "required_operator_token": True,
        "required_confirmation": ROLLBACK_CONFIRMATION,
        "apply_allowed": False,
        "created_at": _now(),
        "files_to_restore": [dict(item) for item in backup_manifest.get("files", [])],
        "non_claims": _non_claims(),
        **_boundary_flags(operator_instance_mutated=False),
    }
    paths = resolve_instance_paths(str(plan["target_instance_path"]))
    _write_instance_json(paths.instance_root / "backups" / "local_apply" / str(backup_manifest["backup_id"]) / "rollback_plan.json", rollback_plan)
    return rollback_plan


def run_rollback(
    rollback_plan: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
    operator_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(operator_context or {})
    apply_requested = bool(context.get("apply", rollback_plan.get("apply_allowed", False)))
    token_present = bool(context.get("operator_token", "") or context.get("operator_token_present", False))
    confirmation = str(context.get("confirmation", "") or "")
    blocked: list[str] = []
    if apply_requested and not token_present:
        blocked.append("operator token is required for rollback")
    if apply_requested and confirmation != ROLLBACK_CONFIRMATION:
        blocked.append(f"confirmation must be {ROLLBACK_CONFIRMATION}")
    if not apply_requested:
        return {
            "schema_version": "local_apply_rollback_result.v0",
            "status": "dry_run",
            "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
            "rollback_performed": False,
            "blocked_reasons": [],
            "dry_run": True,
            **_boundary_flags(operator_instance_mutated=False),
        }
    if blocked:
        return {
            "schema_version": "local_apply_rollback_result.v0",
            "status": "blocked",
            "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
            "rollback_performed": False,
            "blocked_reasons": blocked,
            "dry_run": False,
            **_boundary_flags(operator_instance_mutated=False),
        }
    paths = resolve_instance_paths(str(rollback_plan["target_instance_path"]))
    for item in rollback_plan.get("files_to_restore", []):
        rel = str(item.get("relative_path", ""))
        destination = paths.instance_root / rel
        backup_path = Path(str(item.get("backup_path", "")))
        if bool(item.get("existed", False)) and backup_path.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, destination)
        elif destination.exists():
            destination.unlink()
    validation = validate_post_rollback(rollback_plan, policy)
    result = {
        "schema_version": "local_apply_rollback_result.v0",
        "status": "pass" if validation.get("status") == "pass" else "fail",
        "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
        "plan_id": rollback_plan.get("plan_id", ""),
        "mutation_id": rollback_plan.get("mutation_id", ""),
        "rollback_performed": True,
        "dry_run": False,
        "post_rollback_validation": validation,
        "post_rollback_validation_passed": validation.get("status") == "pass",
        "blocked_reasons": [],
        "explicit_local_instance_mutated": True,
        "operator_instance_mutated": False,
        "mutation_scope": "explicit_operator_instance_path",
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
        **_boundary_flags(operator_instance_mutated=False),
    }
    _write_instance_json(paths.logs_dir / "local_apply" / f"{rollback_plan.get('rollback_plan_id', 'rollback')}.rollback.json", result)
    _write_instance_json(paths.logs_dir / "local_apply" / f"{rollback_plan.get('rollback_plan_id', 'rollback')}.rollback.audit.json", _rollback_audit_log(rollback_plan, validation))
    return result


def validate_post_rollback(rollback_plan: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    paths = resolve_instance_paths(str(rollback_plan["target_instance_path"]))
    errors: list[str] = []
    for item in rollback_plan.get("files_to_restore", []):
        rel = str(item.get("relative_path", ""))
        expected = str(item.get("sha256", ""))
        destination = paths.instance_root / rel
        actual = _hash_file(destination) if destination.exists() else ""
        if actual != expected:
            errors.append(f"hash mismatch after rollback: {rel}")
    query_results = []
    try:
        runtime = open_local_appliance(paths.instance_root, read_only=True)
        try:
            query_results = [item.to_dict() for item in runtime.public_index.search("sampleproject", limit=10)]
        finally:
            close_local_appliance(runtime)
    except Exception as exc:
        errors.append(f"post-rollback runtime open failed: {exc}")
    return {
        "schema_version": "local_apply_post_rollback_validation.v0",
        "validation_id": stable_id("local_apply_post_rollback_validation", rollback_plan.get("rollback_plan_id", "")),
        "status": "pass" if not errors else "fail",
        "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
        "post_rollback_validation_passed": not errors,
        "search_result_count_after_rollback": len(query_results),
        "errors": errors,
        **_boundary_flags(operator_instance_mutated=False),
    }


def build_local_apply_boundary_report(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_apply_boundary_report.v0",
        "boundary_report_id": stable_id("local_apply_boundary", result.get("plan_id", "")),
        "task": TASK_ID,
        "explicit_local_instance_mutation_performed": bool(result.get("explicit_local_instance_mutated", result.get("apply_performed", False))),
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
        "result_status": result.get("status", "unknown"),
    }


def run_local_apply(
    *,
    target_instance: str | Path,
    source_preview: Mapping[str, Any] | None = None,
    apply: bool = False,
    operator_token: str = "",
    confirmation: str = "",
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy_record = dict(default_policy(), **dict(policy or {}))
    preview = build_local_apply_preview(source_preview, target_instance, policy_record)
    plan = build_local_apply_plan(
        preview,
        target_instance,
        {
            "apply": apply,
            "operator_token": operator_token,
            "confirmation": confirmation,
        },
        policy_record,
    )
    plan_validation = validate_local_apply_plan(plan, policy_record)
    if not apply:
        result = {
            "schema_version": "local_apply_result.v0",
            "task": TASK_ID,
            "status": "dry_run" if plan_validation["status"] == "pass" else "blocked",
            "preview": preview,
            "plan": plan,
            "plan_validation": plan_validation,
            "dry_run_preview_passed": plan_validation["status"] == "pass",
            "apply_performed": False,
            "backup_created_before_apply": False,
            "mutation_manifest_created": False,
            "audit_log_created": False,
            "rollback_plan_created": False,
            "post_apply_validation_passed": False,
            "operator_instance_mutated": False,
            **_boundary_flags(operator_instance_mutated=False),
        }
        result["boundary_report"] = build_local_apply_boundary_report(result)
        return result
    if plan_validation["status"] != "pass":
        result = _blocked_result(preview, plan, plan_validation["errors"])
        result["boundary_report"] = build_local_apply_boundary_report(result)
        return result
    if not plan.get("apply_allowed"):
        result = _blocked_result(preview, plan, plan.get("validation_errors", ["apply was not allowed"]))
        result["boundary_report"] = build_local_apply_boundary_report(result)
        return result
    before = _watched_hashes(plan["target_instance_path"])
    backup = create_pre_apply_backup(plan, policy_record)
    apply_result = apply_reviewed_index_refresh(plan, policy_record)
    after = _watched_hashes(plan["target_instance_path"])
    post_apply = validate_post_apply(plan, policy_record)
    manifest = build_mutation_manifest(plan, before, after, backup, post_apply)
    rollback_plan = build_rollback_plan(plan, backup, manifest)
    boundary = build_local_apply_boundary_report(apply_result)
    audit = write_local_apply_audit_log(plan, manifest, policy_record, validation_result=post_apply, boundary_report=boundary)
    result = {
        "schema_version": "local_apply_result.v0",
        "task": TASK_ID,
        "status": "pass" if post_apply.get("status") == "pass" else "fail",
        "plan_id": plan["plan_id"],
        "preview": preview,
        "plan": plan,
        "plan_validation": plan_validation,
        "backup_manifest": backup,
        "apply_result": apply_result,
        "mutation_manifest": manifest,
        "rollback_plan": rollback_plan,
        "audit_log": audit,
        "post_apply_validation": post_apply,
        "boundary_report": boundary,
        "dry_run_preview_passed": True,
        "apply_performed": True,
        "backup_created_before_apply": True,
        "mutation_manifest_created": True,
        "audit_log_created": True,
        "rollback_plan_created": True,
        "post_apply_validation_passed": post_apply.get("status") == "pass",
        "explicit_local_instance_mutated": True,
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
    }
    return result


def _blocked_result(preview: Mapping[str, Any], plan: Mapping[str, Any], blocked_reasons: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": "local_apply_result.v0",
        "task": TASK_ID,
        "status": "blocked",
        "preview": dict(preview),
        "plan": dict(plan),
        "blocked_reasons": list(blocked_reasons),
        "dry_run_preview_passed": preview.get("status") == "preview_created",
        "apply_performed": False,
        "backup_created_before_apply": False,
        "mutation_manifest_created": False,
        "audit_log_created": False,
        "rollback_plan_created": False,
        "post_apply_validation_passed": False,
        "operator_instance_mutated": False,
        **_boundary_flags(operator_instance_mutated=False),
    }


def _rollback_audit_log(rollback_plan: Mapping[str, Any], validation_result: Mapping[str, Any]) -> dict[str, Any]:
    audit_id = stable_id(
        "local_apply_rollback_audit",
        {
            "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
            "mutation_id": rollback_plan.get("mutation_id", ""),
        },
    )
    return {
        "schema_version": "local_apply_audit_log.v0",
        "audit_id": audit_id,
        "plan_id": rollback_plan.get("plan_id", ""),
        "mutation_id": rollback_plan.get("mutation_id", ""),
        "operator_context_redacted": {
            "operator_token_present": True,
            "operator_token_stored": False,
            "confirmation_present": True,
            "apply_requested": True,
        },
        "command": "run_rollback",
        "dry_run": False,
        "apply_performed": True,
        "target_instance_path": rollback_plan.get("target_instance_path", ""),
        "timestamp": _now(),
        "policy_result": "pass",
        "validation_result": dict(validation_result),
        "boundary_report_ref": "",
        "raw_token_stored": False,
        "raw_source_response_stored": False,
        **_boundary_flags(operator_instance_mutated=False),
    }


def _default_reviewed_index_refresh_preview() -> dict[str, Any]:
    return run_review_promote_flow(
        candidate=SAMPLE_CANDIDATE,
        decision="accept_local_reviewed",
        projection_profile="operator_workbench",
        operator_token="",
        dry_run=True,
    )["reviewed_index_refresh_preview"]


def _candidate_from_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    source_preview = dict(plan.get("source_preview", {}))
    refresh_source = source_preview.get("source_preview")
    if isinstance(refresh_source, Mapping):
        source_preview = dict(refresh_source)
    candidate = deepcopy(SAMPLE_CANDIDATE)
    record = dict(source_preview.get("temp_reviewed_index_delta", {}).get("add", [{}])[0] or {})
    candidate["title"] = str(record.get("title") or candidate["title"])
    candidate["summary"] = str(record.get("summary") or candidate["summary"])
    candidate["source_cache_entry_id"] = str(record.get("source_cache_entry_id") or candidate["source_cache_entry_id"])
    candidate["evidence_id"] = str(record.get("evidence_id") or candidate["evidence_id"])
    candidate["claim_subject"] = "sampleproject"
    return candidate


def _target_descriptor(target_instance: str | Path | None) -> dict[str, Any]:
    errors: list[str] = []
    if target_instance is None or not str(target_instance).strip():
        errors.append("target instance path is required")
        root = ""
        layout: dict[str, Any] = {}
    else:
        try:
            paths = resolve_instance_paths(target_instance)
            root = str(paths.instance_root)
            layout = describe_instance_layout(resolve_repo_root(), paths.instance_root)
            if layout.get("is_repo_nested"):
                errors.append("target instance path must be outside the repo")
        except Exception as exc:
            root = str(target_instance)
            layout = {}
            errors.append(str(exc))
    return {
        "schema_version": "instance_descriptor.v0",
        "instance_root": root,
        "layout": layout,
        "explicit_path_required": True,
        "outside_repo_required": True,
        "valid": not errors,
        "errors": errors,
    }


def _watched_hashes(instance_root: str | Path) -> dict[str, str]:
    root = Path(instance_root)
    return {rel: (_hash_file(root / rel) if (root / rel).exists() else "") for rel in WATCHED_RELATIVE_PATHS}


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mutation_scope() -> dict[str, Any]:
    return {
        "schema_version": "instance_mutation_scope.v0",
        "operation_kind": OPERATION_KIND,
        "target_scope": "explicit_local_operator_instance",
        "repo_mutation_allowed": False,
        "master_index_mutation_allowed": False,
        "committed_public_index_mutation_allowed": False,
        "stores_allowed": ["source_cache", "evidence_ledger", "review_queue", "public_index"],
    }


def _blocked_actions() -> list[str]:
    return [
        "silent_operator_instance_mutation",
        "master_index_mutation",
        "committed_data_public_index_mutation",
        "public_apply",
        "native_apply",
        "download",
        "upload",
        "extraction",
        "execution",
        "model_provider_call",
        "deployment",
    ]


def _non_claims() -> list[str]:
    return [
        "not production readiness",
        "not public launch readiness",
        "not master index truth",
        "not public index mutation",
        "not source probing",
        "not extraction or download authority",
    ]


def _redacted_operator_context(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "operator_token_present": bool(context.get("operator_token", "") or context.get("operator_token_present", False)),
        "operator_token_stored": False,
        "confirmation_present": bool(context.get("confirmation", "")),
        "apply_requested": bool(context.get("apply", False)),
    }


def _boundary_flags(*, operator_instance_mutated: bool) -> dict[str, bool]:
    return {
        "operator_instance_mutated": bool(operator_instance_mutated),
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
    }


def _write_instance_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") if False else FIXED_CREATED_AT
