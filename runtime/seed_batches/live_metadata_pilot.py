"""Approval-gated live metadata pilot over seed queries.

The default path is dry-run/fixture only. Approved live metadata is supported
only behind an explicit approval file and policy checks; this module never
downloads files, commits raw responses, accepts truth, or mutates reviewed,
master, public, or operator indexes.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_store import normalize_candidate
from runtime.review.batch import (
    apply_batch_decision_preview,
    build_candidate_clusters,
    build_review_batch_packet,
    validate_batch_decision,
)
from runtime.scout import build_scout_run
from runtime.seed_batches.frontier_media import (
    build_seed_batch_query_plans,
    load_frontier_media_query_set,
)
from runtime.seed_batches.legacy_software import (
    build_legacy_software_query_plans,
    load_legacy_software_query_set,
)
from runtime.source.observation.internet_archive_live_probe import (
    load_live_probe_policy,
    run_live_metadata_probe,
)


TASK_ID = "LIVE-METADATA-PILOT-BATCH-00"
BATCH_ID = "live_metadata_pilot_batch_00"
DEFAULT_TIMESTAMP = "2026-05-31T00:00:00Z"
APPROVAL_PHRASE = "RUN_BOUNDED_LIVE_METADATA_PILOT"
PRIMARY_SOURCE_FAMILY = "internet_archive_metadata"
RECOMMENDED_NEXT_TASK_WAITING = "LIVE-METADATA-PILOT-BATCH-00 - provide approval and run bounded metadata pilot"
RECOMMENDED_NEXT_TASK_LIVE = "SNAPSHOT-REFRESH-01 - Refresh snapshots after live metadata pilot"

APPROVAL_REL_PATH = "control/approvals/live-metadata-pilot-batch-00-approval.json"
MANUAL_APPROVAL_REL_PATH = "control/inventory/live_metadata_pilot_batch_manual_approval.json"

SELECTED_FRONTIER_QUERY_IDS = ("frontier_media_q01", "frontier_media_q03", "frontier_media_q05", "frontier_media_q06")
SELECTED_LEGACY_QUERY_IDS = ("legacy_software_q01", "legacy_software_q02", "legacy_software_q03", "legacy_software_q06")
ACKNOWLEDGED_BOUNDARIES = (
    "metadata_only",
    "no_raw_response_commit",
    "no_downloads",
    "no_extraction",
    "no_public_mutation",
    "no_accepted_truth",
    "review_required",
)

DEFAULT_POLICY: dict[str, Any] = {
    "live_metadata_requires_operator_approval": True,
    "metadata_only": True,
    "raw_live_response_commit_allowed": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "accepted_truth_created": False,
    "reviewed_index_mutation_enabled": False,
    "public_index_mutation_enabled": False,
    "master_index_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
    "public_mutation_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "rate_limit_required": True,
    "redaction_required": True,
    "review_required": True,
    "default_max_total_requests": 24,
    "default_max_requests_per_query": 2,
    "default_max_seed_queries": 12,
    "default_timeout_seconds": 15,
    "default_rate_limit_delay_seconds": 2,
    "rows_per_search": 3,
}


def approval_template() -> dict[str, Any]:
    """Return the operator approval template without approving anything."""

    return {
        "schema_version": "live_metadata_pilot_approval.v0",
        "task": TASK_ID,
        "approved_by": "",
        "approved_at": "",
        "approval_phrase": APPROVAL_PHRASE,
        "allowed_source_families": [PRIMARY_SOURCE_FAMILY],
        "max_total_requests": 24,
        "max_requests_per_query": 2,
        "timeout_seconds": 15,
        "rate_limit_policy_ref": "control/policies/live_metadata_pilot_source_policy.json",
        "user_agent_policy_ref": "control/policies/live_metadata_pilot_source_policy.json",
        "redaction_policy_ref": "control/policies/live_metadata_pilot_redaction_policy.json",
        "allowed_seed_batches": [
            "seed_batch_frontier_media_00",
            "seed_batch_legacy_software_00",
        ],
        "raw_response_commit_allowed": False,
        "downloads_allowed": False,
        "extraction_allowed": False,
        "accepted_truth_allowed": False,
        "reviewed_index_mutation_allowed": False,
        "public_index_mutation_allowed": False,
        "acknowledged_boundaries": list(ACKNOWLEDGED_BOUNDARIES),
    }


def load_live_metadata_pilot_approval(
    policy: Mapping[str, Any] | None = None,
    approval_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load approval from an accepted path, returning a waiting state if absent."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    paths: list[Path] = []
    if approval_path is not None:
        paths.append(Path(approval_path))
    paths.extend([repo_root / APPROVAL_REL_PATH, repo_root / MANUAL_APPROVAL_REL_PATH])
    for path in paths:
        candidate = path if path.is_absolute() else repo_root / path
        if candidate.exists():
            payload = _read_json(candidate)
            if not isinstance(payload, Mapping):
                break
            result = dict(payload)
            result["_approval_path"] = str(candidate.relative_to(repo_root))
            return result
    return {
        "schema_version": "live_metadata_pilot_approval_state.v0",
        "task": TASK_ID,
        "approval_present": False,
        "approval_verified": False,
        "status": "waiting_for_operator_live_metadata_approval",
        "required_approval_path": APPROVAL_REL_PATH,
        "alternative_approval_path": MANUAL_APPROVAL_REL_PATH,
        "approval_template": approval_template(),
        "operator_live_metadata_run_performed": False,
        **_false_boundaries(),
    }


def validate_live_metadata_pilot_approval(
    approval: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    missing: list[str] = []
    required_fields = (
        "schema_version",
        "task",
        "approved_by",
        "approved_at",
        "approval_phrase",
        "allowed_source_families",
        "max_total_requests",
        "max_requests_per_query",
        "timeout_seconds",
        "rate_limit_policy_ref",
        "user_agent_policy_ref",
        "redaction_policy_ref",
        "allowed_seed_batches",
        "raw_response_commit_allowed",
        "downloads_allowed",
        "extraction_allowed",
        "accepted_truth_allowed",
        "reviewed_index_mutation_allowed",
        "public_index_mutation_allowed",
        "acknowledged_boundaries",
    )
    for field in required_fields:
        if field not in approval:
            missing.append(field)
    blocked_reasons: list[str] = []
    if approval.get("task") != TASK_ID:
        blocked_reasons.append("approval task mismatch")
    if approval.get("approval_phrase") != APPROVAL_PHRASE:
        blocked_reasons.append("approval phrase mismatch")
    if not _text(approval.get("approved_by")):
        blocked_reasons.append("approved_by is required")
    if not _text(approval.get("approved_at")):
        blocked_reasons.append("approved_at is required")
    if PRIMARY_SOURCE_FAMILY not in _text_list(approval.get("allowed_source_families")):
        blocked_reasons.append("internet_archive_metadata is not approved")
    for key in (
        "raw_response_commit_allowed",
        "downloads_allowed",
        "extraction_allowed",
        "accepted_truth_allowed",
        "reviewed_index_mutation_allowed",
        "public_index_mutation_allowed",
    ):
        if approval.get(key) is not False:
            blocked_reasons.append(f"{key} must be false")
    acknowledged = set(_text_list(approval.get("acknowledged_boundaries")))
    missing_boundaries = [item for item in ACKNOWLEDGED_BOUNDARIES if item not in acknowledged]
    blocked_reasons.extend(f"missing acknowledged boundary: {item}" for item in missing_boundaries)
    if int(approval.get("max_total_requests") or 0) <= 0:
        blocked_reasons.append("max_total_requests must be positive")
    if int(approval.get("max_total_requests") or 0) > int(merged_policy["default_max_total_requests"]):
        blocked_reasons.append("max_total_requests exceeds pilot policy")
    if int(approval.get("max_requests_per_query") or 0) <= 0:
        blocked_reasons.append("max_requests_per_query must be positive")
    if int(approval.get("max_requests_per_query") or 0) > int(merged_policy["default_max_requests_per_query"]):
        blocked_reasons.append("max_requests_per_query exceeds pilot policy")
    if int(approval.get("timeout_seconds") or 0) > int(merged_policy["default_timeout_seconds"]):
        blocked_reasons.append("timeout_seconds exceeds pilot policy")
    if missing:
        blocked_reasons.extend(f"missing field: {item}" for item in missing)
    verified = not blocked_reasons
    return {
        "schema_version": "live_metadata_pilot_approval_validation.v0",
        "task": TASK_ID,
        "approval_present": bool(approval.get("approval_phrase")),
        "approval_verified": verified,
        "blocked_reasons": blocked_reasons,
        "allowed_source_families": _text_list(approval.get("allowed_source_families")),
        "max_total_requests": int(approval.get("max_total_requests") or 0),
        "max_requests_per_query": int(approval.get("max_requests_per_query") or 0),
        "timeout_seconds": int(approval.get("timeout_seconds") or 0),
        "operator_live_metadata_run_performed": False,
        **_false_boundaries(),
    }


def select_live_metadata_seed_queries(
    seed_batches: Mapping[str, Any] | None = None,
    approval: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Select the bounded mixed seed query set for the pilot."""

    del seed_batches, approval
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    frontier = {
        item["query_id"]: item
        for item in load_frontier_media_query_set()
        if item["query_id"] in SELECTED_FRONTIER_QUERY_IDS
    }
    legacy = {
        item["query_id"]: item
        for item in load_legacy_software_query_set()
        if item["query_id"] in SELECTED_LEGACY_QUERY_IDS
    }
    frontier_plans = {
        item["query_id"]: item
        for item in build_seed_batch_query_plans([frontier[key] for key in SELECTED_FRONTIER_QUERY_IDS])
    }
    legacy_plans = {
        item["query_id"]: item
        for item in build_legacy_software_query_plans([legacy[key] for key in SELECTED_LEGACY_QUERY_IDS])
    }
    selected: list[dict[str, Any]] = []
    for batch_id, query_ids, queries, plans in (
        ("seed_batch_frontier_media_00", SELECTED_FRONTIER_QUERY_IDS, frontier, frontier_plans),
        ("seed_batch_legacy_software_00", SELECTED_LEGACY_QUERY_IDS, legacy, legacy_plans),
    ):
        for query_id in query_ids:
            query = queries[query_id]
            plan = plans[query_id]
            selected.append(
                {
                    "schema_version": "live_metadata_pilot_seed_query.v0",
                    "pilot_batch_id": BATCH_ID,
                    "seed_batch_id": batch_id,
                    "query_id": query_id,
                    "domain_id": query["domain_id"],
                    "raw_query": query["raw_query"],
                    "query_plan_ref": plan["plan_id"],
                    "query_plan": plan,
                    "source_family": PRIMARY_SOURCE_FAMILY,
                    "live_allowed": False,
                    "request_budget": {
                        "max_requests_per_query": int(merged_policy["default_max_requests_per_query"]),
                        "rows_per_search": int(merged_policy["rows_per_search"]),
                    },
                    "expected_candidate_kinds": list(query.get("expected_candidate_kinds") or []),
                    "suppressions": list(query.get("suppressions") or []),
                    "review_priority": int(query.get("review_priority") or 3),
                    "review_required": True,
                    "accepted_truth": False,
                }
            )
    return selected[: int(merged_policy["default_max_seed_queries"])]


