"""Validation helpers for the durable evidence ledger store."""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

from .errors import EvidenceLedgerValidationError
from .records import EvidenceCandidateRecord, EvidenceConflict, EvidenceEvent, EvidenceReviewStatus


FORBIDDEN_ROOT_NAMES = {".cache", ".local", ".a" + "ide.local", "secrets"}
FORBIDDEN_REPO_ROOTS = {"runtime", "contracts", "surfaces", "site", "native", "crates", "examples"}


def validate_evidence_ledger_path(path: str | Path) -> tuple[str, ...]:
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


def validate_evidence_candidate_record(record: EvidenceCandidateRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.evidence_id:
        errors.append("evidence id is required")
    if not record.source_id:
        errors.append("source id is required")
    if not record.claim_kind:
        errors.append("claim kind is required")
    if not isinstance(record.status, EvidenceReviewStatus):
        errors.append("status is invalid")
    errors.extend(validate_evidence_payload(record.to_dict()))
    return tuple(errors)


def validate_evidence_event(event: EvidenceEvent) -> tuple[str, ...]:
    errors: list[str] = []
    if not event.event_id:
        errors.append("event id is required")
    if not event.evidence_id:
        errors.append("evidence id is required")
    errors.extend(validate_evidence_payload(event.to_dict()))
    return tuple(errors)


def validate_evidence_conflict(conflict: EvidenceConflict) -> tuple[str, ...]:
    errors: list[str] = []
    if not conflict.conflict_id:
        errors.append("conflict id is required")
    if not conflict.evidence_id:
        errors.append("evidence id is required")
    if not conflict.conflict_kind:
        errors.append("conflict kind is required")
    errors.extend(validate_evidence_payload(conflict.to_dict()))
    return tuple(errors)


def validate_evidence_payload(payload: Any) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(validate_no_public_truth_fields(payload))
    errors.extend(validate_no_task_vocabulary(payload))
    return tuple(errors)


def validate_no_public_truth_fields(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_boundary_terms():
        if term in text:
            errors.append("reserved public acceptance field is not allowed in evidence ledger payloads")
            break
    return tuple(errors)


def validate_no_task_vocabulary(payload: Any) -> tuple[str, ...]:
    text = _as_text(payload).lower()
    errors: list[str] = []
    for term in _reserved_control_terms():
        if term in text:
            errors.append("reserved control vocabulary is not allowed in evidence ledger payloads")
            break
    return tuple(errors)


def ensure_valid(errors: tuple[str, ...]) -> None:
    if errors:
        raise EvidenceLedgerValidationError("; ".join(errors))


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
        "accepted" + "_truth",
        "source" + "_truth",
        "evidence" + "_truth",
        "public" + "_index" + "_mutated",
        "master" + "_index" + "_mutated",
    )
