"""Read-only Workbench result lane packet and view-model helpers."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence


LANE_KINDS = (
    "reviewed_local_results",
    "local_candidate_results",
    "source_cache_hits",
    "ia_metadata_candidates",
    "review_queue_items",
    "known_absence",
    "near_misses",
    "blocked_actions",
    "running_workunits",
    "deferred_deepening",
    "future_extraction_work",
)

PROJECTION_PROFILES = ("operator_workbench", "public_web", "native_desktop_read_only")

OPERATOR_ONLY_FIELDS = frozenset(
    {
        "operator_notes",
        "source_record_ids",
        "source_cache_entry_ids",
        "evidence_refs",
        "candidate_refs",
        "review_refs",
        "workunit_refs",
        "private_local_path_refs",
        "debug",
    }
)

PUBLIC_VISIBLE_LANES = frozenset({"reviewed_local_results", "known_absence", "near_misses", "blocked_actions"})
NATIVE_VISIBLE_LANES = frozenset({"reviewed_local_results", "known_absence", "blocked_actions"})

UNSAFE_ACTIONS = (
    "download",
    "extract",
    "execute",
    "call_model_provider",
    "deploy_public_site",
    "run_source_probe",
    "mutate_master_index",
)

LANE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "reviewed_local_results": {
        "truth_level": "reviewed_local_not_master_public_truth",
        "review_required": False,
        "source_mapping": "reviewed local index",
        "can_be_public": True,
    },
    "local_candidate_results": {
        "truth_level": "provisional_candidate_not_truth",
        "review_required": True,
        "source_mapping": "candidate index",
        "can_be_public": False,
    },
    "source_cache_hits": {
        "truth_level": "source_cache_record_not_evidence",
        "review_required": False,
        "source_mapping": "source cache",
        "can_be_public": False,
    },
    "ia_metadata_candidates": {
        "truth_level": "ia_metadata_candidate_not_truth",
        "review_required": True,
        "source_mapping": "IA candidate/index/source-cache/evidence preview records",
        "can_be_public": False,
    },
    "review_queue_items": {
        "truth_level": "review_queue_item_not_accepted_truth",
        "review_required": True,
        "source_mapping": "review queue",
        "can_be_public": False,
    },
    "known_absence": {
        "truth_level": "bounded_absence_not_global_proof",
        "review_required": False,
        "source_mapping": "absence records/absence packets",
        "can_be_public": True,
    },
    "near_misses": {
        "truth_level": "near_miss_not_truth",
        "review_required": True,
        "source_mapping": "candidate/absence/coverage records where available",
        "can_be_public": True,
    },
    "blocked_actions": {
        "truth_level": "policy_block_not_capability_absence",
        "review_required": False,
        "source_mapping": "policy/action posture",
        "can_be_public": True,
    },
    "running_workunits": {
        "truth_level": "operational_state_not_truth",
        "review_required": False,
        "source_mapping": "WorkUnit queue",
        "can_be_public": False,
    },
    "deferred_deepening": {
        "truth_level": "planned_work_not_truth",
        "review_required": False,
        "source_mapping": "SearchNeed/WorkUnit future work",
        "can_be_public": False,
    },
    "future_extraction_work": {
        "truth_level": "deferred_extraction_work_not_enabled",
        "review_required": True,
        "source_mapping": "extraction-deferred WorkUnits only",
        "can_be_public": False,
    },
}


def build_result_lane_packet(
    lane_kind: str,
    items: Sequence[Mapping[str, Any]] | None = None,
    projection_profile: str = "operator_workbench",
) -> dict[str, Any]:
    """Build a read-only ResultLanePacket projection from already-local records."""
    canonical_lane = _canonical_lane_kind(lane_kind)
    _require_projection_profile(projection_profile)
    definition = LANE_DEFINITIONS[canonical_lane]
    operator_lane = {
        "schema_version": "result_lane_packet.v0",
        "packet_type": "ResultLanePacket",
        "emitted_at": _fixed_emitted_at(),
        "lane_id": f"lane-{canonical_lane}",
        "lane_kind": canonical_lane,
        "projection_profile": "operator_workbench",
        "state": "available",
        "visible": True,
        "truth_level": definition["truth_level"],
        "review_required": definition["review_required"],
        "source_mapping": definition["source_mapping"],
        "result_count": 0,
        "result_ids": [],
        "items": [],
        "confidence": 0.8,
        "limitations": _default_limitations(canonical_lane),
        "uncertainty": ["Local projection only; lane content does not create truth."],
        "provenance": {
            "source_mapping": definition["source_mapping"],
            "source_probe_executed": False,
            "live_ia_call_performed": False,
            "store_mutation_performed": False,
        },
        "action_posture": _action_posture(canonical_lane, "operator_workbench"),
        "blocked_actions": list(UNSAFE_ACTIONS) + ["promote_preview", "rebuild_reviewed_index"],
    }
    normalized_items = [_normalize_item(canonical_lane, index, item) for index, item in enumerate(items or [])]
    operator_lane["items"] = normalized_items
    operator_lane["result_ids"] = [item["item_id"] for item in normalized_items]
    operator_lane["result_count"] = len(normalized_items)
    return project_lane_for_profile(operator_lane, projection_profile)


def project_lane_for_profile(lane: Mapping[str, Any], projection_profile: str) -> dict[str, Any]:
    """Project a lane into operator, public, or native read-only form."""
    _require_projection_profile(projection_profile)
    projected = deepcopy(dict(lane))
    canonical_lane = _canonical_lane_kind(str(projected["lane_kind"]))
    visible = _lane_visible(canonical_lane, projection_profile)
    projected["projection_profile"] = projection_profile
    projected["visible"] = visible
    projected["action_posture"] = _action_posture(canonical_lane, projection_profile)

    if projection_profile == "operator_workbench":
        return projected

    projected["operator_only_fields_hidden"] = True
    projected["provenance"] = {
        "source_mapping": projected.get("source_mapping"),
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "store_mutation_performed": False,
    }

    if not visible:
        projected["items"] = []
        projected["result_ids"] = []
        projected["result_count"] = 0
        projected["limitations"] = list(projected.get("limitations", [])) + [
            f"{canonical_lane} is hidden in {projection_profile} by projection policy."
        ]
        return _strip_operator_fields(projected)

    projected["items"] = [_strip_operator_fields(item) for item in projected.get("items", [])]
    projected["result_ids"] = [item["item_id"] for item in projected["items"]]
    projected["result_count"] = len(projected["items"])
    return _strip_operator_fields(projected)


def build_result_lane_page_view(
    query: str,
    lanes: Sequence[Mapping[str, Any]],
    projection_profile: str = "operator_workbench",
) -> dict[str, Any]:
    """Build the page-level view model consumed by Workbench-compatible surfaces."""
    _require_projection_profile(projection_profile)
    projected_lanes = [project_lane_for_profile(lane, projection_profile) for lane in lanes]
    return {
        "schema_version": "workbench_result_lane_page_view.v0",
        "packet_type": "ResultLanePageView",
        "emitted_at": _fixed_emitted_at(),
        "query": query,
        "projection_profile": projection_profile,
        "lanes": projected_lanes,
        "lane_count": len(projected_lanes),
        "visible_lane_count": sum(1 for lane in projected_lanes if lane.get("visible") is True),
        "boundary_report": build_boundary_report(projected_lanes, projection_profile),
        "non_claims": [
            "Result lanes are projections, not truth creation.",
            "No source probes, live IA calls, extraction, model calls, downloads, or deployment are enabled.",
        ],
    }


def build_blocked_action_lane(policy_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build the blocked-actions lane from policy posture only."""
    state = dict(policy_state or {})
    items = [
        {
            "item_id": f"blocked-{action}",
            "title": action.replace("_", " "),
            "summary": state.get(action, "Blocked under current Workbench result-lane policy."),
            "blocked_action": action,
            "operator_notes": "Blocked action lane is policy posture, not evidence of permanent unsupported status.",
        }
        for action in UNSAFE_ACTIONS
    ]
    return build_result_lane_packet("blocked_actions", items, "operator_workbench")