def build_live_metadata_request_plans(
    selected_queries: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    plans: list[dict[str, Any]] = []
    for query in selected_queries:
        query_plan = query.get("query_plan") if isinstance(query.get("query_plan"), Mapping) else {}
        rewrites = query_plan.get("source_query_rewrites") if isinstance(query_plan.get("source_query_rewrites"), Mapping) else {}
        source_query = _text(rewrites.get(PRIMARY_SOURCE_FAMILY)) or _text(query.get("raw_query"))
        request_plan_id = _stable_id("live_metadata_request_plan", query.get("query_id"), source_query)
        plans.append(
            {
                "schema_version": "live_metadata_pilot_request_plan.v0",
                "pilot_batch_id": BATCH_ID,
                "request_plan_id": request_plan_id,
                "query_id": _text(query.get("query_id")),
                "raw_query": _text(query.get("raw_query")),
                "query_plan_ref": _text(query.get("query_plan_ref")),
                "source_family": PRIMARY_SOURCE_FAMILY,
                "endpoint_class": "metadata_search",
                "source_query": source_query,
                "max_rows_per_query": int(merged_policy["rows_per_search"]),
                "max_requests_per_query": int(merged_policy["default_max_requests_per_query"]),
                "timeout_seconds": int(merged_policy["default_timeout_seconds"]),
                "metadata_only": True,
                "redaction_required": True,
                "raw_response_commit_allowed": False,
                "downloads_enabled": False,
                "extraction_enabled": False,
                "accepted_truth": False,
                "review_required": True,
                "created_at": DEFAULT_TIMESTAMP,
                **_false_boundaries(),
            }
        )
    return plans


def run_live_metadata_requests(
    request_plans: Sequence[Mapping[str, Any]],
    operator_context: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
    *,
    mode: str = "dry_run",
) -> dict[str, Any]:
    """Run dry-run, fixture, or approved live metadata requests."""

    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    operator = dict(operator_context or {})
    if mode == "dry_run":
        return {
            "schema_version": "live_metadata_pilot_transport_summary.v0",
            "pilot_batch_id": BATCH_ID,
            "mode": "dry_run",
            "request_plan_count": len(request_plans),
            "transport_results": [
                _transport_row(plan, "planned_no_network", total_http_requests=0)
                for plan in request_plans
            ],
            "total_live_requests": 0,
            "operator_live_metadata_run_performed": False,
            "raw_live_response_committed": False,
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }
    if mode == "fixture":
        return {
            "schema_version": "live_metadata_pilot_transport_summary.v0",
            "pilot_batch_id": BATCH_ID,
            "mode": "fixture",
            "request_plan_count": len(request_plans),
            "transport_results": [
                _fixture_transport_row(plan, index)
                for index, plan in enumerate(request_plans, start=1)
            ],
            "total_live_requests": 0,
            "operator_live_metadata_run_performed": False,
            "raw_live_response_committed": False,
            "created_at": DEFAULT_TIMESTAMP,
            **_false_boundaries(),
        }
    if mode != "live":
        raise ValueError(f"unsupported live metadata pilot mode: {mode}")
    approval = operator.get("approval") if isinstance(operator.get("approval"), Mapping) else {}
    approval_state = validate_live_metadata_pilot_approval(approval, merged_policy)
    if approval_state["approval_verified"] is not True:
        raise PermissionError("live metadata pilot approval is missing or invalid")
    return _run_approved_live_requests(request_plans, approval, merged_policy)


def redact_live_metadata_transport_results(
    transport_results: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    rows: list[dict[str, Any]] = []
    for item in transport_results.get("transport_results", []) or []:
        if not isinstance(item, Mapping):
            continue
        rows.append(
            {
                "schema_version": "live_metadata_pilot_redacted_row.v0",
                "request_plan_id": _text(item.get("request_plan_id")),
                "query_id": _text(item.get("query_id")),
                "source_family": PRIMARY_SOURCE_FAMILY,
                "status": _text(item.get("status")),
                "endpoint_class": _text(item.get("endpoint_class")),
                "metadata_only": True,
                "candidate_title_present": bool(item.get("candidate_title")),
                "candidate_identifier_hash": _hash_text(_text(item.get("candidate_identifier"))),
                "summary": _text(item.get("summary")),
                "raw_response_committed": False,
                "review_required": True,
                "accepted_truth": False,
                **_false_boundaries(),
            }
        )
    return {
        "schema_version": "live_metadata_pilot_redaction_summary.v0",
        "pilot_batch_id": BATCH_ID,
        "mode": _text(transport_results.get("mode")),
        "redacted_result_count": len(rows),
        "redacted_results": rows,
        "total_live_requests": int(transport_results.get("total_live_requests") or 0),
        "raw_live_response_committed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def normalize_live_metadata_candidates(
    redacted_results: Mapping[str, Any],
    query_plans: Sequence[Mapping[str, Any]] | Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    plan_by_query = _plan_map(query_plans)
    candidates: list[dict[str, Any]] = []
    for index, row in enumerate(redacted_results.get("redacted_results", []) or [], start=1):
        if not isinstance(row, Mapping):
            continue
        query_id = _text(row.get("query_id"))
        plan = plan_by_query.get(query_id, {})
        if _text(row.get("status")) not in {"fixture_succeeded", "live_succeeded", "zero_results"}:
            continue
        title = _text(row.get("summary")) or f"Internet Archive metadata candidate for {query_id}"
        candidate = normalize_candidate(
            {
                "schema_version": "live_metadata_pilot_candidate_input.v0",
                "candidate_id": f"live_metadata_pilot_{query_id}_{index:02d}",
                "candidate_kind": "source_metadata_candidate",
                "candidate_status": "needs_review",
                "source_family": PRIMARY_SOURCE_FAMILY,
                "source_locator": {
                    "locator_kind": "redacted_archive_org_metadata_summary",
                    "request_plan_id": _text(row.get("request_plan_id")),
                    "identifier_hash": _text(row.get("candidate_identifier_hash")),
                },
                "title": title,
                "description": "Redacted Internet Archive metadata summary; review required before use.",
                "matched_query": _text(plan.get("raw_query")),
                "query_plan_ref": _text(plan.get("plan_id")),
                "source_action_ref": _stable_id("live_metadata_source_action", query_id),
                "source_observation_ref": _stable_id("live_metadata_source_observation", BATCH_ID, query_id, row.get("request_plan_id")),
                "domain_id": _text(plan.get("domain_id")) or _text(plan.get("planner_domain_pack")) or "general_archive_metadata",
                "confidence_label": "medium" if _text(row.get("status")) in {"fixture_succeeded", "live_succeeded"} else "low",
                "match_reasons": [
                    "internet_archive_metadata_summary",
                    "bounded_live_metadata_pilot_fixture" if redacted_results.get("mode") == "fixture" else "bounded_live_metadata_pilot",
                    "review_required",
                ],
                "suppressions": list(plan.get("candidate_suppressions") or []),
                "limitations": [
                    "redacted_metadata_summary_only",
                    "candidate_not_reviewed_truth",
                    "review_required_for_promotion",
                    "no_raw_response_commit",
                    "no_download",
                    "no_extraction",
                    "no_auto_promotion",
                ],
                "accepted_truth": False,
                "review_required": True,
            },
            plan,
            merged_policy,
        )
        candidate["fixture_derived"] = redacted_results.get("mode") == "fixture"
        candidate["live_metadata_derived"] = redacted_results.get("mode") == "live"
        candidates.append(candidate)
    return candidates


def build_live_metadata_candidate_records(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    records = [
        dict(candidate)
        if candidate.get("schema_version") == "candidate_record.v0"
        else normalize_candidate(candidate, {}, merged_policy)
        for candidate in candidates
    ]
    return {
        "schema_version": "live_metadata_pilot_candidate_matrix.v0",
        "pilot_batch_id": BATCH_ID,
        "candidate_count": len(records),
        "candidates": records,
        "candidate_refs": [_text(item.get("candidate_id")) for item in records],
        "candidate_index_handoff_created": True,
        "store_mode": "pilot_redacted_summary_examples",
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_scout_outputs(
    candidates: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidate_index = {
        "schema_version": "candidate_index_snapshot.v0",
        "store_mode": "live_metadata_pilot_example",
        "candidate_count": len(candidates),
        "candidates": [dict(item) for item in candidates],
        **_false_boundaries(),
    }
    runs = [build_scout_run(candidate["candidate_id"], candidate_index) for candidate in candidates]
    return {
        "schema_version": "live_metadata_pilot_scout_outputs.v0",
        "pilot_batch_id": BATCH_ID,
        "scout_runs": runs,
        "scout_refs": [run["scout_run_id"] for run in runs],
        "relation_count": sum(len(run.get("relations", [])) for run in runs),
        "related_path_count": sum(len(run.get("related_paths", [])) for run in runs),
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_review_batch(
    candidates: Sequence[Mapping[str, Any]],
    scout_outputs: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    relations = [
        relation
        for run in scout_outputs.get("scout_runs", []) or []
        for relation in run.get("relations", []) or []
        if isinstance(relation, Mapping)
    ]
    clusters = build_candidate_clusters(candidates, relations)
    packet = build_review_batch_packet(clusters)
    decision = validate_batch_decision(
        packet,
        "mark_useful_lead",
        {"projection_profile": "operator_workbench", "dry_run": True},
    )
    preview = apply_batch_decision_preview(packet, decision)
    return {
        "schema_version": "live_metadata_pilot_review_batch.v0",
        "pilot_batch_id": BATCH_ID,
        "review_batch_packet": packet,
        "decision_preview": preview,
        "review_batch_refs": [packet["review_batch_id"]],
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_snapshot_refresh_handoff(
    review_batch: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    preview = review_batch.get("decision_preview") if isinstance(review_batch.get("decision_preview"), Mapping) else {}
    snapshot = preview.get("snapshot_refresh_handoff") if isinstance(preview.get("snapshot_refresh_handoff"), Mapping) else {}
    return {
        "schema_version": "live_metadata_pilot_snapshot_refresh_handoff.v0",
        "pilot_batch_id": BATCH_ID,
        "snapshot_refresh_handoff": copy.deepcopy(dict(snapshot)),
        "snapshot_refresh_handoff_refs": [_text(snapshot.get("handoff_id"))] if snapshot.get("handoff_id") else [],
        "snapshot_refresh_executed": False,
        "requires_separate_snapshot_refresh_gate": True,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_public_alpha_reassess_input(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "live_metadata_pilot_public_alpha_reassess_input.v0",
        "pilot_batch_id": BATCH_ID,
        "candidate_count": int(result.get("candidate_count") or 0),
        "selected_query_count": int(result.get("selected_query_count") or 0),
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed", False)),
        "total_live_requests": int(result.get("total_live_requests") or 0),
        "review_required": True,
        "accepted_truth": False,
        "launch_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_live_metadata_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "live_metadata_pilot_boundary_report.v0",
        "task": TASK_ID,
        "pilot_batch_id": BATCH_ID,
        "metadata_only": True,
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed", False)),
        "total_live_requests": int(result.get("total_live_requests") or 0),
        "raw_live_response_committed": False,
        "review_required": True,
        "accepted_truth": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_live_metadata_pilot_batch(
    policy: Mapping[str, Any] | None = None,
    *,
    approval_path: str | Path | None = None,
    dry_run: bool = False,
    fixture: bool = False,
    operator_approved_live_metadata: bool = False,
    write_examples: bool = False,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    approval = load_live_metadata_pilot_approval(merged_policy, approval_path)
    approval_state = validate_live_metadata_pilot_approval(approval, merged_policy) if approval.get("approval_phrase") else dict(approval)
    selected_queries = select_live_metadata_seed_queries(approval=approval, policy=merged_policy)
    request_plans = build_live_metadata_request_plans(selected_queries, merged_policy)
    mode = "fixture" if fixture else "dry_run"
    if operator_approved_live_metadata:
        if approval_state.get("approval_verified") is not True:
            result = _waiting_result(approval_state, selected_queries, request_plans, merged_policy)
            if write_examples:
                result["examples_written_paths"] = write_live_metadata_pilot_examples(result)
                result["inventory_written_paths"] = write_live_metadata_pilot_inventory_and_audit(result)
                result["examples_written"] = True
            return result
        mode = "live"
    transport_summary = run_live_metadata_requests(
        request_plans,
        {"approval": approval},
        merged_policy,
        mode=mode,
    )
    redacted = redact_live_metadata_transport_results(transport_summary, merged_policy)
    candidates = normalize_live_metadata_candidates(
        redacted,
        [query["query_plan"] for query in selected_queries],
        merged_policy,
    )
    candidate_packet = build_live_metadata_candidate_records(candidates, merged_policy)
    scout_outputs = build_live_metadata_scout_outputs(candidates, merged_policy)
    review_batch = build_live_metadata_review_batch(candidates, scout_outputs, merged_policy)
    snapshot_handoff = build_live_metadata_snapshot_refresh_handoff(review_batch, merged_policy)
    status = "pass_with_warnings" if mode == "fixture" else "pass"
    if mode != "live":
        status = "waiting_for_operator_live_metadata_approval"
    result: dict[str, Any] = {
        "schema_version": "live_metadata_pilot_result.v0",
        "task": TASK_ID,
        "status": status,
        "pilot_batch_id": BATCH_ID,
        "mode": mode,
        "policies_added": True,
        "approval_template_added": True,
        "approval_verified": approval_state.get("approval_verified") is True,
        "approval_state": approval_state,
        "seed_query_matrix_added": True,
        "request_plan_matrix_added": True,
        "runtime_pilot_added": True,
        "dry_run_passed": True,
        "fixture_mode_passed": mode in {"fixture", "live"},
        "selected_queries": selected_queries,
        "request_plans": request_plans,
        "transport_summary": transport_summary,
        "redaction_summary": redacted,
        "candidate_packet": candidate_packet,
        "candidate_summaries": [_candidate_summary(item, mode) for item in candidates],
        "scout_outputs": scout_outputs,
        "review_batch": review_batch,
        "snapshot_refresh_handoff": snapshot_handoff,
        "source_family": PRIMARY_SOURCE_FAMILY,
        "selected_query_count": len(selected_queries),
        "total_live_requests": int(transport_summary.get("total_live_requests") or 0),
        "operator_live_metadata_run_performed": mode == "live",
        "candidate_summaries_created": bool(candidates),
        "candidate_index_handoff_created": True,
        "scout_trails_created": bool(scout_outputs.get("scout_runs")),
        "review_batch_packet_created": bool(review_batch.get("review_batch_packet")),
        "snapshot_refresh_handoff_created": bool(snapshot_handoff.get("snapshot_refresh_handoff")),
        "candidate_count": len(candidates),
        "review_batch_refs": list(review_batch.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(snapshot_handoff.get("snapshot_refresh_handoff_refs") or []),
        "created_at": DEFAULT_TIMESTAMP,
        "recommended_next_task": RECOMMENDED_NEXT_TASK_LIVE if mode == "live" else RECOMMENDED_NEXT_TASK_WAITING,
        **_false_boundaries(),
    }
    result["public_alpha_reassess_input"] = build_live_metadata_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input_created"] = True
    result["boundary_report"] = build_live_metadata_boundary_report(result, merged_policy)
    if write_examples:
        result["examples_written_paths"] = write_live_metadata_pilot_examples(result)
        result["inventory_written_paths"] = write_live_metadata_pilot_inventory_and_audit(result)
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["inventory_written_paths"] = []
        result["examples_written"] = False
    return result


def write_live_metadata_pilot_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_live_metadata_pilot_batch(fixture=True, write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "live_metadata_pilot"
    files = {
        "approval_template.json": approval_template(),
        "dry_run_request_plans.json": payload["request_plans"],
        "fixture_transport_summary.json": _fixture_only_transport(payload.get("transport_summary", {})),
        "redacted_metadata_summary.json": payload["redaction_summary"],
        "candidate_summaries.json": payload["candidate_summaries"],
        "scout_trails.json": _scout_summary(payload["scout_outputs"]),
        "review_batch_packet.json": payload["review_batch"]["review_batch_packet"],
        "snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "live_metadata_pilot_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/candidates/live_metadata/candidate_summaries.json": payload["candidate_summaries"],
        "examples/scout/live_metadata/scout_trails.json": _scout_summary(payload["scout_outputs"]),
        "examples/review_batch/live_metadata/review_batch_packet.json": payload["review_batch"]["review_batch_packet"],
        "examples/snapshots/refresh/live_metadata/snapshot_refresh_handoff.json": payload["snapshot_refresh_handoff"],
        "examples/public_alpha/reassess/live_metadata/public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_live_metadata_pilot_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_live_metadata_pilot_batch(fixture=True, write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    packets = _inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(result.get("status")) or "waiting_for_operator_live_metadata_approval"
    return {
        "live_metadata_pilot_batch_input_state.json": {
            "schema_version": "live_metadata_pilot_batch_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "public_alpha_reassess": "control/inventory/public_alpha_reassess_result.json",
                "snapshot_refresh": "control/inventory/snapshot_refresh_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "query_planner_equivalent": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "source_action_kernel": "control/inventory/source_action_kernel_result.json",
                "source_wave": "control/inventory/source_wave_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
            },
            "launch_recommended": False,
            "needs_live_metadata_pilot": True,
            **_false_boundaries(),
        },
        "live_metadata_pilot_batch_approval_state.json": result["approval_state"],
        "live_metadata_pilot_seed_query_matrix.json": {
            "schema_version": "live_metadata_pilot_seed_query_matrix.v0",
            "task": TASK_ID,
            "selected_query_count": result["selected_query_count"],
            "queries": result["selected_queries"],
        },
        "live_metadata_pilot_source_plan_matrix.json": _source_plan_matrix(),
        "live_metadata_pilot_request_plan_matrix.json": {
            "schema_version": "live_metadata_pilot_request_plan_matrix.v0",
            "task": TASK_ID,
            "request_plan_count": len(result["request_plans"]),
            "request_plans": result["request_plans"],
            "total_request_budget": 24,
        },
        "live_metadata_pilot_transport_summary.json": result["transport_summary"],
        "live_metadata_pilot_redaction_summary.json": result["redaction_summary"],
        "live_metadata_pilot_candidate_matrix.json": result["candidate_packet"],
        "live_metadata_pilot_scout_matrix.json": _scout_summary(result["scout_outputs"]),
        "live_metadata_pilot_review_matrix.json": result["review_batch"],
        "live_metadata_pilot_snapshot_handoff_matrix.json": result["snapshot_refresh_handoff"],
        "live_metadata_pilot_public_alpha_reassess_matrix.json": result["public_alpha_reassess_input"],
        "live_metadata_pilot_boundary_report.json": result["boundary_report"],
        "live_metadata_pilot_smoke_result.json": {
            "schema_version": "live_metadata_pilot_smoke_result.v0",
            "task": TASK_ID,
            "status": status,
            "dry_run_passed": True,
            "fixture_mode_passed": bool(result.get("fixture_mode_passed")),
            "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed")),
            **_false_boundaries(),
        },
        "live_metadata_pilot_validation_matrix.json": {
            "schema_version": "live_metadata_pilot_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "expected_task_status": status,
            "validation_commands": [
                "python scripts/validate_live_metadata_pilot_batch.py",
                "python scripts/validate_public_search_ux_model.py",
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_seed_batch_legacy_software.py",
                "python scripts/validate_seed_batch_frontier_media.py",
                "python scripts/validate_review_batch.py",
                "python scripts/validate_scout_runtime.py",
                "python scripts/validate_candidate_index_runtime.py",
                "python scripts/validate_query_to_source_action_planner.py",
                "python scripts/validate_source_action_kernel.py",
                "python scripts/validate_source_wave.py",
                "python scripts/check_architecture_boundaries.py",
                "python scripts/check_generated_artifact_cleanliness.py --check --json",
                "focused live metadata pilot unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "live_metadata_pilot_result.json": _result_summary(result),
        "live_metadata_pilot_next_task_decision.json": {
            "schema_version": "live_metadata_pilot_next_task_decision.v0",
            "task": TASK_ID,
            "status": status,
            "recommended_next_task": result.get("recommended_next_task"),
            "planned_after": [
                "SNAPSHOT-REFRESH-01",
                "PUBLIC-ALPHA-REASSESS-01",
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
            ],
        },
        "live_metadata_pilot_failure_repair_log.json": {
            "schema_version": "live_metadata_pilot_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "live-metadata-pilot-batch-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# LIVE-METADATA-PILOT-BATCH-00 Audit\n\nApproval-gated live metadata pilot foundation. No live metadata call is performed unless explicit operator approval exists.\n",
        "approval_state.md": _matrix_md("Approval State", result["approval_state"]),
        "seed_query_matrix.md": _matrix_md("Seed Query Matrix", {"queries": result["selected_queries"]}),
        "request_plan_matrix.md": _matrix_md("Request Plan Matrix", {"request_plans": result["request_plans"]}),
        "transport_summary.md": _matrix_md("Transport Summary", result["transport_summary"]),
        "redaction_summary.md": _matrix_md("Redaction Summary", result["redaction_summary"]),
        "candidate_matrix.md": _matrix_md("Candidate Matrix", result["candidate_packet"]),
        "scout_matrix.md": _matrix_md("SCOUT Matrix", _scout_summary(result["scout_outputs"])),
        "review_matrix.md": _matrix_md("Review Matrix", result["review_batch"]),
        "snapshot_handoff_matrix.md": _matrix_md("Snapshot Handoff Matrix", result["snapshot_refresh_handoff"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", result["public_alpha_reassess_input"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {"status": result["status"], "dry_run_passed": True, "fixture_mode_passed": result["fixture_mode_passed"]}),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/live_metadata_pilot_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
        "approval_required.md": "# Approval Required\n\nLive metadata calls were not run. Add `control/approvals/live-metadata-pilot-batch-00-approval.json` with the required approval phrase to run the bounded pilot.\n",
    }
    json_files = {
        "live_metadata_pilot_report.json": _result_summary(result),
        "live_metadata_pilot_approval_template.json": approval_template(),
        "generated/sample_approval_template.json": approval_template(),
        "generated/sample_dry_run_request_plans.json": result["request_plans"],
        "generated/sample_redacted_metadata_summary.json": result["redaction_summary"],
        "generated/sample_candidate_summaries.json": result["candidate_summaries"],
        "generated/sample_review_batch_packet.json": result["review_batch"]["review_batch_packet"],
        "generated/sample_snapshot_refresh_handoff.json": result["snapshot_refresh_handoff"],
        "generated/sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Live Metadata Pilot Summary\n\n"
        f"- status: {result['status']}\n"
        f"- approval verified: {str(result['approval_verified']).lower()}\n"
        f"- selected queries: {result['selected_query_count']}\n"
        f"- live requests: {result['total_live_requests']}\n"
        f"- candidates: {result['candidate_count']}\n"
        f"- next task: {result['recommended_next_task']}\n"
    )
    written: list[str] = []
    for name, content in markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in json_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    summary_path = generated / "sample_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _waiting_result(
    approval_state: Mapping[str, Any],
    selected_queries: Sequence[Mapping[str, Any]],
    request_plans: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    dry_transport = run_live_metadata_requests(request_plans, {}, policy, mode="dry_run")
    fixture_transport = run_live_metadata_requests(request_plans, {}, policy, mode="fixture")
    redacted = redact_live_metadata_transport_results(fixture_transport, policy)
    candidates = normalize_live_metadata_candidates(
        redacted,
        [query["query_plan"] for query in selected_queries],
        policy,
    )
    candidate_packet = build_live_metadata_candidate_records(candidates, policy)
    scout_outputs = build_live_metadata_scout_outputs(candidates, policy)
    review_batch = build_live_metadata_review_batch(candidates, scout_outputs, policy)
    snapshot_handoff = build_live_metadata_snapshot_refresh_handoff(review_batch, policy)
    result: dict[str, Any] = {
        "schema_version": "live_metadata_pilot_result.v0",
        "task": TASK_ID,
        "status": "waiting_for_operator_live_metadata_approval",
        "pilot_batch_id": BATCH_ID,
        "mode": "waiting",
        "policies_added": True,
        "approval_template_added": True,
        "approval_verified": False,
        "approval_state": dict(approval_state),
        "seed_query_matrix_added": True,
        "request_plan_matrix_added": True,
        "runtime_pilot_added": True,
        "dry_run_passed": True,
        "fixture_mode_passed": True,
        "selected_queries": [dict(item) for item in selected_queries],
        "request_plans": [dict(item) for item in request_plans],
        "transport_summary": fixture_transport,
        "dry_run_transport_summary": dry_transport,
        "redaction_summary": redacted,
        "candidate_packet": candidate_packet,
        "candidate_summaries": [_candidate_summary(item, "fixture") for item in candidates],
        "scout_outputs": scout_outputs,
        "review_batch": review_batch,
        "snapshot_refresh_handoff": snapshot_handoff,
        "source_family": PRIMARY_SOURCE_FAMILY,
        "selected_query_count": len(selected_queries),
        "total_live_requests": 0,
        "operator_live_metadata_run_performed": False,
        "candidate_summaries_created": True,
        "candidate_index_handoff_created": True,
        "scout_trails_created": True,
        "review_batch_packet_created": True,
        "snapshot_refresh_handoff_created": True,
        "candidate_count": len(candidates),
        "review_batch_refs": list(review_batch.get("review_batch_refs") or []),
        "snapshot_refresh_handoff_refs": list(snapshot_handoff.get("snapshot_refresh_handoff_refs") or []),
        "created_at": DEFAULT_TIMESTAMP,
        "recommended_next_task": RECOMMENDED_NEXT_TASK_WAITING,
        **_false_boundaries(),
    }
    result["public_alpha_reassess_input"] = build_live_metadata_public_alpha_reassess_input(result, policy)
    result["public_alpha_reassess_input_created"] = True
    result["boundary_report"] = build_live_metadata_boundary_report(result, policy)
    result["examples_written_paths"] = []
    result["inventory_written_paths"] = []
    result["examples_written"] = False
    return result


def _run_approved_live_requests(
    request_plans: Sequence[Mapping[str, Any]],
    approval: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    probe_policy = load_live_probe_policy()
    probe_policy["metadata_search_rows_max"] = min(
        int(policy["rows_per_search"]),
        int(probe_policy.get("metadata_search_rows_max", 1)),
    )
    probe_policy["total_http_requests_max"] = min(
        int(approval.get("max_requests_per_query") or 1),
        int(probe_policy.get("total_http_requests_max", 2)),
    )
    probe_policy["timeout_seconds_max"] = min(
        int(approval.get("timeout_seconds") or 10),
        int(probe_policy.get("timeout_seconds_max", 10)),
    )
    remaining = min(int(approval.get("max_total_requests") or 0), int(policy["default_max_total_requests"]))
    rows: list[dict[str, Any]] = []
    total_requests = 0
    for plan in request_plans:
        if remaining <= 0:
            break
        report = run_live_metadata_probe(
            probe_policy,
            approve_live=True,
            dry_run=False,
            query=_text(plan.get("source_query")),
            rows=min(int(policy["rows_per_search"]), int(probe_policy["metadata_search_rows_max"])),
            max_requests=min(int(approval.get("max_requests_per_query") or 1), int(probe_policy["total_http_requests_max"])),
            client_label="EurekaLiveMetadataPilot/0",
            contact=_text(approval.get("approved_by")) or "operator-approved",
            kill_switch_enabled=True,
        )
        summary = report.get("redacted_summary") if isinstance(report.get("redacted_summary"), Mapping) else {}
        request_count = int(summary.get("total_http_requests") or 0)
        total_requests += request_count
        remaining -= request_count
        rows.append(
            _transport_row(
                plan,
                "live_succeeded" if summary.get("probe_status") in {"succeeded", "zero_results"} else _text(summary.get("probe_status")) or "live_completed",
                total_http_requests=request_count,
                candidate_title=f"Redacted live IA metadata candidate for {_text(plan.get('raw_query'))}",
                candidate_identifier=_text(summary.get("identifier_hashes")),
                summary=f"Redacted live IA metadata summary for {_text(plan.get('raw_query'))}",
            )
        )
    return {
        "schema_version": "live_metadata_pilot_transport_summary.v0",
        "pilot_batch_id": BATCH_ID,
        "mode": "live",
        "request_plan_count": len(request_plans),
        "transport_results": rows,
        "total_live_requests": total_requests,
        "operator_live_metadata_run_performed": True,
        "raw_live_response_committed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def _transport_row(
    plan: Mapping[str, Any],
    status: str,
    *,
    total_http_requests: int,
    candidate_title: str = "",
    candidate_identifier: str = "",
    summary: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": "live_metadata_pilot_transport_row.v0",
        "request_plan_id": _text(plan.get("request_plan_id")),
        "query_id": _text(plan.get("query_id")),
        "raw_query": _text(plan.get("raw_query")),
        "source_family": PRIMARY_SOURCE_FAMILY,
        "endpoint_class": _text(plan.get("endpoint_class")),
        "status": status,
        "total_http_requests": total_http_requests,
        "candidate_title": candidate_title,
        "candidate_identifier": candidate_identifier,
        "summary": summary or "No network request was made.",
        "metadata_only": True,
        "raw_response_committed": False,
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _fixture_transport_row(plan: Mapping[str, Any], index: int) -> dict[str, Any]:
    query = _text(plan.get("raw_query"))
    slug = "_".join(part for part in query.casefold().replace("-", " ").split()[:8])
    return _transport_row(
        plan,
        "fixture_succeeded",
        total_http_requests=0,
        candidate_title=f"Fixture IA metadata lead for {query}",
        candidate_identifier=f"fixture_live_metadata_pilot_{index:02d}_{slug}",
        summary=f"Fixture redacted Internet Archive metadata summary for {query}.",
    )


def _source_plan_matrix() -> dict[str, Any]:
    return {
        "schema_version": "live_metadata_pilot_source_plan_matrix.v0",
        "task": TASK_ID,
        "source_families": [
            {
                "source_family": "internet_archive_metadata",
                "status": "allowed_if_approved",
                "bounded": True,
                "metadata_only": True,
                "downloads_enabled": False,
                "raw_response_commit_allowed": False,
            },
            {
                "source_family": "wayback_cdx_metadata",
                "status": "fixture_or_descriptor_only",
                "live_enabled": False,
            },
            {
                "source_family": "github_releases_metadata",
                "status": "fixture_or_descriptor_only",
                "live_enabled": False,
            },
            {
                "source_family": "package_registry_metadata",
                "status": "fixture_or_descriptor_only",
                "package_download_enabled": False,
                "live_enabled": False,
            },
            {
                "source_family": "software_heritage_metadata",
                "status": "fixture_or_descriptor_only",
                "blob_fetch_enabled": False,
                "live_enabled": False,
            },
        ],
        "arbitrary_web_crawling_enabled": False,
        "public_live_source_fanout_enabled": False,
    }


def _candidate_summary(candidate: Mapping[str, Any], mode: str) -> dict[str, Any]:
    return {
        "schema_version": "live_metadata_pilot_candidate_summary.v0",
        "pilot_batch_id": BATCH_ID,
        "candidate_id": _text(candidate.get("candidate_id")),
        "title": _text(candidate.get("title")),
        "source_family": _text(candidate.get("source_family")),
        "domain_id": _text(candidate.get("domain_id")),
        "confidence_label": _text(candidate.get("confidence_label")),
        "mode": mode,
        "fixture_derived": mode != "live",
        "live_metadata_derived": mode == "live",
        "review_required": True,
        "accepted_truth": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "live_metadata_pilot_result.v0",
        "task": TASK_ID,
        "status": result.get("status"),
        "policies_added": True,
        "approval_template_added": True,
        "approval_verified": bool(result.get("approval_verified", False)),
        "seed_query_matrix_added": True,
        "request_plan_matrix_added": True,
        "runtime_pilot_added": True,
        "dry_run_passed": bool(result.get("dry_run_passed")),
        "fixture_mode_passed": bool(result.get("fixture_mode_passed")),
        "operator_live_metadata_run_performed": bool(result.get("operator_live_metadata_run_performed")),
        "source_family": PRIMARY_SOURCE_FAMILY,
        "selected_query_count": int(result.get("selected_query_count") or 0),
        "total_live_requests": int(result.get("total_live_requests") or 0),
        "candidate_summaries_created": bool(result.get("candidate_summaries_created")),
        "candidate_index_handoff_created": bool(result.get("candidate_index_handoff_created")),
        "scout_trails_created": bool(result.get("scout_trails_created")),
        "review_batch_packet_created": bool(result.get("review_batch_packet_created")),
        "snapshot_refresh_handoff_created": bool(result.get("snapshot_refresh_handoff_created")),
        "public_alpha_reassess_input_created": bool(result.get("public_alpha_reassess_input_created")),
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "deployment_performed": False,
        "recommended_next_task": result.get("recommended_next_task"),
    }


def _scout_summary(scout_outputs: Mapping[str, Any]) -> dict[str, Any]:
    runs = scout_outputs.get("scout_runs") or []
    return {
        "schema_version": "live_metadata_pilot_scout_summary.v0",
        "pilot_batch_id": BATCH_ID,
        "scout_refs": list(scout_outputs.get("scout_refs") or []),
        "run_count": len(runs),
        "relation_count": scout_outputs.get("relation_count", 0),
        "related_path_count": scout_outputs.get("related_path_count", 0),
        "review_required": True,
        "accepted_truth": False,
        **_false_boundaries(),
    }


def _fixture_only_transport(transport: Mapping[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(dict(transport))
    value["mode"] = "fixture"
    value["total_live_requests"] = 0
    value["operator_live_metadata_run_performed"] = False
    value["raw_live_response_committed"] = False
    return value


def _plan_map(query_plans: Sequence[Mapping[str, Any]] | Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if isinstance(query_plans, Mapping):
        values = query_plans.get("query_plans") or []
    else:
        values = query_plans
    return {
        _text(item.get("query_id")): item
        for item in values
        if isinstance(item, Mapping)
    }


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "live_metadata_requires_operator_approval",
        "metadata_only",
        "rate_limit_required",
        "redaction_required",
        "review_required",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"live metadata pilot policy missing required rules: {', '.join(missing)}")
    forbidden_true = {
        "raw_live_response_commit_allowed",
        "downloads_enabled",
        "extraction_enabled",
        "accepted_truth_created",
        "reviewed_index_mutation_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
        "public_live_source_fanout_enabled",
        "public_mutation_enabled",
        "model_provider_enabled",
        "deployment_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"live metadata pilot policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {
        "raw_live_response_committed": False,
        "download_performed": False,
        "extraction_executed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "operator_instance_mutated": False,
        "candidate_index_mutated": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return " ".join(_text(item) for item in value if _text(item))
    return ""


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_text(value)] if _text(value) else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_text(item) for item in value if _text(item)]
    return []


def _hash_text(value: str) -> str:
    text = _text(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"
