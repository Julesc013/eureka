"""Validation helpers for deterministic Search Hunt replay."""

from typing import Any, Mapping

from .errors import SearchHuntValidationError
from .replay_records import BLOCKED_REPLAY_STEP_KINDS, ENABLED_REPLAY_STEP_KINDS, HuntReplayFixture, HuntReplayRecord, HuntReplayResult


FORBIDDEN_REPLAY_TRUE_FLAGS = (
    "source_probe_executed",
    "extraction_executed",
    "external_network_used",
    "model_provider_used",
    "download_install_execute_performed",
    "master_index_mutated",
    "site_dist_mutated",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)

FORBIDDEN_REPLAY_CLAIMS = (
    "production ready",
    "public launch ready",
    "proves global absence",
    "exhausted internet",
    "accepted as truth",
    "rights cleared",
    "malware safe",
)


def validate_replay_fixture(fixture: HuntReplayFixture) -> HuntReplayFixture:
    if not fixture.hunt_id:
        raise SearchHuntValidationError("replay fixture requires a hunt id")
    if not fixture.query:
        raise SearchHuntValidationError("replay fixture requires a query")
    enabled = {item.kind for item in fixture.expected_steps}
    blocked = {item.kind for item in fixture.blocked_steps}
    missing = [item.value for item in ENABLED_REPLAY_STEP_KINDS if item not in enabled]
    missing_blocked = [item.value for item in BLOCKED_REPLAY_STEP_KINDS if item not in blocked]
    if missing:
        raise SearchHuntValidationError("replay fixture missing enabled steps: " + ", ".join(missing))
    if missing_blocked:
        raise SearchHuntValidationError("replay fixture missing blocked steps: " + ", ".join(missing_blocked))
    validate_no_forbidden_replay_side_effects(fixture.expected_outputs)
    validate_no_replay_truth_claims(fixture.to_dict())
    return fixture


def validate_replay_record(record: HuntReplayRecord) -> HuntReplayRecord:
    if not record.replay_id:
        raise SearchHuntValidationError("replay record requires replay_id")
    if not record.hunt_id:
        raise SearchHuntValidationError("replay record requires hunt_id")
    validate_no_forbidden_replay_side_effects(record.to_dict())
    validate_no_replay_truth_claims(record.to_dict())
    return record


def validate_replay_result(result: HuntReplayResult) -> HuntReplayResult:
    validate_replay_fixture(result.fixture)
    validate_replay_record(result.record)
    return result


def validate_no_forbidden_replay_side_effects(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in FORBIDDEN_REPLAY_TRUE_FLAGS:
        if payload.get(key) is True:
            raise SearchHuntValidationError(f"forbidden replay side effect flag set: {key}")
    return payload


def validate_no_replay_truth_claims(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    text = str(payload).lower()
    for claim in FORBIDDEN_REPLAY_CLAIMS:
        if claim in text:
            raise SearchHuntValidationError(f"forbidden replay claim: {claim}")
    return payload
