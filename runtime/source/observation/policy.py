"""Source policy and decision objects."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from .ids import canonical_json
from .records import SourceRecord


BLOCKED_OPERATIONS = (
    "live_network_request",
    "source_sync",
    "download",
    "upload",
    "execution",
    "private_source_access",
    "registry_mutation",
    "public_index_write",
)


class PolicyDecisionStatus(Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REQUIRES_REVIEW = "requires_review"
    NOT_EVALUABLE = "not_evaluable"


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    allowed_operations: tuple[str, ...] = ("metadata_observation",)
    blocked_operations: tuple[str, ...] = BLOCKED_OPERATIONS
    review_operations: tuple[str, ...] = ()
    required_trust_lanes: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_operations": list(self.allowed_operations),
            "blocked_operations": list(self.blocked_operations),
            "review_operations": list(self.review_operations),
            "required_trust_lanes": list(self.required_trust_lanes),
            "limitations": list(self.limitations),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourcePolicy":
        return cls(
            allowed_operations=tuple(str(item) for item in data.get("allowed_operations", []) or []),
            blocked_operations=tuple(str(item) for item in data.get("blocked_operations", []) or []),
            review_operations=tuple(str(item) for item in data.get("review_operations", []) or []),
            required_trust_lanes=tuple(str(item) for item in data.get("required_trust_lanes", []) or []),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "SourcePolicy":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    status: PolicyDecisionStatus
    requested_operation: str
    reason: str
    source_id: str = ""
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "requested_operation": self.requested_operation,
            "reason": self.reason,
            "source_id": self.source_id,
            "limitations": list(self.limitations),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PolicyDecision":
        return cls(
            status=PolicyDecisionStatus(str(data.get("status", PolicyDecisionStatus.NOT_EVALUABLE.value))),
            requested_operation=str(data.get("requested_operation", "")),
            reason=str(data.get("reason", "")),
            source_id=str(data.get("source_id", "")),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
        )


def evaluate_source_policy(
    record: SourceRecord,
    requested_operation: str,
    context: Mapping[str, Any] | None = None,
) -> PolicyDecision:
    policy = SourcePolicy()
    if context and isinstance(context.get("policy"), SourcePolicy):
        policy = context["policy"]

    if requested_operation in policy.blocked_operations:
        return PolicyDecision(
            status=PolicyDecisionStatus.BLOCKED,
            requested_operation=requested_operation,
            reason="operation is blocked by source policy",
            source_id=str(record.source_id),
            limitations=policy.limitations,
        )
    if policy.required_trust_lanes and record.trust_lane not in policy.required_trust_lanes:
        return PolicyDecision(
            status=PolicyDecisionStatus.REQUIRES_REVIEW,
            requested_operation=requested_operation,
            reason="source trust lane requires review before use",
            source_id=str(record.source_id),
            limitations=policy.limitations,
        )
    if requested_operation in policy.review_operations:
        return PolicyDecision(
            status=PolicyDecisionStatus.REQUIRES_REVIEW,
            requested_operation=requested_operation,
            reason="operation requires review by policy",
            source_id=str(record.source_id),
            limitations=policy.limitations,
        )
    if requested_operation in policy.allowed_operations:
        return PolicyDecision(
            status=PolicyDecisionStatus.ALLOWED,
            requested_operation=requested_operation,
            reason="operation is allowed for metadata observation",
            source_id=str(record.source_id),
            limitations=policy.limitations,
        )
    return PolicyDecision(
        status=PolicyDecisionStatus.NOT_EVALUABLE,
        requested_operation=requested_operation,
        reason="operation is not covered by this source policy",
        source_id=str(record.source_id),
        limitations=policy.limitations,
    )
