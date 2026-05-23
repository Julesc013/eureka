"""Local review decision service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from runtime.review.queue import ReviewDecision, ReviewDecisionKind

from .audit import build_review_audit_event
from .errors import LocalReviewDecisionError
from .validation import validate_decision_name, validate_local_only_confirmation, validate_reason


@dataclass(frozen=True)
class LocalReviewDecisionRequest:
    review_item_id: str
    decision: str
    reason: str | None = None
    operator_label: str = "local_operator"
    local_only_confirmed: bool = False
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LocalReviewDecisionResult:
    schema_version: str
    status: str
    review_item_id: str
    decision_id: str
    decision: str
    review_status: str
    audit_event: Mapping[str, Any]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "local review state only",
        "review decision does not directly rebuild the reviewed index",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "review_item_id": self.review_item_id,
            "decision_id": self.decision_id,
            "decision": self.decision,
            "review_status": self.review_status,
            "audit_event": dict(self.audit_event),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "review_decision_persisted": True,
            "public_index_mutated": False,
            "master_index_mutated": False,
        }


def validate_decision_request(request: LocalReviewDecisionRequest) -> LocalReviewDecisionRequest:
    if not str(request.review_item_id or "").strip():
        raise LocalReviewDecisionError("review item id is required")
    decision = validate_decision_name(request.decision)
    validate_reason(decision, request.reason)
    validate_local_only_confirmation(decision, request.local_only_confirmed)
    if not str(request.operator_label or "").strip():
        raise LocalReviewDecisionError("operator label is required")
    return request


def apply_local_review_decision(runtime: Any, request: LocalReviewDecisionRequest) -> LocalReviewDecisionResult:
    validate_decision_request(request)
    item = runtime.review_queue.get_review_item(request.review_item_id)
    if item is None:
        raise LocalReviewDecisionError("review item was not found")
    decision = ReviewDecision(
        review_item_id=request.review_item_id,
        decision_kind=_decision_kind(request.decision),
        decision_actor=request.operator_label,
        reason=validate_reason(request.decision, request.reason),
        payload={
            "local_only_confirmed": bool(request.local_only_confirmed),
            "decision_source": "localhost_operator",
            **dict(request.payload),
        },
        limitations=("local review state only", "separate rebuild is required for reviewed index projection"),
    )
    stored = runtime.review_queue.record_decision(request.review_item_id, decision)
    audit_event = build_review_audit_event(
        request.review_item_id,
        request.decision,
        request.operator_label,
        request.reason,
    )
    return LocalReviewDecisionResult(
        schema_version="local_review_decision_result.v0",
        status="pass",
        review_item_id=request.review_item_id,
        decision_id=str(stored.get("record_id", decision.decision_id)),
        decision=request.decision,
        review_status=str(stored.get("status", "")),
        audit_event=audit_event,
    )


def _decision_kind(value: str) -> ReviewDecisionKind:
    return {
        "accept": ReviewDecisionKind.ACCEPT,
        "reject": ReviewDecisionKind.REJECT,
        "block": ReviewDecisionKind.BLOCK,
        "request_more_evidence": ReviewDecisionKind.REQUEST_MORE_EVIDENCE,
        "note_only": ReviewDecisionKind.NOTE_ONLY,
    }[value]
