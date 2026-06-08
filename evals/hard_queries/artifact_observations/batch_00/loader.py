"""Loader, validation, and projection helpers for manual artifact observations."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.artifact_record_gate.gate_00 import ARTIFACT_LEVELS
from evals.hard_queries.seed_corpus.loader import BASELINE_PROFILES, REQUIRED_HARD_QUERY_IDS, SEED_STATUSES
from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.surface import SurfaceKernel, SurfaceRequest


CANONICAL_STATUSES = tuple(SEED_STATUSES)
REVIEW_RECOMMENDATIONS = frozenset(
    {"review_candidate", "request_more_evidence", "mark_need", "mark_near_miss", "blocked_for_user_details"}
)
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
FORBIDDEN_PUBLIC_ACTIONS = frozenset(
    {
        "review_candidate",
        "promote",
        "reject",
        "request_more_evidence",
        "rebuild_index",
        "download",
        "install",
        "launch_emulator",
        "crawl_source",
        "arbitrary_live_lookup",
    }
)
TRUTH_FLAGS = (
    "reviewed_artifact_records_created",
    "verified_artifacts_created",
    "review_events_created",
    "reviewed_index_mutated",
    "public_index_mutated",
    "master_index_mutated",
    "runtime_source_calls_performed",
    "downloads_performed",
    "file_fetches_performed",
    "wayback_replay_performed",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "synthetic_eval_fixtures_used_as_evidence",
)


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_artifact_observations(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "artifact_observations.json")


def load_query_mapping(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_mapping.json")


def load_reviewable_artifact_items(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewable_artifact_items.json")


def load_evidence_level_summary(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "evidence_level_summary.json")


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "public_alpha_artifact_gate.json")


def load_source_reference_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_reference_index.json")


def load_surface_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "surface_projection_fixtures.json")


def load_renderer_expected_outputs(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "renderer_expected_outputs.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def observation_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("observations") or [] if isinstance(item, Mapping))


def reviewable_item_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("reviewable_artifact_items") or [] if isinstance(item, Mapping))


def source_reference_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("source_references") or [] if isinstance(item, Mapping))


def artifact_level_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {level: 0 for level in ARTIFACT_LEVELS}
    for observation in observation_records(payload):
        counts[artifact_level_for_observation(observation)] += 1
    return counts


def status_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    counts = {status: 0 for status in ("candidate", "need", "near_miss", "unavailable", "unknown")}
    for observation in observation_records(payload):
        status = _projected_status(observation)
        counts[status if status in counts else "unknown"] += 1
    return counts


def validation_truth_flags(payload: Mapping[str, Any]) -> dict[str, bool]:
    boundary = payload.get("batch_truth_boundary") or {}
    return {flag: boundary.get(flag) is not False for flag in TRUTH_FLAGS}


def validate_artifact_observations(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = observation_records(payload)
    if len(records) != 11:
        errors.append("batch must contain 11 manual artifact observations")
    ids = [str(item.get("observation_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("observation IDs must be unique")
    query_ids = {str(item.get("query_id") or "") for item in records}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing hard query observation: {required}")
    for flag, value in validation_truth_flags(payload).items():
        if value:
            errors.append(f"truth boundary flag must be false: {flag}")
    for item in records:
        errors.extend(_validate_observation(item))
    return tuple(errors)


def validate_query_mapping(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    maps = payload.get("query_maps")
    if not isinstance(maps, list):
        return ("query_maps must be a list",)
    observation_ids = {item["observation_id"] for item in observation_records(observations or load_artifact_observations())}
    query_ids = {str(item.get("query_id") or "") for item in maps if isinstance(item, Mapping)}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing query map for {required}")
    for item in maps:
        if not isinstance(item, Mapping):
            errors.append("query map item must be object")
            continue
        query_id = str(item.get("query_id") or "<missing>")
        for observation_id in _strings(item.get("observation_ids")):
            if observation_id not in observation_ids:
                errors.append(f"{query_id} references unknown observation {observation_id}")
        if item.get("public_alpha_artifact_readiness") not in {"not_ready", "blocked_for_user_details"}:
            errors.append(f"{query_id} must not be public-alpha ready")
    return tuple(errors)


def validate_reviewable_artifact_items(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    records = reviewable_item_records(payload)
    if len(records) != 10:
        errors.append("batch must contain 10 reviewable artifact items")
    observation_ids = {item["observation_id"] for item in observation_records(observations or load_artifact_observations())}
    if payload.get("review_ledger_decisions_created") is not False:
        errors.append("review ledger decisions must not be created")
    if payload.get("reviewed_artifact_records_created") is not False:
        errors.append("reviewed artifact records must not be created")
    for item in records:
        item_id = str(item.get("review_item_id") or "<missing>")
        if item.get("artifact_level") not in ARTIFACT_LEVELS:
            errors.append(f"{item_id} has unsupported artifact level")
        if item.get("proposed_decision") not in REVIEW_RECOMMENDATIONS:
            errors.append(f"{item_id} has unsupported proposed decision")
        for observation_id in _strings(item.get("source_observation_ids")):
            if observation_id not in observation_ids:
                errors.append(f"{item_id} references unknown observation {observation_id}")
        for flag in ("review_event_created", "reviewed_artifact_record_created", "reviewed_index_mutated"):
            if item.get(flag) is not False:
                errors.append(f"{item_id} must keep {flag}=false")
    return tuple(errors)


def validate_evidence_level_summary(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    obs_payload = observations or load_artifact_observations()
    expected_levels = artifact_level_counts(obs_payload)
    expected_statuses = status_counts(obs_payload)
    level_counts = payload.get("artifact_level_counts")
    status_count_payload = payload.get("status_counts")
    if not isinstance(level_counts, Mapping) or not isinstance(status_count_payload, Mapping):
        return ("level and status counts must be present",)
    for key, value in expected_levels.items():
        if int(level_counts.get(key, -1)) != value:
            errors.append(f"{key} count mismatch")
    for key, value in expected_statuses.items():
        if int(status_count_payload.get(key, -1)) != value:
            errors.append(f"{key} status count mismatch")
    if int(payload.get("reviewed_artifact_record_count", -1)) != 0:
        errors.append("reviewed_artifact_record_count must be 0")
    if int(payload.get("verified_artifact_count", -1)) != 0:
        errors.append("verified_artifact_count must be 0")
    return tuple(errors)


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("status") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("public alpha artifact gate must remain failed")
    expected = {
        "reviewed_artifact_record_count": 0,
        "verified_artifact_count": 0,
        "manual_artifact_observation_count": 11,
        "reviewable_artifact_item_count": 10,
    }
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    if payload.get("public_alpha_blocked") is not True:
        errors.append("public alpha must remain blocked")
    if payload.get("dev_to_main_blocked") is not True:
        errors.append("dev to main must remain blocked")
    if payload.get("next_recommended_task") != "HUMAN-ARTIFACT-REVIEW-BATCH-00":
        errors.append("next task must be HUMAN-ARTIFACT-REVIEW-BATCH-00")
    return tuple(errors)


def validate_source_reference_index(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    refs = source_reference_records(payload)
    if len(refs) != 11:
        errors.append("source reference index must contain 11 manual references")
    for item in refs:
        source_id = str(item.get("source_id") or "<missing>")
        if item.get("manual_reference_only") is not True:
            errors.append(f"{source_id} must be manual_reference_only")
        for flag in ("runtime_source_call_performed", "download_performed", "file_fetch_performed", "wayback_replay_performed"):
            if item.get(flag) is not False:
                errors.append(f"{source_id} must keep {flag}=false")
    return tuple(errors)


def validate_surface_projection_fixtures(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        return ("fixtures must be a list",)
    obs_by_id = {item["observation_id"]: item for item in observation_records(observations or load_artifact_observations())}
    for fixture in fixtures:
        if not isinstance(fixture, Mapping):
            errors.append("fixture must be object")
            continue
        observation_id = str(fixture.get("observation_id") or "")
        observation = obs_by_id.get(observation_id)
        if observation is None:
            errors.append(f"{observation_id or '<missing>'} references unknown observation")
            continue
        if fixture.get("expected_status") != _projected_status(observation):
            errors.append(f"{observation_id} expected status mismatch")
        if fixture.get("expected_artifact_level") != artifact_level_for_observation(observation):
            errors.append(f"{observation_id} expected artifact level mismatch")
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
    for observation in observation_records(observations or load_artifact_observations()):
        if expected.get(observation["observation_id"]) != _projected_status(observation):
            errors.append(f"{observation['observation_id']} expected status mismatch")
    return tuple(errors)


def project_artifact_observation(observation: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="resolution_run",
            entity_id=str(observation.get("observation_id") or "artifact-observation"),
            payload=_resolution_run_for_observation(observation),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="manual-artifact-observation-batch-00",
        )
    )


def artifact_level_for_observation(observation: Mapping[str, Any]) -> str:
    level = str(observation.get("artifact_level") or "")
    return level if level in ARTIFACT_LEVELS else ARTIFACT_LEVELS[0]


def _validate_observation(item: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    item_id = str(item.get("observation_id") or "<missing>")
    for field in (
        "observation_id",
        "query_id",
        "artifact_subject",
        "observation_kind",
        "artifact_level",
        "status",
        "source_refs",
        "observed_claims",
        "artifact_identity_fields",
        "missing_for_reviewed_artifact_record",
        "rights_risk_posture",
        "review_recommendation",
        "public_projection_status",
    ):
        if field not in item:
            errors.append(f"{item_id} missing {field}")
    if str(item.get("query_id") or "") not in REQUIRED_HARD_QUERY_IDS:
        errors.append(f"{item_id} has unknown query_id")
    if item.get("artifact_level") not in ARTIFACT_LEVELS:
        errors.append(f"{item_id} has unsupported artifact level")
    if _projected_status(item) not in CANONICAL_STATUSES:
        errors.append(f"{item_id} has unsupported public projection status")
    if item.get("review_recommendation") not in REVIEW_RECOMMENDATIONS:
        errors.append(f"{item_id} has unsupported review recommendation")
    if item.get("manual_reference_only") is not True:
        errors.append(f"{item_id} must be manual_reference_only")
    for flag in ("runtime_source_call_performed", "reviewed_artifact_record_created", "verified_artifact_created"):
        if item.get(flag) is not False:
            errors.append(f"{item_id} must keep {flag}=false")
    posture = item.get("rights_risk_posture") or {}
    for flag in ("rights_clearance_claimed", "malware_safety_claimed", "download_offered"):
        if posture.get(flag) is not False:
            errors.append(f"{item_id} must keep {flag}=false")
    for ref in item.get("source_refs") or []:
        if not isinstance(ref, Mapping):
            errors.append(f"{item_id} source ref must be object")
            continue
        if ref.get("manual_reference_only") is not True:
            errors.append(f"{item_id} source ref must be manual_reference_only")
    if item.get("query_id") == "hq_driver_win98" and item.get("unsafe_to_recommend_random_driver") is not True:
        errors.append("Windows 98 driver observation must stay unsafe_to_recommend_random_driver=true")
    return tuple(errors)


def _resolution_run_for_observation(observation: Mapping[str, Any]) -> ResolutionRunRecord:
    refs = observation.get("source_refs") or []
    source_ids = tuple(str(ref.get("source_id") or "") for ref in refs if isinstance(ref, Mapping) and ref.get("source_id"))
    source_types = tuple(str(ref.get("source_type") or "") for ref in refs if isinstance(ref, Mapping) and ref.get("source_type"))
    return ResolutionRunRecord(
        run_id=f"run-{observation.get('observation_id', 'artifact-observation')}",
        run_kind="manual_artifact_observation_batch_00_projection",
        requested_value=str(observation.get("query_text") or observation.get("query_id") or ""),
        status="completed",
        started_at="2026-06-09T00:00:00+00:00",
        completed_at="2026-06-09T00:00:00+00:00",
        checked_source_ids=source_ids,
        checked_source_families=source_types,
        fallback_summary=_fallback_summary(observation),
    )


def _fallback_summary(observation: Mapping[str, Any]) -> dict[str, Any]:
    observation_id = str(observation.get("observation_id") or "artifact-observation")
    status = _projected_status(observation)
    summary = {
        "schema_version": "manual_artifact_observation_batch_00_fallback_summary.v0",
        "mode": "manual_artifact_observation_batch_00",
        "status": status,
        "trigger": "manual_artifact_observation_projection",
        "query": str(observation.get("query_text") or observation.get("query_id") or ""),
        "title": str(observation.get("artifact_subject") or observation_id),
        "artifact_level": artifact_level_for_observation(observation),
        "review_posture": _public_review_posture(observation),
        "source_observation_refs": [f"manual_artifact_observation_batch_00:{observation_id}"],
        "evidence_refs": [f"manual_artifact_observation_batch_00:{observation_id}"],
        "reason_codes": _public_reason_codes(observation),
        "operator_actions": _operator_actions(observation),
        "candidate_count": 0,
        "candidates": [],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "reviewed_artifact_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "live_source_calls": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
    }
    unit = {
        "id": f"artifact_unit_{observation_id}",
        "status": status,
        "title": str(observation.get("artifact_subject") or observation_id),
        "summary": str((observation.get("observed_claims") or [{}])[0].get("claim") or ""),
        "artifact_level": artifact_level_for_observation(observation),
        "verified": False,
        "accepted_truth": False,
        "public_actions": ["view", "inspect_evidence", "cite"],
    }
    if status in {"candidate", "near_miss", "mention_only"}:
        summary["candidate_count"] = 1
        summary["candidates"] = [unit]
    elif status == "need":
        summary["need_count"] = 1
        summary["needs"] = [unit]
    else:
        summary["unavailable_reason"] = "; ".join(summary["reason_codes"])
    return summary


def _operator_actions(observation: Mapping[str, Any]) -> list[str]:
    recommendation = str(observation.get("review_recommendation") or "")
    actions = ["review_candidate"]
    if recommendation and recommendation != "blocked_for_user_details":
        actions.append(recommendation)
    return list(dict.fromkeys(actions))


def _public_reason_codes(observation: Mapping[str, Any]) -> list[str]:
    codes = [artifact_level_for_observation(observation)]
    replacements = {
        "download_or_acquisition_path_not_checked": "acquisition_path_not_checked",
        "license_and_safety_not_reviewed": "license_and_safety_posture_not_reviewed",
    }
    for value in _strings(observation.get("missing_for_reviewed_artifact_record")):
        safe_value = replacements.get(value, value)
        if any(action in safe_value for action in {"download", "install", "crawl"}):
            safe_value = "restricted_action_not_performed"
        codes.append(safe_value)
    return list(dict.fromkeys(codes))


def _public_review_posture(observation: Mapping[str, Any]) -> str:
    recommendation = str(observation.get("review_recommendation") or "")
    return {
        "review_candidate": "human_review_ready",
        "request_more_evidence": "needs_more_evidence",
        "mark_need": "needs_more_evidence",
        "mark_near_miss": "near_miss_review",
        "blocked_for_user_details": "blocked_for_user_details",
    }.get(recommendation, "needs_review")


def _projected_status(observation: Mapping[str, Any]) -> str:
    value = str(observation.get("public_projection_status") or observation.get("status") or "unknown")
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
