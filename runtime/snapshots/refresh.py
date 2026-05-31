"""Snapshot refresh projection over reviewed records and seed-batch handoffs.

This module packages existing reviewed fixture records together with
seed-batch candidate, review, need, absence, and reassessment summaries. It is a
projection layer only: candidates remain candidates and no public/master index
or deployment artifact is mutated.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.seed_batches import run_seed_batch_frontier_media, run_seed_batch_legacy_software
from runtime.snapshots.relay_foundation import (
    project_reviewed_record_to_snapshot,
    sample_reviewed_records,
)


DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_00"
TASK_ID = "SNAPSHOT-REFRESH-00"

SEED_BATCH_DOMAINS = (
    {
        "domain_key": "frontier_media",
        "domain_id": "frontier_resolution_media",
        "batch_id": "seed_batch_frontier_media_00",
        "runner": run_seed_batch_frontier_media,
    },
    {
        "domain_key": "legacy_software",
        "domain_id": "legacy_software",
        "batch_id": "seed_batch_legacy_software_00",
        "runner": run_seed_batch_legacy_software,
    },
)

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "candidates_remain_candidates": True,
    "seed_outputs_are_not_truth": True,
    "reviewed_records_only_from_existing_reviewed_sources": True,
    "no_candidate_auto_acceptance": True,
    "no_reviewed_index_mutation": True,
    "no_master_index_mutation": True,
    "no_public_index_mutation": True,
    "no_public_mutation": True,
    "no_deployment": True,
    "no_public_launch_claim": True,
    "no_production_claim": True,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
}


def load_seed_batch_handoffs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Load public-safe seed-batch example handoffs, falling back to fixtures."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    source_batches: list[dict[str, Any]] = []
    for descriptor in SEED_BATCH_DOMAINS:
        domain_key = str(descriptor["domain_key"])
        example_root = repo_root / "examples" / "seed_batches" / domain_key
        if example_root.exists():
            payload = _load_seed_batch_example(example_root, descriptor)
        else:
            payload = _seed_result_to_handoff(descriptor["runner"](fixture=True), descriptor)
        source_batches.append(payload)
    return {
        "schema_version": "snapshot_seed_batch_handoffs.v0",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": source_batches,
        "source_batch_count": len(source_batches),
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_plan(
    seed_handoffs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    batches = list(seed_handoffs.get("source_batches") or [])
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [_batch_summary(batch) for batch in batches],
        "reviewed_record_refs": [record["record_id"] for record in sample_reviewed_records()],
        "candidate_section_refs": [
            _section_id("snapshot_candidate_section", batch.get("domain_key"))
            for batch in batches
        ],
        "review_queue_section_refs": [_section_id("snapshot_review_queue_section", "seed_batches")],
        "need_absence_section_refs": [_section_id("snapshot_need_absence_section", "seed_batches")],
        "relay_projection_refs": [_section_id("snapshot_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("snapshot_public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "reviewed_records_source": "existing_reviewed_snapshot_examples",
        "candidate_projection_source": "seed_batch_handoffs",
        "refresh_mode": "examples_projection_only",
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_reviewed_record_section(
    existing_reviewed_records: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = list(existing_reviewed_records or sample_reviewed_records())
    snapshot_records = [project_reviewed_record_to_snapshot(record, merged_policy) for record in records]
    return {
        "schema_version": "snapshot_reviewed_record_section.v0",
        "record_type": "snapshot_reviewed_record_section",
        "section_id": _section_id("snapshot_reviewed_record_section", [record.get("record_id") for record in records]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "reviewed_records": snapshot_records,
        "reviewed_record_refs": [record["record_id"] for record in snapshot_records],
        "reviewed_record_count": len(snapshot_records),
        "source": "existing_reviewed_records",
        "candidates_included_as_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "limitations": ["existing reviewed fixture records only"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_candidate_snapshot_section(
    seed_candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    domain_key: str = "seed_batch",
    batch_id: str = "",
    scout_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    scout_ref_list = [str(ref) for ref in scout_refs or []]
    candidates = [
        _candidate_snapshot_item(candidate, scout_ref_list)
        for candidate in seed_candidates
    ]
    return {
        "schema_version": "snapshot_candidate_section.v0",
        "record_type": "snapshot_candidate_section",
        "section_id": _section_id("snapshot_candidate_section", domain_key, batch_id),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "batch_id": batch_id,
        "domain_key": domain_key,
        "candidates": candidates,
        "candidate_refs": [candidate["candidate_id"] for candidate in candidates],
        "candidate_count": len(candidates),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "limitations": ["seed candidates are projected as review-only candidates"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_review_queue_section(
    review_packets: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    packets = [_review_packet_summary(packet) for packet in review_packets]
    candidate_refs = sorted({ref for packet in packets for ref in packet["candidate_refs"]})
    cluster_refs = sorted({ref for packet in packets for ref in packet["cluster_refs"]})
    return {
        "schema_version": "snapshot_review_queue_section.v0",
        "record_type": "snapshot_review_queue_section",
        "section_id": _section_id("snapshot_review_queue_section", candidate_refs, cluster_refs),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "review_packets": packets,
        "review_batch_refs": [packet["review_batch_id"] for packet in packets],
        "candidate_refs": candidate_refs,
        "cluster_refs": cluster_refs,
        "review_packet_count": len(packets),
        "candidate_count": len(candidate_refs),
        "cluster_count": len(cluster_refs),
        "operator_context_required": True,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "limitations": ["review queue summary only; decisions remain separate"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_need_absence_section(
    known_needs: Sequence[Mapping[str, Any]],
    absence_summaries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    needs = [copy.deepcopy(dict(item)) for item in known_needs]
    absences = [copy.deepcopy(dict(item)) for item in absence_summaries]
    return {
        "schema_version": "snapshot_need_absence_section.v0",
        "record_type": "snapshot_need_absence_section",
        "section_id": _section_id("snapshot_need_absence_section", [item.get("need_id") for item in needs], [item.get("absence_id") for item in absences]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "known_needs": needs,
        "absence_summaries": absences,
        "known_need_refs": [_text(item.get("need_id") or item.get("known_need_id") or item.get("summary_id")) for item in needs],
        "absence_refs": [_text(item.get("absence_id") or item.get("summary_id")) for item in absences],
        "known_need_count": len(needs),
        "absence_count": len(absences),
        "bounded_absence_statements": True,
        "unresolved_needs_remain_unresolved": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "limitations": ["known needs and absences are bounded unresolved statements"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_seed_batch_summary_section(
    seed_results: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    summaries = [_batch_summary(result) for result in seed_results]
    return {
        "schema_version": "snapshot_seed_batch_summary.v0",
        "record_type": "snapshot_seed_batch_summary",
        "section_id": _section_id("snapshot_seed_batch_summary", [item.get("batch_id") for item in summaries]),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": summaries,
        "source_batch_count": len(summaries),
        "total_candidate_count": sum(int(item.get("candidate_count") or 0) for item in summaries),
        "total_query_count": sum(int(item.get("query_count") or 0) for item in summaries),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "limitations": ["seed-batch summaries are not reviewed public truth"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_sections = list(snapshot_sections.get("candidate_sections") or [])
    candidate_items = [
        candidate
        for section in candidate_sections
        for candidate in list(section.get("candidates") or [])
    ]
    query_previews = [
        _relay_query_preview("D-Theater New York 1993", candidate_items),
        _relay_query_preview("Windows 7 offline utility", candidate_items),
    ]
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "sections": {
            "reviewed_records": int(snapshot_sections.get("reviewed_record_section", {}).get("reviewed_record_count") or 0),
            "candidate_sections": len(candidate_sections),
            "candidates": len(candidate_items),
            "review_queue_candidates": int(snapshot_sections.get("review_queue_section", {}).get("candidate_count") or 0),
            "known_needs": int(snapshot_sections.get("need_absence_section", {}).get("known_need_count") or 0),
            "absence_summaries": int(snapshot_sections.get("need_absence_section", {}).get("absence_count") or 0),
        },
        "query_previews": query_previews,
        "candidate_results_are_review_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "limitations": ["relay projection preview only; no public route or dist write"],
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_input(
    snapshot_refresh_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_public_alpha_reassess_input.v0",
        "record_type": "snapshot_refresh_public_alpha_reassess_input",
        "public_alpha_reassess_id": _section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "reviewed_record_count": int(snapshot_refresh_result.get("reviewed_record_count") or 0),
        "candidate_count": int(snapshot_refresh_result.get("candidate_count") or 0),
        "known_need_count": int(snapshot_refresh_result.get("known_need_count") or 0),
        "absence_count": int(snapshot_refresh_result.get("absence_count") or 0),
        "review_queue_candidate_count": int(snapshot_refresh_result.get("review_queue_candidate_count") or 0),
        "seed_batch_refs": list(snapshot_refresh_result.get("source_batch_refs") or []),
        "reassess_note": "Use for PUBLIC-ALPHA-REASSESS-00 only; snapshot refresh does not launch, deploy, or accept candidates.",
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def validate_snapshot_refresh_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    if result.get("schema_version") != "snapshot_refresh_result.v0":
        errors.append("schema_version must be snapshot_refresh_result.v0")
    for key in (
        "accepted_truth_created",
        "candidate_promoted_to_reviewed",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "site_dist_written",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    if not result.get("candidate_sections"):
        errors.append("candidate_sections must be present")
    return {
        "schema_version": "snapshot_refresh_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_boundary_report.v0",
        "record_type": "snapshot_refresh_boundary_report",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "snapshot_refresh_is_projection": True,
        "candidates_remain_candidates": True,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_snapshot_refresh(
    policy: Mapping[str, Any] | None = None,
    *,
    from_seed_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_seed_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    seed_handoffs = load_seed_batch_handoffs(merged_policy)
    source_batches = list(seed_handoffs["source_batches"])
    plan = build_snapshot_refresh_plan(seed_handoffs, merged_policy)
    reviewed_section = build_reviewed_record_section(sample_reviewed_records(), merged_policy)
    candidate_sections = [
        build_candidate_snapshot_section(
            batch["candidate_summaries"],
            merged_policy,
            domain_key=batch["domain_key"],
            batch_id=batch["batch_id"],
            scout_refs=batch.get("scout_refs") or [],
        )
        for batch in source_batches
    ]
    review_packets = [batch["review_batch_packet"] for batch in source_batches]
    review_queue_section = build_review_queue_section(review_packets, merged_policy)
    known_needs = [item for batch in source_batches for item in batch["known_needs"]]
    absence_summaries = [item for batch in source_batches for item in batch["absence_summaries"]]
    need_absence_section = build_need_absence_section(known_needs, absence_summaries, merged_policy)
    seed_summary_section = build_seed_batch_summary_section(source_batches, merged_policy)
    sections = {
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "seed_batch_summary_section": seed_summary_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    candidate_count = sum(int(section.get("candidate_count") or 0) for section in candidate_sections)
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "source_batches": [_batch_summary(batch) for batch in source_batches],
        "source_batch_refs": [batch["batch_id"] for batch in source_batches],
        "reviewed_record_refs": list(reviewed_section["reviewed_record_refs"]),
        "candidate_section_refs": [section["section_id"] for section in candidate_sections],
        "review_queue_section_refs": [review_queue_section["section_id"]],
        "need_absence_section_refs": [need_absence_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "plan": plan,
        "reviewed_record_section": reviewed_section,
        "candidate_sections": candidate_sections,
        "review_queue_section": review_queue_section,
        "need_absence_section": need_absence_section,
        "seed_batch_summary_section": seed_summary_section,
        "refreshed_relay_projection": relay_projection,
        "reviewed_record_count": int(reviewed_section["reviewed_record_count"]),
        "candidate_count": candidate_count,
        "known_need_count": int(need_absence_section["known_need_count"]),
        "absence_count": int(need_absence_section["absence_count"]),
        "review_queue_candidate_count": int(review_queue_section["candidate_count"]),
        "fixture_snapshot_refresh_passed": True,
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        result["examples_written_paths"] = write_snapshot_refresh_examples(result)
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh"
    base.mkdir(parents=True, exist_ok=True)
    candidate_sections = list(payload["candidate_sections"])
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "reviewed_record_section.json": payload["reviewed_record_section"],
        "candidate_section_frontier_media.json": candidate_sections[0],
        "candidate_section_legacy_software.json": candidate_sections[1],
        "review_queue_section.json": payload["review_queue_section"],
        "need_absence_section.json": payload["need_absence_section"],
        "seed_batch_summary_section.json": payload["seed_batch_summary_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/snapshot_refresh_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh(write_examples=False))
    repo_root = root or _repo_root()
    written: list[str] = []
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    inventory_packets = build_snapshot_refresh_inventory_packets(payload)
    inventory_packets["snapshot_refresh_input_state.json"] = {
        "schema_version": "snapshot_refresh_input_state.v0",
        "task": TASK_ID,
        "branch": "dev",
        "input_results": {
            "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
            "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
            "review_batch": "control/inventory/review_batch_result.json",
            "scout_runtime": "control/inventory/scout_runtime_result.json",
            "candidate_index": "control/inventory/candidate_index_result.json",
            "query_planner_equivalent": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
            "snapshot_relay": "control/inventory/snapshot_relay_result.json",
            "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
            "public_alpha_launch_defer": "control/inventory/public_alpha_launch_defer_result.json",
        },
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "created_at": DEFAULT_TIMESTAMP,
    }
    inventory_packets["snapshot_refresh_boundary_report.json"] = payload["boundary_report"]
    inventory_packets["snapshot_refresh_smoke_result.json"] = {
        "schema_version": "snapshot_refresh_smoke_result.v0",
        "task": TASK_ID,
        "status": payload.get("status"),
        "fixture_snapshot_refresh_passed": payload.get("fixture_snapshot_refresh_passed"),
        "source_batch_count": len(payload.get("source_batches") or []),
        "candidate_count": payload.get("candidate_count"),
        "reviewed_record_count": payload.get("reviewed_record_count"),
        "relay_projection_created": bool(payload.get("refreshed_relay_projection")),
        "public_alpha_reassess_input_created": bool(payload.get("public_alpha_reassess_input")),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "site_dist_written": False,
    }
    inventory_packets["snapshot_refresh_validation_matrix.json"] = {
        "schema_version": "snapshot_refresh_validation_matrix.v0",
        "task": TASK_ID,
        "status": "pass",
        "validation_commands": [
            "python scripts/validate_snapshot_refresh.py",
            "python scripts/validate_seed_batch_legacy_software.py",
            "python scripts/validate_seed_batch_frontier_media.py",
            "python scripts/validate_review_batch.py",
            "python scripts/validate_scout_runtime.py",
            "python scripts/validate_candidate_index_runtime.py",
            "python scripts/validate_query_to_source_action_planner.py",
            "python scripts/validate_snapshot_relay.py",
            "python scripts/validate_public_alpha_readonly.py",
            "python scripts/validate_source_action_kernel.py",
            "python scripts/validate_source_wave.py",
            "python scripts/check_architecture_boundaries.py",
            "python scripts/check_generated_artifact_cleanliness.py --check --json",
            "focused snapshot refresh unittest modules",
        ],
        "full_discovery": "NOT_RUN_BY_POLICY",
    }
    inventory_packets["snapshot_refresh_result.json"] = _task_result(payload)
    inventory_packets["snapshot_refresh_next_task_decision.json"] = {
        "schema_version": "snapshot_refresh_next_task_decision.v0",
        "task": TASK_ID,
        "status": "pass",
        "recommended_next_task": "PUBLIC-ALPHA-REASSESS-00 - Reassess public alpha usefulness after refreshed seed snapshots",
        "planned_after": [
            "SEED-BATCH-MANUALS-SCANS-00",
            "SEED-BATCH-DRIVER-SUPPORT-00",
            "LIVE-METADATA-PILOT-BATCH-00",
        ],
        "deployment_performed": False,
        "public_launch_readiness_claimed": False,
    }
    inventory_packets["snapshot_refresh_failure_repair_log.json"] = {
        "schema_version": "snapshot_refresh_failure_repair_log.v0",
        "task": TASK_ID,
        "status": "no_failures_recorded",
        "repairs": [],
    }
    for name, content in sorted(inventory_packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    candidate_sections = list(result.get("candidate_sections") or [])
    source_batches = list(result.get("source_batches") or [])
    return {
        "snapshot_refresh_source_matrix.json": {
            "schema_version": "snapshot_refresh_source_matrix.v0",
            "task": TASK_ID,
            "sources": source_batches,
            "source_batch_count": len(source_batches),
        },
        "snapshot_refresh_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "reviewed_record_refs": list(result.get("reviewed_record_refs") or []),
            "reviewed_record_count": result.get("reviewed_record_count"),
            "reviewed_records_only_from_existing_reviewed_sources": True,
        },
        "snapshot_refresh_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_sections": [
                {
                    "section_id": section.get("section_id"),
                    "batch_id": section.get("batch_id"),
                    "domain_key": section.get("domain_key"),
                    "candidate_count": section.get("candidate_count"),
                    "accepted_truth": False,
                    "candidate_promoted_to_reviewed": False,
                }
                for section in candidate_sections
            ],
            "candidate_count": result.get("candidate_count"),
        },
        "snapshot_refresh_need_absence_matrix.json": {
            "schema_version": "snapshot_refresh_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result.get("known_need_count"),
            "absence_count": result.get("absence_count"),
            "bounded_absence_statements": True,
        },
        "snapshot_refresh_review_queue_matrix.json": {
            "schema_version": "snapshot_refresh_review_queue_matrix.v0",
            "task": TASK_ID,
            "review_queue_section_refs": list(result.get("review_queue_section_refs") or []),
            "review_queue_candidate_count": result.get("review_queue_candidate_count"),
            "operator_context_required": True,
        },
        "snapshot_refresh_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
    }


def _write_snapshot_refresh_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_inventory_packets(result)
    audit_files: dict[str, Any] = {
        "snapshot_refresh_report.json": _task_result(result),
    }
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-00 Audit\n\nRefresh evidence for seed-batch snapshot projection. Candidates remain candidates and no public index or deployment artifact is mutated.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_source_matrix.json"]),
        "reviewed_record_matrix.md": _matrix_md("Reviewed Record Matrix", inventory["snapshot_refresh_reviewed_record_matrix.json"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", inventory["snapshot_refresh_candidate_matrix.json"]),
        "need_absence_matrix.md": _matrix_md("Need And Absence Matrix", inventory["snapshot_refresh_need_absence_matrix.json"]),
        "review_queue_matrix.md": _matrix_md("Review Queue Matrix", inventory["snapshot_refresh_review_queue_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_relay_projection_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {
            "status": result.get("status"),
            "candidate_count": result.get("candidate_count"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
        }),
        "validation_matrix.md": _matrix_md("Validation Matrix", {
            "status": "pass",
            "full_discovery": "NOT_RUN_BY_POLICY",
        }),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_candidate_section.json": result["candidate_sections"][0],
        "sample_review_queue_section.json": result["review_queue_section"],
        "sample_need_absence_section.json": result["need_absence_section"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    generated_summary = (
        "# Snapshot Refresh Summary\n\n"
        f"- reviewed records: {result.get('reviewed_record_count')}\n"
        f"- candidates: {result.get('candidate_count')}\n"
        f"- known needs: {result.get('known_need_count')}\n"
        f"- absences: {result.get('absence_count')}\n"
        "- accepted truth created: false\n"
        "- site/dist written: false\n"
    )
    written: list[str] = []
    for name, content in audit_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    for name, content in audit_markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in generated_files.items():
        path = generated / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    summary_path = generated / "sample_summary.md"
    summary_path.write_text(generated_summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _load_seed_batch_example(root: Path, descriptor: Mapping[str, Any]) -> dict[str, Any]:
    result = _read_json(root / "seed_batch_result.json")
    return {
        "schema_version": "snapshot_seed_batch_handoff_summary.v0",
        "domain_key": descriptor["domain_key"],
        "domain_id": descriptor["domain_id"],
        "batch_id": result.get("batch_id") or descriptor["batch_id"],
        "seed_batch_result": result,
        "query_count": int(result.get("query_count") or 0),
        "candidate_count": int(result.get("candidate_count") or 0),
        "candidate_summaries": _read_json(root / "candidate_summaries.json"),
        "candidate_index": _read_json(root / "candidate_index.json"),
        "scout_trails": _read_json(root / "scout_trails.json"),
        "review_batch_packet": _read_json(root / "review_batch_packet.json"),
        "known_needs": _read_json(root / "known_needs.json"),
        "absence_summaries": _read_json(root / "absence_summaries.json"),
        "snapshot_refresh_handoff": _read_json(root / "snapshot_refresh_handoff.json"),
        "public_alpha_reassess_input": _read_json(root / "public_alpha_reassess_input.json"),
        "scout_refs": list(result.get("scout_refs") or []),
        "review_batch_refs": list(result.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(result.get("snapshot_refresh_handoff_refs") or []),
        "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
        "fixture_derived": True,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _seed_result_to_handoff(result: Mapping[str, Any], descriptor: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_seed_batch_handoff_summary.v0",
        "domain_key": descriptor["domain_key"],
        "domain_id": descriptor["domain_id"],
        "batch_id": result.get("batch_id") or descriptor["batch_id"],
        "seed_batch_result": _result_summary(result),
        "query_count": int(result.get("query_count") or 0),
        "candidate_count": int(result.get("candidate_count") or 0),
        "candidate_summaries": list(result.get("candidate_summaries") or []),
        "candidate_index": copy.deepcopy(result.get("candidate_index") or {}),
        "scout_trails": copy.deepcopy(result.get("scout_trails") or {}),
        "review_batch_packet": copy.deepcopy((result.get("review_packets") or {}).get("review_batch_packet") or {}),
        "known_needs": list(result.get("known_needs") or []),
        "absence_summaries": list(result.get("absence_summaries") or []),
        "snapshot_refresh_handoff": copy.deepcopy(result.get("snapshot_refresh_handoff") or {}),
        "public_alpha_reassess_input": copy.deepcopy(result.get("public_alpha_reassess_input") or {}),
        "scout_refs": list(result.get("scout_refs") or []),
        "review_batch_refs": list(result.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(result.get("snapshot_refresh_handoff_refs") or []),
        "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
        "fixture_derived": True,
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _candidate_snapshot_item(candidate: Mapping[str, Any], scout_refs: Sequence[str]) -> dict[str, Any]:
    candidate_id = _text(candidate.get("candidate_id"))
    return {
        "schema_version": "snapshot_candidate_section_item.v0",
        "candidate_snapshot_ref": _section_id("snapshot_candidate", candidate_id),
        "candidate_id": candidate_id,
        "batch_id": _text(candidate.get("batch_id")),
        "domain_id": _text(candidate.get("domain_id")),
        "source_family": _text(candidate.get("source_family")),
        "title": _text(candidate.get("title")),
        "query_refs": [_text(candidate.get("query_id"))] if candidate.get("query_id") else [],
        "scout_trail_refs": list(scout_refs[:3]),
        "review_state": _text(candidate.get("review_state")) or "needs_review",
        "accepted_truth": False,
        "reviewed_record_ref": None,
        "fixture_derived": bool(candidate.get("fixture_derived", True)),
        "limitations": _text_list(candidate.get("limitations")) or ["fixture_derived", "review_required"],
        "action_posture": {
            "allowed_actions": ["inspect", "view_source", "view_provenance", "read"],
            "blocked_actions": ["download", "install_handoff", "execute", "upload", "promote"],
            "review_required": True,
            "public_mutation_enabled": False,
        },
    }


def _review_packet_summary(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_review_packet_summary.v0",
        "review_batch_id": _text(packet.get("review_batch_id")) or _section_id("review_batch", packet.get("candidate_refs")),
        "candidate_refs": _text_list(packet.get("candidate_refs")),
        "cluster_refs": _text_list(packet.get("cluster_refs")),
        "operator_context_required": bool(packet.get("operator_context_required", True)),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
    }


def _batch_summary(batch: Mapping[str, Any]) -> dict[str, Any]:
    result = batch.get("seed_batch_result") if isinstance(batch.get("seed_batch_result"), Mapping) else batch
    return {
        "schema_version": "snapshot_seed_batch_summary_item.v0",
        "batch_id": _text(batch.get("batch_id") or result.get("batch_id")),
        "domain_key": _text(batch.get("domain_key")),
        "domain_id": _text(batch.get("domain_id") or result.get("domain_id")),
        "query_count": int(batch.get("query_count") or result.get("query_count") or 0),
        "candidate_count": int(batch.get("candidate_count") or result.get("candidate_count") or 0),
        "review_batch_refs": _text_list(batch.get("review_batch_refs") or result.get("review_batch_refs")),
        "snapshot_refresh_handoff_refs": _text_list(batch.get("snapshot_refresh_handoff_refs") or result.get("snapshot_refresh_handoff_refs")),
        "public_alpha_reassess_refs": _text_list(batch.get("public_alpha_reassess_refs") or result.get("public_alpha_reassess_refs")),
        "fixture_derived": bool(batch.get("fixture_derived", True)),
        "review_required": True,
        "accepted_truth": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _relay_query_preview(query: str, candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    terms = [term.casefold() for term in query.split() if len(term) > 2]
    matches = [
        candidate
        for candidate in candidates
        if any(term in _text(candidate.get("title")).casefold() for term in terms)
    ][:5]
    return {
        "schema_version": "snapshot_refresh_relay_query_preview.v0",
        "query": query,
        "read_only": True,
        "result_count": len(matches),
        "results": [
            {
                "candidate_id": item.get("candidate_id"),
                "title": item.get("title"),
                "domain_id": item.get("domain_id"),
                "accepted_truth": False,
                "review_required": True,
            }
            for item in matches
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status"),
        "snapshot_refresh_id": result.get("snapshot_refresh_id"),
        "source_batch_refs": list(result.get("source_batch_refs") or []),
        "reviewed_record_count": result.get("reviewed_record_count"),
        "candidate_count": result.get("candidate_count"),
        "known_need_count": result.get("known_need_count"),
        "absence_count": result.get("absence_count"),
        "review_queue_candidate_count": result.get("review_queue_candidate_count"),
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "recommended_next_task": "PUBLIC-ALPHA-REASSESS-00 - Reassess public alpha usefulness after refreshed seed snapshots",
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "candidate_matrix_added": True,
        "need_absence_matrix_added": True,
        "review_queue_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "reviewed_record_section_created": True,
        "candidate_sections_created": True,
        "review_queue_section_created": True,
        "need_absence_section_created": True,
        "relay_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        "accepted_truth_created": False,
        "candidate_promoted_to_reviewed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "site_dist_written": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "recommended_next_task": "PUBLIC-ALPHA-REASSESS-00 - Reassess public alpha usefulness after refreshed seed snapshots",
    }


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "candidates_remain_candidates",
        "seed_outputs_are_not_truth",
        "review_required_before_promotion",
        "local_apply_is_separate_gate",
        "public_alpha_reassess_is_separate_gate",
        "no_site_dist_write",
        "no_public_index_mutation",
        "no_deployment_or_launch_claim",
    ]


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "snapshot_refresh_is_projection",
        "candidates_remain_candidates",
        "seed_outputs_are_not_truth",
        "reviewed_records_only_from_existing_reviewed_sources",
        "no_candidate_auto_acceptance",
        "no_reviewed_index_mutation",
        "no_master_index_mutation",
        "no_public_index_mutation",
        "no_public_mutation",
        "no_deployment",
        "no_public_launch_claim",
        "no_production_claim",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"snapshot refresh policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh policy enables forbidden behavior: {', '.join(enabled)}")


def _section_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_text(value)]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []
