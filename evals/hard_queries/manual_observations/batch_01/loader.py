"""Loader and projection helpers for manual observation batch one."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.seed_corpus.loader import BASELINE_PROFILES, REQUIRED_HARD_QUERY_IDS, SEED_STATUSES
from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.surface import SurfaceKernel, SurfaceRequest


CANONICAL_STATUSES = tuple(SEED_STATUSES)
OBSERVATION_STATUS_RECOMMENDATIONS = (
    "candidate",
    "need",
    "near_miss",
    "policy_blocked",
    "unavailable",
    "request_more_evidence",
)
OBSERVATION_REVIEWABILITY = (
    "reviewable",
    "not_reviewable",
    "blocked_for_user_details",
    "requires_more_evidence",
)
SOURCE_QUALITY = (
    "primary",
    "official",
    "reputable_secondary",
    "archive_reference",
    "community_reference",
    "weak",
    "unknown",
)
REVIEW_DECISIONS = frozenset(
    {"promote", "reject", "supersede", "mark_near_miss", "mark_need", "mark_policy_blocked", "request_more_evidence"}
)
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
FORBIDDEN_PUBLIC_ACTIONS = frozenset(
    {
        "review_candidate",
        "promote",
        "reject",
        "supersede",
        "request_more_evidence",
        "rebuild_index",
        "freeze_review",
        "download",
        "install",
        "launch_emulator",
        "run_extraction",
        "submit_direct_evidence",
        "crawl_source",
        "arbitrary_live_lookup",
    }
)
REQUIRED_OBSERVATION_FIELDS = (
    "observation_id",
    "query_id",
    "source_title",
    "source_url",
    "source_kind",
    "observed_at",
    "observed_by",
    "claim_summary",
    "supports_answer_shape",
    "status_recommendation",
    "projected_status",
    "reviewability",
    "source_quality",
    "confidence",
    "risk_rights_notes",
    "compatibility_notes",
    "evidence_summary",
    "short_quote_if_needed",
    "quote_word_count",
    "manual_verification_steps",
    "forbidden_actions_confirmed",
    "notes",
    "allowed_public_actions",
    "operator_actions",
    "source_observation_self_promoted",
    "candidate_self_promoted",
    "reviewed_record_created",
    "review_event_created",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "product_runtime_live_source_call",
    "synthetic_eval_fixture_used_as_evidence",
)
TRUTH_FLAGS = (
    "source_observation_self_promoted",
    "candidate_self_promoted",
    "reviewed_record_created",
    "review_event_created",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "product_runtime_live_source_call",
    "synthetic_eval_fixture_used_as_evidence",
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    return batch_root().parents[3]


def review_backlog_root() -> Path:
    return repo_root() / "evals" / "hard_queries" / "review_backlog" / "batch_01"


def load_observations(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "observations.json")


def load_query_mapping(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_mapping.json")


def load_reviewable_items(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewable_items.json")


def load_non_reviewable_items(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "non_reviewable_items.json")


def load_public_alpha_corpus_delta(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_corpus_delta.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def load_validation_summary(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "validation_summary.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def observation_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("observations") or [] if isinstance(item, Mapping))


def reviewable_item_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewable_items") or [] if isinstance(item, Mapping))


def manual_observation_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {
        "reviewed": 0,
        "candidate": 0,
        "need": 0,
        "near_miss": 0,
        "mention_only": 0,
        "policy_blocked": 0,
        "unavailable": 0,
        "unknown": 0,
        "blocked_for_user_details": 0,
    }
    for item in observation_records(payload):
        status = _projected_status(item)
        if item.get("reviewability") == "blocked_for_user_details":
            counts["blocked_for_user_details"] += 1
        if status == "verified" and item.get("review_event_created") is True:
            counts["reviewed"] += 1
        elif status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
    return counts


def validation_truth_flags(payload: Mapping[str, Any]) -> dict[str, bool]:
    flags = {flag: False for flag in TRUTH_FLAGS}
    for item in observation_records(payload):
        for flag in TRUTH_FLAGS:
            flags[flag] = flags[flag] or item.get(flag) is not False
    return flags


def validate_observations(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    observations = payload.get("observations")
    if not isinstance(observations, list):
        return ("observations must be a list",)
    records = observation_records(payload)
    ids = [str(item.get("observation_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("observation_id values must be unique")
    query_ids = {str(item.get("query_id") or "") for item in records}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing observation attempt for {required}")
    for item in records:
        errors.extend(_validate_observation(item))
    return tuple(errors)


def validate_query_mapping(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    maps = payload.get("query_maps")
    if not isinstance(maps, list):
        return ("query_maps must be a list",)
    obs_by_id = {item["observation_id"]: item for item in observation_records(observations or load_observations())}
    query_ids = {str(item.get("query_id") or "") for item in maps if isinstance(item, Mapping)}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing query map for {required}")
    for item in maps:
        if not isinstance(item, Mapping):
            errors.append("query map item must be an object")
            continue
        query_id = str(item.get("query_id") or "<missing>")
        observation_ids = _strings(item.get("observation_ids"))
        if not observation_ids:
            errors.append(f"{query_id} must include observations")
        for observation_id in observation_ids:
            if observation_id not in obs_by_id:
                errors.append(f"{query_id} references unknown observation {observation_id}")
        if item.get("public_alpha_readiness") != "not_ready":
            errors.append(f"{query_id} must remain not_ready")
    return tuple(errors)


def validate_reviewable_items(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("reviewable_items")
    if not isinstance(items, list):
        return ("reviewable_items must be a list",)
    observation_ids = {item["observation_id"] for item in observation_records(observations or load_observations())}
    for item in reviewable_item_records(payload):
        item_id = str(item.get("review_item_id") or "<missing>")
        source_ids = _strings(item.get("source_observation_ids"))
        if not source_ids:
            errors.append(f"{item_id} must include source observations")
        for source_id in source_ids:
            if source_id not in observation_ids:
                errors.append(f"{item_id} references unknown observation {source_id}")
        if str(item.get("proposed_decision") or "") not in REVIEW_DECISIONS:
            errors.append(f"{item_id} has unsupported proposed decision")
        if not item.get("evidence_summary"):
            errors.append(f"{item_id} must include evidence summary")
        for flag in ("review_event_created", "reviewed_record_created", "reviewed_index_mutated"):
            if item.get(flag) is not False:
                errors.append(f"{item_id} must keep {flag}=false")
    if payload.get("review_ledger_decisions_created") is not False:
        errors.append("batch must not create review ledger decisions")
    return tuple(errors)


def validate_non_reviewable_items(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("non_reviewable_items")
    if not isinstance(items, list):
        return ("non_reviewable_items must be a list",)
    observation_ids = {item["observation_id"] for item in observation_records(observations or load_observations())}
    for item in items:
        if not isinstance(item, Mapping):
            errors.append("non_reviewable item must be an object")
            continue
        item_id = str(item.get("non_reviewable_item_id") or "<missing>")
        if str(item.get("observation_id") or "") not in observation_ids:
            errors.append(f"{item_id} references unknown observation")
        if not item.get("manual_followup_reason"):
            errors.append(f"{item_id} must include manual followup reason")
        if item.get("reviewable_now") is not False:
            errors.append(f"{item_id} must keep reviewable_now=false")
    return tuple(errors)


def validate_public_alpha_corpus_delta(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("public alpha corpus gate must remain failed")
    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        return tuple(errors + ["counts must be present"])
    if observations is not None:
        computed = manual_observation_counts(observations)
        for key, value in computed.items():
            count_key = f"{key}_count"
            if int(counts.get(count_key, -1)) != value:
                errors.append(f"{count_key} does not match observations")
    for key, value in (payload.get("truth_boundary") or {}).items():
        if value is not False:
            errors.append(f"truth boundary flag must be false: {key}")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        return ("surface projection fixtures must be a list",)
    obs_by_id = {item["observation_id"]: item for item in observation_records(observations or load_observations())}
    for fixture in fixtures:
        if not isinstance(fixture, Mapping):
            errors.append("surface projection fixture must be an object")
            continue
        observation_id = str(fixture.get("observation_id") or "")
        observation = obs_by_id.get(observation_id)
        if observation is None:
            errors.append(f"{observation_id or '<missing>'} references unknown observation")
            continue
        if fixture.get("expected_status") != _projected_status(observation):
            errors.append(f"{observation_id} expected status does not match observation")
        if tuple(fixture.get("renderer_profiles_expected") or ()) != BASELINE_PROFILES:
            errors.append(f"{observation_id} must cover baseline profiles")
    return tuple(errors)


def validate_renderer_expected_outputs(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if tuple(payload.get("renderer_profiles") or ()) != BASELINE_PROFILES:
        errors.append("renderer profiles must match baseline profiles")
    expected = payload.get("expected_status_by_observation")
    if not isinstance(expected, Mapping):
        return tuple(errors + ["expected_status_by_observation must be present"])
    for observation in observation_records(observations or load_observations()):
        if expected.get(observation["observation_id"]) != _projected_status(observation):
            errors.append(f"{observation['observation_id']} expected status mismatch")
    return tuple(errors)


def project_observation(observation: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    run = _resolution_run_for_observation(observation)
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="resolution_run",
            entity_id=str(observation.get("observation_id") or "manual-observation"),
            payload=run,
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="manual-observation-batch-01",
        )
    )


def _validate_observation(item: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    item_id = str(item.get("observation_id") or "<missing>")
    for field in REQUIRED_OBSERVATION_FIELDS:
        if field not in item:
            errors.append(f"{item_id} missing {field}")
    if str(item.get("query_id") or "") not in REQUIRED_HARD_QUERY_IDS:
        errors.append(f"{item_id} has unknown query_id")
    if str(item.get("status_recommendation") or "") not in OBSERVATION_STATUS_RECOMMENDATIONS:
        errors.append(f"{item_id} has unsupported status recommendation")
    if _projected_status(item) not in CANONICAL_STATUSES:
        errors.append(f"{item_id} has unsupported projected status")
    if str(item.get("reviewability") or "") not in OBSERVATION_REVIEWABILITY:
        errors.append(f"{item_id} has unsupported reviewability")
    if str(item.get("source_quality") or "") not in SOURCE_QUALITY:
        errors.append(f"{item_id} has unsupported source quality")
    if item.get("reviewability") == "blocked_for_user_details":
        if _projected_status(item) != "need":
            errors.append(f"{item_id} blocked detail item must project as need")
    elif not str(item.get("source_url") or "").startswith("https://"):
        errors.append(f"{item_id} reviewable/manual source observation must include https source_url")
    quote = str(item.get("short_quote_if_needed") or "").strip()
    quote_count = len(quote.split()) if quote else 0
    if int(item.get("quote_word_count", -1)) != quote_count:
        errors.append(f"{item_id} quote_word_count mismatch")
    if quote_count > 25:
        errors.append(f"{item_id} quote exceeds 25 words")
    if not isinstance(item.get("manual_verification_steps"), list) or not item["manual_verification_steps"]:
        errors.append(f"{item_id} must include manual verification steps")
    for action in _strings(item.get("forbidden_actions_confirmed")):
        if action not in FORBIDDEN_PUBLIC_ACTIONS:
            errors.append(f"{item_id} has unknown forbidden action confirmation: {action}")
    public_actions = set(_strings(item.get("allowed_public_actions")))
    if not public_actions.issubset(PUBLIC_ALLOWED_ACTIONS):
        errors.append(f"{item_id} has unsafe public action")
    for flag in TRUTH_FLAGS:
        if item.get(flag) is not False:
            errors.append(f"{item_id} must keep {flag}=false")
    return tuple(errors)


def _resolution_run_for_observation(observation: Mapping[str, Any]) -> ResolutionRunRecord:
    observation_id = str(observation.get("observation_id") or "manual-observation")
    source_url = str(observation.get("source_url") or "")
    source_kind = str(observation.get("source_kind") or "")
    checked_source_ids = (source_url,) if source_url else ()
    checked_source_families = (source_kind,) if source_kind else ()
    return ResolutionRunRecord(
        run_id=f"run-{observation_id}",
        run_kind="manual_observation_batch_01_projection",
        requested_value=str(observation.get("query_id") or ""),
        status="completed",
        started_at="2026-06-05T00:00:00+00:00",
        completed_at="2026-06-05T00:00:00+00:00",
        checked_source_ids=checked_source_ids,
        checked_source_families=checked_source_families,
        fallback_summary=_fallback_summary(observation),
    )


def _fallback_summary(observation: Mapping[str, Any]) -> dict[str, Any]:
    status = _projected_status(observation)
    observation_id = str(observation.get("observation_id") or "manual-observation")
    title = str(observation.get("source_title") or observation_id)
    summary = {
        "schema_version": "manual_observation_batch_01_fallback_summary.v0",
        "mode": "manual_observation_batch_01",
        "status": status,
        "trigger": "manual_observation_projection",
        "query": str(observation.get("query_id") or ""),
        "source_id": str(observation.get("source_url") or "manual_followup"),
        "source_family": str(observation.get("source_kind") or "manual_observation"),
        "source_allowlisted": True,
        "fallback_enabled": True,
        "title": title,
        "evidence_summary": str(observation.get("evidence_summary") or ""),
        "reason_codes": _strings(observation.get("known_gaps")) + [str(observation.get("reviewability") or "")],
        "source_observation_refs": [f"manual_source_observation_batch_01:{observation_id}"],
        "evidence_refs": [f"manual_observation_batch_01:{observation_id}"],
        "source_observation": {"observation_id": f"manual_source_observation_batch_01:{observation_id}"},
        "operator_actions": _operator_actions(observation),
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
    if status in {"candidate", "near_miss", "mention_only"}:
        summary["candidate_count"] = 1
        summary["candidates"] = [
            {
                "candidate_id": f"candidate_{observation_id}",
                "status": status,
                "title": title,
                "summary": str(observation.get("evidence_summary") or ""),
                "verified": False,
                "accepted_truth": False,
                "public_actions": _strings(observation.get("allowed_public_actions")),
            }
        ]
    if status == "need":
        summary["need_count"] = 1
        summary["needs"] = [
            {
                "need_id": f"need_{observation_id}",
                "status": "need",
                "title": title,
                "summary": str(observation.get("evidence_summary") or ""),
                "verified": False,
                "accepted_truth": False,
                "public_actions": _strings(observation.get("allowed_public_actions")),
            }
        ]
    if status == "policy_blocked":
        summary["policy_block_reason"] = str(observation.get("evidence_summary") or "")
    if status in {"unknown", "unavailable"}:
        summary["unavailable_reason"] = "; ".join(_strings(observation.get("known_gaps")))
    return summary


def _operator_actions(observation: Mapping[str, Any]) -> list[str]:
    actions = ["review_candidate"]
    recommendation = str(observation.get("recommended_review_decision") or observation.get("status_recommendation") or "").strip()
    if recommendation and recommendation in REVIEW_DECISIONS:
        actions.append(recommendation)
    return list(dict.fromkeys(actions))


def _projected_status(observation: Mapping[str, Any]) -> str:
    value = str(observation.get("projected_status") or observation.get("status_recommendation") or "unknown").strip()
    return value if value in CANONICAL_STATUSES else "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []
