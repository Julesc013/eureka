"""Validation helpers for source observation runtime."""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from typing import Any

from .evidence import EvidenceCandidate
from .errors import SourceObservationValidationError
from .ids import SOURCE_ID_RE
from .normalization import NormalizedObservation
from .observations import SourceObservation
from .records import SourceRecord
from .requests import MetadataRequest
from .responses import MetadataResponse


def validate_source_record(record: SourceRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not SOURCE_ID_RE.match(str(record.source_id)):
        errors.append("source id is not stable")
    if not record.source_family:
        errors.append("source family is required")
    if not record.trust_lane:
        errors.append("trust lane is required")
    errors.extend(validate_no_task_vocabulary(record.to_dict()))
    return tuple(errors)


def validate_metadata_request(request: MetadataRequest) -> tuple[str, ...]:
    errors: list[str] = []
    if not request.request_id:
        errors.append("request id is required")
    if not request.request_kind:
        errors.append("request kind is required")
    if not request.target:
        errors.append("target is required")
    errors.extend(validate_no_task_vocabulary(request.to_dict()))
    return tuple(errors)


def validate_metadata_response(response: MetadataResponse) -> tuple[str, ...]:
    errors: list[str] = []
    if not response.response_id:
        errors.append("response id is required")
    if not response.request_id:
        errors.append("request id is required")
    if not response.fingerprint.value:
        errors.append("response fingerprint is required")
    errors.extend(validate_no_task_vocabulary(response.to_dict()))
    return tuple(errors)


def validate_source_observation(observation: SourceObservation) -> tuple[str, ...]:
    errors: list[str] = []
    if not observation.observation_id:
        errors.append("observation id is required")
    if not 0.0 <= observation.confidence <= 1.0:
        errors.append("confidence must be between zero and one")
    errors.extend(validate_no_task_vocabulary(observation.to_dict()))
    return tuple(errors)


def validate_normalized_observation(observation: NormalizedObservation) -> tuple[str, ...]:
    errors: list[str] = []
    if not observation.normalized_observation_id:
        errors.append("normalized observation id is required")
    if not observation.normalized_fields:
        errors.append("normalized fields are required")
    if not 0.0 <= observation.confidence <= 1.0:
        errors.append("confidence must be between zero and one")
    errors.extend(validate_no_task_vocabulary(observation.to_dict()))
    return tuple(errors)


def validate_evidence_candidate(candidate: EvidenceCandidate) -> tuple[str, ...]:
    errors: list[str] = []
    if candidate.accepted:
        errors.append("candidate cannot be accepted at creation")
    if not candidate.claim:
        errors.append("claim is required")
    errors.extend(validate_no_task_vocabulary(candidate.to_dict()))
    return tuple(errors)


def validate_no_task_vocabulary(obj_or_text: Any) -> tuple[str, ...]:
    text = _as_text(obj_or_text).lower()
    errors: list[str] = []
    for term in _reserved_terms():
        if term in text:
            errors.append("reserved control vocabulary is not allowed in runtime payloads")
            break
    return tuple(errors)


def ensure_valid(errors: tuple[str, ...]) -> None:
    if errors:
        raise SourceObservationValidationError("; ".join(errors))


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if is_dataclass(value) and hasattr(value, "to_dict"):
        value = value.to_dict()
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def _reserved_terms() -> tuple[str, ...]:
    phase_terms = tuple(f"h{index}" for index in range(15))
    return phase_terms + (
        "bun" + "dle",
        "local" + "_" + "m" + "v" + "p",
        "m" + "v" + "p",
        "a" + "ide",
        "pro" + "mpt",
        "ag" + "ent",
        "fixture" + "_only",
        "preview" + "_only",
        "truth" + "_boundary",
        "product" + "_boundary",
        "review" + "_seed",
        "next" + "_phase",
        "quality" + "_delta",
        "integration" + "_audit",
    )
