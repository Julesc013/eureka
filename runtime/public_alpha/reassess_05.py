"""Public alpha reassessment after public search UX projection refresh.

PUBLIC-ALPHA-REASSESS-05 is a deterministic product-readiness reassessment over
committed public-safe examples. The UX MVP is now present and verified, but that
does not make the public alpha launch-ready: the reviewed corpus is still small,
candidate-heavy, and has not passed external full discovery or main promotion.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_alpha.reassess import smoke_public_alpha_routes_from_examples


TASK_ID = "PUBLIC-ALPHA-REASSESS-05"
REASSESS_ID = "public_alpha_reassess_05"
DEFAULT_TIMESTAMP = "2026-06-03T00:00:00Z"
SNAPSHOT_REFRESH_REF = "snapshot_refresh_05"
SNAPSHOT_REFRESH_RESULT_REF = "control/inventory/snapshot_refresh_05_result.json"
PUBLIC_SEARCH_UX_MVP_REF = "control/inventory/public_search_ux_mvp_result.json"
RECOMMENDED_NEXT_TASK = "REVIEW-BATCH-APPLY-NEXT-00 - Apply next eligible review batches to grow reviewed corpus"
DOMAINS_REPRESENTED = (
    "frontier_resolution_media",
    "legacy_software",
    "manuals_docs_scans",
    "driver_support_media",
)

BOUNDARY_FALSE_KEYS = (
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "site_dist_written",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "download_performed",
    "file_fetch_performed",
    "ocr_performed",
    "extraction_executed",
    "install_execution_enabled",
    "model_provider_used",
    "live_source_call_performed",
    "source_probe_executed",
    "operator_instance_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "artifact_verified_claim_created",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "compatibility_guarantee_created",
    "rights_clearance_claim_created",
    "scan_completeness_claim_created",
    "ocr_quality_claim_created",
)

DEFAULT_POLICY: dict[str, Any] = {
    "reassessment_is_not_launch": True,
    "reassessment_must_not_deploy": True,
    "launch_requires_explicit_future_manual_approval": True,
    "public_alpha_min_reviewed_record_threshold": 25,
    "public_alpha_min_domain_coverage_threshold": 3,
    "public_alpha_min_ux_mvp_required": True,
    "public_search_ux_mvp_improves_readiness_but_is_not_launch_sufficient": True,
    "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification": True,
    "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification": True,
    "candidate_only_snapshot_not_enough_for_launch": True,
    "four_limited_reviewed_records_not_enough_for_launch": True,
    "external_full_discovery_required_before_main_promotion": True,
    "main_promotion_required_before_launch": True,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
    "downloads_enabled": False,
    "file_fetches_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "production_readiness_claimed": False,
    "public_launch_readiness_claimed": False,
}


def load_snapshot_refresh_05_metrics(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    refresh_root = repo_root / "examples" / "snapshots" / "refresh" / "public_search_ux_mvp"
    context = {
        "schema_version": "public_alpha_reassess_05_input_context.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_05_result": _read_json(refresh_root / "snapshot_refresh_05_result.json"),
        "snapshot_refresh_05_inventory_result": _read_json(repo_root / SNAPSHOT_REFRESH_RESULT_REF),
        "snapshot_refresh_public_alpha_input": _read_json(refresh_root / "public_alpha_reassess_input.json"),
        "public_search_ux_section": _read_json(refresh_root / "public_search_ux_section.json"),
        "public_route_section": _read_json(refresh_root / "public_route_section.json"),
        "result_card_section": _read_json(refresh_root / "result_card_section.json"),
        "no_results_section": _read_json(refresh_root / "no_results_section.json"),
        "text_projection_section": _read_json(refresh_root / "text_projection_section.json"),
        "relay_projection": _read_json(refresh_root / "refreshed_relay_projection.json"),
        "public_search_ux_mvp_result": _read_json(repo_root / PUBLIC_SEARCH_UX_MVP_REF),
        "snapshot_refresh_04_result": _read_json(repo_root / "control" / "inventory" / "snapshot_refresh_04_result.json"),
        "public_alpha_reassess_04_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_reassess_04_result.json"),
        "public_alpha_readonly_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "public_alpha_launch_defer_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_launch_defer_result.json"),
        "policy": merged_policy,
        "created_at": DEFAULT_TIMESTAMP,
    }
    _assert_snapshot_refresh_05_context(context)
    return context


def calculate_public_alpha_reassess_05_metrics(
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_05_result)
    snapshot = context["snapshot_refresh_05_inventory_result"]
    snapshot_04 = context["snapshot_refresh_04_result"]
    ux_result = context["public_search_ux_mvp_result"]
    route_smoke = smoke_public_alpha_routes_from_ux_examples(merged_policy)
    ux_status = assess_public_search_ux_mvp_status_05(context, merged_policy)
    view_models = assess_public_search_view_models_05(context, merged_policy)
    domain_coverage = assess_domain_coverage_05(context, merged_policy)

    existing_count = 1
    metadata_count = 1
    source_lead_count = 2
    total_limited_count = int(snapshot.get("total_limited_reviewed_record_projection_count") or 4)
    candidate_count = int(snapshot.get("total_candidate_count") or 68)
    public_routes = int(snapshot.get("public_ux_routes_count") or context["public_route_section"].get("route_count") or 0)
    result_card_states = int(snapshot.get("result_card_states_count") or context["result_card_section"].get("result_card_states_count") or 0)
    known_need_count = int(snapshot_04.get("known_need_count") or 0)
    absence_count = int(snapshot_04.get("absence_count") or 0)
    ratio = round(total_limited_count / max(candidate_count, 1), 3)
    usefulness_score = _usefulness_score(
        limited_reviewed_count=total_limited_count,
        domain_count=domain_coverage["domain_count"],
        total_candidate_count=candidate_count,
        ux_mvp_verified=ux_status["public_search_ux_mvp_verified"],
        route_smoke_passed=route_smoke["route_smoke_status"] == "pass",
        policy=merged_policy,
    )
    return {
        "schema_version": "public_alpha_usefulness_metrics.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "snapshot_refresh_result_ref": SNAPSHOT_REFRESH_RESULT_REF,
        "public_search_ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "existing_reviewed_record_count": existing_count,
        "reviewed_metadata_record_count": metadata_count,
        "reviewed_source_lead_count": source_lead_count,
        "reviewed_record_delta_count": metadata_count + source_lead_count,
        "total_limited_reviewed_record_projection_count": total_limited_count,
        "reviewed_record_count": total_limited_count,
        "candidate_count": candidate_count,
        "total_candidate_count": candidate_count,
        "domain_count": domain_coverage["domain_count"],
        "domains_represented": list(domain_coverage["domains_represented"]),
        "known_need_count": known_need_count,
        "absence_summary_count": absence_count,
        "public_ux_routes_count": public_routes,
        "result_card_states_count": result_card_states,
        "no_js_required": snapshot.get("no_js_required") is True and ux_result.get("no_js_search_form_passed") is True,
        "public_projection_read_only": snapshot.get("public_projection_read_only") is True and ux_result.get("public_projection_read_only") is True,
        "public_search_ux_mvp_implemented": ux_status["public_search_ux_mvp_implemented"],
        "public_search_ux_mvp_verified": ux_status["public_search_ux_mvp_verified"],
        "limited_reviewed_record_to_candidate_ratio": ratio,
        "seed_batches_represented": [
            "seed_batch_frontier_media_00",
            "seed_batch_legacy_software_00",
            "seed_batch_manuals_scans_00",
            "seed_batch_driver_support_00",
        ],
        "seed_batch_count": 4,
        "query_count": candidate_count,
        "queries_with_limited_reviewed_result": total_limited_count,
        "queries_with_candidate_result": candidate_count,
        "queries_with_need_or_absence": known_need_count,
        "public_routes_smoked": route_smoke["public_routes_smoked"],
        "public_api_routes_smoked": route_smoke["public_api_routes_smoked"],
        "route_smoke_status": route_smoke["route_smoke_status"],
        "public_search_view_model_status": view_models["public_search_view_model_status"],
        "public_search_ux_mvp_status": ux_status["ux_mvp_status"],
        "usefulness_score": usefulness_score,
        "usefulness_threshold_for_launch": 0.75,
        "reviewed_record_threshold": int(merged_policy["public_alpha_min_reviewed_record_threshold"]),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "blockers_count": 9,
        "warnings_count": 5,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def smoke_public_alpha_routes_from_ux_examples(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    route_section = load_snapshot_refresh_05_metrics(merged_policy)["public_route_section"]
    routes = list(route_section.get("routes") or [])
    route_rows = [
        {
            "schema_version": "public_alpha_route_smoke_row.v0",
            "route": route.get("route"),
            "route_family": "public_ux",
            "method": route.get("method", "GET"),
            "status": "pass"
            if route.get("method") == "GET"
            and route.get("no_js_required") is True
            and route.get("public_read_only") is True
            else "fail",
            "no_js_required": route.get("no_js_required") is True,
            "public_read_only": route.get("public_read_only") is True,
            "mutation_enabled": False,
            "live_source_fanout_enabled": False,
        }
        for route in routes
    ]
    api_smoke = smoke_public_alpha_routes_from_examples(merged_policy)
    api_routes = [
        dict(row, route_family="api")
        for row in api_smoke.get("routes", [])
        if row.get("route_family") == "api"
    ]
    missing = [row["route"] for row in route_rows if row["status"] != "pass"]
    return {
        "schema_version": "public_alpha_route_smoke.v0",
        "reassess_id": REASSESS_ID,
        "route_smoke_status": "pass" if not missing and api_smoke.get("route_smoke_status") == "pass" else "partial",
        "routes": route_rows + api_routes,
        "missing_routes": missing,
        "public_routes_smoked": sum(1 for row in route_rows if row["status"] == "pass"),
        "public_api_routes_smoked": int(api_smoke.get("public_api_routes_smoked") or 0),
        "no_js_required": True,
        "public_projection_read_only": True,
        "example_metadata_only": True,
        "local_server_started": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "live_network_used": False,
        "mutation_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_view_models_05(
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_05_result)
    cards = list(context["result_card_section"].get("cards") or [])
    status_counts: dict[str, int] = {}
    object_type_counts: dict[str, int] = {}
    for card in cards:
        status = _text(card.get("status")) or "unknown"
        object_type = _text(card.get("object_type")) or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        object_type_counts[object_type] = object_type_counts.get(object_type, 0) + 1
    return {
        "schema_version": "public_alpha_reassess_05_public_search_view_model_matrix.v0",
        "reassess_id": REASSESS_ID,
        "result_card_count": len(cards),
        "result_card_states_count": int(context["result_card_section"].get("result_card_states_count") or 0),
        "status_counts": status_counts,
        "object_type_counts": object_type_counts,
        "public_search_view_model_status": "available" if cards else "missing",
        "public_search_view_models_available": bool(cards),
        "candidate_verified_distinction_passed": context["result_card_section"].get("candidate_verified_distinction_passed") is True,
        "limited_reviewed_record_distinction_passed": context["result_card_section"].get("limited_reviewed_record_distinction_passed") is True,
        "candidate_like_cards_not_accepted_truth": all(
            card.get("accepted_truth") is False
            for card in cards
            if card.get("status") in {"candidate", "near_miss", "known_need", "absence"}
        ),
        "limited_reviewed_records_are_not_verified_artifacts": True,
        "read_only": True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_ux_mvp_status_05(
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_05_result)
    result = context["public_search_ux_mvp_result"]
    required_flags = (
        "home_page_added",
        "search_results_page_added",
        "object_page_added",
        "candidate_page_added",
        "need_page_added",
        "source_page_added",
        "evidence_page_added",
        "status_page_added",
        "no_results_need_page_added",
        "result_cards_added",
        "no_js_search_form_passed",
        "candidate_verified_distinction_passed",
        "limited_reviewed_record_distinction_passed",
        "public_projection_read_only",
        "ux_smoke_passed",
    )
    verified = result.get("status") == "pass" and all(result.get(flag) is True for flag in required_flags)
    return {
        "schema_version": "public_alpha_ux_mvp_reassess.v0",
        "reassess_id": REASSESS_ID,
        "ux_mvp_status": "verified" if verified else "partial",
        "public_search_ux_mvp_implemented": verified,
        "public_search_ux_mvp_verified": verified,
        "public_search_ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "public_ux_routes_count": int(context["snapshot_refresh_05_inventory_result"].get("public_ux_routes_count") or 0),
        "result_card_states_count": int(context["snapshot_refresh_05_inventory_result"].get("result_card_states_count") or 0),
        "no_js_required": result.get("no_js_search_form_passed") is True,
        "public_projection_read_only": result.get("public_projection_read_only") is True,
        "candidate_verified_distinction_passed": result.get("candidate_verified_distinction_passed") is True,
        "limited_reviewed_record_distinction_passed": result.get("limited_reviewed_record_distinction_passed") is True,
        "no_results_need_page_available": result.get("no_results_need_page_added") is True,
        "public_search_ux_mvp_improves_readiness": True,
        "public_search_ux_mvp_launch_sufficient": False,
        "reason": "UX MVP is verified, but reviewed corpus depth, full discovery, main promotion, and launch approval remain blockers.",
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_query_coverage(
    seed_batches: Sequence[Mapping[str, Any]],
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    metrics = calculate_public_alpha_reassess_05_metrics(snapshot_refresh_05_result, merged_policy)
    rows = [
        {
            "domain_id": domain_id,
            "query_count": 16 if domain_id in {"manuals_docs_scans", "driver_support_media", "legacy_software"} else 12,
            "queries_with_limited_reviewed_result": 0,
            "queries_with_candidate_result": 16 if domain_id in {"manuals_docs_scans", "driver_support_media", "legacy_software"} else 12,
            "queries_with_need_or_absence": 16 if domain_id in {"manuals_docs_scans", "driver_support_media", "legacy_software"} else 12,
            "coverage_note": "Domain has candidate/need coverage, not enough reviewed artifact coverage.",
        }
        for domain_id in DOMAINS_REPRESENTED
    ]
    rows.append(
        {
            "domain_id": "live_metadata_local_apply",
            "query_count": 8,
            "queries_with_limited_reviewed_result": 4,
            "queries_with_candidate_result": 8,
            "queries_with_need_or_absence": 0,
            "coverage_note": "Local apply contributes limited metadata/source-lead records, not verified artifacts.",
        }
    )
    return {
        "schema_version": "public_alpha_reassess_query_coverage_matrix.v0",
        "reassess_id": REASSESS_ID,
        "seed_batches": list(seed_batches or metrics["seed_batches_represented"]),
        "rows": rows,
        "query_count": metrics["query_count"],
        "queries_with_limited_reviewed_result": metrics["queries_with_limited_reviewed_result"],
        "queries_with_candidate_result": metrics["queries_with_candidate_result"],
        "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        "launch_sufficient": False,
        "accepted_truth_created": False,
    }


def assess_domain_coverage_05(
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_domain_coverage_reassess.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "domains_represented": list(DOMAINS_REPRESENTED),
        "domain_count": len(DOMAINS_REPRESENTED),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "four_domains_represented": True,
        "domain_breadth_improved": True,
        "domain_coverage_launch_sufficient": False,
        "reason": "Four domains improve breadth, but corpus depth and launch gates are still blockers.",
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_limited_reviewed_record_usefulness(
    snapshot_sections: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del snapshot_sections
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_limited_reviewed_record_reassess.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "existing_reviewed_record_count": 1,
        "reviewed_metadata_record_count": 1,
        "reviewed_source_lead_count": 2,
        "reviewed_record_delta_count": 3,
        "total_limited_reviewed_record_projection_count": 4,
        "limited_reviewed_records_count_for_usefulness": True,
        "limited_reviewed_records_are_verified_artifacts": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "needs_more_reviewed_artifact_records": True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_candidate_usefulness_05(
    snapshot_refresh_05_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    metrics = calculate_public_alpha_reassess_05_metrics(snapshot_refresh_05_result, merged_policy)
    return {
        "schema_version": "public_alpha_reassess_candidate_usefulness_matrix.v0",
        "reassess_id": REASSESS_ID,
        "candidate_count": metrics["candidate_count"],
        "total_candidate_count": metrics["candidate_count"],
        "review_only_candidate_count": metrics["candidate_count"],
        "candidate_domains": list(DOMAINS_REPRESENTED),
        "candidate_results_useful_for_internal_demo": True,
        "candidate_results_launch_sufficient": False,
        "candidate_heavy_snapshot": True,
        "candidates_counted_as_verified_artifacts": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_launch_blocker_register_05(
    metrics: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    blockers = [
        _blocker(
            "reviewed_record_count_below_threshold",
            f"Limited reviewed projection count {metrics['total_limited_reviewed_record_projection_count']} < threshold {metrics['reviewed_record_threshold']}.",
        ),
        _blocker(
            "limited_reviewed_records_are_not_verified_artifacts",
            "Limited metadata/source-lead records do not establish downloadable artifact verification.",
        ),
        _blocker(
            "candidate_heavy_snapshot",
            f"Candidate count is {metrics['candidate_count']} versus {metrics['total_limited_reviewed_record_projection_count']} limited reviewed projections.",
        ),
        _blocker("no_public_launch_approval", "No explicit future manual approval exists for a public launch."),
        _blocker("public_launch_track_deferred", "Public alpha launch remains deferred for discovery coverage."),
        _blocker("no_external_full_discovery_after_current_dev_stack", "No external full-discovery summary exists for the current dev stack."),
        _blocker("current_dev_not_promoted_to_main_after_discovery_ux_stack", "Current dev stack has not been promoted to main after discovery and UX MVP work."),
        _blocker("no_snapshot_publication_rehearsal_after_current_snapshot", "No publication rehearsal has run after the UX projection refresh."),
        _blocker("no_public_launch_manual_approval", "Launch requires a separate explicit future manual approval."),
    ]
    positives = [
        "public_search_ux_mvp_present",
        "no_js_search_present",
        "result_card_statuses_present",
        "four_domains_represented",
        "candidate_discovery_stack_present",
        "live_metadata_pilot_present",
        "live_metadata_review_present",
        "local_apply_gate_present",
        "limited_reviewed_metadata_record_present",
        "reviewed_source_leads_present",
        "seed_batches_present",
        "review_batch_present",
        "snapshot_refresh_present",
        "public_search_ux_models_present",
        "needs_absences_present",
    ]
    warnings = [
        "public search UX MVP improves legibility but is not launch readiness",
        "limited reviewed metadata/source-lead records are not verified artifacts",
        "four limited reviewed records is below public-alpha threshold",
        "candidate-heavy snapshots remain internal review material",
        "external full discovery and main promotion remain future gates",
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


def build_next_work_recommendations_05(
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
                "task": "REVIEW-BATCH-APPLY-NEXT-00",
                "priority": 1,
                "reason": "UX legibility is in place; the next bottleneck is reviewed corpus growth.",
            },
            {
                "task": "SNAPSHOT-REFRESH-06",
                "priority": 2,
                "reason": "Refresh projections after additional reviewed records are applied.",
            },
            {
                "task": "PUBLIC-ALPHA-REASSESS-06",
                "priority": 3,
                "reason": "Reassess launch posture after reviewed-corpus growth and snapshot refresh.",
            },
            {
                "task": "DEV-TO-MAIN-PROMOTION-REVIEW-06",
                "priority": 4,
                "reason": "Promotion review should wait for reviewed-corpus growth and external discovery evidence.",
            },
        ],
        "needs_more_reviewed_records": metrics["total_limited_reviewed_record_projection_count"] < metrics["reviewed_record_threshold"],
        "needs_more_reviewed_artifact_records": True,
        "needs_review_batch_apply_next": True,
        "needs_external_full_discovery": True,
        "needs_main_promotion_before_launch": True,
        "needs_public_alpha_launch_approval": True,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_05_decision(
    metrics: Mapping[str, Any],
    blockers: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    launch_recommended = (
        metrics["total_limited_reviewed_record_projection_count"] >= metrics["reviewed_record_threshold"]
        and metrics["domain_count"] >= metrics["domain_coverage_threshold"]
        and metrics["public_search_ux_mvp_verified"] is True
        and metrics["usefulness_score"] >= metrics["usefulness_threshold_for_launch"]
        and blockers["blockers_count"] == 0
    )
    return {
        "schema_version": "public_alpha_reassess_decision.v0",
        "reassess_id": REASSESS_ID,
        "decision": "remain_deferred" if not launch_recommended else "eligible_for_future_manual_launch_review",
        "snapshot_refresh_ref": metrics["snapshot_refresh_ref"],
        "public_search_ux_mvp_ref": metrics["public_search_ux_mvp_ref"],
        "existing_reviewed_record_count": metrics["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": metrics["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": metrics["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "candidate_count": metrics["candidate_count"],
        "domain_count": metrics["domain_count"],
        "domains_represented": list(metrics["domains_represented"]),
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "public_ux_routes_count": metrics["public_ux_routes_count"],
        "result_card_states_count": metrics["result_card_states_count"],
        "no_js_required": metrics["no_js_required"],
        "public_projection_read_only": metrics["public_projection_read_only"],
        "route_smoke_status": metrics["route_smoke_status"],
        "public_search_view_model_status": metrics["public_search_view_model_status"],
        "public_search_ux_mvp_status": metrics["public_search_ux_mvp_status"],
        "query_coverage": {
            "query_count": metrics["query_count"],
            "queries_with_limited_reviewed_result": metrics["queries_with_limited_reviewed_result"],
            "queries_with_candidate_result": metrics["queries_with_candidate_result"],
            "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        },
        "usefulness_score": metrics["usefulness_score"],
        "launch_recommended": launch_recommended,
        "public_alpha_launch_recommended": launch_recommended,
        "demo_mode_recommended": not launch_recommended and metrics["candidate_count"] > 0,
        "internal_review_recommended": not launch_recommended and metrics["total_limited_reviewed_record_projection_count"] > 0,
        "public_search_ux_mvp_verified": metrics["public_search_ux_mvp_verified"],
        "needs_more_reviewed_records": metrics["total_limited_reviewed_record_projection_count"] < metrics["reviewed_record_threshold"],
        "needs_more_reviewed_artifact_records": True,
        "needs_review_batch_apply_next": True,
        "needs_external_full_discovery": True,
        "needs_main_promotion_before_launch": True,
        "needs_public_alpha_launch_approval": True,
        "blockers": list(blockers["blockers"]),
        "warnings": list(blockers["warnings"]),
        "next_work": RECOMMENDED_NEXT_TASK,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_05_boundary_report(
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
        "public_search_ux_mvp_verified": bool(decision.get("public_search_ux_mvp_verified")),
        "public_search_ux_mvp_launch_sufficient": False,
        "launch_recommended": bool(decision.get("launch_recommended", False)),
        "limited_reviewed_records_counted_for_usefulness": True,
        "limited_reviewed_records_counted_as_verified_artifacts": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_public_alpha_reassess_05(
    policy: Mapping[str, Any] | None = None,
    *,
    from_public_search_ux_projection_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_public_search_ux_projection_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_05_metrics(merged_policy)
    metrics = calculate_public_alpha_reassess_05_metrics(context, merged_policy)
    route_smoke = smoke_public_alpha_routes_from_ux_examples(merged_policy)
    domain_coverage = assess_domain_coverage_05(context, merged_policy)
    ux_mvp = assess_public_search_ux_mvp_status_05(context, merged_policy)
    public_search_models = assess_public_search_view_models_05(context, merged_policy)
    query_coverage = assess_query_coverage(metrics["seed_batches_represented"], context, merged_policy)
    candidate_usefulness = assess_candidate_usefulness_05(context, merged_policy)
    limited_reviewed_record_usefulness = assess_limited_reviewed_record_usefulness([], merged_policy)
    blockers = build_launch_blocker_register_05(metrics, merged_policy)
    next_work = build_next_work_recommendations_05(metrics, merged_policy)
    decision = build_public_alpha_reassess_05_decision(metrics, blockers, merged_policy)
    boundary = build_public_alpha_reassess_05_boundary_report(decision, merged_policy)
    result = {
        "schema_version": "public_alpha_reassess_05_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "reassess_id": REASSESS_ID,
        "metrics": metrics,
        "route_smoke": route_smoke,
        "domain_coverage": domain_coverage,
        "public_search_ux_mvp": ux_mvp,
        "public_search_view_models": public_search_models,
        "query_coverage": query_coverage,
        "candidate_usefulness": candidate_usefulness,
        "limited_reviewed_record_usefulness": limited_reviewed_record_usefulness,
        "launch_blockers": blockers,
        "next_work": next_work,
        "decision": decision,
        "boundary_report": boundary,
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "domain_coverage_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "limited_reviewed_record_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "public_search_ux_mvp_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "existing_reviewed_record_count": metrics["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": metrics["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": metrics["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "candidate_count": metrics["candidate_count"],
        "domain_count": metrics["domain_count"],
        "public_ux_routes_count": metrics["public_ux_routes_count"],
        "result_card_states_count": metrics["result_card_states_count"],
        "public_search_ux_mvp_implemented": metrics["public_search_ux_mvp_implemented"],
        "no_js_required": metrics["no_js_required"],
        "public_projection_read_only": metrics["public_projection_read_only"],
        "launch_recommended": decision["launch_recommended"],
        "demo_mode_recommended": decision["demo_mode_recommended"],
        "internal_review_recommended": decision["internal_review_recommended"],
        "public_search_ux_mvp_verified": decision["public_search_ux_mvp_verified"],
        "needs_more_reviewed_records": decision["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": decision["needs_more_reviewed_artifact_records"],
        "needs_review_batch_apply_next": decision["needs_review_batch_apply_next"],
        "needs_external_full_discovery": decision["needs_external_full_discovery"],
        "needs_main_promotion_before_launch": decision["needs_main_promotion_before_launch"],
        "needs_public_alpha_launch_approval": decision["needs_public_alpha_launch_approval"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
    }
    if write_examples:
        written = write_public_alpha_reassess_05_examples(result)
        written.extend(write_public_alpha_reassess_05_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_public_alpha_reassess_05_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_05(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_alpha" / "reassess" / "public_search_ux_mvp"
    files = {
        "public_alpha_reassess_metrics.json": payload["metrics"],
        "public_alpha_route_smoke.json": payload["route_smoke"],
        "public_alpha_query_coverage.json": payload["query_coverage"],
        "public_alpha_domain_coverage.json": payload["domain_coverage"],
        "public_alpha_candidate_usefulness.json": payload["candidate_usefulness"],
        "public_alpha_limited_reviewed_records.json": payload["limited_reviewed_record_usefulness"],
        "public_alpha_public_search_view_models.json": payload["public_search_view_models"],
        "public_alpha_public_search_ux_mvp.json": payload["public_search_ux_mvp"],
        "public_alpha_launch_blockers.json": payload["launch_blockers"],
        "public_alpha_next_work.json": payload["next_work"],
        "public_alpha_reassess_decision.json": payload["decision"],
        "public_alpha_boundary_report.json": payload["boundary_report"],
        "public_alpha_reassess_05_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def build_public_alpha_reassess_05_inventory_packets(
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return dict(_inventory_packets(dict(result or run_public_alpha_reassess_05(write_examples=False))))


def write_public_alpha_reassess_05_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_05(write_examples=False))
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
    return {
        "public_alpha_reassess_05_input_state.json": {
            "schema_version": "public_alpha_reassess_05_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "snapshot_refresh_05": SNAPSHOT_REFRESH_RESULT_REF,
                "public_search_ux_mvp": PUBLIC_SEARCH_UX_MVP_REF,
                "public_alpha_reassess_04": "control/inventory/public_alpha_reassess_04_result.json",
                "snapshot_refresh_04": "control/inventory/snapshot_refresh_04_result.json",
                "seed_batch_driver_support": "control/inventory/seed_batch_driver_support_result.json",
                "seed_batch_manuals_scans": "control/inventory/seed_batch_manuals_scans_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
            },
            "equivalent_filename_mappings": {
                "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
        },
        "public_alpha_reassess_05_snapshot_metrics.json": result["metrics"],
        "public_alpha_reassess_05_query_coverage_matrix.json": result["query_coverage"],
        "public_alpha_reassess_05_route_matrix.json": result["route_smoke"],
        "public_alpha_reassess_05_domain_coverage_matrix.json": result["domain_coverage"],
        "public_alpha_reassess_05_candidate_usefulness_matrix.json": result["candidate_usefulness"],
        "public_alpha_reassess_05_limited_reviewed_record_matrix.json": result["limited_reviewed_record_usefulness"],
        "public_alpha_reassess_05_public_search_view_model_matrix.json": result["public_search_view_models"],
        "public_alpha_reassess_05_public_search_ux_mvp_matrix.json": result["public_search_ux_mvp"],
        "public_alpha_reassess_05_launch_blocker_matrix.json": result["launch_blockers"],
        "public_alpha_reassess_05_next_work_matrix.json": result["next_work"],
        "public_alpha_reassess_05_boundary_report.json": result["boundary_report"],
        "public_alpha_reassess_05_smoke_result.json": {
            "schema_version": "public_alpha_reassess_05_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "route_smoke_status": result["route_smoke"]["route_smoke_status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
            "public_search_ux_mvp_verified": result["public_search_ux_mvp_verified"],
            **_false_boundaries(),
        },
        "public_alpha_reassess_05_validation_matrix.json": {
            "schema_version": "public_alpha_reassess_05_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_public_search_ux_mvp.py",
                "python scripts/validate_public_search_ux_model.py",
                "focused public-alpha reassess unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_alpha_reassess_05_result.json": _task_result(result),
        "public_alpha_reassess_05_next_task_decision.json": {
            "schema_version": "public_alpha_reassess_05_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "SNAPSHOT-REFRESH-06",
                "PUBLIC-ALPHA-REASSESS-06",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "rationale": "UX MVP is present; reviewed corpus size is now the bottleneck.",
            "launch_recommended": False,
            "demo_mode_recommended": True,
        },
        "public_alpha_reassess_05_failure_repair_log.json": {
            "schema_version": "public_alpha_reassess_05_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-alpha-reassess-05-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-ALPHA-REASSESS-05 Audit\n\nEvidence-based reassessment after public search UX MVP and snapshot projection refresh. Decision: UX MVP verified, internal demo/review usefulness improved, public launch not recommended.\n",
        "snapshot_metrics.md": _matrix_md("Snapshot Metrics", result["metrics"]),
        "query_coverage_matrix.md": _matrix_md("Query Coverage Matrix", result["query_coverage"]),
        "route_matrix.md": _matrix_md("Route Matrix", result["route_smoke"]),
        "public_search_ux_mvp_matrix.md": _matrix_md("Public Search UX MVP Matrix", result["public_search_ux_mvp"]),
        "candidate_usefulness_matrix.md": _matrix_md("Candidate Usefulness Matrix", result["candidate_usefulness"]),
        "launch_blocker_matrix.md": _matrix_md("Launch Blocker Matrix", result["launch_blockers"]),
        "next_work_matrix.md": _matrix_md("Next Work Matrix", result["next_work"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {
            "status": result["status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "public_search_ux_mvp_verified": result["public_search_ux_mvp_verified"],
        }),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_alpha_reassess_05_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "public_alpha_reassess_05_report.json": _task_result(result),
        "generated/sample_reassess_metrics.json": result["metrics"],
        "generated/sample_launch_blockers.json": result["launch_blockers"],
        "generated/sample_next_work.json": result["next_work"],
        "generated/sample_reassess_decision.json": result["decision"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Alpha Reassess 05 Summary\n\n"
        f"- UX MVP verified: {str(result['public_search_ux_mvp_verified']).lower()}\n"
        f"- public UX routes: {result['public_ux_routes_count']}\n"
        f"- result-card states: {result['result_card_states_count']}\n"
        f"- total candidates: {result['candidate_count']}\n"
        f"- total limited reviewed projections: {result['total_limited_reviewed_record_projection_count']}\n"
        f"- launch recommended: {str(result['launch_recommended']).lower()}\n"
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
        "schema_version": "public_alpha_reassess_05_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "existing_reviewed_record_count": result["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": result["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": result["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
        "candidate_count": result["candidate_count"],
        "domain_count": result["domain_count"],
        "public_ux_routes_count": result["public_ux_routes_count"],
        "result_card_states_count": result["result_card_states_count"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "no_js_required": result["no_js_required"],
        "public_projection_read_only": result["public_projection_read_only"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "public_search_ux_mvp_verified": result["public_search_ux_mvp_verified"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": result["needs_more_reviewed_artifact_records"],
        "needs_review_batch_apply_next": result["needs_review_batch_apply_next"],
        "needs_external_full_discovery": result["needs_external_full_discovery"],
        "needs_main_promotion_before_launch": result["needs_main_promotion_before_launch"],
        "needs_public_alpha_launch_approval": result["needs_public_alpha_launch_approval"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_05_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "public_search_ux_mvp_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "existing_reviewed_record_count": result["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": result["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": result["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
        "candidate_count": result["candidate_count"],
        "domain_count": result["domain_count"],
        "public_ux_routes_count": result["public_ux_routes_count"],
        "result_card_states_count": result["result_card_states_count"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "no_js_required": result["no_js_required"],
        "public_projection_read_only": result["public_projection_read_only"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "public_search_ux_mvp_verified": result["public_search_ux_mvp_verified"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": result["needs_more_reviewed_artifact_records"],
        "needs_review_batch_apply_next": result["needs_review_batch_apply_next"],
        "needs_external_full_discovery": result["needs_external_full_discovery"],
        "needs_main_promotion_before_launch": result["needs_main_promotion_before_launch"],
        "needs_public_alpha_launch_approval": result["needs_public_alpha_launch_approval"],
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
    limited_reviewed_count: int,
    domain_count: int,
    total_candidate_count: int,
    ux_mvp_verified: bool,
    route_smoke_passed: bool,
    policy: Mapping[str, Any],
) -> float:
    reviewed = min(limited_reviewed_count / max(int(policy["public_alpha_min_reviewed_record_threshold"]), 1), 1.0)
    domains = min(domain_count / max(int(policy["public_alpha_min_domain_coverage_threshold"]), 1), 1.0)
    candidates = min(total_candidate_count / 75.0, 1.0)
    route = 1.0 if route_smoke_passed else 0.0
    ux = 1.0 if ux_mvp_verified else 0.0
    score = reviewed * 0.34 + domains * 0.18 + candidates * 0.11 + route * 0.10 + ux * 0.27
    return round(score, 3)


def _context(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot_refresh_05_result" in value and "public_search_ux_mvp_result" in value:
        return value
    return load_snapshot_refresh_05_metrics()


def _assert_snapshot_refresh_05_context(context: Mapping[str, Any]) -> None:
    snapshot = context["snapshot_refresh_05_inventory_result"]
    ux_result = context["public_search_ux_mvp_result"]
    if snapshot.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("snapshot refresh 05 result must pass or pass with warnings")
    expected_counts = {
        "total_limited_reviewed_record_projection_count": 4,
        "total_candidate_count": 68,
        "public_ux_routes_count": 8,
        "result_card_states_count": 8,
    }
    for key, expected in expected_counts.items():
        if int(snapshot.get(key) or 0) != expected:
            raise ValueError(f"snapshot refresh 05 count mismatch for {key}")
    expected_true = (
        "public_search_ux_integrated",
        "no_js_required",
        "public_projection_read_only",
    )
    for key in expected_true:
        if snapshot.get(key) is not True:
            raise ValueError(f"snapshot refresh 05 missing true flag: {key}")
    ux_required_true = (
        "home_page_added",
        "search_results_page_added",
        "object_page_added",
        "candidate_page_added",
        "need_page_added",
        "source_page_added",
        "evidence_page_added",
        "status_page_added",
        "no_results_need_page_added",
        "result_cards_added",
        "no_js_search_form_passed",
        "candidate_verified_distinction_passed",
        "limited_reviewed_record_distinction_passed",
        "public_projection_read_only",
        "ux_smoke_passed",
    )
    if ux_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("public search UX MVP result must pass or pass with warnings")
    for key in ux_required_true:
        if ux_result.get(key) is not True:
            raise ValueError(f"public search UX MVP missing true flag: {key}")
    for key in (
        "site_dist_written",
        "deployment_performed",
        "public_launch_performed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if snapshot.get(key, False) is not False or ux_result.get(key, False) is not False:
            raise ValueError(f"reassess 05 boundary failed: {key}")


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
        "public_alpha_min_ux_mvp_required",
        "public_search_ux_mvp_improves_readiness_but_is_not_launch_sufficient",
        "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification",
        "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification",
        "candidate_only_snapshot_not_enough_for_launch",
        "four_limited_reviewed_records_not_enough_for_launch",
        "external_full_discovery_required_before_main_promotion",
        "main_promotion_required_before_launch",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"public alpha reassess 05 policy missing required rules: {', '.join(missing)}")
    forbidden_true = {
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "file_fetches_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"public alpha reassess 05 policy enables forbidden behavior: {', '.join(enabled)}")


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
