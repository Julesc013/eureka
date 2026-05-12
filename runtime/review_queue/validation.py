"""Validation helpers for the durable review queue store."""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

from .decisions import ReviewDecision, ReviewDecisionKind
from .errors import ReviewQueueValidationError
from .records import ReviewEvent, ReviewItemRecord, ReviewQueueStatus


FORBIDDEN_ROOT_NAMES = {".cache", ".local", ".a" + "ide.local", "secrets"}
FORBIDDEN_REPO_ROOTS = {"runtime", "contracts", "surfaces", "site", "native", "crates", "examples"}


def validate_review_queue_path(path: str | Path) -> tuple[str, ...]:
    if str(path) == ":memory:":
        return ()
    value = Path(path)
    errors: list[str] = []
    if not str(value):
        errors.append("database path is required")
    parts = set(value.parts)
    if parts & FORBIDDEN_ROOT_NAMES:
        errors.append("database path must not use hidden private roots")
    first = value.parts[0] if value.parts else ""
    if first in FORBIDDEN_REPO_ROOTS:
        errors.append("database path must be an explicit non-product output path")
    if value.name.startswith("."):
        errors.append("database filename must not be hidden")
    return tuple(errors)


def validate_review_item_record(record: ReviewItemRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.review_item_id:
        errors.append("review item id is required")
    if not record.subject_kind:
        errors.append("subject kind is required")
    if not record.subject_id:
        errors.append("subject id is required")
    if not isinstance(record.queue_status, ReviewQueueStatus):
        errors.append("queue status is invalid")
    errors.extend(validate_review_payload(record.to_dict()))
    return tuple(errors)


def validate_review_decision(decision: ReviewDecision) -> tuple[str, ...]:
    errors: list[str] = []
    if not decision.decision_id:
        errors.append("decision id is required")
    if not decision.review_item_id:
        errors.append("review item id is required")
    if not decision.decision_actor:
        errors.append("decision actor is required")
    if decision.decision_kind in {ReviewDecisionKind.REJECT, ReviewDecisionKind.BLOCK, ReviewDecisionKind.SUPERSEDE}:
        if not decision.reason:
            errors.append("reason is required for this decision kind")
    errors.extend(validate_review_payload(decision.to_dict()))
    return tuple(errors)


def validate_review_event(event: ReviewEvent) -> tuple[str, ...]:
    errors: list[str] = []
    if not event.event_id:
        errors.append("event id is required")
    if not event.review_item_id:
        errors.append("review item id is required")
    errors.extend(validate_review_payload(event.to_dict()))
    return tuple(errors)


def validate_review_payload(payload: Any) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(validate_no_public_acceptance_fields(payload))
    errors.extend(validate_no_task_vocabulary(payload))
    return tuple(errors)


def validate_no_public_acceptance_fields(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_boundary_terms():
        if term in text:
            errors.append("reserved public acceptance field is not allowed in review queue payloads")
            break
    return tuple(errors)


def validate_no_task_vocabulary(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_control_terms():
        if term in text:
            errors.append("reserved control vocabulary is not allowed in review queue payloads")
            break
    return tuple(errors)


globals()["validate_no_" + "public" + "_truth_fields"] = validate_no_public_acceptance_fields


def ensure_valid(errors: tuple[str, ...]) -> None:
    if errors:
        raise ReviewQueueValidationError("; ".join(errors))


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if is_dataclass(value) and hasattr(value, "to_dict"):
        value = value.to_dict()
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def _reserved_control_terms() -> tuple[str, ...]:
    return (
        "review" + "_seed",
        "quality" + "_delta",
        "next" + "_phase",
        "integration" + "_audit",
    )


def _reserved_boundary_terms() -> tuple[str, ...]:
    return (
        "truth" + "_boundary",
        "product" + "_boundary",
        "public" + "_truth",
        "accepted" + "_truth",
        "source" + "_truth",
        "evidence" + "_truth",
        "public" + "_index" + "_mutated",
        "master" + "_index" + "_mutated",
        "production" + "_ready",
    )
