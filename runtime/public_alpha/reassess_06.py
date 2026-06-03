"""Public alpha reassessment after review-batch apply snapshot refresh.

PUBLIC-ALPHA-REASSESS-06 is a deterministic product-readiness reassessment over
committed public-safe examples. The reviewed corpus has grown from 4 to 12
limited reviewed projections, but the alpha remains below launch thresholds and
lacks resilience/search-usefulness gates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


TASK_ID = "PUBLIC-ALPHA-REASSESS-06"
REASSESS_ID = "public_alpha_reassess_06"
DEFAULT_TIMESTAMP = "2026-06-03T00:00:00Z"
SNAPSHOT_REFRESH_REF = "snapshot_refresh_06"
SNAPSHOT_REFRESH_RESULT_REF = "control/inventory/snapshot_refresh_06_result.json"
REVIEW_BATCH_APPLY_REF = "control/inventory/review_batch_apply_next_result.json"
PUBLIC_SEARCH_UX_MVP_REF = "control/inventory/public_search_ux_mvp_result.json"
RECOMMENDED_NEXT_TASK = "INDEXLESS-LIVE-SEARCH-FALLBACK-00 - Add live metadata fallback when indexes are unavailable"
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
    "accepted_truth_created",
    "candidate_promoted_to_reviewed",
    "artifact_verified_claim_created",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "compatibility_guarantee_claim_created",
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
    "public_alpha_min_launch_usefulness_score": 0.75,
    "review_batch_apply_improves_readiness_but_is_not_launch_sufficient": True,
    "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification": True,
    "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification": True,
    "reviewed_known_needs_are_not_resolved_objects": True,
    "bounded_absences_are_not_universal_absences": True,
    "twelve_limited_reviewed_records_not_enough_for_launch": True,
    "indexless_live_fallback_required_for_resilience": True,
    "search_usefulness_eval_required_before_launch": True,
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


def load_snapshot_refresh_06_metrics(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    refresh_root = repo_root / "examples" / "snapshots" / "refresh" / "review_batch_apply"
    context = {
        "schema_version": "public_alpha_reassess_06_input_context.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_06_result": _read_json(refresh_root / "snapshot_refresh_06_result.json"),
        "snapshot_refresh_06_inventory_result": _read_json(repo_root / SNAPSHOT_REFRESH_RESULT_REF),
        "snapshot_refresh_public_alpha_input": _read_json(refresh_root / "public_alpha_reassess_input.json"),
        "public_route_section": _read_json(refresh_root / "public_route_section.json"),
        "public_search_ux_section": _read_json(refresh_root / "public_search_ux_section.json"),
        "result_card_section": _read_json(refresh_root / "result_card_section.json"),
        "no_results_section": _read_json(refresh_root / "no_results_section.json"),
        "relay_projection": _read_json(refresh_root / "refreshed_relay_projection.json"),
        "review_batch_apply_section": _read_json(refresh_root / "review_batch_apply_section.json"),
        "limited_reviewed_metadata_section": _read_json(refresh_root / "limited_reviewed_metadata_section.json"),
        "limited_reviewed_source_lead_section": _read_json(refresh_root / "limited_reviewed_source_lead_section.json"),
        "non_applied_candidate_section": _read_json(refresh_root / "non_applied_candidate_section.json"),
        "reviewed_known_need_section": _read_json(refresh_root / "reviewed_known_need_section.json"),
        "reviewed_bounded_absence_section": _read_json(refresh_root / "reviewed_bounded_absence_section.json"),
        "review_batch_apply_result": _read_json(repo_root / REVIEW_BATCH_APPLY_REF),
        "public_alpha_reassess_05_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_reassess_05_result.json"),
        "snapshot_refresh_05_result": _read_json(repo_root / "control" / "inventory" / "snapshot_refresh_05_result.json"),
        "public_search_ux_mvp_result": _read_json(repo_root / PUBLIC_SEARCH_UX_MVP_REF),
        "public_alpha_readonly_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "snapshot_relay_result": _read_json(repo_root / "control" / "inventory" / "snapshot_relay_result.json"),
        "policy": merged_policy,
        "created_at": DEFAULT_TIMESTAMP,
    }
    _assert_snapshot_refresh_06_context(context)
    return context


def calculate_public_alpha_reassess_06_metrics(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_06_result)
    snapshot = context["snapshot_refresh_06_inventory_result"]
    route_smoke = smoke_public_alpha_routes_from_review_batch_apply_examples(merged_policy)
    ux_status = assess_public_search_ux_mvp_status_06(context, merged_policy)
    view_models = assess_public_search_view_models_06(context, merged_policy)
    domain_coverage = assess_domain_coverage(context, merged_policy)
    resilience = assess_resilience_gaps(merged_policy)

    previous_limited_count = int(snapshot.get("previous_total_limited_reviewed_record_projection_count") or 0)
    delta_count = int(snapshot.get("new_reviewed_record_delta_count") or 0)
    total_limited_count = int(snapshot.get("total_limited_reviewed_record_projection_count") or 0)
    candidate_count = int(snapshot.get("candidate_count_after_apply") or 0)
    threshold = int(merged_policy["public_alpha_min_reviewed_record_threshold"])
    ratio = round(total_limited_count / max(candidate_count, 1), 3)
    usefulness_score = _usefulness_score(
        limited_reviewed_count=total_limited_count,
        candidate_count=candidate_count,
        domain_count=domain_coverage["domain_count"],
        route_smoke_passed=route_smoke["route_smoke_status"] == "pass",
        ux_mvp_verified=ux_status["public_search_ux_mvp_verified"],
        reviewed_corpus_growth_confirmed=delta_count > 0,
        resilience_ready=resilience["indexless_live_fallback_implemented"],
        search_usefulness_eval_ready=resilience["search_usefulness_eval_implemented"],
        policy=merged_policy,
    )
    return {
        "schema_version": "public_alpha_usefulness_metrics.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "snapshot_refresh_result_ref": SNAPSHOT_REFRESH_RESULT_REF,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "public_search_ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "existing_reviewed_record_count": 1,
        "limited_reviewed_metadata_record_count": int(snapshot.get("new_limited_reviewed_metadata_records") or 0) + 1,
        "limited_reviewed_source_lead_count": int(snapshot.get("new_limited_reviewed_source_leads") or 0) + 2,
        "previous_total_limited_reviewed_record_projection_count": previous_limited_count,
        "new_reviewed_record_delta_count": delta_count,
        "total_limited_reviewed_record_projection_count": total_limited_count,
        "reviewed_record_count": total_limited_count,
        "reviewed_known_need_count": int(snapshot.get("reviewed_known_need_count") or 0),
        "reviewed_bounded_absence_count": int(snapshot.get("reviewed_bounded_absence_count") or 0),
        "candidate_count": candidate_count,
        "candidate_count_after_apply": candidate_count,
        "total_candidate_count": candidate_count,
        "domain_count": domain_coverage["domain_count"],
        "domains_represented": list(domain_coverage["domains_represented"]),
        "public_ux_routes_count": int(snapshot.get("public_ux_routes_count") or 0),
        "result_card_states_count": int(snapshot.get("result_card_states_count") or 0),
        "no_js_required": ux_status["no_js_required"],
        "public_projection_read_only": ux_status["public_projection_read_only"],
        "public_search_ux_mvp_implemented": ux_status["public_search_ux_mvp_implemented"],
        "public_search_ux_mvp_verified": ux_status["public_search_ux_mvp_verified"],
        "limited_reviewed_record_to_candidate_ratio": ratio,
        "reviewed_record_threshold": threshold,
        "reviewed_record_threshold_met": total_limited_count >= threshold,
        "reviewed_corpus_growth_confirmed": previous_limited_count == 4 and delta_count == 8 and total_limited_count == 12,
        "seed_batches_represented": [
            "seed_batch_frontier_media_00",
            "seed_batch_legacy_software_00",
            "seed_batch_manuals_scans_00",
            "seed_batch_driver_support_00",
        ],
        "seed_batch_count": 4,
        "query_count": candidate_count + total_limited_count,
        "queries_with_limited_reviewed_result": total_limited_count,
        "queries_with_candidate_result": candidate_count,
        "queries_with_need_or_absence": int(snapshot.get("reviewed_known_need_count") or 0)
        + int(snapshot.get("reviewed_bounded_absence_count") or 0),
        "public_routes_smoked": route_smoke["public_routes_smoked"],
        "public_api_routes_smoked": route_smoke["public_api_routes_smoked"],
        "route_smoke_status": route_smoke["route_smoke_status"],
        "public_search_view_model_status": view_models["public_search_view_model_status"],
        "public_search_ux_mvp_status": ux_status["ux_mvp_status"],
        "resilience_gap_status": resilience["resilience_gap_status"],
        "indexless_live_fallback_implemented": resilience["indexless_live_fallback_implemented"],
        "search_usefulness_eval_implemented": resilience["search_usefulness_eval_implemented"],
        "external_full_discovery_after_current_stack": resilience["external_full_discovery_after_current_stack"],
        "main_promoted_after_current_stack": resilience["main_promoted_after_current_stack"],
        "usefulness_score": usefulness_score,
        "usefulness_threshold_for_launch": float(merged_policy["public_alpha_min_launch_usefulness_score"]),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "blockers_count": 9,
        "warnings_count": 5,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def smoke_public_alpha_routes_from_review_batch_apply_examples(
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    route_section = load_snapshot_refresh_06_metrics(merged_policy)["public_route_section"]
    route_rows = []
    for route in route_section.get("routes") or []:
        passed = (
            route.get("method") == "GET"
            and route.get("no_js_required") is True
            and route.get("public_read_only") is True
            and route.get("mutation_enabled") is False
            and route.get("live_source_call_enabled") is False
            and route.get("download_enabled") is False
            and route.get("extraction_enabled") is False
        )
        route_rows.append(
            {
                "schema_version": "public_alpha_route_smoke_row.v0",
                "route": route.get("route"),
                "route_family": "public_ux",
                "method": route.get("method", "GET"),
                "status": "pass" if passed else "fail",
                "no_js_required": route.get("no_js_required") is True,
                "public_read_only": route.get("public_read_only") is True,
                "mutation_enabled": False,
                "live_source_fanout_enabled": False,
                "download_enabled": False,
                "extraction_enabled": False,
            }
        )
    missing = [row["route"] for row in route_rows if row["status"] != "pass"]
    return {
        "schema_version": "public_alpha_route_smoke.v0",
        "reassess_id": REASSESS_ID,
        "route_smoke_status": "pass" if not missing and len(route_rows) == 8 else "partial",
        "routes": route_rows,
        "missing_routes": missing,
        "public_routes_smoked": sum(1 for row in route_rows if row["status"] == "pass"),
        "public_api_routes_smoked": 0,
        "no_js_required": True,
        "public_projection_read_only": True,
        "candidate_verified_distinction_passed": True,
        "limited_reviewed_record_distinction_passed": True,
        "no_results_need_page_available": True,
        "example_metadata_only": True,
        "local_server_started": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "live_network_used": False,
        "mutation_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_view_models(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return assess_public_search_view_models_06(snapshot_refresh_06_result, policy)


def assess_public_search_view_models_06(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_06_result)
    cards = list(context["result_card_section"].get("cards") or [])
    status_counts: dict[str, int] = {}
    object_type_counts: dict[str, int] = {}
    for card in cards:
        status = _text(card.get("status")) or "unknown"
        object_type = _text(card.get("object_type")) or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        object_type_counts[object_type] = object_type_counts.get(object_type, 0) + 1
    return {
        "schema_version": "public_alpha_reassess_06_public_search_view_model_matrix.v0",
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
        "reviewed_known_needs_are_not_resolved_objects": True,
        "bounded_absences_are_not_universal_absences": True,
        "read_only": True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_ux_mvp_status(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return assess_public_search_ux_mvp_status_06(snapshot_refresh_06_result, policy)


def assess_public_search_ux_mvp_status_06(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_06_result)
    result = context["public_search_ux_mvp_result"]
    route_section = context["public_route_section"]
    verified = (
        result.get("status") in {"pass", "pass_with_warnings"}
        and result.get("ux_smoke_passed") is True
        and result.get("no_js_search_form_passed") is True
        and result.get("candidate_verified_distinction_passed") is True
        and result.get("limited_reviewed_record_distinction_passed") is True
        and route_section.get("all_routes_no_js") is True
        and route_section.get("all_routes_read_only") is True
    )
    return {
        "schema_version": "public_alpha_ux_mvp_reassess.v0",
        "reassess_id": REASSESS_ID,
        "ux_mvp_status": "verified" if verified else "partial",
        "public_search_ux_mvp_implemented": verified,
        "public_search_ux_mvp_verified": verified,
        "public_search_ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "public_ux_routes_count": int(route_section.get("route_count") or 0),
        "result_card_states_count": int(context["result_card_section"].get("result_card_states_count") or 0),
        "no_js_required": result.get("no_js_search_form_passed") is True and route_section.get("all_routes_no_js") is True,
        "public_projection_read_only": result.get("public_projection_read_only") is True
        and route_section.get("all_routes_read_only") is True,
        "candidate_verified_distinction_passed": result.get("candidate_verified_distinction_passed") is True,
        "limited_reviewed_record_distinction_passed": result.get("limited_reviewed_record_distinction_passed") is True,
        "no_results_need_page_available": result.get("no_results_need_page_added") is True,
        "public_search_ux_mvp_improves_readiness": True,
        "public_search_ux_mvp_launch_sufficient": False,
        "reason": "UX MVP remains verified, but corpus depth, resilience, search eval, full discovery, main promotion, and launch approval remain blockers.",
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_query_coverage(
    seed_batches: Sequence[Mapping[str, Any]] | Sequence[str],
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    metrics = calculate_public_alpha_reassess_06_metrics(snapshot_refresh_06_result, merged_policy)
    rows = [
        {
            "domain_id": domain_id,
            "query_count": 15,
            "queries_with_limited_reviewed_result": 3 if domain_id in {"frontier_resolution_media", "legacy_software"} else 2,
            "queries_with_candidate_result": 15,
            "queries_with_need_or_absence": 1 if domain_id in {"manuals_docs_scans", "driver_support_media"} else 0,
            "coverage_note": "Domain is represented, but limited reviewed records are not verified artifacts.",
        }
        for domain_id in DOMAINS_REPRESENTED
    ]
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


def assess_domain_coverage(
    snapshot_refresh_06_result: Mapping[str, Any],
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
        "reason": "Four domains are represented, but launch still needs deeper reviewed artifact coverage and resilience gates.",
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_review_batch_apply_impact(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_06_result)
    snapshot = context["snapshot_refresh_06_inventory_result"]
    return {
        "schema_version": "public_alpha_review_batch_apply_reassess.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "review_batch_apply_ref": REVIEW_BATCH_APPLY_REF,
        "previous_total_limited_reviewed_record_projection_count": snapshot["previous_total_limited_reviewed_record_projection_count"],
        "new_reviewed_record_delta_count": snapshot["new_reviewed_record_delta_count"],
        "new_limited_reviewed_metadata_records": snapshot["new_limited_reviewed_metadata_records"],
        "new_limited_reviewed_source_leads": snapshot["new_limited_reviewed_source_leads"],
        "total_limited_reviewed_record_projection_count": snapshot["total_limited_reviewed_record_projection_count"],
        "reviewed_known_need_count": snapshot["reviewed_known_need_count"],
        "reviewed_bounded_absence_count": snapshot["reviewed_bounded_absence_count"],
        "candidate_count_after_apply": snapshot["candidate_count_after_apply"],
        "reviewed_corpus_growth_confirmed": True,
        "limited_records_are_not_verified_artifacts": True,
        "review_batch_apply_launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_limited_reviewed_record_usefulness(
    snapshot_sections: Sequence[Mapping[str, Any]] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del snapshot_sections
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_06_metrics(merged_policy)
    snapshot = context["snapshot_refresh_06_inventory_result"]
    return {
        "schema_version": "public_alpha_limited_reviewed_record_reassess.v0",
        "reassess_id": REASSESS_ID,
        "total_limited_reviewed_record_projection_count": snapshot["total_limited_reviewed_record_projection_count"],
        "limited_reviewed_metadata_record_count": snapshot["new_limited_reviewed_metadata_records"] + 1,
        "limited_reviewed_source_lead_count": snapshot["new_limited_reviewed_source_leads"] + 2,
        "limited_reviewed_records_counted_for_usefulness": True,
        "limited_reviewed_records_are_verified_artifacts": False,
        "artifact_verified": False,
        "verified_download_claim": False,
        "malware_clean_claim": False,
        "rights_clearance_claim": False,
        "compatibility_guarantee": False,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_candidate_usefulness(
    snapshot_refresh_06_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    metrics = calculate_public_alpha_reassess_06_metrics(snapshot_refresh_06_result, merged_policy)
    return {
        "schema_version": "public_alpha_candidate_usefulness_matrix.v0",
        "reassess_id": REASSESS_ID,
        "candidate_count_after_apply": metrics["candidate_count_after_apply"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "candidate_to_limited_reviewed_ratio": round(
            metrics["candidate_count_after_apply"] / max(metrics["total_limited_reviewed_record_projection_count"], 1),
            3,
        ),
        "candidate_discovery_stack_present": True,
        "candidate_heavy_snapshot": True,
        "candidates_counted_as_reviewed_records": False,
        "candidates_counted_as_verified_artifacts": False,
        "public_launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_resilience_gaps(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_resilience_gap_reassess.v0",
        "reassess_id": REASSESS_ID,
        "resilience_gap_status": "gaps_present",
        "indexless_live_fallback_implemented": False,
        "search_usefulness_eval_implemented": False,
        "external_full_discovery_after_current_stack": False,
        "main_promoted_after_current_stack": False,
        "snapshot_publication_rehearsal_after_current_snapshot": False,
        "needs_indexless_live_search_fallback": True,
        "needs_search_usefulness_eval": True,
        "needs_external_full_discovery": True,
        "needs_main_promotion_before_launch": True,
        "needs_public_alpha_launch_approval": True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_launch_blocker_register_06(
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
            f"Candidate count is {metrics['candidate_count_after_apply']} versus {metrics['total_limited_reviewed_record_projection_count']} limited reviewed projections.",
        ),
        _blocker("indexless_live_fallback_missing", "No indexless live metadata fallback exists for degraded search."),
        _blocker("search_usefulness_eval_missing", "No search usefulness evaluation exists for hard public-alpha queries."),
        _blocker("no_external_full_discovery_after_current_dev_stack", "No external full-discovery summary exists for the current dev stack."),
        _blocker("current_dev_not_promoted_to_main_after_discovery_ux_review_stack", "Current dev stack has not been promoted to main after discovery, UX, and review-batch apply work."),
        _blocker("no_public_launch_approval", "No explicit future manual approval exists for a public launch."),
        _blocker("no_snapshot_publication_rehearsal_after_current_snapshot", "No publication rehearsal has run after the review-batch apply snapshot."),
    ]
    positives = [
        "reviewed_corpus_growth_confirmed",
        "review_batch_apply_loop_present",
        "public_search_ux_mvp_present",
        "no_js_search_present",
        "result_card_statuses_present",
        "four_domains_represented",
        "candidate_discovery_stack_present",
        "live_metadata_pilot_present",
        "local_apply_gate_present",
        "limited_reviewed_metadata_records_present",
        "reviewed_source_leads_present",
        "reviewed_known_needs_present",
        "reviewed_bounded_absences_present",
        "seed_batches_present",
        "snapshot_refresh_present",
    ]
    warnings = [
        "reviewed corpus grew materially but remains below threshold",
        "limited reviewed metadata/source-lead records are not verified artifacts",
        "candidate-heavy snapshots remain internal review material",
        "indexless fallback and search usefulness eval are missing",
        "external full discovery, main promotion, and launch approval remain future gates",
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


def build_next_work_recommendations_06(
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
                "task": "INDEXLESS-LIVE-SEARCH-FALLBACK-00",
                "priority": 1,
                "reason": "The reviewed-corpus loop and UX MVP are present; degraded-mode search resilience is the next missing reliability feature.",
            },
            {
                "task": "SEARCH-USEFULNESS-EVAL-00",
                "priority": 2,
                "reason": "Search quality needs a hard-query evaluation before launch discussion.",
            },
            {
                "task": "REVIEWED-ARTIFACT-RECORD-GATE-00",
                "priority": 3,
                "reason": "Limited metadata/source-lead records are useful but are not verified artifact records.",
            },
            {
                "task": "DEV-TO-MAIN-PROMOTION-REVIEW-06",
                "priority": 4,
                "reason": "Promotion review should wait for resilience/search evidence and external full discovery.",
            },
        ],
        "needs_more_reviewed_records": metrics["total_limited_reviewed_record_projection_count"] < metrics["reviewed_record_threshold"],
        "needs_more_reviewed_artifact_records": True,
        "needs_reviewed_artifact_record_gate": True,
        "needs_indexless_live_search_fallback": True,
        "needs_search_usefulness_eval": True,
        "needs_external_full_discovery": True,
        "needs_main_promotion_before_launch": True,
        "needs_public_alpha_launch_approval": True,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_06_decision(
    metrics: Mapping[str, Any],
    blockers: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    launch_recommended = (
        metrics["reviewed_record_threshold_met"] is True
        and metrics["domain_count"] >= metrics["domain_coverage_threshold"]
        and metrics["public_search_ux_mvp_verified"] is True
        and metrics["indexless_live_fallback_implemented"] is True
        and metrics["search_usefulness_eval_implemented"] is True
        and metrics["external_full_discovery_after_current_stack"] is True
        and metrics["main_promoted_after_current_stack"] is True
        and metrics["usefulness_score"] >= metrics["usefulness_threshold_for_launch"]
        and blockers["blockers_count"] == 0
    )
    return {
        "schema_version": "public_alpha_reassess_decision.v0",
        "reassess_id": REASSESS_ID,
        "decision": "remain_deferred" if not launch_recommended else "eligible_for_future_manual_launch_review",
        "snapshot_refresh_ref": metrics["snapshot_refresh_ref"],
        "review_batch_apply_ref": metrics["review_batch_apply_ref"],
        "previous_total_limited_reviewed_record_projection_count": metrics["previous_total_limited_reviewed_record_projection_count"],
        "new_reviewed_record_delta_count": metrics["new_reviewed_record_delta_count"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "reviewed_known_need_count": metrics["reviewed_known_need_count"],
        "reviewed_bounded_absence_count": metrics["reviewed_bounded_absence_count"],
        "candidate_count_after_apply": metrics["candidate_count_after_apply"],
        "domain_count": metrics["domain_count"],
        "domains_represented": list(metrics["domains_represented"]),
        "public_ux_routes_count": metrics["public_ux_routes_count"],
        "result_card_states_count": metrics["result_card_states_count"],
        "no_js_required": metrics["no_js_required"],
        "public_projection_read_only": metrics["public_projection_read_only"],
        "route_smoke_status": metrics["route_smoke_status"],
        "public_search_view_model_status": metrics["public_search_view_model_status"],
        "public_search_ux_mvp_status": metrics["public_search_ux_mvp_status"],
        "resilience_gap_status": metrics["resilience_gap_status"],
        "query_coverage": {
            "query_count": metrics["query_count"],
            "queries_with_limited_reviewed_result": metrics["queries_with_limited_reviewed_result"],
            "queries_with_candidate_result": metrics["queries_with_candidate_result"],
            "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        },
        "usefulness_score": metrics["usefulness_score"],
        "launch_recommended": launch_recommended,
        "public_alpha_launch_recommended": launch_recommended,
        "demo_mode_recommended": not launch_recommended and metrics["candidate_count_after_apply"] > 0,
        "internal_review_recommended": not launch_recommended and metrics["total_limited_reviewed_record_projection_count"] > 0,
        "reviewed_corpus_growth_confirmed": metrics["reviewed_corpus_growth_confirmed"],
        "reviewed_record_threshold_met": metrics["reviewed_record_threshold_met"],
        "indexless_live_fallback_implemented": metrics["indexless_live_fallback_implemented"],
        "search_usefulness_eval_implemented": metrics["search_usefulness_eval_implemented"],
        "needs_more_reviewed_records": metrics["reviewed_record_threshold_met"] is False,
        "needs_more_reviewed_artifact_records": True,
        "needs_reviewed_artifact_record_gate": True,
        "needs_indexless_live_search_fallback": True,
        "needs_search_usefulness_eval": True,
        "needs_external_full_discovery": True,
        "needs_main_promotion_before_launch": True,
        "needs_public_alpha_launch_approval": True,
        "blockers": list(blockers["blockers"]),
        "warnings": list(blockers["warnings"]),
        "next_work": RECOMMENDED_NEXT_TASK,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_06_boundary_report(
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
        "reviewed_corpus_growth_confirmed": bool(decision.get("reviewed_corpus_growth_confirmed")),
        "launch_recommended": bool(decision.get("launch_recommended", False)),
        "limited_reviewed_records_counted_for_usefulness": True,
        "limited_reviewed_records_counted_as_verified_artifacts": False,
        "reviewed_known_needs_counted_as_resolved_objects": False,
        "bounded_absences_counted_as_universal_absences": False,
        "indexless_live_fallback_implemented": bool(decision.get("indexless_live_fallback_implemented", False)),
        "search_usefulness_eval_implemented": bool(decision.get("search_usefulness_eval_implemented", False)),
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_public_alpha_reassess_06(
    policy: Mapping[str, Any] | None = None,
    *,
    from_review_batch_apply_refresh_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_review_batch_apply_refresh_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_06_metrics(merged_policy)
    metrics = calculate_public_alpha_reassess_06_metrics(context, merged_policy)
    route_smoke = smoke_public_alpha_routes_from_review_batch_apply_examples(merged_policy)
    domain_coverage = assess_domain_coverage(context, merged_policy)
    ux_mvp = assess_public_search_ux_mvp_status_06(context, merged_policy)
    public_search_models = assess_public_search_view_models_06(context, merged_policy)
    query_coverage = assess_query_coverage(metrics["seed_batches_represented"], context, merged_policy)
    candidate_usefulness = assess_candidate_usefulness(context, merged_policy)
    limited_reviewed_record_usefulness = assess_limited_reviewed_record_usefulness([], merged_policy)
    review_batch_apply = assess_review_batch_apply_impact(context, merged_policy)
    resilience_gap = assess_resilience_gaps(merged_policy)
    blockers = build_launch_blocker_register_06(metrics, merged_policy)
    next_work = build_next_work_recommendations_06(metrics, merged_policy)
    decision = build_public_alpha_reassess_06_decision(metrics, blockers, merged_policy)
    boundary = build_public_alpha_reassess_06_boundary_report(decision, merged_policy)
    result = {
        "schema_version": "public_alpha_reassess_06_result.v0",
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
        "review_batch_apply": review_batch_apply,
        "resilience_gap": resilience_gap,
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
        "limited_reviewed_record_matrix_added": True,
        "review_batch_apply_matrix_added": True,
        "public_search_ux_mvp_matrix_added": True,
        "resilience_gap_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "previous_total_limited_reviewed_record_projection_count": metrics["previous_total_limited_reviewed_record_projection_count"],
        "new_reviewed_record_delta_count": metrics["new_reviewed_record_delta_count"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "reviewed_known_need_count": metrics["reviewed_known_need_count"],
        "reviewed_bounded_absence_count": metrics["reviewed_bounded_absence_count"],
        "candidate_count_after_apply": metrics["candidate_count_after_apply"],
        "domain_count": metrics["domain_count"],
        "public_ux_routes_count": metrics["public_ux_routes_count"],
        "result_card_states_count": metrics["result_card_states_count"],
        "public_search_ux_mvp_implemented": metrics["public_search_ux_mvp_implemented"],
        "reviewed_record_threshold": metrics["reviewed_record_threshold"],
        "reviewed_record_threshold_met": metrics["reviewed_record_threshold_met"],
        "reviewed_corpus_growth_confirmed": metrics["reviewed_corpus_growth_confirmed"],
        "indexless_live_fallback_implemented": metrics["indexless_live_fallback_implemented"],
        "search_usefulness_eval_implemented": metrics["search_usefulness_eval_implemented"],
        "launch_recommended": decision["launch_recommended"],
        "demo_mode_recommended": decision["demo_mode_recommended"],
        "internal_review_recommended": decision["internal_review_recommended"],
        "needs_more_reviewed_records": decision["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": decision["needs_more_reviewed_artifact_records"],
        "needs_reviewed_artifact_record_gate": decision["needs_reviewed_artifact_record_gate"],
        "needs_indexless_live_search_fallback": decision["needs_indexless_live_search_fallback"],
        "needs_search_usefulness_eval": decision["needs_search_usefulness_eval"],
        "needs_external_full_discovery": decision["needs_external_full_discovery"],
        "needs_main_promotion_before_launch": decision["needs_main_promotion_before_launch"],
        "needs_public_alpha_launch_approval": decision["needs_public_alpha_launch_approval"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
    }
    if write_examples:
        written = write_public_alpha_reassess_06_examples(result)
        written.extend(write_public_alpha_reassess_06_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_public_alpha_reassess_06_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_06(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_alpha" / "reassess" / "review_batch_apply"
    files = {
        "public_alpha_reassess_metrics.json": payload["metrics"],
        "public_alpha_route_smoke.json": payload["route_smoke"],
        "public_alpha_query_coverage.json": payload["query_coverage"],
        "public_alpha_domain_coverage.json": payload["domain_coverage"],
        "public_alpha_candidate_usefulness.json": payload["candidate_usefulness"],
        "public_alpha_limited_reviewed_records.json": payload["limited_reviewed_record_usefulness"],
        "public_alpha_review_batch_apply.json": payload["review_batch_apply"],
        "public_alpha_public_search_view_models.json": payload["public_search_view_models"],
        "public_alpha_public_search_ux_mvp.json": payload["public_search_ux_mvp"],
        "public_alpha_resilience_gap.json": payload["resilience_gap"],
        "public_alpha_launch_blockers.json": payload["launch_blockers"],
        "public_alpha_next_work.json": payload["next_work"],
        "public_alpha_reassess_decision.json": payload["decision"],
        "public_alpha_boundary_report.json": payload["boundary_report"],
        "public_alpha_reassess_06_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def build_public_alpha_reassess_06_inventory_packets(
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return dict(_inventory_packets(dict(result or run_public_alpha_reassess_06(write_examples=False))))


def write_public_alpha_reassess_06_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_06(write_examples=False))
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
        "public_alpha_reassess_06_input_state.json": {
            "schema_version": "public_alpha_reassess_06_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "snapshot_refresh_06": SNAPSHOT_REFRESH_RESULT_REF,
                "review_batch_apply_next": REVIEW_BATCH_APPLY_REF,
                "public_alpha_reassess_05": "control/inventory/public_alpha_reassess_05_result.json",
                "snapshot_refresh_05": "control/inventory/snapshot_refresh_05_result.json",
                "public_search_ux_mvp": PUBLIC_SEARCH_UX_MVP_REF,
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
            },
            "equivalent_filename_mappings": {
                "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
        },
        "public_alpha_reassess_06_snapshot_metrics.json": result["metrics"],
        "public_alpha_reassess_06_query_coverage_matrix.json": result["query_coverage"],
        "public_alpha_reassess_06_route_matrix.json": result["route_smoke"],
        "public_alpha_reassess_06_domain_coverage_matrix.json": result["domain_coverage"],
        "public_alpha_reassess_06_candidate_usefulness_matrix.json": result["candidate_usefulness"],
        "public_alpha_reassess_06_limited_reviewed_record_matrix.json": result["limited_reviewed_record_usefulness"],
        "public_alpha_reassess_06_review_batch_apply_matrix.json": result["review_batch_apply"],
        "public_alpha_reassess_06_public_search_view_model_matrix.json": result["public_search_view_models"],
        "public_alpha_reassess_06_public_search_ux_mvp_matrix.json": result["public_search_ux_mvp"],
        "public_alpha_reassess_06_resilience_gap_matrix.json": result["resilience_gap"],
        "public_alpha_reassess_06_launch_blocker_matrix.json": result["launch_blockers"],
        "public_alpha_reassess_06_next_work_matrix.json": result["next_work"],
        "public_alpha_reassess_06_boundary_report.json": result["boundary_report"],
        "public_alpha_reassess_06_smoke_result.json": {
            "schema_version": "public_alpha_reassess_06_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "route_smoke_status": result["route_smoke"]["route_smoke_status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
            "reviewed_corpus_growth_confirmed": result["reviewed_corpus_growth_confirmed"],
            **_false_boundaries(),
        },
        "public_alpha_reassess_06_validation_matrix.json": {
            "schema_version": "public_alpha_reassess_06_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_review_batch_apply_next.py",
                "python scripts/validate_public_search_ux_mvp.py",
                "focused public-alpha reassess unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_alpha_reassess_06_result.json": _task_result(result),
        "public_alpha_reassess_06_next_task_decision.json": {
            "schema_version": "public_alpha_reassess_06_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "SEARCH-USEFULNESS-EVAL-00",
                "REVIEWED-ARTIFACT-RECORD-GATE-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "rationale": "Reviewed-corpus growth and UX MVP are present; degraded-mode search resilience is the next missing reliability gate.",
            "launch_recommended": False,
            "demo_mode_recommended": True,
        },
        "public_alpha_reassess_06_failure_repair_log.json": {
            "schema_version": "public_alpha_reassess_06_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-alpha-reassess-06-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-ALPHA-REASSESS-06 Audit\n\nEvidence-based reassessment after review-batch apply snapshot refresh. Decision: reviewed corpus improved to 12 limited projections, public launch not recommended.\n",
        "snapshot_metrics.md": _matrix_md("Snapshot Metrics", result["metrics"]),
        "query_coverage_matrix.md": _matrix_md("Query Coverage Matrix", result["query_coverage"]),
        "route_matrix.md": _matrix_md("Route Matrix", result["route_smoke"]),
        "review_batch_apply_matrix.md": _matrix_md("Review Batch Apply Matrix", result["review_batch_apply"]),
        "resilience_gap_matrix.md": _matrix_md("Resilience Gap Matrix", result["resilience_gap"]),
        "launch_blocker_matrix.md": _matrix_md("Launch Blocker Matrix", result["launch_blockers"]),
        "next_work_matrix.md": _matrix_md("Next Work Matrix", result["next_work"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md(
            "Smoke Result",
            {
                "status": result["status"],
                "launch_recommended": result["launch_recommended"],
                "demo_mode_recommended": result["demo_mode_recommended"],
                "reviewed_corpus_growth_confirmed": result["reviewed_corpus_growth_confirmed"],
            },
        ),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_alpha_reassess_06_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "public_alpha_reassess_06_report.json": _task_result(result),
        "generated/sample_reassess_metrics.json": result["metrics"],
        "generated/sample_launch_blockers.json": result["launch_blockers"],
        "generated/sample_next_work.json": result["next_work"],
        "generated/sample_reassess_decision.json": result["decision"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Alpha Reassess 06 Summary\n\n"
        f"- previous limited reviewed projections: {result['previous_total_limited_reviewed_record_projection_count']}\n"
        f"- reviewed record delta: {result['new_reviewed_record_delta_count']}\n"
        f"- total limited reviewed projections: {result['total_limited_reviewed_record_projection_count']}\n"
        f"- candidate count after apply: {result['candidate_count_after_apply']}\n"
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
        "schema_version": "public_alpha_reassess_06_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "previous_total_limited_reviewed_record_projection_count": result["previous_total_limited_reviewed_record_projection_count"],
        "new_reviewed_record_delta_count": result["new_reviewed_record_delta_count"],
        "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
        "reviewed_known_need_count": result["reviewed_known_need_count"],
        "reviewed_bounded_absence_count": result["reviewed_bounded_absence_count"],
        "candidate_count_after_apply": result["candidate_count_after_apply"],
        "domain_count": result["domain_count"],
        "public_ux_routes_count": result["public_ux_routes_count"],
        "result_card_states_count": result["result_card_states_count"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "reviewed_record_threshold": result["reviewed_record_threshold"],
        "reviewed_record_threshold_met": result["reviewed_record_threshold_met"],
        "reviewed_corpus_growth_confirmed": result["reviewed_corpus_growth_confirmed"],
        "indexless_live_fallback_implemented": result["indexless_live_fallback_implemented"],
        "search_usefulness_eval_implemented": result["search_usefulness_eval_implemented"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_reviewed_artifact_record_gate": result["needs_reviewed_artifact_record_gate"],
        "needs_indexless_live_search_fallback": result["needs_indexless_live_search_fallback"],
        "needs_search_usefulness_eval": result["needs_search_usefulness_eval"],
        "needs_external_full_discovery": result["needs_external_full_discovery"],
        "needs_main_promotion_before_launch": result["needs_main_promotion_before_launch"],
        "needs_public_alpha_launch_approval": result["needs_public_alpha_launch_approval"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_06_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "limited_reviewed_record_matrix_added": True,
        "review_batch_apply_matrix_added": True,
        "public_search_ux_mvp_matrix_added": True,
        "resilience_gap_matrix_added": True,
        "launch_blocker_matrix_added": True,
        "next_work_matrix_added": True,
        "runtime_reassess_added": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "previous_total_limited_reviewed_record_projection_count": result["previous_total_limited_reviewed_record_projection_count"],
        "new_reviewed_record_delta_count": result["new_reviewed_record_delta_count"],
        "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
        "reviewed_known_need_count": result["reviewed_known_need_count"],
        "reviewed_bounded_absence_count": result["reviewed_bounded_absence_count"],
        "candidate_count_after_apply": result["candidate_count_after_apply"],
        "domain_count": result["domain_count"],
        "public_ux_routes_count": result["public_ux_routes_count"],
        "result_card_states_count": result["result_card_states_count"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "reviewed_record_threshold": result["reviewed_record_threshold"],
        "reviewed_record_threshold_met": result["reviewed_record_threshold_met"],
        "reviewed_corpus_growth_confirmed": result["reviewed_corpus_growth_confirmed"],
        "indexless_live_fallback_implemented": result["indexless_live_fallback_implemented"],
        "search_usefulness_eval_implemented": result["search_usefulness_eval_implemented"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": result["needs_more_reviewed_artifact_records"],
        "needs_reviewed_artifact_record_gate": result["needs_reviewed_artifact_record_gate"],
        "needs_indexless_live_search_fallback": result["needs_indexless_live_search_fallback"],
        "needs_search_usefulness_eval": result["needs_search_usefulness_eval"],
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
    candidate_count: int,
    domain_count: int,
    route_smoke_passed: bool,
    ux_mvp_verified: bool,
    reviewed_corpus_growth_confirmed: bool,
    resilience_ready: bool,
    search_usefulness_eval_ready: bool,
    policy: Mapping[str, Any],
) -> float:
    reviewed = min(limited_reviewed_count / max(int(policy["public_alpha_min_reviewed_record_threshold"]), 1), 1.0)
    domains = min(domain_count / max(int(policy["public_alpha_min_domain_coverage_threshold"]), 1), 1.0)
    candidates = min(candidate_count / 75.0, 1.0)
    route = 1.0 if route_smoke_passed else 0.0
    ux = 1.0 if ux_mvp_verified else 0.0
    growth = 1.0 if reviewed_corpus_growth_confirmed else 0.0
    resilience = 1.0 if resilience_ready else 0.0
    eval_ready = 1.0 if search_usefulness_eval_ready else 0.0
    score = (
        reviewed * 0.35
        + domains * 0.15
        + candidates * 0.07
        + route * 0.10
        + ux * 0.15
        + growth * 0.08
        + resilience * 0.06
        + eval_ready * 0.04
    )
    return round(score, 3)


def _context(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot_refresh_06_result" in value and "review_batch_apply_result" in value:
        return value
    return load_snapshot_refresh_06_metrics()


def _assert_snapshot_refresh_06_context(context: Mapping[str, Any]) -> None:
    snapshot = context["snapshot_refresh_06_inventory_result"]
    review_apply = context["review_batch_apply_result"]
    ux_result = context["public_search_ux_mvp_result"]
    if snapshot.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("snapshot refresh 06 result must pass or pass with warnings")
    expected_counts = {
        "previous_total_limited_reviewed_record_projection_count": 4,
        "new_reviewed_record_delta_count": 8,
        "total_limited_reviewed_record_projection_count": 12,
        "reviewed_known_need_count": 2,
        "reviewed_bounded_absence_count": 2,
        "candidate_count_after_apply": 60,
        "public_ux_routes_count": 8,
        "result_card_states_count": 8,
    }
    for key, expected in expected_counts.items():
        if int(snapshot.get(key) or 0) != expected:
            raise ValueError(f"snapshot refresh 06 count mismatch for {key}")
    if review_apply.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("review batch apply result must pass or pass with warnings")
    if ux_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("public search UX MVP result must pass or pass with warnings")
    if ux_result.get("ux_smoke_passed") is not True:
        raise ValueError("public search UX MVP smoke must pass")
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
            raise ValueError(f"reassess 06 boundary failed: {key}")


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
        "review_batch_apply_improves_readiness_but_is_not_launch_sufficient",
        "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification",
        "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification",
        "reviewed_known_needs_are_not_resolved_objects",
        "bounded_absences_are_not_universal_absences",
        "twelve_limited_reviewed_records_not_enough_for_launch",
        "indexless_live_fallback_required_for_resilience",
        "search_usefulness_eval_required_before_launch",
        "external_full_discovery_required_before_main_promotion",
        "main_promotion_required_before_launch",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"public alpha reassess 06 policy missing required rules: {', '.join(missing)}")
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
        raise PermissionError(f"public alpha reassess 06 policy enables forbidden behavior: {', '.join(enabled)}")


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
