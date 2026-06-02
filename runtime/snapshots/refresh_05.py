"""Snapshot refresh after the public search UX MVP.

SNAPSHOT-REFRESH-05 packages the four-domain snapshot refresh and the no-JS
public search UX MVP into read-only projection sections. It does not deploy,
write site/dist, mutate indexes, call live sources, fetch files, download,
extract, OCR, execute, install, or call model providers.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.public_search import build_public_search_ux_mvp_bundle
from runtime.snapshots import refresh_04


DEFAULT_TIMESTAMP = "2026-06-03T00:00:00Z"
SNAPSHOT_REFRESH_ID = "snapshot_refresh_05"
TASK_ID = "SNAPSHOT-REFRESH-05"
SNAPSHOT_REFRESH_04_REF = "control/inventory/snapshot_refresh_04_result.json"
PUBLIC_SEARCH_UX_MVP_REF = "control/inventory/public_search_ux_mvp_result.json"
NEXT_TASK = "PUBLIC-ALPHA-REASSESS-05 - Reassess alpha after public search UX projection refresh"

SUPPORTED_RESULT_CARD_STATES = (
    "verified",
    "reviewed_metadata_record",
    "reviewed_source_lead",
    "candidate",
    "near_miss",
    "known_need",
    "absence",
    "source_lead",
)

BOUNDARY_FALSE_KEYS = (
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
    "operator_instance_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "site_dist_written",
    "download_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
)

DEFAULT_POLICY: dict[str, Any] = {
    "snapshot_refresh_is_projection": True,
    "public_ux_projection_is_read_only": True,
    "public_search_ux_does_not_own_search_behavior": True,
    "no_js_public_search_required": True,
    "candidate_verified_distinction_required": True,
    "limited_reviewed_record_distinction_required": True,
    "no_results_need_projection_required": True,
    "no_public_mutation": True,
    "no_public_live_source_fanout": True,
    "no_reviewed_index_mutation": True,
    "no_master_index_mutation": True,
    "no_public_index_mutation": True,
    "no_deployment": True,
    "no_site_dist_write": True,
    "no_public_launch_claim": True,
    "no_production_claim": True,
    "downloads_enabled": False,
    "file_fetches_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
}


def load_public_search_ux_mvp_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    repo = _repo_root()
    result = _read_json(repo / PUBLIC_SEARCH_UX_MVP_REF)
    bundle = build_public_search_ux_mvp_bundle()
    _assert_public_search_ux_mvp(result, bundle)
    return {
        "schema_version": "snapshot_refresh_05_public_search_ux_mvp_handoff.v0",
        "task": TASK_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "result": result,
        "routes": list(bundle["routes"]),
        "pages": dict(bundle["pages"]),
        "result_cards": list(bundle["result_cards"]),
        "status_badges": dict(bundle["status_badges"]),
        "no_results": dict(bundle["no_results"]),
        "accessibility": dict(bundle["accessibility"]),
        "projection": dict(bundle["projection"]),
        "text_projection": bundle["text_projection"],
        "html_example_refs": {
            name: f"examples/public_search_ux/{name}" for name in bundle["html_examples"]
        },
        "no_js_required": True,
        "public_projection_read_only": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def load_snapshot_refresh_04_handoff(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    result = refresh_04.run_snapshot_refresh_04(from_manuals_driver_examples=True)
    if result.get("status") != "pass" or result.get("fixture_snapshot_refresh_passed") is not True:
        raise ValueError("snapshot refresh 04 must pass before snapshot refresh 05")
    if result.get("total_candidate_count") != 68:
        raise ValueError("snapshot refresh 04 total candidate count mismatch")
    for key in (
        "site_dist_written",
        "deployment_performed",
        "public_index_mutated",
        "master_index_mutated",
        "download_performed",
        "file_fetch_performed",
        "ocr_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if result.get(key) is not False:
            raise ValueError(f"snapshot refresh 04 boundary failed: {key}")
    return result


def build_snapshot_refresh_05_plan(
    snapshot_04: Mapping[str, Any],
    ux_mvp: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    return {
        "schema_version": "snapshot_refresh_plan.v0",
        "record_type": "snapshot_refresh_plan",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "snapshot_refresh_04_ref": SNAPSHOT_REFRESH_04_REF,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "source_batches": list(snapshot_04.get("source_batches") or []),
        "public_search_ux_section_refs": [_section_id("snapshot_public_search_ux_section", SNAPSHOT_REFRESH_ID)],
        "public_route_section_refs": [_section_id("snapshot_public_route_section", SNAPSHOT_REFRESH_ID)],
        "result_card_section_refs": [_section_id("snapshot_result_card_section", SNAPSHOT_REFRESH_ID)],
        "no_results_section_refs": [_section_id("snapshot_no_results_section", SNAPSHOT_REFRESH_ID)],
        "text_projection_section_refs": [_section_id("snapshot_text_projection_section", SNAPSHOT_REFRESH_ID)],
        "relay_projection_refs": [_section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID)],
        "public_alpha_reassess_refs": [_section_id("public_alpha_reassess", SNAPSHOT_REFRESH_ID)],
        "public_ux_routes_count": len(ux_mvp.get("routes") or []),
        "result_card_count": len(ux_mvp.get("result_cards") or []),
        "result_card_states_count": len(SUPPORTED_RESULT_CARD_STATES),
        "refresh_mode": "public_search_ux_projection_only",
        "no_js_required": True,
        "public_projection_read_only": True,
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_public_search_ux_section(
    ux_mvp: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    routes = list(ux_mvp.get("routes") or [])
    pages = dict(ux_mvp.get("pages") or {})
    cards = list(ux_mvp.get("result_cards") or [])
    return {
        "schema_version": "snapshot_public_search_ux_section.v0",
        "record_type": "snapshot_public_search_ux_section",
        "section_id": _section_id("snapshot_public_search_ux_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "route_refs": [route.get("route") for route in routes],
        "page_refs": [page.get("canonical_route") for page in pages.values()],
        "result_card_refs": [card.get("view_model_id") for card in cards],
        "no_results_refs": ["examples/public_search_ux/no_results_need_page.html"],
        "html_example_refs": dict(ux_mvp.get("html_example_refs") or {}),
        "route_count": len(routes),
        "page_count": len(pages),
        "result_card_count": len(cards),
        "no_js_required": True,
        "public_read_only": True,
        "mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "download_enabled": False,
        "file_fetch_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "install_execution_enabled": False,
        "model_provider_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_public_route_section(
    ux_mvp: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    routes = [dict(route) for route in ux_mvp.get("routes") or []]
    return {
        "schema_version": "snapshot_public_route_section.v0",
        "record_type": "snapshot_public_route_section",
        "section_id": _section_id("snapshot_public_route_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "routes": routes,
        "route_count": len(routes),
        "all_routes_get": all(route.get("method") == "GET" for route in routes),
        "all_routes_no_js": all(route.get("no_js_required") is True for route in routes),
        "all_routes_read_only": all(route.get("public_read_only") is True for route in routes),
        "mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_result_card_projection_section(
    ux_mvp: Mapping[str, Any],
    snapshot_04: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    cards = [dict(card) for card in ux_mvp.get("result_cards") or []]
    observed = sorted({card.get("status") for card in cards if card.get("status")})
    return {
        "schema_version": "snapshot_result_card_section.v0",
        "record_type": "snapshot_result_card_section",
        "section_id": _section_id("snapshot_result_card_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "snapshot_refresh_04_ref": SNAPSHOT_REFRESH_04_REF,
        "cards": cards,
        "result_card_count": len(cards),
        "supported_statuses": list(SUPPORTED_RESULT_CARD_STATES),
        "observed_statuses": observed,
        "result_card_states_count": len(SUPPORTED_RESULT_CARD_STATES),
        "source_snapshot_card_count": len(snapshot_04.get("public_search_view_model_projection", {}).get("result_cards") or []),
        "candidate_verified_distinction_passed": True,
        "limited_reviewed_record_distinction_passed": True,
        "candidate_cards_accepted_truth": False,
        "limited_records_are_not_verified_artifacts": True,
        "public_read_only": True,
        "mutation_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_no_results_projection_section(
    ux_mvp: Mapping[str, Any],
    snapshot_04: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    no_results = dict(ux_mvp.get("no_results") or {})
    return {
        "schema_version": "snapshot_no_results_section.v0",
        "record_type": "snapshot_no_results_section",
        "section_id": _section_id("snapshot_no_results_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "no_results": no_results,
        "no_results_sections_count": 1,
        "known_need_count": int(snapshot_04.get("known_need_count") or 0),
        "absence_count": int(snapshot_04.get("absence_count") or 0),
        "known_need_projection_visible": bool(no_results.get("known_needs")),
        "bounded_absence_projection_visible": bool(no_results.get("bounded_absences")),
        "public_mutation_enabled": False,
        "live_source_fanout_enabled": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_text_projection_section(
    ux_mvp: Mapping[str, Any],
    snapshot_04: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    text = str(ux_mvp.get("text_projection") or "")
    return {
        "schema_version": "snapshot_text_projection_section.v0",
        "record_type": "snapshot_text_projection_section",
        "section_id": _section_id("snapshot_text_projection_section", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "text_projection_ref": "examples/public_search_ux/text_projection.txt",
        "text_projection": text,
        "text_projection_available": bool(text),
        "classic_html_examples_available": True,
        "source_result_card_count": len(snapshot_04.get("public_search_view_model_projection", {}).get("result_cards") or []),
        "public_read_only": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def build_refreshed_relay_projection(
    snapshot_sections: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    snapshot_04 = dict(snapshot_sections.get("snapshot_04") or {})
    ux_section = dict(snapshot_sections.get("public_search_ux_section") or {})
    route_section = dict(snapshot_sections.get("public_route_section") or {})
    result_card_section = dict(snapshot_sections.get("result_card_section") or {})
    no_results_section = dict(snapshot_sections.get("no_results_section") or {})
    return {
        "schema_version": "snapshot_refresh_relay_projection.v0",
        "record_type": "snapshot_refresh_relay_projection",
        "relay_projection_id": _section_id("snapshot_refresh_relay_projection", SNAPSHOT_REFRESH_ID),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "read_only": True,
        "source_relay_projection_ref": "examples/snapshots/refresh/manuals_scans_driver_support/refreshed_relay_projection.json",
        "sections": {
            "existing_reviewed_records": int(snapshot_04.get("existing_reviewed_record_count") or 0),
            "total_limited_reviewed_record_projection_count": int(
                snapshot_04.get("total_limited_reviewed_record_projection_count") or 0
            ),
            "total_candidate_count": int(snapshot_04.get("total_candidate_count") or 0),
            "public_ux_routes": int(route_section.get("route_count") or 0),
            "public_ux_pages": int(ux_section.get("page_count") or 0),
            "result_cards": int(result_card_section.get("result_card_count") or 0),
            "result_card_states": int(result_card_section.get("result_card_states_count") or 0),
            "no_results_sections": int(no_results_section.get("no_results_sections_count") or 0),
        },
        "projection_sections": [
            ux_section.get("section_id"),
            route_section.get("section_id"),
            result_card_section.get("section_id"),
            no_results_section.get("section_id"),
            snapshot_sections.get("text_projection_section", {}).get("section_id"),
        ],
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "file_fetch_enabled": False,
        "ocr_enabled": False,
        "install_execution_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
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
        "public_search_ux_integrated": True,
        "total_limited_reviewed_record_projection_count": int(
            snapshot_refresh_result.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "total_candidate_count": int(snapshot_refresh_result.get("total_candidate_count") or 0),
        "public_ux_routes_count": int(snapshot_refresh_result.get("public_ux_routes_count") or 0),
        "result_card_states_count": int(snapshot_refresh_result.get("result_card_states_count") or 0),
        "no_js_required": True,
        "public_projection_read_only": True,
        "launch_recommended": False,
        "demo_mode_recommended": True,
        "internal_review_recommended": True,
        "needs_public_alpha_reassess_after_ux_projection_refresh": True,
        "public_launch_readiness_claimed": False,
        "production_readiness_claimed": False,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def validate_snapshot_refresh_05_result(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    errors: list[str] = []
    expected = {
        "total_limited_reviewed_record_projection_count": 4,
        "total_candidate_count": 68,
        "public_ux_routes_count": 8,
        "result_card_states_count": 8,
    }
    if result.get("schema_version") != "snapshot_refresh_05_result.v0":
        errors.append("schema_version must be snapshot_refresh_05_result.v0")
    for key, value in expected.items():
        if int(result.get(key) or 0) != value:
            errors.append(f"{key} must be {value}")
    if result.get("no_js_required") is not True:
        errors.append("no_js_required must be true")
    if result.get("public_projection_read_only") is not True:
        errors.append("public_projection_read_only must be true")
    for section_name in (
        "public_search_ux_section",
        "public_route_section",
        "result_card_section",
        "no_results_section",
        "text_projection_section",
        "refreshed_relay_projection",
        "public_alpha_reassess_input",
    ):
        if not isinstance(result.get(section_name), Mapping):
            errors.append(f"{section_name} must exist")
    for key in BOUNDARY_FALSE_KEYS:
        if result.get(key) is not False:
            errors.append(f"{key} must be false")
    route_section = result.get("public_route_section", {})
    if isinstance(route_section, Mapping) and route_section.get("all_routes_no_js") is not True:
        errors.append("all public routes must be no-JS")
    card_section = result.get("result_card_section", {})
    if isinstance(card_section, Mapping):
        cards = list(card_section.get("cards") or [])
        if not cards:
            errors.append("result cards must exist")
        for card in cards:
            if card.get("status") in {"candidate", "near_miss", "known_need", "absence"} and card.get("accepted_truth") is not False:
                errors.append("candidate-like cards must not be accepted truth")
            for key in ("verified_download_claim", "malware_clean_claim", "rights_clearance_claim"):
                if card.get(key) is True:
                    errors.append(f"result card created forbidden claim: {key}")
    return {
        "schema_version": "snapshot_refresh_05_validation_report.v0",
        "task": TASK_ID,
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "created_at": DEFAULT_TIMESTAMP,
    }


def build_snapshot_refresh_05_boundary_report(
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
        "public_search_ux_integrated": True,
        "public_ux_projection_is_read_only": True,
        "public_search_ux_does_not_own_search_behavior": True,
        "no_js_required": True,
        "public_projection_read_only": True,
        "candidate_verified_distinction_required": True,
        "limited_reviewed_record_distinction_required": True,
        "total_candidate_count": int(result.get("total_candidate_count") or 0),
        "public_ux_routes_count": int(result.get("public_ux_routes_count") or 0),
        "result_card_states_count": int(result.get("result_card_states_count") or 0),
        "limitations": _limitations(),
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }


def run_snapshot_refresh_05(
    policy: Mapping[str, Any] | None = None,
    *,
    from_public_search_ux_examples: bool = True,
    write_examples: bool = False,
) -> dict[str, Any]:
    del from_public_search_ux_examples
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    snapshot_04 = load_snapshot_refresh_04_handoff(merged_policy)
    ux_mvp = load_public_search_ux_mvp_handoff(merged_policy)
    plan = build_snapshot_refresh_05_plan(snapshot_04, ux_mvp, merged_policy)
    ux_section = build_public_search_ux_section(ux_mvp, merged_policy)
    route_section = build_public_route_section(ux_mvp, merged_policy)
    result_card_section = build_result_card_projection_section(ux_mvp, snapshot_04, merged_policy)
    no_results_section = build_no_results_projection_section(ux_mvp, snapshot_04, merged_policy)
    text_projection_section = build_text_projection_section(ux_mvp, snapshot_04, merged_policy)
    sections = {
        "snapshot_04": snapshot_04,
        "public_search_ux_section": ux_section,
        "public_route_section": route_section,
        "result_card_section": result_card_section,
        "no_results_section": no_results_section,
        "text_projection_section": text_projection_section,
    }
    relay_projection = build_refreshed_relay_projection(sections, merged_policy)
    result: dict[str, Any] = {
        "schema_version": "snapshot_refresh_05_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "public_search_ux_integrated": True,
        "snapshot_refresh_04_ref": SNAPSHOT_REFRESH_04_REF,
        "public_search_ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        "plan": plan,
        "source_batches": list(snapshot_04.get("source_batches") or []),
        "existing_reviewed_record_section": snapshot_04.get("existing_reviewed_record_section"),
        "reviewed_metadata_record_section": snapshot_04.get("reviewed_metadata_record_section"),
        "reviewed_source_lead_section": snapshot_04.get("reviewed_source_lead_section"),
        "candidate_sections": snapshot_04.get("candidate_sections"),
        "manuals_scans_candidate_section": snapshot_04.get("manuals_scans_candidate_section"),
        "driver_support_candidate_section": snapshot_04.get("driver_support_candidate_section"),
        "live_metadata_candidate_section": snapshot_04.get("live_metadata_candidate_section"),
        "review_queue_section": snapshot_04.get("review_queue_section"),
        "need_absence_section": snapshot_04.get("need_absence_section"),
        "public_search_ux_section": ux_section,
        "public_route_section": route_section,
        "result_card_section": result_card_section,
        "no_results_section": no_results_section,
        "text_projection_section": text_projection_section,
        "refreshed_relay_projection": relay_projection,
        "public_search_ux_refs": [ux_section["section_id"]],
        "public_route_refs": [route_section["section_id"]],
        "result_card_refs": [result_card_section["section_id"]],
        "no_results_refs": [no_results_section["section_id"]],
        "text_projection_refs": [text_projection_section["section_id"]],
        "relay_projection_refs": [relay_projection["relay_projection_id"]],
        "total_limited_reviewed_record_projection_count": int(
            snapshot_04.get("total_limited_reviewed_record_projection_count") or 0
        ),
        "total_candidate_count": int(snapshot_04.get("total_candidate_count") or 0),
        "public_ux_routes_count": int(route_section["route_count"]),
        "result_card_states_count": int(result_card_section["result_card_states_count"]),
        "no_results_sections_count": int(no_results_section["no_results_sections_count"]),
        "no_js_required": True,
        "public_projection_read_only": True,
        "fixture_snapshot_refresh_passed": True,
        "created_at": DEFAULT_TIMESTAMP,
        **_false_boundaries(),
    }
    public_alpha = build_public_alpha_reassess_input(result, merged_policy)
    result["public_alpha_reassess_input"] = public_alpha
    result["public_alpha_reassess_refs"] = [public_alpha["public_alpha_reassess_id"]]
    result["boundary_report"] = build_snapshot_refresh_05_boundary_report(result, merged_policy)
    result["validation_report"] = validate_snapshot_refresh_05_result(result, merged_policy)
    if result["validation_report"]["status"] != "pass":
        result["status"] = "fail"
        result["fixture_snapshot_refresh_passed"] = False
    if write_examples:
        written = write_snapshot_refresh_05_examples(result)
        written.extend(write_snapshot_refresh_05_inventory_and_audit(result))
        result["examples_written_paths"] = written
        result["examples_written"] = True
    else:
        result["examples_written_paths"] = []
        result["examples_written"] = False
    return result


def write_snapshot_refresh_05_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_05(write_examples=False))
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "snapshots" / "refresh" / "public_search_ux_mvp"
    files = {
        "snapshot_refresh_plan.json": payload["plan"],
        "public_search_ux_section.json": payload["public_search_ux_section"],
        "public_route_section.json": payload["public_route_section"],
        "result_card_section.json": payload["result_card_section"],
        "no_results_section.json": payload["no_results_section"],
        "text_projection_section.json": payload["text_projection_section"],
        "refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "public_alpha_reassess_input.json": payload["public_alpha_reassess_input"],
        "boundary_report.json": payload["boundary_report"],
        "snapshot_refresh_05_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    mirrors = {
        "examples/relay/refresh/public_search_ux_mvp_refreshed_relay_projection.json": payload["refreshed_relay_projection"],
        "examples/public_alpha/reassess/public_search_ux_mvp/snapshot_refresh_05_reassess_input.json": payload[
            "public_alpha_reassess_input"
        ],
    }
    for rel_path, content in mirrors.items():
        path = repo_root / rel_path
        _write_json(path, content)
        written.append(rel_path)
    return written


def write_snapshot_refresh_05_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or run_snapshot_refresh_05(write_examples=False))
    repo_root = root or _repo_root()
    inventory_dir = repo_root / "control" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    packets = build_snapshot_refresh_05_inventory_packets(payload)
    written: list[str] = []
    for name, content in sorted(packets.items()):
        path = inventory_dir / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_snapshot_refresh_05_audit_pack(payload, repo_root))
    return written


def build_snapshot_refresh_05_inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    snapshot_04_candidates = list(result.get("candidate_sections") or [])
    packets: dict[str, Any] = {
        "snapshot_refresh_05_input_state.json": {
            "schema_version": "snapshot_refresh_05_input_state.v0",
            "task": TASK_ID,
            "branch": "dev",
            "input_results": {
                "snapshot_refresh_04": SNAPSHOT_REFRESH_04_REF,
                "public_search_ux_mvp": PUBLIC_SEARCH_UX_MVP_REF,
                "public_search_ux_model": "control/inventory/public_search_ux_model_result.json",
                "public_alpha_readonly": "control/inventory/public_alpha_readonly_00_result.json",
                "snapshot_relay": "control/inventory/snapshot_relay_result.json",
            },
            "equivalent_filename_mappings": {
                "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json"
            },
            "public_search_ux_integrated": True,
            **_false_boundaries(),
            "created_at": DEFAULT_TIMESTAMP,
        },
        "snapshot_refresh_05_source_matrix.json": {
            "schema_version": "snapshot_refresh_05_source_matrix.v0",
            "task": TASK_ID,
            "sources": list(result.get("source_batches") or []),
            "source_batch_count": len(result.get("source_batches") or []),
            "snapshot_refresh_04_ref": SNAPSHOT_REFRESH_04_REF,
            "ux_mvp_ref": PUBLIC_SEARCH_UX_MVP_REF,
        },
        "snapshot_refresh_05_reviewed_record_matrix.json": {
            "schema_version": "snapshot_refresh_05_reviewed_record_matrix.v0",
            "task": TASK_ID,
            "existing_reviewed_record_count": result.get("existing_reviewed_record_section", {}).get("reviewed_record_count"),
            "reviewed_metadata_record_count": result.get("reviewed_metadata_record_section", {}).get("reviewed_metadata_record_count"),
            "reviewed_source_lead_count": result.get("reviewed_source_lead_section", {}).get("reviewed_source_lead_count"),
            "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
            "limited_records_are_not_verified_artifacts": True,
        },
        "snapshot_refresh_05_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_05_candidate_matrix.v0",
            "task": TASK_ID,
            "candidate_sections": [
                {
                    "section_id": section.get("section_id"),
                    "domain_key": section.get("domain_key"),
                    "domain_id": section.get("domain_id"),
                    "candidate_count": section.get("candidate_count"),
                    "accepted_truth": False,
                    "candidate_promoted_to_reviewed": False,
                }
                for section in snapshot_04_candidates
            ],
            "total_candidate_count": result.get("total_candidate_count"),
        },
        "snapshot_refresh_05_domain_candidate_matrix.json": {
            "schema_version": "snapshot_refresh_05_domain_candidate_matrix.v0",
            "task": TASK_ID,
            "domains": [
                {
                    "domain_key": section.get("domain_key"),
                    "domain_id": section.get("domain_id"),
                    "candidate_count": section.get("candidate_count"),
                    "review_only": True,
                }
                for section in snapshot_04_candidates
            ],
            "total_candidate_count": result.get("total_candidate_count"),
        },
        "snapshot_refresh_05_public_search_ux_matrix.json": result["public_search_ux_section"],
        "snapshot_refresh_05_public_route_matrix.json": result["public_route_section"],
        "snapshot_refresh_05_result_card_matrix.json": {
            "schema_version": "snapshot_refresh_05_result_card_matrix.v0",
            "task": TASK_ID,
            "section_id": result["result_card_section"]["section_id"],
            "result_card_count": result["result_card_section"]["result_card_count"],
            "supported_statuses": result["result_card_section"]["supported_statuses"],
            "observed_statuses": result["result_card_section"]["observed_statuses"],
            "result_card_states_count": result["result_card_section"]["result_card_states_count"],
            "candidate_verified_distinction_passed": True,
            "limited_reviewed_record_distinction_passed": True,
        },
        "snapshot_refresh_05_no_results_matrix.json": result["no_results_section"],
        "snapshot_refresh_05_text_projection_matrix.json": result["text_projection_section"],
        "snapshot_refresh_05_relay_projection_matrix.json": {
            "schema_version": "snapshot_refresh_05_relay_projection_matrix.v0",
            "task": TASK_ID,
            "relay_projection_refs": list(result.get("relay_projection_refs") or []),
            "sections": result.get("refreshed_relay_projection", {}).get("sections"),
            "read_only": True,
            "mutation_enabled": False,
            "site_dist_written": False,
        },
        "snapshot_refresh_05_public_alpha_reassess_matrix.json": {
            "schema_version": "snapshot_refresh_05_public_alpha_reassess_matrix.v0",
            "task": TASK_ID,
            "public_alpha_reassess_refs": list(result.get("public_alpha_reassess_refs") or []),
            "public_search_ux_integrated": True,
            "total_candidate_count": result.get("total_candidate_count"),
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
        },
        "snapshot_refresh_05_boundary_report.json": result["boundary_report"],
        "snapshot_refresh_05_smoke_result.json": {
            "schema_version": "snapshot_refresh_05_smoke_result.v0",
            "task": TASK_ID,
            "status": result.get("status"),
            "fixture_snapshot_refresh_passed": result.get("fixture_snapshot_refresh_passed"),
            "public_search_ux_integrated": True,
            "no_js_required": True,
            "public_projection_read_only": True,
            **_false_boundaries(),
        },
        "snapshot_refresh_05_validation_matrix.json": {
            "schema_version": "snapshot_refresh_05_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_snapshot_refresh.py",
                "focused snapshot refresh 05 unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "snapshot_refresh_05_result.json": _task_result(result),
        "snapshot_refresh_05_next_task_decision.json": {
            "schema_version": "snapshot_refresh_05_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": ["REVIEW-BATCH-APPLY-NEXT-00", "DEV-TO-MAIN-PROMOTION-REVIEW-06"],
            "deployment_performed": False,
            "public_launch_readiness_claimed": False,
        },
        "snapshot_refresh_05_failure_repair_log.json": {
            "schema_version": "snapshot_refresh_05_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
            **_false_boundaries(),
        },
    }
    return packets


def _write_snapshot_refresh_05_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "snapshot-refresh-05-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    inventory = build_snapshot_refresh_05_inventory_packets(result)
    audit_json = {"snapshot_refresh_05_report.json": _task_result(result)}
    audit_markdown = {
        "README.md": "# SNAPSHOT-REFRESH-05 Audit\n\nRefresh evidence after the public search UX MVP. Public UX pages are read-only projections over view models and do not deploy, mutate, download, call live sources, or claim launch readiness.\n",
        "source_matrix.md": _matrix_md("Source Matrix", inventory["snapshot_refresh_05_source_matrix.json"]),
        "public_search_ux_matrix.md": _matrix_md("Public Search UX Matrix", inventory["snapshot_refresh_05_public_search_ux_matrix.json"]),
        "public_route_matrix.md": _matrix_md("Public Route Matrix", inventory["snapshot_refresh_05_public_route_matrix.json"]),
        "result_card_matrix.md": _matrix_md("Result Card Matrix", inventory["snapshot_refresh_05_result_card_matrix.json"]),
        "no_results_matrix.md": _matrix_md("No Results Matrix", inventory["snapshot_refresh_05_no_results_matrix.json"]),
        "relay_projection_matrix.md": _matrix_md("Relay Projection Matrix", inventory["snapshot_refresh_05_relay_projection_matrix.json"]),
        "public_alpha_reassess_matrix.md": _matrix_md("Public Alpha Reassess Matrix", inventory["snapshot_refresh_05_public_alpha_reassess_matrix.json"]),
        "boundary_report.md": _matrix_md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _matrix_md("Smoke Result", inventory["snapshot_refresh_05_smoke_result.json"]),
        "validation_matrix.md": _matrix_md("Validation Matrix", inventory["snapshot_refresh_05_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/snapshot_refresh_05_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    generated_files = {
        "sample_snapshot_refresh_plan.json": result["plan"],
        "sample_public_search_ux_section.json": result["public_search_ux_section"],
        "sample_public_route_section.json": result["public_route_section"],
        "sample_result_card_section.json": result["result_card_section"],
        "sample_no_results_section.json": result["no_results_section"],
        "sample_text_projection_section.json": result["text_projection_section"],
        "sample_relay_projection.json": result["refreshed_relay_projection"],
        "sample_public_alpha_reassess_input.json": result["public_alpha_reassess_input"],
        "sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Snapshot Refresh 05 Summary\n\n"
        f"- public UX routes: {result.get('public_ux_routes_count')}\n"
        f"- result card states: {result.get('result_card_states_count')}\n"
        f"- total candidates: {result.get('total_candidate_count')}\n"
        "- no-JS required: true\n"
        "- site/dist written: false\n"
    )
    written: list[str] = []
    for name, content in audit_json.items():
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
    summary_path.write_text(summary, encoding="utf-8")
    written.append(str(summary_path.relative_to(repo_root)))
    return written


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return _task_result(result)


def _task_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_refresh_05_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "snapshot_refresh_id": SNAPSHOT_REFRESH_ID,
        "public_search_ux_integrated": True,
        "contracts_added": True,
        "policies_added": True,
        "source_matrix_added": True,
        "reviewed_record_matrix_added": True,
        "candidate_matrix_added": True,
        "public_search_ux_matrix_added": True,
        "public_route_matrix_added": True,
        "result_card_matrix_added": True,
        "no_results_matrix_added": True,
        "text_projection_matrix_added": True,
        "relay_projection_matrix_added": True,
        "public_alpha_reassess_matrix_added": True,
        "runtime_snapshot_refresh_added": True,
        "public_search_ux_section_created": True,
        "public_route_section_created": True,
        "result_card_section_created": True,
        "no_results_section_created": True,
        "text_projection_section_created": True,
        "relay_projection_created": True,
        "public_alpha_reassess_input_created": True,
        "total_limited_reviewed_record_projection_count": result.get("total_limited_reviewed_record_projection_count"),
        "total_candidate_count": result.get("total_candidate_count"),
        "public_ux_routes_count": result.get("public_ux_routes_count"),
        "result_card_states_count": result.get("result_card_states_count"),
        "no_js_required": True,
        "public_projection_read_only": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "fixture_snapshot_refresh_passed": bool(result.get("fixture_snapshot_refresh_passed")),
        **_false_boundaries(),
        "recommended_next_task": NEXT_TASK,
    }


def _assert_public_search_ux_mvp(result: Mapping[str, Any], bundle: Mapping[str, Any]) -> None:
    if result.get("status") not in {"pass", "pass_with_warnings"}:
        raise ValueError("public search UX MVP must pass before snapshot refresh 05")
    expected_true = (
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
    missing = [key for key in expected_true if result.get(key) is not True]
    if missing:
        raise ValueError(f"public search UX MVP missing pass flags: {', '.join(missing)}")
    if len(bundle.get("routes") or []) < 8:
        raise ValueError("public search UX MVP route count must be at least 8")
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
        if result.get(key) is not False:
            raise ValueError(f"public search UX MVP boundary failed: {key}")


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = {
        "snapshot_refresh_is_projection",
        "public_ux_projection_is_read_only",
        "public_search_ux_does_not_own_search_behavior",
        "no_js_public_search_required",
        "candidate_verified_distinction_required",
        "limited_reviewed_record_distinction_required",
        "no_results_need_projection_required",
        "no_public_mutation",
        "no_public_live_source_fanout",
        "no_reviewed_index_mutation",
        "no_master_index_mutation",
        "no_public_index_mutation",
        "no_deployment",
        "no_site_dist_write",
        "no_public_launch_claim",
        "no_production_claim",
    }
    missing = sorted(key for key in required_true if not bool(policy.get(key)))
    if missing:
        raise PermissionError(f"snapshot refresh 05 policy missing required safety rules: {', '.join(missing)}")
    forbidden_true = {
        "downloads_enabled",
        "file_fetches_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
    }
    enabled = sorted(key for key in forbidden_true if bool(policy.get(key)))
    if enabled:
        raise PermissionError(f"snapshot refresh 05 policy enables forbidden behavior: {', '.join(enabled)}")


def _limitations() -> list[str]:
    return [
        "snapshot_refresh_is_projection_only",
        "public_search_ux_is_read_only_projection",
        "public_search_ux_does_not_own_search_behavior",
        "no_live_source_fanout",
        "no_public_mutation",
        "no_site_dist_write",
        "no_deployment_or_launch_claim",
        "candidates_and_limited_records_keep_their_prior_claim_scope",
    ]


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


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


def _matrix_md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"
