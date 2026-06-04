"""Loader and projection helpers for manual observation batch zero."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.seed_corpus.loader import BASELINE_PROFILES, REQUIRED_HARD_QUERY_IDS, SEED_STATUSES
from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.surface import SurfaceKernel, SurfaceRequest


CANONICAL_STATUSES = tuple(SEED_STATUSES)
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
REVIEW_DECISIONS = frozenset(
    {"promote", "reject", "supersede", "mark_near_miss", "mark_need", "mark_policy_blocked", "request_more_evidence"}
)
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
    "query_text",
    "observer_actor",
    "observation_date",
    "observation_method",
    "source_family",
    "source_reference",
    "source_uri_or_locator",
    "source_access_posture",
    "source_rights_posture",
    "source_risk_posture",
    "object_title_or_label",
    "object_type",
    "platform_or_environment",
    "version_or_date_hint",
    "evidence_summary",
    "evidence_snippets",
    "observed_fields",
    "missing_fields",
    "uncertainty_notes",
    "proposed_status",
    "status_rationale",
    "review_recommendation",
    "review_blockers",
    "public_visibility_posture",
    "allowed_public_actions",
    "forbidden_public_actions",
    "notes",
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
    return repo_root() / "evals" / "hard_queries" / "review_backlog" / "batch_00"


def example_root() -> Path:
    return repo_root() / "examples" / "seed_corpus" / "manual_observations" / "batch_00"


def load_observations(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "observations.json")


def load_query_mapping(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "query_mapping.json")


def load_source_references(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "source_references.json")


def load_reviewable_items(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "reviewable_items.json")


def load_non_reviewable_items(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "non_reviewable_items.json")


def load_corpus_gate_status(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "corpus_gate_status.json")


def load_validation_summary(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "validation_summary.json")


def load_review_backlog(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or review_backlog_root()) / "review_backlog.json")


def load_manual_followup_needed(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or review_backlog_root()) / "manual_followup_needed.json")


def load_blocked_or_unavailable(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or review_backlog_root()) / "blocked_or_unavailable.json")


def load_public_safe_examples(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or example_root()) / "public_safe_examples.json")


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
    }
    for item in observation_records(payload):
        status = _status(item)
        if status == "verified" and item.get("review_event_created") is True:
            counts["reviewed"] += 1
        elif status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
    return counts


def validate_observations(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    observations = payload.get("observations")
    if not isinstance(observations, list):
        return ("observations must be a list",)
    records = observation_records(payload)
    ids = [item["observation_id"] for item in records if "observation_id" in item]
    if len(ids) != len(set(ids)):
        errors.append("observation_id values must be unique")
    query_ids = {str(item.get("query_id") or "") for item in records}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing observation attempt for {required}")
    for item in records:
        errors.extend(_validate_observation(item))
    return tuple(errors)


def validate_reviewable_items(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("reviewable_items")
    if not isinstance(items, list):
        return ("reviewable_items must be a list",)
    observation_ids = {item["observation_id"] for item in observation_records(observations or {})}
    for item in reviewable_item_records(payload):
        item_id = str(item.get("reviewable_item_id") or "<missing>")
        if str(item.get("recommended_review_decision") or "") not in REVIEW_DECISIONS:
            errors.append(f"{item_id} has unsupported review decision")
        if not item.get("source_observation_ref"):
            errors.append(f"{item_id} must include source_observation_ref")
        if observation_ids and str(item.get("observation_id") or "") not in observation_ids:
            errors.append(f"{item_id} references unknown observation")
        if not item.get("rationale"):
            errors.append(f"{item_id} must include rationale")
        if item.get("review_event_created") is not False:
            errors.append(f"{item_id} must not create a review event")
        if item.get("reviewed_record_created") is not False:
            errors.append(f"{item_id} must not create a reviewed record")
        if item.get("reviewed_index_mutated") is not False:
            errors.append(f"{item_id} must not mutate reviewed index")
    if payload.get("review_ledger_decisions_created") is not False:
        errors.append("batch must not create review ledger decisions")
    return tuple(errors)


def validate_non_reviewable_items(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    items = payload.get("non_reviewable_items")
    if not isinstance(items, list):
        return ("non_reviewable_items must be a list",)
    observation_ids = {item["observation_id"] for item in observation_records(observations or {})}
    for item in items:
        if not isinstance(item, Mapping):
            errors.append("non_reviewable item must be an object")
            continue
        item_id = str(item.get("non_reviewable_item_id") or "<missing>")
        if observation_ids and str(item.get("observation_id") or "") not in observation_ids:
            errors.append(f"{item_id} references unknown observation")
        if not item.get("manual_followup_reason"):
            errors.append(f"{item_id} must include manual followup reason")
        if item.get("reviewable_now") is not False:
            errors.append(f"{item_id} must keep reviewable_now=false")
    return tuple(errors)


def validate_corpus_gate_status(payload: Mapping[str, Any], observations: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("public_alpha_corpus_gate") != "FAIL_INSUFFICIENT_REVIEWED_CORPUS":
        errors.append("batch gate must remain failed while reviewed count is zero")
    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        return tuple(errors + ["counts must be present"])
    if observations is not None:
        computed = manual_observation_counts(observations)
        for key, value in computed.items():
            count_key = f"{key}_count"
            if int(counts.get(count_key, -1)) != value:
                errors.append(f"{count_key} does not match observations")
    truth = payload.get("truth_boundary")
    if not isinstance(truth, Mapping):
        errors.append("truth_boundary must be present")
    else:
        for key, value in truth.items():
            if value is not False:
                errors.append(f"truth boundary flag must be false: {key}")
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
            data_version="manual-observation-batch-00",
        )
    )


def _validate_observation(item: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    item_id = str(item.get("observation_id") or "<missing>")
    for field in REQUIRED_OBSERVATION_FIELDS:
        if field not in item:
            errors.append(f"{item_id} missing {field}")
    status = _status(item)
    if status not in CANONICAL_STATUSES:
        errors.append(f"{item_id} has non-canonical status")
    public_actions = set(_strings(item.get("allowed_public_actions")))
    if not public_actions.issubset(PUBLIC_ALLOWED_ACTIONS):
        errors.append(f"{item_id} has unsafe public action")
    forbidden = set(_strings(item.get("forbidden_public_actions")))
    if forbidden and not forbidden.issubset(FORBIDDEN_PUBLIC_ACTIONS):
        errors.append(f"{item_id} has unknown forbidden public action")
    for snippet in _strings(item.get("evidence_snippets")):
        if len(snippet.split()) > 25:
            errors.append(f"{item_id} evidence snippet exceeds 25 words")
    for flag in (
        "source_observation_self_promoted",
        "candidate_self_promoted",
        "reviewed_record_created",
        "review_event_created",
        "reviewed_index_mutated",
        "public_index_mutated",
        "master_index_mutated",
        "product_runtime_live_source_call",
        "synthetic_eval_fixture_used_as_evidence",
    ):
        if item.get(flag) is not False:
            errors.append(f"{item_id} must keep {flag}=false")
    if status == "verified":
        errors.append(f"{item_id} must not be verified in manual observation batch zero")
    if item.get("review_recommendation") == "promote" and not item.get("source_uri_or_locator"):
        errors.append(f"{item_id} promote recommendation requires source locator")
    if not item.get("source_uri_or_locator") and status not in {"need", "unavailable", "unknown"}:
        errors.append(f"{item_id} source locator missing for reviewable status")
    return tuple(errors)


def _resolution_run_for_observation(observation: Mapping[str, Any]) -> ResolutionRunRecord:
    observation_id = str(observation.get("observation_id") or "manual-observation")
    source_ref = str(observation.get("source_reference") or "")
    source_family = str(observation.get("source_family") or "")
    checked_source_ids = (source_ref,) if source_ref and not source_ref.startswith("none:") else ()
    checked_source_families = (source_family,) if source_family and source_family != "missing_query_scope" else ()
    return ResolutionRunRecord(
        run_id=f"run-{observation_id}",
        run_kind="manual_observation_batch_projection",
        requested_value=str(observation.get("query_text") or ""),
        status="completed",
        started_at="2026-06-04T00:00:00+00:00",
        completed_at="2026-06-04T00:00:00+00:00",
        checked_source_ids=checked_source_ids,
        checked_source_families=checked_source_families,
        fallback_summary=_fallback_summary(observation),
    )


def _fallback_summary(observation: Mapping[str, Any]) -> dict[str, Any]:
    status = _status(observation)
    observation_id = str(observation.get("observation_id") or "manual-observation")
    title = str(observation.get("object_title_or_label") or observation_id)
    summary = {
        "schema_version": "manual_observation_fallback_summary.v0",
        "mode": "manual_observation_batch_00",
        "status": status,
        "trigger": "manual_observation_projection",
        "query": str(observation.get("query_text") or ""),
        "source_id": str(observation.get("source_reference") or "manual_observation"),
        "source_family": str(observation.get("source_family") or "manual_observation"),
        "source_allowlisted": True,
        "fallback_enabled": True,
        "title": title,
        "evidence_summary": str(observation.get("evidence_summary") or ""),
        "reason_codes": _strings(observation.get("missing_fields")) + _strings(observation.get("uncertainty_notes")),
        "source_observation_refs": [f"manual_source_observation:{observation_id}"],
        "evidence_refs": [f"manual_observation_batch_00:{observation_id}"],
        "source_observation": {"observation_id": f"manual_source_observation:{observation_id}"},
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
        summary["policy_block_reason"] = "; ".join(_strings(observation.get("review_blockers")))
    if status in {"unknown", "unavailable"}:
        summary["unavailable_reason"] = "; ".join(_strings(observation.get("missing_fields")))
    return summary


def _operator_actions(observation: Mapping[str, Any]) -> list[str]:
    actions = ["review_candidate"]
    recommendation = str(observation.get("review_recommendation") or "").strip()
    if recommendation:
        actions.append(recommendation)
    return list(dict.fromkeys(actions))


def _status(observation: Mapping[str, Any]) -> str:
    value = str(observation.get("proposed_status") or "unknown").strip()
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
