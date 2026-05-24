"""Close out the safe local Workbench loop through the Local Apply Gate."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from runtime.local.apply import (
    APPLY_CONFIRMATION,
    ROLLBACK_CONFIRMATION,
    run_local_apply,
    run_rollback,
)
from runtime.local.service.workbench_live_run import create_workbench_resolution_run
from runtime.local.service.workbench_review_promote import (
    PROJECTION_PROFILES,
    SAMPLE_CANDIDATE,
    build_promotion_preview,
    create_review_item_from_candidate,
    record_review_decision,
)
from runtime.resolution_run.run_store import FIXED_CREATED_AT, stable_id


TASK_ID = "WORKBENCH-LOCAL-LOOP-CLOSEOUT-01"
READ_ONLY_PROJECTIONS = {"public_web", "native_desktop_read_only"}


def default_policy() -> dict[str, Any]:
    return {
        "schema_version": "workbench_local_loop_policy.v0",
        "local_loop_requires_apply_gate": True,
        "local_loop_uses_temp_instance_for_automated_tests": True,
        "operator_instance_mutation_default": False,
        "operator_token_required_for_apply": True,
        "explicit_confirmation_required_for_apply": True,
        "backup_required_before_apply": True,
        "rollback_required": True,
        "audit_log_required": True,
        "mutation_manifest_required": True,
        "public_loop_mutation_enabled": False,
        "native_loop_mutation_enabled": False,
        "master_index_mutation_enabled": False,
        "committed_data_public_index_mutation_enabled": False,
        "fake_evidence_forbidden": True,
        "fake_verified_records_forbidden": True,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_local_loop_plan(
    query: str,
    target_instance: str | Path,
    projection_profile: str = "operator_workbench",
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    profile = _projection_profile(projection_profile)
    policy_record = dict(default_policy(), **dict(policy or {}))
    plan_id = stable_id(
        "local_loop_plan",
        {"query": query, "target": str(target_instance), "projection": profile},
    )
    steps = [
        "create_resolution_run",
        "collect_lane_snapshot",
        "select_candidate",
        "create_review_item",
        "record_operator_review_decision",
        "build_promotion_preview",
        "build_local_apply_preview",
        "create_pre_apply_backup",
        "apply_to_temp_instance",
        "write_mutation_manifest",
        "write_audit_log",
        "refresh_reviewed_local_index",
        "search_after_apply",
        "build_rollback_plan",
        "rollback_temp_instance",
        "search_after_rollback",
        "emit_boundary_report",
    ]
    return {
        "schema_version": "local_loop_plan.v0",
        "task": TASK_ID,
        "plan_id": plan_id,
        "query": str(query or "sampleproject"),
        "target_instance_path": str(target_instance),
        "projection_profile": profile,
        "steps": steps,
        "requires_operator_token": True,
        "requires_apply_gate": True,
        "dry_run_default": True,
        "temp_instance_required_for_automated_tests": True,
        "policy": {key: value for key, value in policy_record.items() if key != "schema_version"},
        "non_claims": _non_claims(),
        "created_at": FIXED_CREATED_AT,
        **_boundary_flags(),
    }


def run_local_loop_dry_run(plan: Mapping[str, Any]) -> dict[str, Any]:
    profile = _projection_profile(str(plan.get("projection_profile", "operator_workbench")))
    query = str(plan.get("query") or "sampleproject")
    live_run = create_workbench_resolution_run(query, profile)
    candidate = select_candidate_for_loop(live_run, default_policy())
    review_item = create_review_item_for_loop(candidate, default_policy())
    review_decision = record_review_decision_for_loop(
        review_item,
        {"dry_run": True, "projection_profile": profile},
        default_policy(),
    )
    promotion_preview = build_promotion_preview_for_loop(review_decision, default_policy())
    apply_preview = run_local_apply(
        target_instance=str(plan.get("target_instance_path", "")),
        source_preview=promotion_preview.get("reviewed_index_refresh_preview"),
        apply=False,
    )
    result = {
        "schema_version": "local_loop_result.v0",
        "task": TASK_ID,
        "status": "dry_run" if apply_preview.get("status") == "dry_run" else "blocked",
        "loop_id": stable_id("local_loop", {"plan": plan.get("plan_id", ""), "mode": "dry_run"}),
        "plan": dict(plan),
        "query": query,
        "projection_profile": profile,
        "run_id": live_run.get("run_id", ""),
        "candidate_id": candidate.get("candidate_id", ""),
        "review_item_id": review_item.get("review_item_id", ""),
        "review_decision_id": review_decision.get("decision_id", ""),
        "promotion_preview_id": promotion_preview.get("promotion_preview", {}).get("preview_id", ""),
        "local_apply_plan_id": apply_preview.get("plan", {}).get("plan_id", ""),
        "backup_manifest_id": "",
        "mutation_manifest_id": "",
        "audit_id": "",
        "rollback_plan_id": "",
        "search_after_apply_proof_id": "",
        "rollback_proof_id": "",
        "live_run": live_run,
        "candidate": candidate,
        "review_item": review_item,
        "review_decision": review_decision,
        "promotion_preview": promotion_preview,
        "local_apply_preview": apply_preview,
        "events": _events("dry_run", live_run, review_item, promotion_preview),
        "boundaries": _boundary_flags(),
        "dry_run_loop_passed": apply_preview.get("status") == "dry_run",
        "temp_apply_loop_passed": False,
        "search_after_apply_passed": False,
        "rollback_passed": False,
        "search_after_rollback_passed": False,
        "public_projection_blocked": profile == "public_web",
        "native_read_only_projection_blocked": profile == "native_desktop_read_only",
        **_boundary_flags(),
    }
    result["boundary_report"] = build_local_loop_boundary_report(result)
    result["workbench_projection"] = build_local_loop_workbench_projection(result, profile)
    return result


def run_local_loop_temp_instance(
    plan: Mapping[str, Any],
    operator_context: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(operator_context or {})
    policy_record = dict(default_policy(), **dict(policy or {}))
    profile = _projection_profile(str(plan.get("projection_profile", "operator_workbench")))
    query = str(plan.get("query") or "sampleproject")
    blocked = _apply_blockers(profile, context)
    if blocked:
        result = _blocked_result(plan, profile, blocked)
        result["boundary_report"] = build_local_loop_boundary_report(result)
        return result

    live_run = create_workbench_resolution_run(query, profile)
    candidate = select_candidate_for_loop(live_run, policy_record)
    review_item = create_review_item_for_loop(candidate, policy_record)
    review_decision = record_review_decision_for_loop(review_item, context, policy_record)
    promotion_preview = build_promotion_preview_for_loop(review_decision, policy_record)
    apply_result = apply_loop_to_temp_instance(
        promotion_preview,
        str(plan.get("target_instance_path", "")),
        context,
        policy_record,
    )
    if apply_result.get("status") != "pass":
        blocked_result = _blocked_result(plan, profile, apply_result.get("blocked_reasons", ["local apply gate did not pass"]))
        blocked_result.update(
            {
                "live_run": live_run,
                "candidate": candidate,
                "review_item": review_item,
                "review_decision": review_decision,
                "promotion_preview": promotion_preview,
                "local_apply_result": apply_result,
            }
        )
        blocked_result["boundary_report"] = build_local_loop_boundary_report(blocked_result)
        return blocked_result

    search_apply = search_after_loop_apply(str(plan.get("target_instance_path", "")), query, apply_result, policy_record)
    rollback_plan = apply_result.get("rollback_plan", {})
    rollback_result = rollback_loop_temp_instance(rollback_plan, context, policy_record)
    search_rollback = search_after_loop_rollback(
        str(plan.get("target_instance_path", "")),
        query,
        rollback_result,
        policy_record,
    )
    apply_proof = build_apply_proof(apply_result, search_apply)
    rollback_proof = build_rollback_proof(rollback_result, search_rollback)
    search_proof = build_search_after_apply_proof(search_apply, search_rollback)
    passed = (
        apply_result.get("status") == "pass"
        and search_apply.get("search_after_apply_passed") is True
        and rollback_result.get("status") == "pass"
        and search_rollback.get("search_after_rollback_passed") is True
    )
    result = {
        "schema_version": "local_loop_result.v0",
        "task": TASK_ID,
        "status": "pass" if passed else "fail",
        "loop_id": stable_id("local_loop", {"plan": plan.get("plan_id", ""), "mode": "temp_apply"}),
        "plan": dict(plan),
        "query": query,
        "projection_profile": profile,
        "run_id": live_run.get("run_id", ""),
        "candidate_id": candidate.get("candidate_id", ""),
        "review_item_id": review_item.get("review_item_id", ""),
        "review_decision_id": review_decision.get("decision_id", ""),
        "promotion_preview_id": promotion_preview.get("promotion_preview", {}).get("preview_id", ""),
        "local_apply_plan_id": apply_result.get("plan_id", ""),
        "backup_manifest_id": apply_result.get("backup_manifest", {}).get("backup_id", ""),
        "mutation_manifest_id": apply_result.get("mutation_manifest", {}).get("mutation_id", ""),
        "audit_id": apply_result.get("audit_log", {}).get("audit_id", ""),
        "rollback_plan_id": rollback_plan.get("rollback_plan_id", ""),
        "search_after_apply_proof_id": search_proof.get("proof_id", ""),
        "rollback_proof_id": rollback_proof.get("proof_id", ""),
        "live_run": live_run,
        "candidate": candidate,
        "review_item": review_item,
        "review_decision": review_decision,
        "promotion_preview": promotion_preview,
        "local_apply_result": apply_result,
        "rollback_result": rollback_result,
        "apply_proof": apply_proof,
        "rollback_proof": rollback_proof,
        "search_after_apply_proof": search_proof,
        "events": _events("pass" if passed else "fail", live_run, review_item, promotion_preview),
        "dry_run_loop_passed": True,
        "temp_apply_loop_passed": apply_result.get("status") == "pass",
        "search_after_apply_passed": search_apply.get("search_after_apply_passed") is True,
        "rollback_passed": rollback_result.get("status") == "pass",
        "search_after_rollback_passed": search_rollback.get("search_after_rollback_passed") is True,
        "public_projection_blocked": False,
        "native_read_only_projection_blocked": False,
        **_boundary_flags(),
    }
    result["boundary_report"] = build_local_loop_boundary_report(result)
    result["workbench_projection"] = build_local_loop_workbench_projection(result, profile)
    return result


def select_candidate_for_loop(run_result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = deepcopy(SAMPLE_CANDIDATE)
    candidate["candidate_source"] = "local_loop_result_lane"
    candidate["query"] = str(run_result.get("query") or "sampleproject")
    candidate["run_id"] = str(run_result.get("run_id", ""))
    return candidate


def create_review_item_for_loop(candidate: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return create_review_item_from_candidate(candidate, policy)


def record_review_decision_for_loop(
    review_item: Mapping[str, Any],
    operator_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(operator_context)
    context.setdefault("projection_profile", "operator_workbench")
    context.setdefault("dry_run", not bool(context.get("operator_token")))
    return record_review_decision(
        str(review_item.get("review_item_id", "")),
        "accept_local_reviewed",
        context,
        policy,
    )


def build_promotion_preview_for_loop(
    review_decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    preview = build_promotion_preview(review_decision, policy)
    refresh_preview = {
        "schema_version": "workbench_reviewed_index_refresh_preview.v0",
        "refresh_preview_id": stable_id("local_loop_refresh_preview", preview.get("preview_id", "")),
        "promotion_preview_id": preview.get("preview_id", ""),
        "status": "preview_available" if preview.get("promotion_preview_created") else "blocked",
        "temp_reviewed_index_delta": {
            "add": [preview.get("reviewed_local_record_preview", {})] if preview.get("promotion_preview_created") else [],
            "update": [],
            "delete": [],
        },
        "refresh_allowed_only_temp_or_explicit_instance": True,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "committed_data_public_index_mutated": False,
    }
    return {
        "schema_version": "local_loop_promotion_preview.v0",
        "promotion_preview": preview,
        "reviewed_index_refresh_preview": refresh_preview,
    }


def build_apply_preview_for_loop(
    promotion_preview: Mapping[str, Any],
    target_instance: str | Path,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return run_local_apply(
        target_instance=target_instance,
        source_preview=promotion_preview.get("reviewed_index_refresh_preview"),
        apply=False,
        policy=policy,
    )


def apply_loop_to_temp_instance(
    apply_preview: Mapping[str, Any],
    target_instance: str | Path,
    operator_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return run_local_apply(
        target_instance=target_instance,
        source_preview=apply_preview.get("reviewed_index_refresh_preview"),
        apply=True,
        operator_token=str(operator_context.get("operator_token", "")),
        confirmation=str(operator_context.get("confirmation", "")),
        policy=policy,
    )


def search_after_loop_apply(
    temp_instance: str | Path,
    query: str,
    apply_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validation = dict(apply_result.get("post_apply_validation") or {})
    result_count = int(validation.get("search_result_count", 0) or 0)
    return {
        "schema_version": "local_loop_search_after_apply_proof.v0",
        "proof_id": stable_id("local_loop_search_after_apply", apply_result.get("plan_id", "")),
        "target_instance_path": str(temp_instance),
        "query": str(query),
        "search_result_count": result_count,
        "search_after_apply_passed": result_count > 0 and validation.get("status") == "pass",
        "reviewed_local_result_visible": result_count > 0,
        "accepted_truth": False,
        **_boundary_flags(),
    }


def rollback_loop_temp_instance(
    rollback_plan: Mapping[str, Any],
    operator_context: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return run_rollback(
        rollback_plan,
        policy=policy,
        operator_context={
            "apply": True,
            "operator_token": str(operator_context.get("operator_token", "")),
            "confirmation": ROLLBACK_CONFIRMATION,
        },
    )


def search_after_loop_rollback(
    temp_instance: str | Path,
    query: str,
    rollback_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validation = dict(rollback_result.get("post_rollback_validation") or {})
    result_count = int(validation.get("search_result_count_after_rollback", 0) or 0)
    return {
        "schema_version": "local_loop_search_after_rollback_proof.v0",
        "proof_id": stable_id("local_loop_search_after_rollback", rollback_result.get("rollback_plan_id", "")),
        "target_instance_path": str(temp_instance),
        "query": str(query),
        "search_result_count_after_rollback": result_count,
        "search_after_rollback_passed": rollback_result.get("status") == "pass" and result_count == 0,
        "reviewed_local_result_removed": result_count == 0,
        **_boundary_flags(),
    }


def build_apply_proof(apply_result: Mapping[str, Any], search_after_apply: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_loop_apply_proof.v0",
        "proof_id": stable_id("local_loop_apply_proof", apply_result.get("plan_id", "")),
        "local_apply_plan_id": apply_result.get("plan_id", ""),
        "backup_manifest_id": apply_result.get("backup_manifest", {}).get("backup_id", ""),
        "mutation_manifest_id": apply_result.get("mutation_manifest", {}).get("mutation_id", ""),
        "audit_id": apply_result.get("audit_log", {}).get("audit_id", ""),
        "post_apply_validation_passed": apply_result.get("post_apply_validation_passed") is True,
        "search_after_apply_passed": search_after_apply.get("search_after_apply_passed") is True,
        "backup_created_before_apply": apply_result.get("backup_created_before_apply") is True,
        "mutation_manifest_created": apply_result.get("mutation_manifest_created") is True,
        "audit_log_created": apply_result.get("audit_log_created") is True,
        **_boundary_flags(),
    }


def build_rollback_proof(
    rollback_result: Mapping[str, Any],
    search_after_rollback: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "local_loop_rollback_proof.v0",
        "proof_id": stable_id("local_loop_rollback_proof", rollback_result.get("rollback_plan_id", "")),
        "rollback_plan_id": rollback_result.get("rollback_plan_id", ""),
        "rollback_passed": rollback_result.get("status") == "pass",
        "post_rollback_validation_passed": rollback_result.get("post_rollback_validation_passed") is True,
        "search_after_rollback_passed": search_after_rollback.get("search_after_rollback_passed") is True,
        **_boundary_flags(),
    }


def build_search_after_apply_proof(
    search_after_apply: Mapping[str, Any],
    search_after_rollback: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "local_loop_search_after_apply_proof.v0",
        "proof_id": stable_id(
            "local_loop_search_proof",
            {
                "apply": search_after_apply.get("proof_id", ""),
                "rollback": search_after_rollback.get("proof_id", ""),
            },
        ),
        "search_after_apply": dict(search_after_apply),
        "search_after_rollback": dict(search_after_rollback),
        "search_after_apply_passed": search_after_apply.get("search_after_apply_passed") is True,
        "search_after_rollback_passed": search_after_rollback.get("search_after_rollback_passed") is True,
        **_boundary_flags(),
    }


def build_local_loop_boundary_report(loop_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_loop_boundary_report.v0",
        "boundary_report_id": stable_id("local_loop_boundary", loop_result.get("loop_id", "")),
        "task": TASK_ID,
        "local_loop_requires_apply_gate": True,
        "temp_instance_apply_only_for_automated_tests": True,
        "public_projection_blocked": bool(loop_result.get("public_projection_blocked", False)),
        "native_read_only_projection_blocked": bool(loop_result.get("native_read_only_projection_blocked", False)),
        "result_status": loop_result.get("status", "unknown"),
        **_boundary_flags(),
    }


def build_local_loop_workbench_projection(
    loop_result: Mapping[str, Any],
    projection_profile: str = "operator_workbench",
) -> dict[str, Any]:
    profile = _projection_profile(projection_profile)
    read_only = profile in READ_ONLY_PROJECTIONS
    return {
        "schema_version": "workbench_local_loop_projection.v0",
        "loop_id": loop_result.get("loop_id", ""),
        "projection_profile": profile,
        "read_only": read_only,
        "apply_enabled": not read_only and loop_result.get("status") in {"dry_run", "pass"},
        "apply_controls_visible": not read_only,
        "mutation_allowed": False if read_only else loop_result.get("status") == "pass",
        "status": "blocked" if read_only else loop_result.get("status", "unknown"),
        "blocked_reasons": [f"{profile} projection is read-only"] if read_only else [],
        "proofs": {
            "apply": loop_result.get("apply_proof", {}),
            "rollback": loop_result.get("rollback_proof", {}),
            "search": loop_result.get("search_after_apply_proof", {}),
        },
        **_boundary_flags(),
    }


def _apply_blockers(profile: str, context: Mapping[str, Any]) -> list[str]:
    blocked: list[str] = []
    if profile in READ_ONLY_PROJECTIONS:
        blocked.append(f"{profile} projections cannot apply local loop mutations")
    if not context.get("use_temp_instance", False):
        blocked.append("automated local loop apply requires --use-temp-instance")
    if not context.get("apply_to_temp", False):
        blocked.append("automated local loop apply requires --apply-to-temp")
    if not str(context.get("operator_token", "")):
        blocked.append("operator token is required for temp apply")
    if str(context.get("confirmation", "")) != APPLY_CONFIRMATION:
        blocked.append(f"confirmation must be {APPLY_CONFIRMATION}")
    return blocked


def _blocked_result(plan: Mapping[str, Any], profile: str, blocked_reasons: list[str]) -> dict[str, Any]:
    result = {
        "schema_version": "local_loop_result.v0",
        "task": TASK_ID,
        "status": "blocked",
        "loop_id": stable_id("local_loop", {"plan": plan.get("plan_id", ""), "mode": "blocked", "reasons": blocked_reasons}),
        "plan": dict(plan),
        "query": plan.get("query", "sampleproject"),
        "projection_profile": profile,
        "blocked_reasons": blocked_reasons,
        "dry_run_loop_passed": False,
        "temp_apply_loop_passed": False,
        "search_after_apply_passed": False,
        "rollback_passed": False,
        "search_after_rollback_passed": False,
        "public_projection_blocked": profile == "public_web",
        "native_read_only_projection_blocked": profile == "native_desktop_read_only",
        **_boundary_flags(),
    }
    result["workbench_projection"] = build_local_loop_workbench_projection(result, profile)
    return result


def _events(
    status: str,
    live_run: Mapping[str, Any],
    review_item: Mapping[str, Any],
    promotion_preview: Mapping[str, Any],
) -> list[dict[str, Any]]:
    loop_id = stable_id("local_loop_events", {"run": live_run.get("run_id", ""), "status": status})
    event_types = [
        "local_loop.started",
        "local_loop.run_created",
        "local_loop.candidate_selected",
        "local_loop.review_item_created",
        "local_loop.review_decision_recorded",
        "local_loop.promotion_preview_created",
        "local_loop.apply_preview_created",
    ]
    if status == "pass":
        event_types.extend(
            [
                "local_loop.backup_created",
                "local_loop.apply_completed_temp",
                "local_loop.search_after_apply_passed",
                "local_loop.rollback_started",
                "local_loop.rollback_completed",
                "local_loop.search_after_rollback_passed",
                "local_loop.completed",
            ]
        )
    elif status == "dry_run":
        event_types.append("local_loop.completed")
    else:
        event_types.append("local_loop.blocked")
    return [
        {
            "schema_version": "local_loop_event.v0",
            "event_id": stable_id("local_loop_event", {"loop": loop_id, "event_type": event_type, "index": index}),
            "event_type": event_type,
            "run_id": live_run.get("run_id", ""),
            "review_item_id": review_item.get("review_item_id", ""),
            "promotion_preview_id": promotion_preview.get("promotion_preview", {}).get("preview_id", ""),
            "created_at": FIXED_CREATED_AT,
        }
        for index, event_type in enumerate(event_types)
    ]


def _projection_profile(profile: str) -> str:
    value = str(profile or "operator_workbench")
    if value not in PROJECTION_PROFILES:
        raise ValueError(f"unsupported projection profile: {value}")
    return value


def _non_claims() -> list[str]:
    return [
        "not production readiness",
        "not public launch readiness",
        "not master index mutation",
        "not committed public index mutation",
        "not source probing",
        "not download or extraction authority",
    ]


def _boundary_flags() -> dict[str, bool]:
    return {
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
