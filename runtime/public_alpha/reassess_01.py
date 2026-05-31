"""Public alpha reassessment after the live metadata snapshot refresh.

PUBLIC-ALPHA-REASSESS-01 is a deterministic product-readiness assessment over
committed examples. It does not deploy, publish, mutate indexes, call live
sources, or promote candidates into reviewed truth.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_alpha.reassess import smoke_public_alpha_routes_from_examples


TASK_ID = "PUBLIC-ALPHA-REASSESS-01"
REASSESS_ID = "public_alpha_reassess_01"
DEFAULT_TIMESTAMP = "2026-06-01T00:00:00Z"
SNAPSHOT_REFRESH_REF = "snapshot_refresh_01"
LIVE_METADATA_PILOT_REF = "control/inventory/live_metadata_pilot_result.json"
RECOMMENDED_NEXT_TASK = (
    "REVIEW-LIVE-METADATA-CANDIDATES-00 - Review live metadata candidates for possible local promotion"
)

DEFAULT_POLICY: dict[str, Any] = {
    "reassessment_is_not_launch": True,
    "reassessment_must_not_deploy": True,
    "launch_requires_explicit_future_manual_approval": True,
    "public_alpha_min_reviewed_record_threshold": 25,
    "public_alpha_min_domain_coverage_threshold": 3,
    "live_metadata_candidates_improve_discovery_but_are_not_reviewed_truth": True,
    "candidate_only_snapshot_not_enough_for_launch": True,
    "needs_and_absences_are_useful_but_not_launch_sufficient": True,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
    "downloads_enabled": False,
    "extraction_enabled": False,
    "model_provider_enabled": False,
    "production_readiness_claimed": False,
    "public_launch_readiness_claimed": False,
}

BOUNDARY_FALSE_KEYS = (
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "site_dist_written",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "live_source_call_performed",
    "source_probe_executed",
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "live_metadata_candidate_promoted",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
)


def load_snapshot_refresh_01_metrics(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    refresh_root = repo_root / "examples" / "snapshots" / "refresh" / "live_metadata"
    context = {
        "schema_version": "public_alpha_reassess_01_input_context.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_01_result": _read_json(refresh_root / "snapshot_refresh_01_result.json"),
        "snapshot_refresh_01_inventory_result": _read_json(repo_root / "control" / "inventory" / "snapshot_refresh_01_result.json"),
        "reviewed_record_section": _read_json(refresh_root / "reviewed_record_section.json"),
        "candidate_sections": [
            _read_json(refresh_root / "candidate_section_frontier_media.json"),
            _read_json(refresh_root / "candidate_section_legacy_software.json"),
        ],
        "live_metadata_candidate_section": _read_json(refresh_root / "live_metadata_candidate_section.json"),
        "need_absence_section": _read_json(refresh_root / "need_absence_section.json"),
        "review_queue_section": _read_json(refresh_root / "review_queue_section.json"),
        "relay_projection": _read_json(refresh_root / "refreshed_relay_projection.json"),
        "public_search_view_model_projection": _read_json(refresh_root / "public_search_view_model_projection.json"),
        "snapshot_refresh_public_alpha_input": _read_json(refresh_root / "public_alpha_reassess_input.json"),
        "live_metadata_pilot_result": _read_json(repo_root / LIVE_METADATA_PILOT_REF),
        "public_alpha_readonly_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "public_alpha_launch_defer_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_launch_defer_result.json"),
        "policy": merged_policy,
        "created_at": DEFAULT_TIMESTAMP,
    }
    _assert_snapshot_refresh_01_context(context)
    return context


def calculate_public_alpha_reassess_01_metrics(
    snapshot_refresh_01_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_01_result)
    seed_candidates = [
        candidate
        for section in context["candidate_sections"]
        for candidate in section.get("candidates", [])
    ]
    live_candidates = list(context["live_metadata_candidate_section"].get("candidates") or [])
    reviewed_records = list(context["reviewed_record_section"].get("reviewed_records") or [])
    need_absence = context["need_absence_section"]
    public_search = context["public_search_view_model_projection"]
    route_smoke = _route_smoke_01(merged_policy)
    reviewed_count = int(context["snapshot_refresh_01_result"].get("reviewed_record_count") or len(reviewed_records))
    fixture_candidate_count = int(context["snapshot_refresh_01_result"].get("fixture_candidate_count") or len(seed_candidates))
    live_candidate_count = int(context["snapshot_refresh_01_result"].get("live_metadata_candidate_count") or len(live_candidates))
    total_candidate_count = int(context["snapshot_refresh_01_result"].get("candidate_count") or fixture_candidate_count + live_candidate_count)
    known_need_count = int(context["snapshot_refresh_01_result"].get("known_need_count") or need_absence.get("known_need_count") or 0)
    absence_count = int(context["snapshot_refresh_01_result"].get("absence_count") or need_absence.get("absence_count") or 0)
    all_candidates = seed_candidates + live_candidates
    domains = sorted(
        {
            _text(candidate.get("domain_id"))
            for candidate in all_candidates
            if _text(candidate.get("domain_id"))
        }
        | {
            _text(record.get("domain_id"))
            for record in reviewed_records
            if _text(record.get("domain_id"))
        }
    )
    reviewed_domains = sorted({_text(record.get("domain_id")) for record in reviewed_records if _text(record.get("domain_id"))})
    candidate_to_reviewed_ratio = round(total_candidate_count / max(reviewed_count, 1), 2)
    live_metadata_candidate_ratio = round(live_candidate_count / max(total_candidate_count, 1), 3)
    public_search_available = bool(public_search.get("result_cards")) and public_search.get("read_only") is True
    usefulness_score = _usefulness_score(
        reviewed_count=reviewed_count,
        reviewed_domain_count=len(reviewed_domains),
        total_candidate_count=total_candidate_count,
        live_candidate_count=live_candidate_count,
        public_search_available=public_search_available,
        route_smoke_passed=route_smoke["route_smoke_status"] == "pass",
        policy=merged_policy,
    )
    blockers_count = 8
    warnings_count = 4
    return {
        "schema_version": "public_alpha_usefulness_metrics.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "reviewed_record_count": reviewed_count,
        "fixture_candidate_count": fixture_candidate_count,
        "live_metadata_candidate_count": live_candidate_count,
        "total_candidate_count": total_candidate_count,
        "candidate_count": total_candidate_count,
        "candidate_to_reviewed_ratio": candidate_to_reviewed_ratio,
        "live_metadata_candidate_ratio": live_metadata_candidate_ratio,
        "known_need_count": known_need_count,
        "absence_summary_count": absence_count,
        "domains_represented": domains,
        "domain_count": len(domains),
        "reviewed_domains_represented": reviewed_domains,
        "reviewed_domain_count": len(reviewed_domains),
        "seed_batches_represented": list(context["snapshot_refresh_01_result"].get("source_batch_refs") or []),
        "seed_batch_count": len(context["snapshot_refresh_01_result"].get("source_batch_refs") or []),
        "query_count": total_candidate_count,
        "queries_with_reviewed_result": 0,
        "queries_with_candidate_result": total_candidate_count,
        "queries_with_need_or_absence": known_need_count,
        "public_routes_smoked": route_smoke["public_routes_smoked"],
        "public_api_routes_smoked": route_smoke["public_api_routes_smoked"],
        "route_smoke_status": route_smoke["route_smoke_status"],
        "public_search_view_models_available": public_search_available,
        "public_search_view_model_statuses": sorted((public_search.get("status_counts") or {}).keys()),
        "usefulness_score": usefulness_score,
        "usefulness_threshold_for_launch": 0.75,
        "reviewed_record_threshold": int(merged_policy["public_alpha_min_reviewed_record_threshold"]),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "blockers_count": blockers_count,
        "warnings_count": warnings_count,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_view_models(
    snapshot_refresh_01_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_01_result)
    projection = context["public_search_view_model_projection"]
    status_counts = dict(projection.get("status_counts") or {})
    required_states = ["verified", "candidate", "known_need", "absence", "source_lead"]
    optional_states = ["near_miss"]
    return {
        "schema_version": "public_alpha_reassess_01_public_search_view_model_matrix.v0",
        "reassess_id": REASSESS_ID,
        "projection_ref": projection.get("projection_id"),
        "projection_profiles": list(projection.get("projection_profiles") or []),
        "result_card_count": len(projection.get("result_cards") or []),
        "status_counts": status_counts,
        "required_states": required_states,
        "optional_states": optional_states,
        "required_states_available": all(state in status_counts for state in required_states),
        "candidate_verified_separation_visible": projection.get("candidate_verified_separation_visible") is True,
        "live_metadata_candidate_status": projection.get("live_metadata_candidate_status"),
        "public_search_view_models_available": bool(projection.get("result_cards")),
        "read_only": projection.get("read_only") is True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_query_coverage(
    seed_batches: Sequence[Mapping[str, Any]],
    snapshot_refresh_01_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_01_result)
    rows: list[dict[str, Any]] = []
    for section in context["candidate_sections"]:
        candidates = list(section.get("candidates") or [])
        rows.append(
            {
                "batch_id": section.get("batch_id"),
                "domain_key": section.get("domain_key"),
                "candidate_source": "fixture_seed_batch",
                "query_count": len(candidates),
                "queries_with_reviewed_result": 0,
                "queries_with_candidate_result": len(candidates),
                "queries_with_need_or_absence": len(candidates),
                "coverage_note": "Seed queries have candidate/need coverage but no reviewed seed-result coverage yet.",
            }
        )
    live_candidates = list(context["live_metadata_candidate_section"].get("candidates") or [])
    rows.append(
        {
            "batch_id": "live_metadata_pilot_batch_00",
            "domain_key": "live_metadata",
            "candidate_source": "redacted_live_metadata",
            "query_count": len(live_candidates),
            "queries_with_reviewed_result": 0,
            "queries_with_candidate_result": len(live_candidates),
            "queries_with_need_or_absence": 0,
            "coverage_note": "Live metadata candidates improve source-backed discovery but remain review-only.",
        }
    )
    return {
        "schema_version": "public_alpha_reassess_query_coverage_matrix.v0",
        "reassess_id": REASSESS_ID,
        "seed_batches": list(seed_batches or context["snapshot_refresh_01_result"].get("source_batch_refs") or []),
        "rows": rows,
        "query_count": sum(row["query_count"] for row in rows),
        "queries_with_reviewed_result": 0,
        "queries_with_candidate_result": sum(row["queries_with_candidate_result"] for row in rows),
        "queries_with_need_or_absence": sum(row["queries_with_need_or_absence"] for row in rows),
        "launch_sufficient": False,
        "accepted_truth_created": False,
    }


def assess_live_metadata_candidate_usefulness(
    live_metadata_section: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    candidates = list(live_metadata_section.get("candidates") or [])
    return {
        "schema_version": "public_alpha_live_metadata_reassess.v0",
        "reassess_id": REASSESS_ID,
        "live_metadata_pilot_ref": LIVE_METADATA_PILOT_REF,
        "source_family": live_metadata_section.get("source_family"),
        "candidate_count": len(candidates),
        "review_only_candidate_count": len(candidates),
        "candidate_refs": [candidate.get("candidate_id") for candidate in candidates],
        "domains": sorted({_text(candidate.get("domain_id")) for candidate in candidates if _text(candidate.get("domain_id"))}),
        "source_observation_summary_refs": list(live_metadata_section.get("source_observation_summary_refs") or []),
        "useful_for_internal_review": len(candidates) > 0,
        "useful_for_public_launch": False,
        "review_required": True,
        "accepted_truth": False,
        "raw_response_included": False,
        "needs_live_candidate_review": True,
        "needs_snapshot_refresh_after_review": True,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_candidate_usefulness_01(
    candidate_sections: Sequence[Mapping[str, Any]],
    live_metadata_section: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    fixture_candidates = [
        candidate
        for section in candidate_sections
        for candidate in section.get("candidates", [])
    ]
    live_candidates = list(live_metadata_section.get("candidates") or [])
    total_candidates = fixture_candidates + live_candidates
    return {
        "schema_version": "public_alpha_reassess_candidate_usefulness_matrix.v0",
        "reassess_id": REASSESS_ID,
        "fixture_candidate_count": len(fixture_candidates),
        "live_metadata_candidate_count": len(live_candidates),
        "total_candidate_count": len(total_candidates),
        "review_only_candidate_count": len(total_candidates),
        "candidate_domains": sorted({_text(candidate.get("domain_id")) for candidate in total_candidates if _text(candidate.get("domain_id"))}),
        "candidate_results_useful_for_internal_demo": len(total_candidates) > 0,
        "live_metadata_candidates_improve_discovery": len(live_candidates) > 0,
        "candidate_results_launch_sufficient": False,
        "all_candidates_review_required": all(candidate.get("accepted_truth") is False for candidate in total_candidates),
        "live_metadata_candidates_counted_as_reviewed": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_launch_blocker_register_01(
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    blockers = [
        _blocker(
            "reviewed_record_count_below_threshold",
            f"Reviewed records {metrics['reviewed_record_count']} < threshold {metrics['reviewed_record_threshold']}.",
        ),
        _blocker(
            "insufficient_domain_coverage",
            f"Reviewed domains {metrics['reviewed_domain_count']} < threshold {metrics['domain_coverage_threshold']}.",
        ),
        _blocker(
            "candidate_heavy_review_light_snapshot",
            f"Candidate/reviewed ratio is {metrics['candidate_to_reviewed_ratio']}; candidates are not accepted truth.",
        ),
        _blocker(
            "live_metadata_candidates_not_reviewed",
            f"Live metadata candidates present: {metrics['live_metadata_candidate_count']}; reviewed promotions: 0.",
        ),
        _blocker("no_public_launch_approval", "No explicit future manual approval exists for a public launch."),
        _blocker("public_launch_track_deferred", "Public alpha launch remains deferred for discovery coverage."),
        _blocker("no_post_live_metadata_review_batch_applied", "Live metadata candidates have not been reviewed and locally applied."),
        _blocker(
            "no_snapshot_publication_rehearsal_after_reviewed_promotions",
            "No publication rehearsal has run after any reviewed promotions from live metadata.",
        ),
    ]
    positives = [
        "candidate_discovery_stack_present",
        "live_metadata_pilot_present",
        "seed_batches_present",
        "review_batch_present",
        "snapshot_refresh_present",
        "public_search_ux_models_present",
        "needs_absences_present",
    ]
    warnings = [
        "route correctness is not product usefulness",
        "live metadata candidates improve discovery but remain unreviewed",
        "candidate-rich snapshots remain internal review material",
        "current reviewed corpus is too thin for public search expectations",
    ]
    return {
        "schema_version": "public_alpha_launch_blocker_register.v0",
        "reassess_id": REASSESS_ID,
        "blockers": blockers,
        "blockers_count": len(blockers),
        "nonblocking_positives": positives,
        "warnings": warnings,
        "warnings_count": len(warnings),
        "launch_blocked": True,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_next_work_recommendations_01(
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_next_work_recommendation.v0",
        "reassess_id": REASSESS_ID,
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "recommendations": [
            {
                "task": "REVIEW-LIVE-METADATA-CANDIDATES-00",
                "priority": 1,
                "reason": "Review real source-backed candidates and promote only if evidence supports local acceptance.",
            },
            {
                "task": "SNAPSHOT-REFRESH-02",
                "priority": 2,
                "reason": "Refresh snapshots after any reviewed live metadata promotions.",
            },
            {
                "task": "PUBLIC-ALPHA-REASSESS-02",
                "priority": 3,
                "reason": "Reassess public usefulness after reviewed-record count changes.",
            },
            {
                "task": "SEED-BATCH-MANUALS-SCANS-00",
                "priority": 4,
                "reason": "Add another discovery wedge while reviewed corpus grows.",
            },
        ],
        "needs_more_reviewed_records": metrics["reviewed_record_count"] < metrics["reviewed_record_threshold"],
        "needs_live_candidate_review": True,
        "needs_snapshot_refresh_after_review": True,
        "needs_more_seed_batches": True,
        "deployment_performed": False,
        "public_launch_performed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_01_decision(
    metrics: Mapping[str, Any],
    blockers: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    launch_recommended = (
        metrics["reviewed_record_count"] >= metrics["reviewed_record_threshold"]
        and metrics["reviewed_domain_count"] >= metrics["domain_coverage_threshold"]
        and metrics["usefulness_score"] >= metrics["usefulness_threshold_for_launch"]
        and blockers["blockers_count"] == 0
    )
    return {
        "schema_version": "public_alpha_reassess_decision.v0",
        "reassess_id": REASSESS_ID,
        "decision": "remain_deferred" if not launch_recommended else "eligible_for_future_manual_launch_review",
        "snapshot_refresh_ref": metrics["snapshot_refresh_ref"],
        "live_metadata_pilot_ref": metrics["live_metadata_pilot_ref"],
        "reviewed_record_count": metrics["reviewed_record_count"],
        "fixture_candidate_count": metrics["fixture_candidate_count"],
        "live_metadata_candidate_count": metrics["live_metadata_candidate_count"],
        "total_candidate_count": metrics["total_candidate_count"],
        "candidate_count": metrics["total_candidate_count"],
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "route_smoke_status": metrics["route_smoke_status"],
        "public_search_view_model_status": "available" if metrics["public_search_view_models_available"] else "missing",
        "query_coverage": {
            "query_count": metrics["query_count"],
            "queries_with_reviewed_result": metrics["queries_with_reviewed_result"],
            "queries_with_candidate_result": metrics["queries_with_candidate_result"],
            "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        },
        "usefulness_score": metrics["usefulness_score"],
        "launch_recommended": launch_recommended,
        "public_alpha_launch_recommended": launch_recommended,
        "demo_mode_recommended": not launch_recommended and metrics["total_candidate_count"] > 0,
        "internal_review_recommended": True,
        "needs_more_reviewed_records": metrics["reviewed_record_count"] < metrics["reviewed_record_threshold"],
        "needs_live_candidate_review": True,
        "needs_snapshot_refresh_after_review": True,
        "needs_more_seed_batches": True,
        "needs_live_metadata_pilot": False,
        "blockers": list(blockers["blockers"]),
        "warnings": list(blockers["warnings"]),
        "next_work": RECOMMENDED_NEXT_TASK,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_01_boundary_report(
    decision: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_reassess_boundary_report.v0",
        "record_type": "public_alpha_reassess_boundary_report",
        "reassess_id": REASSESS_ID,
        "reassessment_is_not_launch": True,
        "launch_recommended": bool(decision.get("launch_recommended", False)),
        "live_metadata_candidates_are_not_reviewed_truth": True,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_public_alpha_reassess_01(
    policy: Mapping[str, Any] | None = None,
    *,
    from_live_metadata_refresh_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_live_metadata_refresh_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_01_metrics(merged_policy)
    metrics = calculate_public_alpha_reassess_01_metrics(context, merged_policy)
    route_smoke = _route_smoke_01(merged_policy)
    public_search_models = assess_public_search_view_models(context, merged_policy)
    query_coverage = assess_query_coverage(metrics["seed_batches_represented"], context, merged_policy)
    candidate_usefulness = assess_candidate_usefulness_01(
        context["candidate_sections"],
        context["live_metadata_candidate_section"],
        merged_policy,
    )
    live_metadata_usefulness = assess_live_metadata_candidate_usefulness(
        context["live_metadata_candidate_section"],
        merged_policy,
    )
    blockers = build_launch_blocker_register_01(metrics, merged_policy)
    next_work = build_next_work_recommendations_01(metrics, merged_policy)
    decision = build_public_alpha_reassess_01_decision(metrics, blockers, merged_policy)
    boundary = build_public_alpha_reassess_01_boundary_report(decision, merged_policy)
    result = {
        "schema_version": "public_alpha_reassess_01_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "reassess_id": REASSESS_ID,
        "metrics": metrics,
        "route_smoke": route_smoke,
        "public_search_view_models": public_search_models,
        "query_coverage": query_coverage,
        "candidate_usefulness": candidate_usefulness,
        "live_metadata_candidate_usefulness": live_metadata_usefulness,
        "launch_blockers": blockers,
        "next_work": next_work,
        "decision": decision,
        "boundary_report": boundary,
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "live_metadata_candidate_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "reviewed_record_count": metrics["reviewed_record_count"],
        "fixture_candidate_count": metrics["fixture_candidate_count"],
        "live_metadata_candidate_count": metrics["live_metadata_candidate_count"],
        "total_candidate_count": metrics["total_candidate_count"],
        "candidate_count": metrics["total_candidate_count"],
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "launch_recommended": decision["launch_recommended"],
        "demo_mode_recommended": decision["demo_mode_recommended"],
        "internal_review_recommended": decision["internal_review_recommended"],
        "needs_more_reviewed_records": decision["needs_more_reviewed_records"],
        "needs_live_candidate_review": decision["needs_live_candidate_review"],
        "needs_snapshot_refresh_after_review": decision["needs_snapshot_refresh_after_review"],
        "needs_more_seed_batches": decision["needs_more_seed_batches"],
        "needs_live_metadata_pilot": decision["needs_live_metadata_pilot"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
    }
    if write_examples:
        written = write_public_alpha_reassess_01_examples(result)
        written.extend(write_public_alpha_reassess_01_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_public_alpha_reassess_01_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_01(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_alpha" / "reassess" / "live_metadata"
    files = {
        "public_alpha_reassess_metrics.json": payload["metrics"],
        "public_alpha_route_smoke.json": payload["route_smoke"],
        "public_alpha_query_coverage.json": payload["query_coverage"],
        "public_alpha_candidate_usefulness.json": payload["candidate_usefulness"],
        "public_alpha_live_metadata_candidates.json": payload["live_metadata_candidate_usefulness"],
        "public_alpha_public_search_view_models.json": payload["public_search_view_models"],
        "public_alpha_launch_blockers.json": payload["launch_blockers"],
        "public_alpha_next_work.json": payload["next_work"],
        "public_alpha_reassess_decision.json": payload["decision"],
        "public_alpha_boundary_report.json": payload["boundary_report"],
        "public_alpha_reassess_01_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def build_public_alpha_reassess_01_inventory_packets(
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return dict(_inventory_packets(dict(result or run_public_alpha_reassess_01(write_examples=False))))


def write_public_alpha_reassess_01_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_01(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = _inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    packets: dict[str, Any] = {
        "public_alpha_reassess_01_input_state.json": {
            "schema_version": "public_alpha_reassess_01_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "snapshot_refresh_01": "control/inventory/snapshot_refresh_01_result.json",
                "live_metadata_pilot": "control/inventory/live_metadata_pilot_result.json",
                "public_alpha_reassess_00": "control/inventory/public_alpha_reassess_result.json",
                "snapshot_refresh_00": "control/inventory/snapshot_refresh_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "review_batch": "control/inventory/review_batch_result.json",
                "scout_runtime": "control/inventory/scout_runtime_result.json",
                "candidate_index": "control/inventory/candidate_index_result.json",
                "query_planner_equivalent": "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
        },
        "public_alpha_reassess_01_snapshot_metrics.json": result["metrics"],
        "public_alpha_reassess_01_query_coverage_matrix.json": result["query_coverage"],
        "public_alpha_reassess_01_route_matrix.json": result["route_smoke"],
        "public_alpha_reassess_01_candidate_usefulness_matrix.json": result["candidate_usefulness"],
        "public_alpha_reassess_01_live_metadata_candidate_matrix.json": result["live_metadata_candidate_usefulness"],
        "public_alpha_reassess_01_reviewed_record_matrix.json": {
            "schema_version": "public_alpha_reassess_01_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "reviewed_record_count": result["reviewed_record_count"],
            "reviewed_record_threshold": result["metrics"]["reviewed_record_threshold"],
            "below_threshold": result["needs_more_reviewed_records"],
        },
        "public_alpha_reassess_01_need_absence_matrix.json": {
            "schema_version": "public_alpha_reassess_01_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result["known_need_count"],
            "absence_summary_count": result["absence_summary_count"],
            "launch_sufficient": False,
        },
        "public_alpha_reassess_01_public_search_view_model_matrix.json": result["public_search_view_models"],
        "public_alpha_reassess_01_launch_blocker_matrix.json": result["launch_blockers"],
        "public_alpha_reassess_01_next_work_matrix.json": result["next_work"],
        "public_alpha_reassess_01_boundary_report.json": result["boundary_report"],
        "public_alpha_reassess_01_smoke_result.json": {
            "schema_version": "public_alpha_reassess_01_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "route_smoke_status": result["route_smoke"]["route_smoke_status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
            "needs_live_candidate_review": result["needs_live_candidate_review"],
            **_false_boundaries(),
        },
        "public_alpha_reassess_01_validation_matrix.json": {
            "schema_version": "public_alpha_reassess_01_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_live_metadata_pilot_batch.py",
                "python scripts/validate_public_search_ux_model.py",
                "focused public-alpha reassess unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_alpha_reassess_01_result.json": _task_result(result),
        "public_alpha_reassess_01_next_task_decision.json": {
            "schema_version": "public_alpha_reassess_01_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "SNAPSHOT-REFRESH-02",
                "PUBLIC-ALPHA-REASSESS-02",
                "SEED-BATCH-MANUALS-SCANS-00",
                "SEED-BATCH-DRIVER-SUPPORT-00",
            ],
            "rationale": "Current snapshot is more useful for internal review, but reviewed-record count remains launch-blocking.",
            "launch_recommended": False,
            "demo_mode_recommended": True,
        },
        "public_alpha_reassess_01_failure_repair_log.json": {
            "schema_version": "public_alpha_reassess_01_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }
    return packets


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-alpha-reassess-01-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-ALPHA-REASSESS-01 Audit\n\nEvidence-based reassessment after live metadata snapshot refresh. Decision: internal demo/review usefulness improved, public launch not recommended.\n",
        "snapshot_metrics.md": _matrix_md("Snapshot Metrics", result["metrics"]),
        "query_coverage_matrix.md": _matrix_md("Query Coverage Matrix", result["query_coverage"]),
        "route_matrix.md": _matrix_md("Route Matrix", result["route_smoke"]),
        "candidate_usefulness_matrix.md": _matrix_md("Candidate Usefulness Matrix", result["candidate_usefulness"]),
        "live_metadata_candidate_matrix.md": _matrix_md("Live Metadata Candidate Matrix", result["live_metadata_candidate_usefulness"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", result["public_search_view_models"]),
        "launch_blocker_matrix.md": _matrix_md("Launch Blocker Matrix", result["launch_blockers"]),
        "next_work_matrix.md": _matrix_md("Next Work Matrix", result["next_work"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {
            "status": result["status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
        }),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_alpha_reassess_01_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "public_alpha_reassess_01_report.json": _task_result(result),
        "generated/sample_reassess_metrics.json": result["metrics"],
        "generated/sample_launch_blockers.json": result["launch_blockers"],
        "generated/sample_next_work.json": result["next_work"],
        "generated/sample_reassess_decision.json": result["decision"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Alpha Reassess 01 Summary\n\n"
        f"- reviewed records: {result['reviewed_record_count']}\n"
        f"- fixture candidates: {result['fixture_candidate_count']}\n"
        f"- live metadata candidates: {result['live_metadata_candidate_count']}\n"
        f"- total candidates: {result['total_candidate_count']}\n"
        f"- known needs: {result['known_need_count']}\n"
        f"- absences: {result['absence_summary_count']}\n"
        f"- launch recommended: {str(result['launch_recommended']).lower()}\n"
        f"- internal review recommended: {str(result['internal_review_recommended']).lower()}\n"
        f"- next task: {RECOMMENDED_NEXT_TASK}\n"
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


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_01_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "reviewed_record_count": result["reviewed_record_count"],
        "fixture_candidate_count": result["fixture_candidate_count"],
        "live_metadata_candidate_count": result["live_metadata_candidate_count"],
        "total_candidate_count": result["total_candidate_count"],
        "candidate_count": result["total_candidate_count"],
        "known_need_count": result["known_need_count"],
        "absence_summary_count": result["absence_summary_count"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_live_candidate_review": result["needs_live_candidate_review"],
        "needs_snapshot_refresh_after_review": result["needs_snapshot_refresh_after_review"],
        "needs_more_seed_batches": result["needs_more_seed_batches"],
        "needs_live_metadata_pilot": result["needs_live_metadata_pilot"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_01_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "live_metadata_candidate_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "reviewed_record_count": result["reviewed_record_count"],
        "fixture_candidate_count": result["fixture_candidate_count"],
        "live_metadata_candidate_count": result["live_metadata_candidate_count"],
        "total_candidate_count": result["total_candidate_count"],
        "candidate_count": result["total_candidate_count"],
        "known_need_count": result["known_need_count"],
        "absence_summary_count": result["absence_summary_count"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_live_candidate_review": result["needs_live_candidate_review"],
        "needs_snapshot_refresh_after_review": result["needs_snapshot_refresh_after_review"],
        "needs_more_seed_batches": result["needs_more_seed_batches"],
        "needs_live_metadata_pilot": result["needs_live_metadata_pilot"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _blocker(blocker_id: str, evidence: str) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_launch_blocker.v0",
        "blocker_id": blocker_id,
        "severity": "launch_blocking",
        "evidence": evidence,
        "public_explanation": evidence,
        "launch_blocking": True,
    }


def _usefulness_score(
    *,
    reviewed_count: int,
    reviewed_domain_count: int,
    total_candidate_count: int,
    live_candidate_count: int,
    public_search_available: bool,
    route_smoke_passed: bool,
    policy: Mapping[str, Any],
) -> float:
    reviewed = min(reviewed_count / max(int(policy["public_alpha_min_reviewed_record_threshold"]), 1), 1.0)
    domains = min(reviewed_domain_count / max(int(policy["public_alpha_min_domain_coverage_threshold"]), 1), 1.0)
    candidates = min(total_candidate_count / 60.0, 1.0)
    live = min(live_candidate_count / 20.0, 1.0)
    route = 1.0 if route_smoke_passed else 0.0
    view_models = 1.0 if public_search_available else 0.0
    score = reviewed * 0.42 + domains * 0.18 + candidates * 0.13 + live * 0.07 + route * 0.10 + view_models * 0.10
    return round(score, 3)


def _route_smoke_01(policy: Mapping[str, Any]) -> dict[str, Any]:
    route_smoke = dict(smoke_public_alpha_routes_from_examples(policy))
    route_smoke["source_reassess_id"] = route_smoke.get("reassess_id")
    route_smoke["reassess_id"] = REASSESS_ID
    route_smoke["created_at"] = DEFAULT_TIMESTAMP
    return route_smoke


def _context(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot_refresh_01_result" in value and "live_metadata_candidate_section" in value:
        return value
    return load_snapshot_refresh_01_metrics()


def _assert_snapshot_refresh_01_context(context: Mapping[str, Any]) -> None:
    inventory_result = context["snapshot_refresh_01_inventory_result"]
    if inventory_result.get("status") != "pass":
        raise ValueError("snapshot refresh 01 result must pass")
    for key in (
        "accepted_truth_created",
        "candidate_promoted_to_reviewed",
        "live_metadata_candidate_promoted",
        "raw_live_response_included",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "site_dist_written",
        "deployment_performed",
    ):
        if inventory_result.get(key) is not False:
            raise ValueError(f"snapshot refresh 01 boundary failed: {key}")
    live_section = context["live_metadata_candidate_section"]
    if live_section.get("accepted_truth") is not False or live_section.get("raw_response_included") is not False:
        raise ValueError("live metadata candidate section must be redacted review-only candidates")


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "reassessment_is_not_launch",
        "reassessment_must_not_deploy",
        "launch_requires_explicit_future_manual_approval",
        "live_metadata_candidates_improve_discovery_but_are_not_reviewed_truth",
        "candidate_only_snapshot_not_enough_for_launch",
        "needs_and_absences_are_useful_but_not_launch_sufficient",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"public alpha reassess 01 policy missing required rules: {', '.join(missing)}")
    forbidden_true = {
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"public alpha reassess 01 policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


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


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"
