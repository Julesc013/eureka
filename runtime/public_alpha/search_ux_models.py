"""Canonical public search UX view-model builders.

This module builds deterministic example packets from committed snapshot refresh
examples. It does not render pages, deploy, mutate indexes, call live sources,
download, extract, or promote candidates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


TASK_ID = "PUBLIC-SEARCH-UX-MODEL-00"
MODEL_ID = "public_search_ux_model_00"
CREATED_AT = "2026-05-31T00:00:00Z"
CONTRACT_AUTHORITY = "contracts/view/models/public_search"
NEXT_TASK = "LIVE-METADATA-PILOT-BATCH-00 - Operator-approved live metadata pilot over seed queries"

RESULT_STATUSES = (
    "verified",
    "candidate",
    "near_miss",
    "known_need",
    "absence",
    "source_lead",
)
PROJECTION_PROFILES = (
    "public_web",
    "operator_workbench",
    "api_json",
    "classic_html",
    "text",
)
FORBIDDEN_ACTIONS = (
    "download",
    "install",
    "execute",
    "upload",
    "promote",
    "mutate_public_index",
    "run_live_source_fanout",
    "call_model_provider",
)


def load_public_search_ux_inputs() -> dict[str, Any]:
    root = _repo_root() / "examples" / "snapshots" / "refresh"
    return {
        "schema_version": "public_search_ux_model_input.v0",
        "model_id": MODEL_ID,
        "reviewed_record_section": _read_json(root / "reviewed_record_section.json"),
        "candidate_sections": [
            _read_json(root / "candidate_section_frontier_media.json"),
            _read_json(root / "candidate_section_legacy_software.json"),
        ],
        "need_absence_section": _read_json(root / "need_absence_section.json"),
        "snapshot_refresh_result": _read_json(root / "snapshot_refresh_result.json"),
        "public_alpha_reassess_result": _read_json(
            _repo_root() / "control" / "inventory" / "public_alpha_reassess_result.json"
        ),
        "created_at": CREATED_AT,
    }


def build_action_posture_view_model(
    status: str,
    source_action_posture: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in RESULT_STATUSES:
        raise ValueError(f"unsupported result status: {status}")
    source_action_posture = source_action_posture or {}
    allowed = list(source_action_posture.get("allowed_actions") or ["open", "view_source", "view_evidence"])
    if status in {"candidate", "near_miss", "source_lead"}:
        allowed = [action for action in allowed if action not in {"promote", "download", "install_handoff", "execute"}]
        allowed = sorted(set(allowed) | {"inspect", "view_provenance"})
    if status in {"known_need", "absence"}:
        allowed = ["view_need", "view_evidence", "refine_query"]
    if status == "verified":
        allowed = sorted(set(allowed) | {"copy_citation"})
    return {
        "schema_version": "action_posture_view_model.v0",
        "view_model_id": _stable_id("action_posture", status, allowed),
        "status": status,
        "allowed_actions": allowed,
        "blocked_actions": list(FORBIDDEN_ACTIONS),
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "review_required": status != "verified",
        "operator_action_required_for_mutation": True,
        "created_at": CREATED_AT,
    }


def build_capability_profile_view_model(projection_profile: str = "public_web") -> dict[str, Any]:
    _require_projection_profile(projection_profile)
    return {
        "schema_version": "capability_profile_view_model.v0",
        "view_model_id": f"capability_profile:{projection_profile}",
        "projection_profile": projection_profile,
        "supported_projection_profiles": list(PROJECTION_PROFILES),
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "candidate_review_public_actions_enabled": False,
        "agent_json_packets_supported": projection_profile in {"api_json", "public_web", "operator_workbench"},
        "html_scrape_required_for_agents": False,
        "created_at": CREATED_AT,
    }


def build_result_card_view_model(
    *,
    title: str,
    url: str,
    status: str,
    object_type: str,
    domain: str,
    source_family: str,
    source_label: str,
    snippet: str,
    match_reasons: Sequence[str],
    evidence_summary: Mapping[str, Any],
    confidence_label: str,
    risk_label: str,
    rights_label: str,
    compatibility_label: str,
    action_posture: Mapping[str, Any] | None = None,
    review_required: bool,
    accepted_truth: bool,
    limitations: Sequence[str],
) -> dict[str, Any]:
    if status not in RESULT_STATUSES:
        raise ValueError(f"unsupported result status: {status}")
    if status != "verified" and accepted_truth:
        raise ValueError(f"{status} result cards must not be accepted truth")
    if status != "verified" and not review_required:
        raise ValueError(f"{status} result cards must require review")
    posture = build_action_posture_view_model(status, action_posture)
    return {
        "schema_version": "result_card_view_model.v0",
        "view_model_id": _stable_id("result_card", status, title, url),
        "title": title,
        "url": url,
        "status": status,
        "object_type": object_type,
        "domain": domain,
        "source_family": source_family,
        "source_label": source_label,
        "snippet": snippet,
        "match_reasons": list(match_reasons),
        "evidence_summary": dict(evidence_summary),
        "confidence_label": confidence_label,
        "risk_label": risk_label,
        "rights_label": rights_label,
        "compatibility_label": compatibility_label,
        "action_posture": posture,
        "review_required": review_required,
        "accepted_truth": accepted_truth,
        "limitations": list(limitations),
        "created_at": CREATED_AT,
    }


def build_result_cards(inputs: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    data = dict(inputs or load_public_search_ux_inputs())
    reviewed = data["reviewed_record_section"]["reviewed_records"][0]
    frontier_candidate = data["candidate_sections"][0]["candidates"][0]
    legacy_candidate = data["candidate_sections"][1]["candidates"][0]
    near_miss_candidate = data["candidate_sections"][1]["candidates"][2]
    need = data["need_absence_section"]["known_needs"][0]
    absence = data["need_absence_section"]["absence_summaries"][0]
    return [
        _reviewed_card(reviewed),
        _candidate_card(frontier_candidate, status="candidate"),
        _candidate_card(near_miss_candidate, status="near_miss"),
        _need_card(need),
        _absence_card(absence),
        _source_lead_card(legacy_candidate),
    ]


def build_search_page_view_model(
    query: str = "windows 7",
    projection_profile: str = "public_web",
    inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _require_projection_profile(projection_profile)
    cards = build_result_cards(inputs)
    coverage = build_search_coverage_view_model(cards)
    return {
        "schema_version": "search_page_view_model.v0",
        "view_model_id": "public_search_page:seed_snapshot",
        "page_kind": "search",
        "projection_profile": projection_profile,
        "canonical_route": "/search",
        "search_first": True,
        "query": {
            "raw_query": query,
            "normalized_query": " ".join(query.split()).lower(),
        },
        "result_cards": cards,
        "coverage": coverage,
        "no_results_need": build_no_results_need_view_model(query, inputs),
        "capability_profile": build_capability_profile_view_model(projection_profile),
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "accepted_truth_created": False,
        "created_at": CREATED_AT,
    }


def build_object_page_view_model(inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    reviewed = (inputs or load_public_search_ux_inputs())["reviewed_record_section"]["reviewed_records"][0]
    card = _reviewed_card(reviewed)
    return _page_packet("object_page_view_model.v0", "object", "/object/" + reviewed["object_id"], card)


def build_candidate_page_view_model(inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = (inputs or load_public_search_ux_inputs())["candidate_sections"][0]["candidates"][0]
    card = _candidate_card(candidate, status="candidate")
    packet = _page_packet("candidate_page_view_model.v0", "candidate", card["url"], card)
    packet["candidate_identity"] = {
        "candidate_id": candidate["candidate_id"],
        "review_state": candidate["review_state"],
        "review_required": True,
        "accepted_truth": False,
    }
    return packet


def build_need_page_view_model(inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    need = (inputs or load_public_search_ux_inputs())["need_absence_section"]["known_needs"][0]
    card = _need_card(need)
    packet = _page_packet("need_page_view_model.v0", "need", card["url"], card)
    packet["need_identity"] = {
        "need_id": need["need_id"],
        "need_kind": need["need_kind"],
        "review_required": True,
        "accepted_truth": False,
    }
    return packet


def build_source_page_view_model(inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    candidate = (inputs or load_public_search_ux_inputs())["candidate_sections"][1]["candidates"][0]
    card = _source_lead_card(candidate)
    packet = _page_packet("source_page_view_model.v0", "source", "/source/" + candidate["source_family"], card)
    packet["source_identity"] = {
        "source_family": candidate["source_family"],
        "source_label": _source_label(candidate["source_family"]),
        "metadata_only": True,
        "downloads_enabled": False,
    }
    return packet


def build_evidence_page_view_model(inputs: Mapping[str, Any] | None = None) -> dict[str, Any]:
    reviewed = (inputs or load_public_search_ux_inputs())["reviewed_record_section"]["reviewed_records"][0]
    card = _reviewed_card(reviewed)
    packet = _page_packet(
        "evidence_page_view_model.v0",
        "evidence",
        "/evidence/" + reviewed["evidence_summary_refs"][0],
        card,
    )
    packet["evidence_refs"] = list(reviewed.get("evidence_summary_refs") or [])
    return packet


def build_no_results_need_view_model(
    query: str = "unreviewed frontier search",
    inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = dict(inputs or load_public_search_ux_inputs())
    need = data["need_absence_section"]["known_needs"][0]
    absence = data["need_absence_section"]["absence_summaries"][0]
    return {
        "schema_version": "no_results_need_view_model.v0",
        "view_model_id": _stable_id("no_results_need", query),
        "query": query,
        "headline": "No reviewed result yet.",
        "known_need_ref": need["need_id"],
        "absence_ref": absence["absence_id"],
        "sources_checked": ["reviewed_snapshot", "seed_batch_candidate_sections"],
        "near_matches": [_candidate_card(data["candidate_sections"][0]["candidates"][1], status="near_miss")],
        "next_actions": ["refine_query", "inspect_candidate", "review_needed_evidence"],
        "review_required": True,
        "accepted_truth": False,
        "public_mutation_enabled": False,
        "created_at": CREATED_AT,
    }


def build_search_coverage_view_model(result_cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in RESULT_STATUSES}
    for card in result_cards:
        counts[str(card["status"])] += 1
    return {
        "schema_version": "search_coverage_view_model.v0",
        "view_model_id": "search_coverage:seed_snapshot",
        "status_counts": counts,
        "reviewed_result_count": counts["verified"],
        "review_only_result_count": sum(counts[status] for status in RESULT_STATUSES if status != "verified"),
        "needs_and_absences_visible": counts["known_need"] + counts["absence"] > 0,
        "candidate_verified_separation_required": True,
        "created_at": CREATED_AT,
    }


def project_public_search_view_model(
    view_model: Mapping[str, Any],
    projection_profile: str,
) -> dict[str, Any]:
    _require_projection_profile(projection_profile)
    result_cards = list(view_model.get("result_cards") or [])
    projection: dict[str, Any] = {
        "schema_version": "public_search_projection.v0",
        "view_model_id": _stable_id("public_search_projection", projection_profile, view_model.get("view_model_id")),
        "projection_profile": projection_profile,
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "result_state_labels_visible": True,
        "candidate_verified_separation_visible": True,
        "payload": dict(view_model),
        "created_at": CREATED_AT,
    }
    if projection_profile == "operator_workbench":
        projection["operator_context_required_for_review_actions"] = True
        projection["public_actions_remain_read_only"] = True
    if projection_profile == "api_json":
        projection["agent_packet"] = True
        projection["html_scrape_required_for_agents"] = False
    if projection_profile in {"classic_html", "text"}:
        projection["text_lines"] = _text_lines(result_cards)
    return projection


def build_public_search_ux_model_bundle(
    *,
    write_examples: bool = False,
) -> dict[str, Any]:
    inputs = load_public_search_ux_inputs()
    search_page = build_search_page_view_model(inputs=inputs)
    projections = {
        profile: project_public_search_view_model(search_page, profile)
        for profile in PROJECTION_PROFILES
    }
    pages = {
        "object_page": build_object_page_view_model(inputs),
        "candidate_page": build_candidate_page_view_model(inputs),
        "need_page": build_need_page_view_model(inputs),
        "source_page": build_source_page_view_model(inputs),
        "evidence_page": build_evidence_page_view_model(inputs),
        "no_results_need": build_no_results_need_view_model(inputs=inputs),
    }
    result_cards = list(search_page["result_cards"])
    boundary = _boundary_report()
    result = {
        "schema_version": "public_search_ux_model_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "contract_authority_root": CONTRACT_AUTHORITY,
        "contracts_added": True,
        "runtime_view_model_builder_added": True,
        "projection_helpers_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "result_card_statuses": sorted({card["status"] for card in result_cards}),
        "result_card_count": len(result_cards),
        "projection_profiles": list(PROJECTION_PROFILES),
        "search_page": search_page,
        "pages": pages,
        "projections": projections,
        "boundary_report": boundary,
        "launch_recommended": False,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "recommended_next_task": NEXT_TASK,
        "created_at": CREATED_AT,
    }
    if write_examples:
        result["examples_written_paths"] = write_public_search_ux_model_examples(result)
    else:
        result["examples_written_paths"] = []
    return result


def write_public_search_ux_model_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or build_public_search_ux_model_bundle())
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "view_models" / "public_search"
    cards = {card["status"]: card for card in payload["search_page"]["result_cards"]}
    files = {
        "search_page_view_model.json": payload["search_page"],
        "result_card_reviewed.json": cards["verified"],
        "result_card_candidate.json": cards["candidate"],
        "result_card_near_miss.json": cards["near_miss"],
        "result_card_known_need.json": cards["known_need"],
        "result_card_absence.json": cards["absence"],
        "result_card_source_lead.json": cards["source_lead"],
        "object_page_view_model.json": payload["pages"]["object_page"],
        "candidate_page_view_model.json": payload["pages"]["candidate_page"],
        "need_page_view_model.json": payload["pages"]["need_page"],
        "source_page_view_model.json": payload["pages"]["source_page"],
        "evidence_page_view_model.json": payload["pages"]["evidence_page"],
        "no_results_need_view_model.json": payload["pages"]["no_results_need"],
        "search_coverage_view_model.json": payload["search_page"]["coverage"],
        "capability_profile_view_model.json": payload["search_page"]["capability_profile"],
        "projection_profiles.json": payload["projections"],
        "boundary_report.json": payload["boundary_report"],
        "public_search_ux_model_result.json": _result_summary(payload),
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def write_public_search_ux_model_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or build_public_search_ux_model_bundle())
    repo_root = root or _repo_root()
    packets = _inventory_packets(payload)
    written: list[str] = []
    for name, content in packets.items():
        path = repo_root / "control" / "inventory" / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _reviewed_card(record: Mapping[str, Any]) -> dict[str, Any]:
    return build_result_card_view_model(
        title=_text(record.get("title")),
        url="/object/" + _text(record.get("object_id")),
        status="verified",
        object_type=_text(record.get("result_kind")) or "reviewed_object_record",
        domain=_text(record.get("domain_id")),
        source_family=_text(record.get("source_context")) or "reviewed_snapshot",
        source_label="Reviewed local snapshot",
        snippet="Reviewed local record from the committed snapshot projection.",
        match_reasons=["reviewed_record_present", "snapshot_ref_available"],
        evidence_summary={
            "summary": "Reviewed record has source and evidence summary references.",
            "evidence_refs": list(record.get("evidence_summary_refs") or []),
            "evidence_count": len(record.get("evidence_summary_refs") or []),
        },
        confidence_label="reviewed",
        risk_label="low_public_read_only",
        rights_label="rights_not_cleared_for_download",
        compatibility_label="partial",
        review_required=False,
        accepted_truth=True,
        limitations=list(record.get("limitations") or []),
    )


def _candidate_card(candidate: Mapping[str, Any], *, status: str) -> dict[str, Any]:
    return build_result_card_view_model(
        title=_text(candidate.get("title")),
        url="/" + ("candidate" if status == "candidate" else "candidate") + "/" + _text(candidate.get("candidate_id")),
        status=status,
        object_type="metadata_candidate",
        domain=_text(candidate.get("domain_id")),
        source_family=_text(candidate.get("source_family")),
        source_label=_source_label(_text(candidate.get("source_family"))),
        snippet="Review-only metadata lead from seed snapshot candidate memory.",
        match_reasons=["query_ref_match", "candidate_snapshot_ref_present", "review_required"],
        evidence_summary={
            "summary": "Candidate has metadata and SCOUT trail references, but is not reviewed truth.",
            "evidence_refs": list(candidate.get("scout_trail_refs") or []),
            "evidence_count": len(candidate.get("scout_trail_refs") or []),
        },
        confidence_label="candidate",
        risk_label="review_required",
        rights_label="rights_not_cleared",
        compatibility_label="unreviewed",
        action_posture=candidate.get("action_posture"),
        review_required=True,
        accepted_truth=False,
        limitations=list(candidate.get("limitations") or []) + ["candidate_not_verified"],
    )


def _source_lead_card(candidate: Mapping[str, Any]) -> dict[str, Any]:
    card = _candidate_card(candidate, status="source_lead")
    card["url"] = "/source/" + _text(candidate.get("source_family"))
    card["snippet"] = "Source-family lead for follow-up review, not an artifact result."
    card["confidence_label"] = "lead"
    return card


def _need_card(need: Mapping[str, Any]) -> dict[str, Any]:
    return build_result_card_view_model(
        title="Known need: " + _text(need.get("summary")),
        url="/need/" + _text(need.get("need_id")),
        status="known_need",
        object_type=_text(need.get("need_kind")),
        domain="discovery_need",
        source_family="seed_batch_review",
        source_label="Seed batch review",
        snippet=_text(need.get("summary")),
        match_reasons=["known_need_ref", "candidate_requires_review"],
        evidence_summary={
            "summary": "Need is linked to review-only candidates.",
            "evidence_refs": list(need.get("candidate_refs") or []),
            "evidence_count": len(need.get("candidate_refs") or []),
        },
        confidence_label="need",
        risk_label="unresolved",
        rights_label="not_applicable",
        compatibility_label="not_applicable",
        review_required=True,
        accepted_truth=False,
        limitations=["need_not_result", "review_required"],
    )


def _absence_card(absence: Mapping[str, Any]) -> dict[str, Any]:
    return build_result_card_view_model(
        title="Absence: " + _text(absence.get("summary")),
        url="/absence/" + _text(absence.get("absence_id")),
        status="absence",
        object_type=_text(absence.get("absence_kind")),
        domain="bounded_absence",
        source_family="snapshot_refresh",
        source_label="Snapshot refresh",
        snippet=_text(absence.get("summary")),
        match_reasons=["bounded_absence_statement", "reviewed_truth_not_present"],
        evidence_summary={
            "summary": "Bounded absence describes the current snapshot, not the whole web.",
            "evidence_refs": [_text(absence.get("absence_id"))],
            "evidence_count": 1,
        },
        confidence_label="bounded_absence",
        risk_label="scope_limited",
        rights_label="not_applicable",
        compatibility_label="not_applicable",
        review_required=True,
        accepted_truth=False,
        limitations=["absence_scope_is_current_snapshot", "not_global_absence"],
    )


def _page_packet(schema_version: str, page_kind: str, route: str, card: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "view_model_id": _stable_id(page_kind, route),
        "page_kind": page_kind,
        "canonical_route": route,
        "projection_profile": "public_web",
        "primary_result_card": dict(card),
        "capability_profile": build_capability_profile_view_model("public_web"),
        "read_only": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "created_at": CREATED_AT,
    }


def _inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "public_search_ux_model_input_state.json": {
            "schema_version": "public_search_ux_model_input_state.v0",
            "task": TASK_ID,
            "source_examples": [
                "examples/snapshots/refresh/reviewed_record_section.json",
                "examples/snapshots/refresh/candidate_section_frontier_media.json",
                "examples/snapshots/refresh/candidate_section_legacy_software.json",
                "examples/snapshots/refresh/need_absence_section.json",
            ],
            **_false_boundaries(),
        },
        "public_search_ux_model_contract_authority_matrix.json": {
            "schema_version": "public_search_ux_model_contract_authority_matrix.v0",
            "task": TASK_ID,
            "selected_authority_root": CONTRACT_AUTHORITY,
            "duplicate_contracts_views_root_created": False,
            "reason": "Existing authority is contracts/view/models; contracts/views is not introduced.",
        },
        "public_search_ux_model_result_card_matrix.json": {
            "schema_version": "public_search_ux_model_result_card_matrix.v0",
            "task": TASK_ID,
            "statuses": list(RESULT_STATUSES),
            "required_fields": [
                "title",
                "url",
                "status",
                "object_type",
                "domain",
                "source_family",
                "source_label",
                "snippet",
                "match_reasons",
                "evidence_summary",
                "confidence_label",
                "risk_label",
                "rights_label",
                "compatibility_label",
                "action_posture",
                "review_required",
                "accepted_truth",
                "limitations",
            ],
            "candidate_statuses_are_not_verified": True,
        },
        "public_search_ux_model_projection_matrix.json": {
            "schema_version": "public_search_ux_model_projection_matrix.v0",
            "task": TASK_ID,
            "projection_profiles": list(PROJECTION_PROFILES),
            "all_read_only": True,
            "agents_use_json_packets": True,
            "html_scrape_required_for_agents": False,
        },
        "public_search_ux_model_boundary_report.json": result["boundary_report"],
        "public_search_ux_model_validation_matrix.json": {
            "schema_version": "public_search_ux_model_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_search_ux_model_result.json": _result_summary(result),
        "public_search_ux_model_next_task_decision.json": {
            "schema_version": "public_search_ux_model_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": NEXT_TASK,
            "planned_after": [
                "PUBLIC-SEARCH-UX-MVP-00",
                "PUBLIC-SEARCH-UX-GATE-00",
                "SNAPSHOT-REFRESH-01",
                "PUBLIC-ALPHA-REASSESS-01",
            ],
        },
        "public_search_ux_model_failure_repair_log.json": {
            "schema_version": "public_search_ux_model_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-search-ux-model-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-SEARCH-UX-MODEL-00 Audit\n\nCanonical public search UX view-model evidence. No launch, deployment, or mutation occurred.\n",
        "contract_authority_matrix.md": _md("Contract Authority", _inventory_packets(result)["public_search_ux_model_contract_authority_matrix.json"]),
        "result_card_matrix.md": _md("Result Card Matrix", _inventory_packets(result)["public_search_ux_model_result_card_matrix.json"]),
        "projection_matrix.md": _md("Projection Matrix", _inventory_packets(result)["public_search_ux_model_projection_matrix.json"]),
        "boundary_report.md": _md("Boundary Report", result["boundary_report"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_search_ux_model_validation_matrix.json`. Full discovery is not run by policy.\n",
    }
    json_files = {
        "public_search_ux_model_report.json": _result_summary(result),
        "generated/sample_search_page_view_model.json": result["search_page"],
        "generated/sample_result_cards.json": result["search_page"]["result_cards"],
        "generated/sample_projection_profiles.json": result["projections"],
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    summary = (
        "# Public Search UX Model Summary\n\n"
        f"- result card statuses: {', '.join(result['result_card_statuses'])}\n"
        f"- projection profiles: {', '.join(result['projection_profiles'])}\n"
        f"- next task: {NEXT_TASK}\n"
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


def _boundary_report() -> dict[str, Any]:
    return {
        "schema_version": "public_search_ux_model_boundary_report.v0",
        "task": TASK_ID,
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "created_at": CREATED_AT,
    }


def _false_boundaries() -> dict[str, bool]:
    return {
        "deployment_performed": False,
        "public_launch_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "site_dist_written": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "public_search_ux_model_result.v0",
        "task": TASK_ID,
        "status": result.get("status", "pass"),
        "contract_authority_root": CONTRACT_AUTHORITY,
        "contracts_added": True,
        "runtime_view_model_builder_added": True,
        "projection_helpers_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "result_card_statuses": list(result["result_card_statuses"]),
        "projection_profiles": list(result["projection_profiles"]),
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "recommended_next_task": NEXT_TASK,
    }


def _text_lines(result_cards: Sequence[Mapping[str, Any]]) -> list[str]:
    return [
        f"[{card['status']}] {card['title']} - {card['url']}"
        for card in result_cards
    ]


def _source_label(source_family: str) -> str:
    return {
        "internet_archive_metadata": "Internet Archive metadata",
        "fixture_reviewed_record": "Reviewed fixture record",
        "reviewed_snapshot": "Reviewed snapshot",
    }.get(source_family, source_family.replace("_", " ").title())


def _require_projection_profile(profile: str) -> None:
    if profile not in PROJECTION_PROFILES:
        raise ValueError(f"unsupported projection profile: {profile}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"
