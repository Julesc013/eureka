"""Loader, validation, and projection helpers for human artifact review batch one."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries.artifact_record_gate.gate_00 import ARTIFACT_LEVELS
from runtime.surface import SurfaceKernel, SurfaceRequest


CANONICAL_DECISIONS = {
    "promote",
    "reject",
    "supersede",
    "mark_near_miss",
    "mark_need",
    "mark_policy_blocked",
    "request_more_evidence",
}
EXPECTED_REVIEW_COUNT = 6
EXPECTED_PROMOTE_COUNT = 2


def batch_root() -> Path:
    return Path(__file__).resolve().parent


def load_review_decisions(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_decisions.json")


def load_review_events(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_events.json")


def load_review_decision_backed_outcomes(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "review_decision_backed_outcomes.json")


def load_artifact_review_summary(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or batch_root()) / "artifact_review_summary.json")


def read_batch_text(name: str, root: Path | None = None) -> str:
    return ((root or batch_root()) / name).read_text(encoding="utf-8")


def review_decision_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("review_decisions") or [] if isinstance(item, Mapping))


def review_event_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("review_events") or [] if isinstance(item, Mapping))


def outcome_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(deepcopy(dict(item)) for item in payload.get("outcomes") or [] if isinstance(item, Mapping))


def validate_review_decisions(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = review_decision_records(payload)
    if len(records) != EXPECTED_REVIEW_COUNT:
        errors.append(f"must contain {EXPECTED_REVIEW_COUNT} review decisions")
    ids = [str(item.get("review_id") or "") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("review IDs must be unique")
    promote_count = 0
    for item in records:
        item_id = str(item.get("review_id") or "<missing>")
        decision = str(item.get("review_decision") or "")
        if decision not in CANONICAL_DECISIONS:
            errors.append(f"{item_id} has unsupported decision")
        if item.get("artifact_level") not in ARTIFACT_LEVELS:
            errors.append(f"{item_id} has unsupported artifact level")
        if not item.get("rationale"):
            errors.append(f"{item_id} missing rationale")
        if not item.get("evidence_refs"):
            errors.append(f"{item_id} missing evidence refs")
        if decision == "promote":
            promote_count += 1
            if not item.get("reviewed_artifact_record_id"):
                errors.append(f"{item_id} promote decision must link reviewed artifact record")
            if item.get("artifact_level") not in {"artifact_level_3_artifact_identity_evidence", "artifact_level_4_artifact_integrity_evidence"}:
                errors.append(f"{item_id} promote decision must be level 3 or 4")
        elif item.get("reviewed_artifact_record_id"):
            errors.append(f"{item_id} non-promote must not link reviewed artifact record")
        if item.get("verified_artifact_created") is not False:
            errors.append(f"{item_id} must not create verified artifact")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if item.get(flag) is not False:
                errors.append(f"{item_id} must keep {flag}=false")
    if promote_count != EXPECTED_PROMOTE_COUNT:
        errors.append(f"promote count must be {EXPECTED_PROMOTE_COUNT}")
    return tuple(errors)


def validate_review_events(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    records = review_event_records(payload)
    if len(records) != EXPECTED_REVIEW_COUNT:
        errors.append(f"must contain {EXPECTED_REVIEW_COUNT} review events")
    decision_ids = {item["review_id"] for item in review_decision_records(decisions or load_review_decisions())}
    for item in records:
        event_id = str(item.get("review_event_id") or "<missing>")
        if item.get("review_id") not in decision_ids:
            errors.append(f"{event_id} references unknown decision")
        if item.get("created_verified_artifact") is not False:
            errors.append(f"{event_id} must not create verified artifact")
        for flag in ("reviewed_index_mutated", "public_index_mutated", "master_index_mutated"):
            if item.get(flag) is not False:
                errors.append(f"{event_id} must keep {flag}=false")
    return tuple(errors)


def validate_review_decision_backed_outcomes(payload: Mapping[str, Any], decisions: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    errors: list[str] = []
    records = outcome_records(payload)
    if len(records) != EXPECTED_REVIEW_COUNT:
        errors.append(f"must contain {EXPECTED_REVIEW_COUNT} review-backed outcomes")
    decision_by_id = {item["review_id"]: item for item in review_decision_records(decisions or load_review_decisions())}
    promote_count = 0
    for item in records:
        outcome_id = str(item.get("outcome_id") or "<missing>")
        decision = decision_by_id.get(item.get("review_id"))
        if decision is None:
            errors.append(f"{outcome_id} references unknown decision")
            continue
        if item.get("decision") != decision.get("review_decision"):
            errors.append(f"{outcome_id} decision mismatch")
        if item.get("verified_artifact_created") is not False:
            errors.append(f"{outcome_id} must not create verified artifact")
        if item.get("reviewed_artifact_record_created") is True:
            promote_count += 1
            if item.get("decision") != "promote":
                errors.append(f"{outcome_id} non-promote cannot create reviewed artifact record")
            if not item.get("reviewed_artifact_record_id"):
                errors.append(f"{outcome_id} promoted outcome must link reviewed artifact record")
        elif item.get("reviewed_artifact_record_id"):
            errors.append(f"{outcome_id} non-created outcome must not link reviewed artifact record")
    if promote_count != EXPECTED_PROMOTE_COUNT:
        errors.append(f"outcome promote count must be {EXPECTED_PROMOTE_COUNT}")
    return tuple(errors)


def validate_artifact_review_summary(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "artifact_observations_reviewed": 6,
        "reviewable_items_reviewed": 6,
        "new_reviewed_artifact_record_count": 2,
        "cumulative_reviewed_artifact_record_count": 4,
        "verified_artifact_count": 0,
    }
    for key, value in expected.items():
        if int(payload.get(key, -1)) != value:
            errors.append(f"{key} must be {value}")
    counts = payload.get("decision_counts")
    if not isinstance(counts, Mapping):
        errors.append("decision_counts missing")
    else:
        for key, value in {"promote": 2, "request_more_evidence": 3, "mark_near_miss": 1}.items():
            if int(counts.get(key, -1)) != value:
                errors.append(f"{key} count must be {value}")
    if payload.get("public_alpha_artifact_gate") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("artifact gate must remain failed")
    if payload.get("next_recommended_task") != "REVIEWED-ARTIFACT-RECORD-GATE-02":
        errors.append("next recommended task must be REVIEWED-ARTIFACT-RECORD-GATE-02")
    return tuple(errors)


def project_review_outcome(outcome: Mapping[str, Any], profile: str, *, visibility_posture: str = "public") -> dict[str, Any]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="object",
            entity_id=str(outcome.get("reviewed_artifact_record_id") or outcome.get("outcome_id") or "artifact-review-outcome"),
            payload=_view_payload(outcome),
            requested_profile=profile,
            visibility_posture=visibility_posture,
            data_version="human-artifact-review-batch-01",
        )
    )


def _view_payload(outcome: Mapping[str, Any]) -> dict[str, Any]:
    status = str(outcome.get("outcome_status") or "unknown")
    return {
        "schema_version": "human_artifact_review_outcome_view.v0",
        "id": str(outcome.get("reviewed_artifact_record_id") or outcome.get("outcome_id") or "artifact-review-outcome"),
        "title": str(outcome.get("title") or outcome.get("outcome_id") or "Artifact review outcome"),
        "summary": str(outcome.get("public_summary") or outcome.get("reason") or ""),
        "status": status,
        "artifact_claim_status": str(outcome.get("artifact_claim_status") or "artifact_review_outcome"),
        "verified_artifact": False,
        "review_decision_id": str(outcome.get("review_id") or ""),
        "known_gaps": _strings(outcome.get("known_gaps")),
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


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
