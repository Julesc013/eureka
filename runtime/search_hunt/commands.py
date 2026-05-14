"""Operator command records for local Search Hunt sessions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
import uuid

from .records import SearchHuntState, coerce_state, utc_now


class SearchHuntCommandType(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    BLOCK = "block"
    WAIT_FOR_USER = "wait_for_user"
    WAIT_FOR_POLICY = "wait_for_policy"
    COMPLETE = "complete"
    FAIL = "fail"
    REMOVE_STEERING = "remove_steering_preference"


STATE_COMMAND_TARGETS: dict[SearchHuntCommandType, SearchHuntState] = {
    SearchHuntCommandType.PAUSE: SearchHuntState.PAUSED,
    SearchHuntCommandType.RESUME: SearchHuntState.RUNNING,
    SearchHuntCommandType.CANCEL: SearchHuntState.CANCELLED,
    SearchHuntCommandType.BLOCK: SearchHuntState.BLOCKED,
    SearchHuntCommandType.WAIT_FOR_USER: SearchHuntState.WAITING_FOR_USER,
    SearchHuntCommandType.WAIT_FOR_POLICY: SearchHuntState.WAITING_FOR_POLICY,
    SearchHuntCommandType.COMPLETE: SearchHuntState.COMPLETE,
    SearchHuntCommandType.FAIL: SearchHuntState.FAILED,
}

REASON_REQUIRED_COMMANDS = {
    SearchHuntCommandType.BLOCK,
    SearchHuntCommandType.FAIL,
}


@dataclass(frozen=True)
class SearchHuntCommand:
    command_id: str
    hunt_id: str
    command_type: str
    previous_state: str
    resulting_state: str
    operator_label: str
    reason: str
    policy_decision: str
    side_effects: Mapping[str, Any]
    value: str | None = None
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(
        cls,
        hunt_id: str,
        command_type: SearchHuntCommandType | str,
        *,
        previous_state: SearchHuntState | str | None = None,
        resulting_state: SearchHuntState | str | None = None,
        operator_label: str | None = None,
        reason: str | None = None,
        policy_decision: str = "allowed_local_operator_command",
        value: str | None = None,
        side_effects: Mapping[str, Any] | None = None,
    ) -> "SearchHuntCommand":
        return cls(
            command_id="shc_" + uuid.uuid4().hex,
            hunt_id=str(hunt_id),
            command_type=command_type_text(command_type),
            previous_state=state_text(previous_state),
            resulting_state=state_text(resulting_state),
            operator_label=str(operator_label or "local_operator"),
            reason=str(reason or ""),
            policy_decision=str(policy_decision),
            value=value,
            side_effects=dict(side_effects or default_command_side_effects()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "hunt_id": self.hunt_id,
            "command_type": self.command_type,
            "value": self.value,
            "reason": self.reason,
            "operator_label": self.operator_label,
            "previous_state": self.previous_state,
            "resulting_state": self.resulting_state,
            "policy_decision": self.policy_decision,
            "created_at": self.created_at,
            "side_effects": dict(self.side_effects),
        }


@dataclass(frozen=True)
class SearchHuntCommandResult:
    command: SearchHuntCommand
    hunt: Mapping[str, Any] | None
    status: str = "pass"
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "command mutates local hunt state only",
        "command does not execute investigation work",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "search_hunt_command_result_payload.v0",
            "status": self.status,
            "command": self.command.to_dict(),
            "hunt": dict(self.hunt or {}),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "workunit_creation_performed": False,
            "source_probe_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


def coerce_command_type(value: SearchHuntCommandType | str) -> SearchHuntCommandType:
    return value if isinstance(value, SearchHuntCommandType) else SearchHuntCommandType(str(value))


def command_type_text(value: SearchHuntCommandType | str) -> str:
    return value.value if isinstance(value, SearchHuntCommandType) else str(value)


def target_state_for_command(value: SearchHuntCommandType | str) -> SearchHuntState:
    return STATE_COMMAND_TARGETS[coerce_command_type(value)]


def command_requires_reason(value: SearchHuntCommandType | str) -> bool:
    return coerce_command_type(value) in REASON_REQUIRED_COMMANDS


def default_command_side_effects() -> dict[str, bool]:
    return {
        "hunt_state_mutated": False,
        "hunt_command_history_mutated": True,
        "hunt_steering_mutated": False,
        "workunit_created": False,
        "source_probe_executed": False,
        "extraction_executed": False,
        "external_network_used": False,
        "model_provider_used": False,
        "review_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "deployment_performed": False,
    }


def state_text(value: SearchHuntState | str | None) -> str:
    if value is None:
        return ""
    return coerce_state(value).value
