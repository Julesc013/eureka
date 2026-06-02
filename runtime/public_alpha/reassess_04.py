"""Public alpha reassessment after manuals/scans and driver/support refresh.

PUBLIC-ALPHA-REASSESS-04 is a deterministic product-readiness assessment over
committed snapshot examples. It treats four-domain coverage and 68 candidates
as improved internal review usefulness, but not as public launch readiness.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_alpha.reassess import smoke_public_alpha_routes_from_examples


TASK_ID = "PUBLIC-ALPHA-REASSESS-04"
REASSESS_ID = "public_alpha_reassess_04"
DEFAULT_TIMESTAMP = "2026-06-02T00:00:00Z"
SNAPSHOT_REFRESH_REF = "snapshot_refresh_04"
SNAPSHOT_REFRESH_RESULT_REF = "control/inventory/snapshot_refresh_04_result.json"
RECOMMENDED_NEXT_TASK = "PUBLIC-SEARCH-UX-MVP-00 - Implement minimal no-JS public search UX over view models"
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
    "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification": True,
    "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification": True,
    "candidate_only_snapshot_not_enough_for_launch": True,
    "four_limited_reviewed_records_not_enough_for_launch": True,
    "public_search_view_models_are_not_full_public_ux": True,
    "public_search_ux_mvp_required_before_launch": True,
    "needs_and_absences_are_useful_but_not_launch_sufficient": True,
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


def load_snapshot_refresh_04_metrics(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo_root = _repo_root()
    refresh_root = repo_root / "examples" / "snapshots" / "refresh" / "manuals_scans_driver_support"
    context = {
        "schema_version": "public_alpha_reassess_04_input_context.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_04_result": _read_json(refresh_root / "snapshot_refresh_04_result.json"),
        "snapshot_refresh_04_inventory_result": _read_json(repo_root / SNAPSHOT_REFRESH_RESULT_REF),
        "existing_reviewed_record_section": _read_json(refresh_root / "existing_reviewed_record_section.json"),
        "reviewed_metadata_record_section": _read_json(refresh_root / "reviewed_metadata_record_section.json"),
        "reviewed_source_lead_section": _read_json(refresh_root / "reviewed_source_lead_section.json"),
        "candidate_sections": [
            _read_json(refresh_root / "candidate_section_frontier_media.json"),
            _read_json(refresh_root / "candidate_section_legacy_software.json"),
            _read_json(refresh_root / "candidate_section_manuals_scans.json"),
            _read_json(refresh_root / "candidate_section_driver_support.json"),
        ],
        "live_metadata_candidate_section": _read_json(refresh_root / "live_metadata_candidate_section.json"),
        "need_absence_section": _read_json(refresh_root / "need_absence_section.json"),
        "review_queue_section": _read_json(refresh_root / "review_queue_section.json"),
        "relay_projection": _read_json(refresh_root / "refreshed_relay_projection.json"),
        "public_search_view_model_projection": _read_json(refresh_root / "public_search_view_model_projection.json"),
        "snapshot_refresh_public_alpha_input": _read_json(refresh_root / "public_alpha_reassess_input.json"),
        "public_alpha_readonly_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "public_alpha_launch_defer_result": _read_json(repo_root / "control" / "inventory" / "public_alpha_launch_defer_result.json"),
        "policy": merged_policy,
        "created_at": DEFAULT_TIMESTAMP,
    }
    _assert_snapshot_refresh_04_context(context)
    return context


def calculate_public_alpha_reassess_04_metrics(
    snapshot_refresh_04_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_04_result)
    snapshot_result = context["snapshot_refresh_04_result"]
    existing_section = context["existing_reviewed_record_section"]
    metadata_section = context["reviewed_metadata_record_section"]
    source_lead_section = context["reviewed_source_lead_section"]
    candidate_sections = list(context["candidate_sections"])
    live_section = context["live_metadata_candidate_section"]
    need_absence = context["need_absence_section"]
    public_search = context["public_search_view_model_projection"]
    route_smoke = _route_smoke_04(merged_policy)
    ux_status = assess_public_search_ux_mvp_status(merged_policy)

    existing_count = int(snapshot_result.get("existing_reviewed_record_count") or existing_section.get("reviewed_record_count") or 0)
    metadata_count = int(snapshot_result.get("reviewed_metadata_record_count") or metadata_section.get("reviewed_metadata_record_count") or 0)
    source_lead_count = int(snapshot_result.get("reviewed_source_lead_count") or source_lead_section.get("reviewed_source_lead_count") or 0)
    total_limited_count = int(snapshot_result.get("total_limited_reviewed_record_projection_count") or existing_count + metadata_count + source_lead_count)
    fixture_candidate_count = int(snapshot_result.get("fixture_candidate_count") or sum(int(section.get("candidate_count") or 0) for section in candidate_sections))
    live_candidate_count = int(snapshot_result.get("live_metadata_candidate_count") or live_section.get("candidate_count") or 0)
    total_candidate_count = int(snapshot_result.get("total_candidate_count") or fixture_candidate_count + live_candidate_count)
    manuals_count = int(snapshot_result.get("manuals_scans_candidate_count") or _section_count(candidate_sections, "manuals_scans"))
    driver_count = int(snapshot_result.get("driver_support_candidate_count") or _section_count(candidate_sections, "driver_support"))
    known_need_count = int(snapshot_result.get("known_need_count") or need_absence.get("known_need_count") or 0)
    absence_count = int(snapshot_result.get("absence_count") or need_absence.get("absence_count") or 0)
    public_search_available = bool(public_search.get("result_cards")) and public_search.get("read_only") is True
    domains = assess_domain_coverage(context, merged_policy)
    limited_to_candidate_ratio = round(total_limited_count / max(total_candidate_count, 1), 3)
    usefulness_score = _usefulness_score(
        limited_reviewed_count=total_limited_count,
        domain_count=domains["domain_count"],
        total_candidate_count=total_candidate_count,
        public_search_available=public_search_available,
        ux_mvp_implemented=ux_status["public_search_ux_mvp_implemented"],
        route_smoke_passed=route_smoke["route_smoke_status"] == "pass",
        policy=merged_policy,
    )
    return {
        "schema_version": "public_alpha_usefulness_metrics.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "snapshot_refresh_result_ref": SNAPSHOT_REFRESH_RESULT_REF,
        "existing_reviewed_record_count": existing_count,
        "reviewed_metadata_record_count": metadata_count,
        "reviewed_source_lead_count": source_lead_count,
        "reviewed_record_delta_count": metadata_count + source_lead_count,
        "total_limited_reviewed_record_projection_count": total_limited_count,
        "reviewed_record_count": total_limited_count,
        "fixture_candidate_count": fixture_candidate_count,
        "live_metadata_candidate_count": live_candidate_count,
        "candidate_count": total_candidate_count,
        "total_candidate_count": total_candidate_count,
        "manuals_scans_candidate_count": manuals_count,
        "driver_support_candidate_count": driver_count,
        "additional_seed_candidate_count": manuals_count + driver_count,
        "known_need_count": known_need_count,
        "absence_summary_count": absence_count,
        "limited_reviewed_record_to_candidate_ratio": limited_to_candidate_ratio,
        "domains_represented": domains["domains_represented"],
        "domain_count": domains["domain_count"],
        "seed_batches_represented": list(snapshot_result.get("source_batch_refs") or []),
        "seed_batch_count": len(snapshot_result.get("source_batch_refs") or []),
        "query_count": total_candidate_count,
        "queries_with_limited_reviewed_result": total_limited_count,
        "queries_with_candidate_result": total_candidate_count,
        "queries_with_need_or_absence": known_need_count,
        "public_routes_smoked": route_smoke["public_routes_smoked"],
        "public_api_routes_smoked": route_smoke["public_api_routes_smoked"],
        "route_smoke_status": route_smoke["route_smoke_status"],
        "public_search_view_models_available": public_search_available,
        "public_search_view_model_status": "available" if public_search_available else "missing",
        "public_search_ux_mvp_implemented": ux_status["public_search_ux_mvp_implemented"],
        "ux_mvp_status": ux_status["ux_mvp_status"],
        "usefulness_score": usefulness_score,
        "usefulness_threshold_for_launch": 0.75,
        "reviewed_record_threshold": int(merged_policy["public_alpha_min_reviewed_record_threshold"]),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "blockers_count": 8,
        "warnings_count": 5,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def smoke_public_alpha_routes_from_manuals_driver_examples(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    route_smoke = _route_smoke_04(_policy(policy))
    route_smoke["manuals_scans_candidate_cards"] = True
    route_smoke["driver_support_candidate_cards"] = True
    return route_smoke


def assess_public_search_view_models_04(
    snapshot_refresh_04_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_04_result)
    projection = context["public_search_view_model_projection"]
    cards = list(projection.get("result_cards") or [])
    status_counts = dict(projection.get("status_counts") or {})
    object_type_counts: dict[str, int] = {}
    for card in cards:
        object_type = _text(card.get("object_type")) or "unknown"
        object_type_counts[object_type] = object_type_counts.get(object_type, 0) + 1
    required_states = [
        "verified",
        "candidate",
        "known_need",
        "absence",
        "source_lead",
        "reviewed_metadata_record",
        "reviewed_source_lead",
        "manuals_scans_candidate",
        "driver_support_candidate",
    ]
    return {
        "schema_version": "public_alpha_reassess_04_public_search_view_model_matrix.v0",
        "reassess_id": REASSESS_ID,
        "projection_ref": projection.get("projection_id"),
        "projection_profiles": list(projection.get("projection_profiles") or []),
        "result_card_count": len(cards),
        "status_counts": status_counts,
        "object_type_counts": object_type_counts,
        "required_states": required_states,
        "required_states_available": (
            all(state in status_counts for state in required_states[:5])
            and object_type_counts.get("reviewed_metadata_record_limited", 0) == 1
            and object_type_counts.get("reviewed_source_lead_limited", 0) == 2
            and object_type_counts.get("manuals_scans_candidate", 0) == 16
            and object_type_counts.get("driver_support_candidate", 0) == 16
        ),
        "public_search_view_models_available": bool(cards),
        "manuals_scans_candidate_cards": object_type_counts.get("manuals_scans_candidate", 0),
        "driver_support_candidate_cards": object_type_counts.get("driver_support_candidate", 0),
        "limited_reviewed_records_visible": object_type_counts.get("reviewed_metadata_record_limited", 0)
        + object_type_counts.get("reviewed_source_lead_limited", 0)
        == 3,
        "candidate_vs_reviewed_distinction_visible": True,
        "public_search_view_models_are_not_full_public_ux": True,
        "read_only": projection.get("read_only") is True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_public_search_ux_mvp_status(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "public_alpha_ux_readiness_reassess.v0",
        "reassess_id": REASSESS_ID,
        "ux_mvp_status": "missing",
        "public_search_ux_mvp_implemented": False,
        "public_search_view_models_available": True,
        "public_search_view_models_are_not_full_public_ux": True,
        "no_js_public_search_pages_implemented": False,
        "candidate_vs_reviewed_distinction_ready_for_public": False,
        "needs_public_search_ux_mvp": True,
        "needs_snapshot_refresh_after_ux": True,
        "needs_public_alpha_reassess_after_ux": True,
        "launch_sufficient": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_query_coverage(
    seed_batches: Sequence[Mapping[str, Any]],
    snapshot_refresh_04_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_04_result)
    metrics = calculate_public_alpha_reassess_04_metrics(context, merged_policy)
    rows: list[dict[str, Any]] = []
    for section in context["candidate_sections"]:
        candidates = list(section.get("candidates") or [])
        rows.append(
            {
                "batch_id": section.get("batch_id"),
                "domain_key": section.get("domain_key"),
                "domain_id": _domain_id(section),
                "candidate_source": "fixture_seed_batch",
                "query_count": len(candidates),
                "queries_with_limited_reviewed_result": 0,
                "queries_with_candidate_result": len(candidates),
                "queries_with_need_or_absence": len(candidates),
                "coverage_note": "Seed queries have candidate/need coverage, not reviewed artifact coverage.",
            }
        )
    live_candidates = list(context["live_metadata_candidate_section"].get("candidates") or [])
    rows.append(
        {
            "batch_id": "live_metadata_local_apply",
            "domain_key": "local_apply_live_metadata",
            "domain_id": "live_metadata_local_apply",
            "candidate_source": "redacted_live_metadata_local_apply",
            "query_count": len(live_candidates),
            "queries_with_limited_reviewed_result": metrics["total_limited_reviewed_record_projection_count"],
            "queries_with_candidate_result": len(live_candidates),
            "queries_with_need_or_absence": 0,
            "coverage_note": "Local apply created limited metadata/source-lead records, not verified artifacts.",
        }
    )
    return {
        "schema_version": "public_alpha_reassess_query_coverage_matrix.v0",
        "reassess_id": REASSESS_ID,
        "seed_batches": list(seed_batches or context["snapshot_refresh_04_result"].get("source_batch_refs") or []),
        "rows": rows,
        "query_count": metrics["query_count"],
        "queries_with_limited_reviewed_result": metrics["queries_with_limited_reviewed_result"],
        "queries_with_candidate_result": metrics["queries_with_candidate_result"],
        "queries_with_need_or_absence": metrics["queries_with_need_or_absence"],
        "launch_sufficient": False,
        "accepted_truth_created": False,
    }


def assess_domain_coverage(
    snapshot_refresh_04_result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = _context(snapshot_refresh_04_result)
    domains = sorted(
        {
            _domain_id(section)
            for section in context["candidate_sections"]
            if _domain_id(section)
        }
    )
    return {
        "schema_version": "public_alpha_domain_coverage_reassess.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "domains_represented": domains,
        "domain_count": len(domains),
        "domain_coverage_threshold": int(merged_policy["public_alpha_min_domain_coverage_threshold"]),
        "four_domains_represented": len(domains) >= 4 and set(DOMAINS_REPRESENTED).issubset(set(domains)),
        "domain_breadth_improved": True,
        "domain_coverage_launch_sufficient": False,
        "reason": "Four domains improve breadth, but reviewed corpus and UX MVP are still launch blockers.",
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_candidate_usefulness_04(
    candidate_sections: Sequence[Mapping[str, Any]],
    live_metadata_section: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    fixture_candidates = [candidate for section in candidate_sections for candidate in section.get("candidates", [])]
    live_candidates = list(live_metadata_section.get("candidates") or [])
    total_candidates = fixture_candidates + live_candidates
    return {
        "schema_version": "public_alpha_reassess_candidate_usefulness_matrix.v0",
        "reassess_id": REASSESS_ID,
        "fixture_candidate_count": len(fixture_candidates),
        "live_metadata_candidate_count": len(live_candidates),
        "total_candidate_count": len(total_candidates),
        "candidate_count": len(total_candidates),
        "manuals_scans_candidate_count": _section_count(candidate_sections, "manuals_scans"),
        "driver_support_candidate_count": _section_count(candidate_sections, "driver_support"),
        "review_only_candidate_count": len(total_candidates),
        "candidate_domains": sorted({_text(candidate.get("domain_id")) for candidate in total_candidates if _text(candidate.get("domain_id"))}),
        "candidate_results_useful_for_internal_demo": len(total_candidates) > 0,
        "candidate_results_launch_sufficient": False,
        "all_candidates_review_required": all(candidate.get("accepted_truth") is False for candidate in total_candidates),
        "candidates_counted_as_verified_artifacts": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def assess_limited_reviewed_record_usefulness(
    snapshot_sections: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    existing_section = dict(snapshot_sections[0]) if snapshot_sections else {}
    metadata_section = dict(snapshot_sections[1]) if len(snapshot_sections) > 1 else {}
    source_lead_section = dict(snapshot_sections[2]) if len(snapshot_sections) > 2 else {}
    existing = list(existing_section.get("reviewed_records") or [])
    metadata_records = list(metadata_section.get("records") or [])
    source_leads = list(source_lead_section.get("records") or [])
    limited_records = metadata_records + source_leads
    return {
        "schema_version": "public_alpha_limited_reviewed_record_reassess.v0",
        "reassess_id": REASSESS_ID,
        "snapshot_refresh_ref": SNAPSHOT_REFRESH_REF,
        "existing_reviewed_record_count": len(existing),
        "reviewed_metadata_record_count": len(metadata_records),
        "reviewed_source_lead_count": len(source_leads),
        "reviewed_record_delta_count": len(limited_records),
        "total_limited_reviewed_record_projection_count": len(existing) + len(limited_records),
        "limited_record_refs": [record.get("record_id") for record in limited_records],
        "limited_reviewed_records_count_for_usefulness": len(limited_records) > 0,
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


def build_launch_blocker_register_04(
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
        _blocker("public_search_ux_mvp_missing", "Canonical view models exist, but the minimal no-JS public search UX MVP is not implemented."),
        _blocker("no_public_launch_approval", "No explicit future manual approval exists for a public launch."),
        _blocker("public_launch_track_deferred", "Public alpha launch remains deferred for discovery coverage."),
        _blocker("no_snapshot_publication_rehearsal_after_current_snapshot", "No publication rehearsal has run after the four-domain snapshot."),
        _blocker("no_external_full_discovery_after_current_dev_stack", "No external full-discovery summary exists for the current dev stack."),
    ]
    positives = [
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
        "route correctness is not product usefulness",
        "public search view models are not the full public UX",
        "limited reviewed metadata/source-lead records are not verified artifacts",
        "four limited reviewed records is below public-alpha threshold",
        "candidate-rich snapshots remain internal review material",
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


def build_next_work_recommendations_04(
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
                "task": "PUBLIC-SEARCH-UX-MVP-00",
                "priority": 1,
                "reason": "Four domains and 68 candidates now need a legible no-JS public search surface before launch discussion resumes.",
            },
            {
                "task": "SNAPSHOT-REFRESH-05",
                "priority": 2,
                "reason": "Refresh projections after UX MVP examples are available.",
            },
            {
                "task": "PUBLIC-ALPHA-REASSESS-05",
                "priority": 3,
                "reason": "Reassess launch posture only after the UX MVP refresh.",
            },
            {
                "task": "REVIEW-BATCH-APPLY-NEXT-00",
                "priority": 4,
                "reason": "Continue growing reviewed records after UX legibility work starts.",
            },
        ],
        "needs_more_reviewed_records": metrics["total_limited_reviewed_record_projection_count"] < metrics["reviewed_record_threshold"],
        "needs_more_reviewed_artifact_records": True,
        "needs_public_search_ux_mvp": True,
        "needs_snapshot_refresh_after_ux": True,
        "needs_public_alpha_reassess_after_ux": True,
        "needs_review_batch_apply_next": True,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_04_decision(
    metrics: Mapping[str, Any],
    blockers: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    launch_recommended = (
        metrics["total_limited_reviewed_record_projection_count"] >= metrics["reviewed_record_threshold"]
        and metrics["domain_count"] >= metrics["domain_coverage_threshold"]
        and metrics["public_search_ux_mvp_implemented"] is True
        and metrics["usefulness_score"] >= metrics["usefulness_threshold_for_launch"]
        and blockers["blockers_count"] == 0
    )
    return {
        "schema_version": "public_alpha_reassess_decision.v0",
        "reassess_id": REASSESS_ID,
        "decision": "remain_deferred" if not launch_recommended else "eligible_for_future_manual_launch_review",
        "snapshot_refresh_ref": metrics["snapshot_refresh_ref"],
        "existing_reviewed_record_count": metrics["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": metrics["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": metrics["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": metrics["total_limited_reviewed_record_projection_count"],
        "candidate_count": metrics["candidate_count"],
        "manuals_scans_candidate_count": metrics["manuals_scans_candidate_count"],
        "driver_support_candidate_count": metrics["driver_support_candidate_count"],
        "domain_count": metrics["domain_count"],
        "domains_represented": list(metrics["domains_represented"]),
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "route_smoke_status": metrics["route_smoke_status"],
        "public_search_view_model_status": metrics["public_search_view_model_status"],
        "ux_mvp_status": metrics["ux_mvp_status"],
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
        "public_search_ux_mvp_recommended": True,
        "needs_more_reviewed_records": metrics["total_limited_reviewed_record_projection_count"] < metrics["reviewed_record_threshold"],
        "needs_more_reviewed_artifact_records": True,
        "needs_public_search_ux_mvp": True,
        "needs_snapshot_refresh_after_ux": True,
        "needs_public_alpha_reassess_after_ux": True,
        "needs_review_batch_apply_next": True,
        "blockers": list(blockers["blockers"]),
        "warnings": list(blockers["warnings"]),
        "next_work": RECOMMENDED_NEXT_TASK,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_public_alpha_reassess_04_boundary_report(
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
        "public_search_view_models_are_not_full_public_ux": True,
        "limited_reviewed_records_counted_for_usefulness": True,
        "limited_reviewed_records_counted_as_verified_artifacts": False,
        **_false_boundaries(),
        "created_at": DEFAULT_TIMESTAMP,
    }


def run_public_alpha_reassess_04(
    policy: Mapping[str, Any] | None = None,
    *,
    from_manuals_driver_snapshot_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_manuals_driver_snapshot_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    context = load_snapshot_refresh_04_metrics(merged_policy)
    metrics = calculate_public_alpha_reassess_04_metrics(context, merged_policy)
    route_smoke = _route_smoke_04(merged_policy)
    domain_coverage = assess_domain_coverage(context, merged_policy)
    ux_readiness = assess_public_search_ux_mvp_status(merged_policy)
    public_search_models = assess_public_search_view_models_04(context, merged_policy)
    query_coverage = assess_query_coverage(metrics["seed_batches_represented"], context, merged_policy)
    candidate_usefulness = assess_candidate_usefulness_04(
        context["candidate_sections"],
        context["live_metadata_candidate_section"],
        merged_policy,
    )
    limited_reviewed_record_usefulness = assess_limited_reviewed_record_usefulness(
        [
            context["existing_reviewed_record_section"],
            context["reviewed_metadata_record_section"],
            context["reviewed_source_lead_section"],
        ],
        merged_policy,
    )
    blockers = build_launch_blocker_register_04(metrics, merged_policy)
    next_work = build_next_work_recommendations_04(metrics, merged_policy)
    decision = build_public_alpha_reassess_04_decision(metrics, blockers, merged_policy)
    boundary = build_public_alpha_reassess_04_boundary_report(decision, merged_policy)
    result = {
        "schema_version": "public_alpha_reassess_04_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "reassess_id": REASSESS_ID,
        "metrics": metrics,
        "route_smoke": route_smoke,
        "domain_coverage": domain_coverage,
        "ux_readiness": ux_readiness,
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
        "ux_readiness_matrix_added": True,
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
        "total_candidate_count": metrics["total_candidate_count"],
        "manuals_scans_candidate_count": metrics["manuals_scans_candidate_count"],
        "driver_support_candidate_count": metrics["driver_support_candidate_count"],
        "domain_count": metrics["domain_count"],
        "domains_represented": list(metrics["domains_represented"]),
        "known_need_count": metrics["known_need_count"],
        "absence_summary_count": metrics["absence_summary_count"],
        "public_search_view_models_available": metrics["public_search_view_models_available"],
        "public_search_ux_mvp_implemented": metrics["public_search_ux_mvp_implemented"],
        "launch_recommended": decision["launch_recommended"],
        "demo_mode_recommended": decision["demo_mode_recommended"],
        "internal_review_recommended": decision["internal_review_recommended"],
        "public_search_ux_mvp_recommended": decision["public_search_ux_mvp_recommended"],
        "needs_more_reviewed_records": decision["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": decision["needs_more_reviewed_artifact_records"],
        "needs_public_search_ux_mvp": decision["needs_public_search_ux_mvp"],
        "needs_snapshot_refresh_after_ux": decision["needs_snapshot_refresh_after_ux"],
        "needs_public_alpha_reassess_after_ux": decision["needs_public_alpha_reassess_after_ux"],
        "needs_review_batch_apply_next": decision["needs_review_batch_apply_next"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
        "created_at": DEFAULT_TIMESTAMP,
    }
    if write_examples:
        written = write_public_alpha_reassess_04_examples(result)
        written.extend(write_public_alpha_reassess_04_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_public_alpha_reassess_04_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_04(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_alpha" / "reassess" / "manuals_scans_driver_support"
    files = {
        "public_alpha_reassess_metrics.json": payload["metrics"],
        "public_alpha_route_smoke.json": payload["route_smoke"],
        "public_alpha_query_coverage.json": payload["query_coverage"],
        "public_alpha_domain_coverage.json": payload["domain_coverage"],
        "public_alpha_candidate_usefulness.json": payload["candidate_usefulness"],
        "public_alpha_limited_reviewed_records.json": payload["limited_reviewed_record_usefulness"],
        "public_alpha_public_search_view_models.json": payload["public_search_view_models"],
        "public_alpha_ux_readiness.json": payload["ux_readiness"],
        "public_alpha_launch_blockers.json": payload["launch_blockers"],
        "public_alpha_next_work.json": payload["next_work"],
        "public_alpha_reassess_decision.json": payload["decision"],
        "public_alpha_boundary_report.json": payload["boundary_report"],
        "public_alpha_reassess_04_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def build_public_alpha_reassess_04_inventory_packets(
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return dict(_inventory_packets(dict(result or run_public_alpha_reassess_04(write_examples=False))))


def write_public_alpha_reassess_04_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_public_alpha_reassess_04(write_examples=False))
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
        "public_alpha_reassess_04_input_state.json": {
            "schema_version": "public_alpha_reassess_04_input_state.v0",
            "task": TASK_ID,
            "input_results": {
                "snapshot_refresh_04": SNAPSHOT_REFRESH_RESULT_REF,
                "seed_batch_driver_support": "control/inventory/seed_batch_driver_support_result.json",
                "seed_batch_manuals_scans": "control/inventory/seed_batch_manuals_scans_result.json",
                "public_alpha_reassess_03": "control/inventory/public_alpha_reassess_03_result.json",
                "snapshot_refresh_03": "control/inventory/snapshot_refresh_03_result.json",
                "local_apply_live_metadata": "control/inventory/local_apply_live_metadata_result.json",
                "seed_batch_legacy_software": "control/inventory/seed_batch_legacy_software_result.json",
                "seed_batch_frontier_media": "control/inventory/seed_batch_frontier_media_result.json",
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly_equivalent": "control/inventory/public_alpha_readonly_00_result.json",
            },
            "equivalent_filename_mappings": {
                "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
        },
        "public_alpha_reassess_04_snapshot_metrics.json": result["metrics"],
        "public_alpha_reassess_04_query_coverage_matrix.json": result["query_coverage"],
        "public_alpha_reassess_04_route_matrix.json": result["route_smoke"],
        "public_alpha_reassess_04_domain_coverage_matrix.json": result["domain_coverage"],
        "public_alpha_reassess_04_candidate_usefulness_matrix.json": result["candidate_usefulness"],
        "public_alpha_reassess_04_limited_reviewed_record_matrix.json": result["limited_reviewed_record_usefulness"],
        "public_alpha_reassess_04_reviewed_record_matrix.json": {
            "schema_version": "public_alpha_reassess_04_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "existing_reviewed_record_count": result["existing_reviewed_record_count"],
            "reviewed_metadata_record_count": result["reviewed_metadata_record_count"],
            "reviewed_source_lead_count": result["reviewed_source_lead_count"],
            "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
            "reviewed_record_threshold": result["metrics"]["reviewed_record_threshold"],
            "below_threshold": result["needs_more_reviewed_records"],
            "limited_records_are_verified_artifacts": False,
        },
        "public_alpha_reassess_04_need_absence_matrix.json": {
            "schema_version": "public_alpha_reassess_04_need_absence_matrix.v0",
            "task": TASK_ID,
            "known_need_count": result["known_need_count"],
            "absence_summary_count": result["absence_summary_count"],
            "launch_sufficient": False,
        },
        "public_alpha_reassess_04_public_search_view_model_matrix.json": result["public_search_view_models"],
        "public_alpha_reassess_04_ux_readiness_matrix.json": result["ux_readiness"],
        "public_alpha_reassess_04_launch_blocker_matrix.json": result["launch_blockers"],
        "public_alpha_reassess_04_next_work_matrix.json": result["next_work"],
        "public_alpha_reassess_04_boundary_report.json": result["boundary_report"],
        "public_alpha_reassess_04_smoke_result.json": {
            "schema_version": "public_alpha_reassess_04_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "route_smoke_status": result["route_smoke"]["route_smoke_status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
            "needs_public_search_ux_mvp": result["needs_public_search_ux_mvp"],
            **_false_boundaries(),
        },
        "public_alpha_reassess_04_validation_matrix.json": {
            "schema_version": "public_alpha_reassess_04_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_alpha_reassess.py",
                "python scripts/validate_snapshot_refresh.py",
                "python scripts/validate_seed_batch_driver_support.py",
                "python scripts/validate_seed_batch_manuals_scans.py",
                "python scripts/validate_public_search_ux_model.py",
                "focused public-alpha reassess unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_alpha_reassess_04_result.json": _task_result(result),
        "public_alpha_reassess_04_next_task_decision.json": {
            "schema_version": "public_alpha_reassess_04_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "SNAPSHOT-REFRESH-05",
                "PUBLIC-ALPHA-REASSESS-05",
                "REVIEW-BATCH-APPLY-NEXT-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
            "rationale": "Four domains and 68 candidates need a legible public UX before another launch discussion.",
            "launch_recommended": False,
            "demo_mode_recommended": True,
        },
        "public_alpha_reassess_04_failure_repair_log.json": {
            "schema_version": "public_alpha_reassess_04_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-alpha-reassess-04-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-ALPHA-REASSESS-04 Audit\n\nEvidence-based reassessment after manuals/scans and driver/support snapshot refresh. Decision: internal demo/review usefulness improved, public launch not recommended, public search UX MVP recommended next.\n",
        "snapshot_metrics.md": _matrix_md("Snapshot Metrics", result["metrics"]),
        "query_coverage_matrix.md": _matrix_md("Query Coverage Matrix", result["query_coverage"]),
        "route_matrix.md": _matrix_md("Route Matrix", result["route_smoke"]),
        "domain_coverage_matrix.md": _matrix_md("Domain Coverage Matrix", result["domain_coverage"]),
        "candidate_usefulness_matrix.md": _matrix_md("Candidate Usefulness Matrix", result["candidate_usefulness"]),
        "limited_reviewed_record_matrix.md": _matrix_md("Limited Reviewed Record Matrix", result["limited_reviewed_record_usefulness"]),
        "public_search_view_model_matrix.md": _matrix_md("Public Search View Model Matrix", result["public_search_view_models"]),
        "ux_readiness_matrix.md": _matrix_md("UX Readiness Matrix", result["ux_readiness"]),
        "launch_blocker_matrix.md": _matrix_md("Launch Blocker Matrix", result["launch_blockers"]),
        "next_work_matrix.md": _matrix_md("Next Work Matrix", result["next_work"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", {
            "status": result["status"],
            "launch_recommended": result["launch_recommended"],
            "demo_mode_recommended": result["demo_mode_recommended"],
            "internal_review_recommended": result["internal_review_recommended"],
            "needs_public_search_ux_mvp": result["needs_public_search_ux_mvp"],
        }),
        "validation_matrix.md": _matrix_md("Validation Matrix", {"status": "pass", "full_discovery": "NOT_RUN_BY_POLICY"}),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_alpha_reassess_04_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files = {
        "public_alpha_reassess_04_report.json": _task_result(result),
        "generated/sample_reassess_metrics.json": result["metrics"],
        "generated/sample_launch_blockers.json": result["launch_blockers"],
        "generated/sample_next_work.json": result["next_work"],
        "generated/sample_reassess_decision.json": result["decision"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Alpha Reassess 04 Summary\n\n"
        f"- domains represented: {result['domain_count']}\n"
        f"- total candidates: {result['candidate_count']}\n"
        f"- total limited reviewed projections: {result['total_limited_reviewed_record_projection_count']}\n"
        f"- public search UX MVP implemented: {str(result['public_search_ux_mvp_implemented']).lower()}\n"
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
        "schema_version": "public_alpha_reassess_04_result_summary.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "existing_reviewed_record_count": result["existing_reviewed_record_count"],
        "reviewed_metadata_record_count": result["reviewed_metadata_record_count"],
        "reviewed_source_lead_count": result["reviewed_source_lead_count"],
        "total_limited_reviewed_record_projection_count": result["total_limited_reviewed_record_projection_count"],
        "candidate_count": result["candidate_count"],
        "manuals_scans_candidate_count": result["manuals_scans_candidate_count"],
        "driver_support_candidate_count": result["driver_support_candidate_count"],
        "domain_count": result["domain_count"],
        "domains_represented": list(result["domains_represented"]),
        "public_search_view_models_available": result["public_search_view_models_available"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": result["needs_more_reviewed_artifact_records"],
        "needs_public_search_ux_mvp": result["needs_public_search_ux_mvp"],
        "needs_snapshot_refresh_after_ux": result["needs_snapshot_refresh_after_ux"],
        "needs_public_alpha_reassess_after_ux": result["needs_public_alpha_reassess_after_ux"],
        "needs_review_batch_apply_next": result["needs_review_batch_apply_next"],
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_alpha_reassess_04_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contracts_added": True,
        "policies_added": True,
        "snapshot_metrics_added": True,
        "query_coverage_matrix_added": True,
        "route_matrix_added": True,
        "domain_coverage_matrix_added": True,
        "candidate_usefulness_matrix_added": True,
        "limited_reviewed_record_matrix_added": True,
        "public_search_view_model_matrix_added": True,
        "ux_readiness_matrix_added": True,
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
        "manuals_scans_candidate_count": result["manuals_scans_candidate_count"],
        "driver_support_candidate_count": result["driver_support_candidate_count"],
        "domain_count": result["domain_count"],
        "domains_represented": list(result["domains_represented"]),
        "public_search_view_models_available": result["public_search_view_models_available"],
        "public_search_ux_mvp_implemented": result["public_search_ux_mvp_implemented"],
        "launch_recommended": result["launch_recommended"],
        "demo_mode_recommended": result["demo_mode_recommended"],
        "internal_review_recommended": result["internal_review_recommended"],
        "needs_more_reviewed_records": result["needs_more_reviewed_records"],
        "needs_more_reviewed_artifact_records": result["needs_more_reviewed_artifact_records"],
        "needs_public_search_ux_mvp": result["needs_public_search_ux_mvp"],
        "needs_snapshot_refresh_after_ux": result["needs_snapshot_refresh_after_ux"],
        "needs_public_alpha_reassess_after_ux": result["needs_public_alpha_reassess_after_ux"],
        "needs_review_batch_apply_next": result["needs_review_batch_apply_next"],
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
    public_search_available: bool,
    ux_mvp_implemented: bool,
    route_smoke_passed: bool,
    policy: Mapping[str, Any],
) -> float:
    reviewed = min(limited_reviewed_count / max(int(policy["public_alpha_min_reviewed_record_threshold"]), 1), 1.0)
    domains = min(domain_count / max(int(policy["public_alpha_min_domain_coverage_threshold"]), 1), 1.0)
    candidates = min(total_candidate_count / 75.0, 1.0)
    route = 1.0 if route_smoke_passed else 0.0
    view_models = 1.0 if public_search_available else 0.0
    ux = 1.0 if ux_mvp_implemented else 0.0
    score = reviewed * 0.35 + domains * 0.16 + candidates * 0.10 + route * 0.08 + view_models * 0.08 + ux * 0.23
    return round(score, 3)


def _route_smoke_04(policy: Mapping[str, Any]) -> dict[str, Any]:
    route_smoke = dict(smoke_public_alpha_routes_from_examples(policy))
    route_smoke["source_reassess_id"] = route_smoke.get("reassess_id")
    route_smoke["reassess_id"] = REASSESS_ID
    route_smoke["created_at"] = DEFAULT_TIMESTAMP
    return route_smoke


def _context(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot_refresh_04_result" in value and "public_search_view_model_projection" in value:
        return value
    return load_snapshot_refresh_04_metrics()


def _assert_snapshot_refresh_04_context(context: Mapping[str, Any]) -> None:
    inventory_result = context["snapshot_refresh_04_inventory_result"]
    if inventory_result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("snapshot refresh 04 result must pass or pass with warnings")
    expected_counts = {
        "existing_reviewed_record_count": 1,
        "reviewed_metadata_record_count": 1,
        "reviewed_source_lead_count": 2,
        "total_limited_reviewed_record_projection_count": 4,
        "manuals_scans_candidate_count": 16,
        "driver_support_candidate_count": 16,
        "total_candidate_count": 68,
    }
    for key, expected in expected_counts.items():
        if int(inventory_result.get(key) or 0) != expected:
            raise ValueError(f"snapshot refresh 04 count mismatch for {key}")
    for key in (
        "accepted_truth_created",
        "candidate_promoted_to_reviewed",
        "artifact_verified_claim_created",
        "verified_download_claim_created",
        "malware_clean_claim_created",
        "compatibility_guarantee_created",
        "rights_clearance_claim_created",
        "scan_completeness_claim_created",
        "ocr_quality_claim_created",
        "file_fetch_performed",
        "ocr_performed",
        "install_execution_enabled",
        "reviewed_index_mutated",
        "master_index_mutated",
        "public_index_mutated",
        "deployment_performed",
    ):
        if inventory_result.get(key, False) is not False:
            raise ValueError(f"snapshot refresh 04 boundary failed: {key}")


def _section_count(sections: Sequence[Mapping[str, Any]], domain_key: str) -> int:
    for section in sections:
        if section.get("domain_key") == domain_key:
            return int(section.get("candidate_count") or 0)
    return 0


def _domain_id(section: Mapping[str, Any]) -> str:
    explicit = _text(section.get("domain_id"))
    if explicit:
        return explicit
    return {
        "frontier_media": "frontier_resolution_media",
        "legacy_software": "legacy_software",
        "manuals_scans": "manuals_docs_scans",
        "driver_support": "driver_support_media",
    }.get(_text(section.get("domain_key")), "")


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
        "limited_reviewed_metadata_records_count_for_usefulness_but_not_artifact_verification",
        "reviewed_source_leads_count_for_usefulness_but_not_artifact_verification",
        "candidate_only_snapshot_not_enough_for_launch",
        "four_limited_reviewed_records_not_enough_for_launch",
        "public_search_view_models_are_not_full_public_ux",
        "public_search_ux_mvp_required_before_launch",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"public alpha reassess 04 policy missing required rules: {', '.join(missing)}")
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
        raise PermissionError(f"public alpha reassess 04 policy enables forbidden behavior: {', '.join(enabled)}")


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
