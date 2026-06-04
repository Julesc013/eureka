"""Seed-corpus readiness loader for hard-query fixtures."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.surface import SurfaceKernel, SurfaceRequest


BASELINE_PROFILES = ("json_v0", "text_v0", "html_basic_v0", "snapshot_v0")
PUBLIC_ALPHA_TARGETS = {
    "hard_queries": 50,
    "reviewed_records": 200,
    "candidates_needs_near_misses_or_absences": 500,
}
SEED_STATUSES = (
    "verified",
    "candidate",
    "need",
    "near_miss",
    "mention_only",
    "policy_blocked",
    "private_local",
    "superseded",
    "rejected",
    "unknown",
    "unavailable",
)
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
OPERATOR_ACTIONS = frozenset(
    {"review_candidate", "promote", "reject", "request_more_evidence", "mark_near_miss", "mark_need", "mark_policy_blocked"}
)
REQUIRED_HARD_QUERY_IDS = (
    "hq_windows_7_apps",
    "hq_driver_win98",
    "hq_blue_ftp_client_xp",
    "hq_sound_blaster_ct1740_manual",
    "hq_firefox_last_xp",
    "hq_ray_tracing_1994_magazine",
)
REVIEW_DECISIONS = (
    "promote",
    "reject",
    "supersede",
    "mark_near_miss",
    "mark_need",
    "mark_policy_blocked",
    "request_more_evidence",
)


def seed_corpus_root() -> Path:
    return Path(__file__).resolve().parent


def load_seed_corpus(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or seed_corpus_root()) / "seed_corpus.v0.json")


def load_query_seed_map(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or seed_corpus_root()) / "query_seed_map.v0.json")


def load_review_backlog(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or seed_corpus_root()) / "review_backlog.v0.json")


def load_public_alpha_readiness(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or seed_corpus_root()) / "public_alpha_corpus_readiness.v0.json")


def validate_seed_corpus(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("seed_items")
    if not isinstance(items, list):
        return ("seed_items must be a list",)
    ids = [str(item.get("seed_item_id", "")) for item in items if isinstance(item, Mapping)]
    if len(ids) != len(set(ids)):
        errors.append("seed_item_id values must be unique")
    hard_query_ids = [str(item.get("hard_query_id", "")) for item in items if isinstance(item, Mapping)]
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in hard_query_ids:
            errors.append(f"missing hard query seed item: {required}")
    for item in items:
        if not isinstance(item, Mapping):
            errors.append("seed item must be an object")
            continue
        errors.extend(_validate_seed_item(item))
    return tuple(errors)


def validate_query_seed_map(payload: Mapping[str, Any], seed_payload: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    maps = payload.get("query_maps")
    if not isinstance(maps, list):
        return ("query_maps must be a list",)
    item_ids = {
        str(item.get("seed_item_id", ""))
        for item in (seed_payload or {}).get("seed_items", [])
        if isinstance(item, Mapping)
    }
    ids = [str(item.get("hard_query_id", "")) for item in maps if isinstance(item, Mapping)]
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in ids:
            errors.append(f"missing query map: {required}")
    for item in maps:
        if not isinstance(item, Mapping):
            errors.append("query map entries must be objects")
            continue
        best = str(item.get("best_available_seed_item_id") or item.get("best_available_item") or "")
        if item_ids and best not in item_ids:
            errors.append(f"{item.get('hard_query_id', '<missing>')} best_available_item is not a seed item")
        counted = sum(
            int(item.get(key, 0))
            for key in (
                "reviewed_record_count",
                "candidate_count",
                "need_count",
                "near_miss_count",
                "policy_blocked_count",
                "unavailable_count",
            )
        )
        if counted <= 0:
            errors.append(f"{item.get('hard_query_id', '<missing>')} has no mapped readiness state")
    return tuple(errors)


def validate_review_backlog(payload: Mapping[str, Any], seed_payload: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("backlog_items")
    if not isinstance(items, list):
        return ("backlog_items must be a list",)
    seed_item_ids = {
        str(item.get("seed_item_id", ""))
        for item in (seed_payload or {}).get("seed_items", [])
        if isinstance(item, Mapping)
    }
    for item in items:
        if not isinstance(item, Mapping):
            errors.append("backlog item must be an object")
            continue
        if seed_item_ids and str(item.get("seed_item_id", "")) not in seed_item_ids:
            errors.append(f"{item.get('backlog_item_id', '<missing>')} references unknown seed item")
        if str(item.get("desired_review_decision", "")) not in REVIEW_DECISIONS:
            errors.append(f"{item.get('backlog_item_id', '<missing>')} has unsupported desired review decision")
        if not item.get("required_evidence"):
            errors.append(f"{item.get('backlog_item_id', '<missing>')} must list required evidence")
    if payload.get("review_decisions_created") is not False:
        errors.append("review backlog must not create review decisions")
    return tuple(errors)


def validate_public_alpha_readiness(payload: Mapping[str, Any], seed_payload: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("current gate must honestly report insufficient reviewed corpus")
    current = payload.get("current")
    if not isinstance(current, Mapping):
        return tuple(errors + ["current readiness counts must be present"])
    if seed_payload is not None:
        counts = seed_corpus_counts(seed_payload)
        if int(current.get("reviewed_count", -1)) != counts["reviewed"]:
            errors.append("readiness reviewed_count does not match seed corpus")
        if int(current.get("candidate_count", -1)) != counts["candidate"]:
            errors.append("readiness candidate_count does not match seed corpus")
        if int(current.get("need_count", -1)) != counts["need"]:
            errors.append("readiness need_count does not match seed corpus")
        if int(current.get("near_miss_count", -1)) != counts["near_miss"]:
            errors.append("readiness near_miss_count does not match seed corpus")
        if int(current.get("policy_blocked_count", -1)) != counts["policy_blocked"]:
            errors.append("readiness policy_blocked_count does not match seed corpus")
        if int(current.get("unavailable_count", -1)) != counts["unavailable"]:
            errors.append("readiness unavailable_count does not match seed corpus")
        if int(current.get("unknown_count", -1)) != counts["unknown"]:
            errors.append("readiness unknown_count does not match seed corpus")
    truth = payload.get("truth_boundary")
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be present")
    else:
        for key in (
            "synthetic_fixtures_count_as_evidence",
            "fallback_output_counted_as_verified",
            "candidate_counted_as_reviewed",
            "need_counted_as_reviewed",
            "near_miss_counted_as_reviewed",
            "review_backlog_items_are_review_decisions",
            "live_source_calls_performed",
            "reviewed_index_mutated",
            "public_index_mutated",
            "master_index_mutated",
        ):
            if truth.get(key) is not False:
                errors.append(f"truth boundary flag must be false: {key}")
    return tuple(errors)


def seed_corpus_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {
        "reviewed": 0,
        "candidate": 0,
        "need": 0,
        "near_miss": 0,
        "policy_blocked": 0,
        "unavailable": 0,
        "unknown": 0,
    }
    for item in payload.get("seed_items") or []:
        if not isinstance(item, Mapping):
            continue
        status = str(item.get("status") or "unknown")
        if _counts_as_reviewed(item):
            counts["reviewed"] += 1
        if status in counts and status != "verified":
            counts[status] += 1
    return counts


def seed_items(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("seed_items") or [] if isinstance(item, Mapping))


def is_reviewed_seed_item(item: Mapping[str, Any]) -> bool:
    return _counts_as_reviewed(item)


def reviewed_seed_items(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("seed_items") or [] if isinstance(item, Mapping) and _counts_as_reviewed(item))


def project_seed_item(seed_item: Mapping[str, Any], profile: str) -> dict[str, Any]:
    run = _resolution_run_for_seed_item(seed_item)
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="resolution_run",
            entity_id=str(seed_item.get("seed_item_id") or "seed-item"),
            payload=run,
            requested_profile=profile,
            visibility_posture="public",
            data_version="hard-query-seed-corpus-v0",
        )
    )


def _validate_seed_item(item: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    for field in _required_seed_fields():
        if field not in item:
            errors.append(f"{item.get('seed_item_id', '<missing>')} missing {field}")
    status = str(item.get("status") or "")
    if status not in SEED_STATUSES:
        errors.append(f"{item.get('seed_item_id', '<missing>')} has unsupported status")
    evidence_refs = _list(item.get("evidence_refs"))
    review_event_ref = item.get("review_event_ref")
    if status == "verified" and (not review_event_ref or not evidence_refs):
        errors.append(f"{item.get('seed_item_id', '<missing>')} verified requires review_event_ref and evidence_refs")
    if status != "verified" and _counts_as_reviewed(item):
        errors.append(f"{item.get('seed_item_id', '<missing>')} non-verified item must not count as reviewed")
    for flag in (
        "reviewed_seed_material",
        "accepted_truth",
        "reviewed_record_created",
        "reviewed_index_mutated",
        "public_index_mutated",
        "master_index_mutated",
        "live_source_calls",
    ):
        if item.get(flag) is not False:
            errors.append(f"{item.get('seed_item_id', '<missing>')} must keep {flag}=false")
    if tuple(item.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
        errors.append(f"{item.get('seed_item_id', '<missing>')} must expect all baseline profiles")
    public_actions = set(_list(item.get("allowed_public_actions")))
    if not public_actions.issubset(PUBLIC_ALLOWED_ACTIONS):
        errors.append(f"{item.get('seed_item_id', '<missing>')} has unsafe public action")
    operator_actions = set(_list(item.get("operator_actions")))
    if operator_actions and not operator_actions.issubset(OPERATOR_ACTIONS):
        errors.append(f"{item.get('seed_item_id', '<missing>')} has unknown operator action")
    if status == "near_miss" and not item.get("known_gaps"):
        errors.append(f"{item.get('seed_item_id', '<missing>')} near_miss requires mismatch/gap explanation")
    if status == "policy_blocked" and not item.get("known_gaps"):
        errors.append(f"{item.get('seed_item_id', '<missing>')} policy_blocked requires policy reason")
    if status in {"unknown", "unavailable"} and not item.get("known_gaps"):
        errors.append(f"{item.get('seed_item_id', '<missing>')} degraded state requires reason")
    return tuple(errors)


def _required_seed_fields() -> tuple[str, ...]:
    return (
        "seed_item_id",
        "hard_query_id",
        "query_text",
        "expected_answer_shape_id",
        "entity_kind",
        "title",
        "status",
        "useful_unit",
        "platform_or_time_hints",
        "source_observation_refs",
        "evidence_refs",
        "review_item_ref",
        "review_event_ref",
        "review_status",
        "rights_risk_posture",
        "compatibility_posture",
        "known_gaps",
        "public_visibility",
        "operator_visibility",
        "allowed_public_actions",
        "operator_actions",
        "renderer_profiles_expected",
        "reviewed_seed_material",
        "accepted_truth",
        "reviewed_record_created",
        "reviewed_index_mutated",
        "public_index_mutated",
        "master_index_mutated",
        "live_source_calls",
        "review_required",
        "notes",
    )


def _counts_as_reviewed(item: Mapping[str, Any]) -> bool:
    return (
        str(item.get("status") or "") == "verified"
        and bool(item.get("review_event_ref"))
        and bool(_list(item.get("evidence_refs")))
    )


def _resolution_run_for_seed_item(seed_item: Mapping[str, Any]) -> ResolutionRunRecord:
    seed_id = str(seed_item.get("seed_item_id") or "seed-item")
    return ResolutionRunRecord(
        run_id=f"run-{seed_id}",
        run_kind="seed_corpus_readiness_projection",
        requested_value=str(seed_item.get("query_text") or ""),
        status="completed",
        started_at="2026-06-04T00:00:00+00:00",
        completed_at="2026-06-04T00:00:00+00:00",
        checked_source_ids=tuple(_list(seed_item.get("source_observation_refs"))),
        checked_source_families=(),
        fallback_summary=_fallback_summary(seed_item),
    )


def _fallback_summary(seed_item: Mapping[str, Any]) -> dict[str, Any]:
    status = str(seed_item.get("status") or "unknown")
    summary = {
        "schema_version": "hard_query_seed_corpus_fallback_summary.v0",
        "mode": "seed_corpus_readiness_projection",
        "status": status,
        "trigger": "seed_corpus_projection",
        "query": str(seed_item.get("query_text") or ""),
        "source_id": "seed_corpus_fixture",
        "source_family": "seed_corpus_readiness",
        "source_allowlisted": True,
        "fallback_enabled": True,
        "title": str(seed_item.get("title") or ""),
        "evidence_summary": str(seed_item.get("useful_unit") or ""),
        "reason_codes": _list(seed_item.get("known_gaps")),
        "source_observation_refs": _list(seed_item.get("source_observation_refs")),
        "evidence_refs": _list(seed_item.get("evidence_refs")),
        "operator_actions": _list(seed_item.get("operator_actions")),
        "candidate_count": 0,
        "candidates": [],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "live_source_calls": False,
    }
    if status in {"candidate", "near_miss"}:
        summary["candidate_count"] = 1
        summary["candidates"] = [
            {
                "candidate_id": str(seed_item.get("seed_item_id") or "seed-candidate"),
                "status": status,
                "title": str(seed_item.get("title") or ""),
                "summary": str(seed_item.get("useful_unit") or ""),
                "verified": False,
                "accepted_truth": False,
                "public_actions": _list(seed_item.get("allowed_public_actions")),
            }
        ]
    if status == "need":
        summary["need_count"] = 1
        summary["needs"] = [
            {
                "need_id": str(seed_item.get("seed_item_id") or "seed-need"),
                "status": "need",
                "title": str(seed_item.get("title") or ""),
                "summary": str(seed_item.get("useful_unit") or ""),
                "verified": False,
                "accepted_truth": False,
                "public_actions": _list(seed_item.get("allowed_public_actions")),
            }
        ]
    if status == "policy_blocked":
        summary["policy_block_reason"] = "; ".join(_list(seed_item.get("known_gaps")))
    if status in {"unknown", "unavailable"}:
        summary["unavailable_reason"] = "; ".join(_list(seed_item.get("known_gaps")))
    return summary


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []
