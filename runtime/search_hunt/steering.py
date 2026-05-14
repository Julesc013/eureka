"""Steering preference records for local Search Hunt sessions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid

from .records import utc_now


class SearchHuntSteeringType(str, Enum):
    INCLUDE_SOURCE_FAMILY = "include_source_family"
    EXCLUDE_SOURCE_FAMILY = "exclude_source_family"
    PREFER_OFFICIAL_SOURCES = "prefer_official_sources"
    ALLOW_COMMUNITY_SOURCES = "allow_community_sources"
    METADATA_ONLY = "metadata_only"
    ALLOW_EXTRACTION_FUTURE = "allow_extraction_future"
    DISALLOW_EXTRACTION = "disallow_extraction"
    ALLOW_AI_ESCALATION_FUTURE = "allow_ai_escalation_future"
    DISALLOW_AI_ESCALATION = "disallow_ai_escalation"
    ADD_NOTE = "add_note"
    SET_PRIORITY = "set_priority"


@dataclass(frozen=True)
class SearchHuntSteeringPreference:
    id: str
    command_id: str
    hunt_id: str
    command_type: str
    value: str
    reason: str
    operator_label: str
    active: bool = True
    limitations: tuple[str, ...] = (
        "steering preference records operator intent only",
        "steering preference does not execute work",
    )
    warnings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @classmethod
    def new(
        cls,
        hunt_id: str,
        steering_type: SearchHuntSteeringType | str,
        *,
        command_id: str,
        value: str | None = None,
        reason: str | None = None,
        operator_label: str | None = None,
    ) -> "SearchHuntSteeringPreference":
        return cls(
            id="shp_" + uuid.uuid4().hex,
            command_id=command_id,
            hunt_id=str(hunt_id),
            command_type=steering_type_text(steering_type),
            value=str(value or ""),
            reason=str(reason or ""),
            operator_label=str(operator_label or "local_operator"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "steering_id": self.id,
            "command_id": self.command_id,
            "hunt_id": self.hunt_id,
            "command_type": self.command_type,
            "value": self.value,
            "reason": self.reason,
            "operator_label": self.operator_label,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active,
            "limitations": list(self.limitations),
            "warnings": list(self.warnings),
            "workunit_creation_performed": False,
            "source_probe_executed": False,
            "model_provider_used": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        }


def coerce_steering_type(value: SearchHuntSteeringType | str) -> SearchHuntSteeringType:
    return value if isinstance(value, SearchHuntSteeringType) else SearchHuntSteeringType(str(value))


def steering_type_text(value: SearchHuntSteeringType | str) -> str:
    return value.value if isinstance(value, SearchHuntSteeringType) else str(value)