def build_absence_lane(query: str, absence_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a known-absence lane without overclaiming global absence."""
    packet = dict(absence_packet or {})
    items = [
        {
            "item_id": packet.get("absence_id", f"absence-{_slug(query)}"),
            "title": f"No reviewed local result for {query}",
            "summary": packet.get("summary", "Known absence is bounded to checked local layers."),
            "checked_layers": packet.get("checked_layers", ["reviewed_local_results"]),
            "operator_notes": "Absence is bounded and does not prove global non-existence.",
        }
    ]
    return build_result_lane_packet("known_absence", items, "operator_workbench")


def build_deferred_deepening_lane(search_need_or_workunits: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Build a deferred-deepening lane from already-local SearchNeed or WorkUnit summaries."""
    if search_need_or_workunits is None:
        records: list[Mapping[str, Any]] = []
    elif isinstance(search_need_or_workunits, Mapping):
        records = [search_need_or_workunits]
    else:
        records = list(search_need_or_workunits)
    items = [
        {
            "item_id": str(record.get("workunit_id") or record.get("search_need_id") or f"deferred-{index}"),
            "title": str(record.get("title") or "Deferred deepening"),
            "summary": str(record.get("summary") or "Future WorkUnit can deepen this result lane after policy gates."),
            "workunit_refs": [str(record.get("workunit_id"))] if record.get("workunit_id") else [],
            "operator_notes": "Deferred lane records future work only; it does not run probes.",
        }
        for index, record in enumerate(records)
    ]
    if not items:
        items = [
            {
                "item_id": "deferred-deepening-placeholder",
                "title": "Deferred deepening available",
                "summary": "Further source-backed work is reserved for IA-HUNT-BRIDGE-00 and later tasks.",
                "workunit_refs": [],
                "operator_notes": "No WorkUnit was created or executed by this projection.",
            }
        ]
    return build_result_lane_packet("deferred_deepening", items, "operator_workbench")


def build_demo_lane_page(
    query: str,
    projection_profile: str = "operator_workbench",
    *,
    from_play_demo: bool = False,
    from_ia_examples: bool = False,
) -> dict[str, Any]:
    """Build deterministic demo lanes from committed fixture-shaped records."""
    _require_projection_profile(projection_profile)
    lanes = [
        build_result_lane_packet(
            "reviewed_local_results",
            [
                {
                    "item_id": "reviewed-sampleproject-001",
                    "title": "SampleProject reviewed local result",
                    "summary": "Reviewed local fixture result for deterministic Workbench lane projection.",
                    "source_record_ids": ["reviewed-public-record-sampleproject"],
                    "evidence_refs": ["evidence-reviewed-sampleproject"],
                    "operator_notes": "Committed fixture-backed reviewed lane; not master/public truth.",
                }
            ] if from_play_demo else [],
        ),
        build_result_lane_packet(
            "local_candidate_results",
            [
                {
                    "item_id": "candidate-stylewriter-2500-001",
                    "title": "StyleWriter 2500 Mac OS 8 driver candidate",
                    "summary": "Candidate fixture requires review before it can become accepted evidence.",
                    "candidate_refs": ["candidate-index-stylewriter-2500"],
                    "review_refs": ["review-required"],
                    "operator_notes": "Candidate does not mean truth.",
                }
            ] if from_play_demo else [],
        ),
        build_result_lane_packet(
            "source_cache_hits",
            [
                {
                    "item_id": "source-cache-ia-sampleproject-001",
                    "title": "Internet Archive metadata cache hit",
                    "summary": "Local IA metadata cache-shaped fixture; source cache is not accepted evidence.",
                    "source_cache_entry_ids": ["ia-metadata-cache-sampleproject"],
                    "operator_notes": "No live IA call was made.",
                }
            ] if from_ia_examples else [],
        ),
        build_result_lane_packet(
            "ia_metadata_candidates",
            [
                {
                    "item_id": "ia-candidate-sampleproject-001",
                    "title": "IA metadata candidate for sampleproject",
                    "summary": "Provisional IA metadata candidate from committed example records.",
                    "candidate_refs": ["ia-candidate-index-sampleproject"],
                    "evidence_refs": ["ia-evidence-preview-sampleproject"],
                    "operator_notes": "IA metadata candidate remains review-required.",
                }
            ] if from_ia_examples else [],
        ),
        build_result_lane_packet(
            "review_queue_items",
            [
                {
                    "item_id": "review-item-sampleproject-001",
                    "title": "Review required for IA candidate",
                    "summary": "Review queue projection only; no review mutation occurred.",
                    "review_refs": ["review-item-sampleproject-001"],
                    "operator_notes": "Review item visibility is operator-only.",
                }
            ] if from_ia_examples else [],
        ),
        build_absence_lane("definitely-not-present-play-00"),
        build_result_lane_packet(
            "near_misses",
            [
                {
                    "item_id": "near-miss-demo-tape-001",
                    "title": "New York 1993 D-Theater HD demo tape near miss",
                    "summary": "Near miss illustrates uncertainty and does not claim a correct match.",
                    "candidate_refs": ["near-miss-candidate-demo-tape"],
                    "operator_notes": "Near miss needs manual review.",
                }
            ],
        ),
        build_blocked_action_lane(),
        build_result_lane_packet(
            "running_workunits",
            [
                {
                    "item_id": "workunit-fixture-001",
                    "title": "Fixture WorkUnit queued",
                    "summary": "Read-only projection of a WorkUnit-shaped fixture; no worker executed.",
                    "workunit_refs": ["workunit-fixture-001"],
                    "operator_notes": "Running lane is operational state only.",
                }
            ],
        ),
        build_deferred_deepening_lane(
            {
                "search_need_id": "need-deepen-sampleproject",
                "title": "Deepen source coverage later",
                "summary": "IA-HUNT-BRIDGE-00 can attach future WorkUnits.",
            }
        ),
        build_result_lane_packet(
            "future_extraction_work",
            [
                {
                    "item_id": "future-extraction-sampleproject",
                    "title": "Extraction deferred",
                    "summary": "Extraction remains disabled and deferred to later governed work.",
                    "workunit_refs": [],
                    "operator_notes": "Future extraction lane does not extract.",
                }
            ],
        ),
    ]
    return build_result_lane_page_view(query, lanes, projection_profile)


def build_boundary_report(lanes: Sequence[Mapping[str, Any]], projection_profile: str) -> dict[str, Any]:
    """Return non-claim and side-effect evidence for a lane projection."""
    return {
        "schema_version": "workbench_result_lane_boundary_report.v0",
        "projection_profile": projection_profile,
        "lane_count": len(lanes),
        "operator_fields_hidden": projection_profile != "operator_workbench",
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "operator_instance_mutated": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "marketplace_or_app_store_readiness_claimed": False,
        "unsafe_actions_blocked": True,
    }


def _normalize_item(lane_kind: str, index: int, item: Mapping[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(dict(item))
    normalized.setdefault("item_id", f"{lane_kind}-{index}")
    normalized.setdefault("title", normalized["item_id"])
    normalized.setdefault("summary", "")
    normalized["truth_level"] = LANE_DEFINITIONS[lane_kind]["truth_level"]
    normalized["review_required"] = LANE_DEFINITIONS[lane_kind]["review_required"]
    normalized.setdefault("limitations", _default_limitations(lane_kind))
    normalized.setdefault("uncertainty", ["Projection is local and bounded."])
    normalized.setdefault("provenance", {"source_mapping": LANE_DEFINITIONS[lane_kind]["source_mapping"]})
    normalized["action_posture"] = _action_posture(lane_kind, "operator_workbench")
    normalized.setdefault("operator_notes", "Operator-only detail.")
    normalized.setdefault("private_local_path_refs", [])
    normalized.setdefault("debug", {"fixture_only": True})
    return normalized


def _action_posture(lane_kind: str, projection_profile: str) -> dict[str, Any]:
    operator = projection_profile == "operator_workbench"
    reviewable = LANE_DEFINITIONS[lane_kind]["review_required"] and operator
    return {
        "can_view": _lane_visible(lane_kind, projection_profile),
        "can_inspect": _lane_visible(lane_kind, projection_profile),
        "can_cite": lane_kind in {"reviewed_local_results", "known_absence", "near_misses"} and _lane_visible(lane_kind, projection_profile),
        "can_export": _lane_visible(lane_kind, projection_profile),
        "can_review": reviewable,
        "can_promote_preview": False,
        "can_rebuild_index": False,
        "can_download": False,
        "can_extract": False,
        "can_execute": False,
        "can_call_model": False,
        "can_deploy": False,
        "blocked_actions": list(UNSAFE_ACTIONS) + ["promote_preview", "rebuild_reviewed_index"],
        "policy_reasons": [
            "Result lanes are read-only projections.",
            "Unsafe actions remain disabled until future governed tasks enable them.",
        ],
    }


def _lane_visible(lane_kind: str, projection_profile: str) -> bool:
    if projection_profile == "operator_workbench":
        return True
    if projection_profile == "public_web":
        return lane_kind in PUBLIC_VISIBLE_LANES
    return lane_kind in NATIVE_VISIBLE_LANES


def _strip_operator_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _strip_operator_fields(inner)
            for key, inner in value.items()
            if str(key) not in OPERATOR_ONLY_FIELDS
        }
    if isinstance(value, list):
        return [_strip_operator_fields(item) for item in value]
    return value


def _canonical_lane_kind(lane_kind: str) -> str:
    if lane_kind == "IA_metadata_candidates":
        lane_kind = "ia_metadata_candidates"
    if lane_kind not in LANE_DEFINITIONS:
        raise ValueError(f"unknown lane_kind: {lane_kind}")
    return lane_kind


def _require_projection_profile(projection_profile: str) -> None:
    if projection_profile not in PROJECTION_PROFILES:
        raise ValueError(f"unknown projection_profile: {projection_profile}")


def _default_limitations(lane_kind: str) -> list[str]:
    if lane_kind == "reviewed_local_results":
        return ["Reviewed local result is not master/public truth."]
    if lane_kind == "known_absence":
        return ["Absence is bounded to checked local layers and is not global proof."]
    if lane_kind == "blocked_actions":
        return ["Blocked action is current policy posture, not a permanent product limitation."]
    return ["Lane is a local projection and does not create truth."]


def _fixed_emitted_at() -> str:
    return datetime(2026, 5, 20, 0, 0, 0, tzinfo=UTC).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-") or "query"


__all__ = [
    "LANE_KINDS",
    "PROJECTION_PROFILES",
    "build_absence_lane",
    "build_blocked_action_lane",
    "build_boundary_report",
    "build_deferred_deepening_lane",
    "build_demo_lane_page",
    "build_result_lane_packet",
    "build_result_lane_page_view",
    "project_lane_for_profile",
]
