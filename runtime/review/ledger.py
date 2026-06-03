"""Review ledger boundary over durable review queue state."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from runtime.review.queue import (
    ReviewDecision,
    ReviewDecisionKind,
    ReviewEvent,
    ReviewEventKind,
    ReviewItemRecord,
    ReviewQueueStatus,
    ReviewQueueStore,
)
from runtime.review.queue.records import canonical_json, utc_now


REVIEW_LEDGER_DECISIONS = (
    "promote",
    "reject",
    "supersede",
    "mark_near_miss",
    "mark_need",
    "mark_policy_blocked",
    "request_more_evidence",
)


@dataclass(frozen=True)
class ReviewLedgerDecisionRequest:
    review_item_id: str
    decision: str
    actor: str
    reason: str | None = None
    evidence_refs: tuple[str, ...] = ()
    source_observation_refs: tuple[str, ...] = ()
    absence_refs: tuple[str, ...] = ()
    fallback_refs: tuple[str, ...] = ()
    visibility_posture: str = "operator_private"
    supersedes_review_item_id: str | None = None
    local_only_confirmed: bool = False


@dataclass(frozen=True)
class ReviewLedgerDecisionResult:
    schema_version: str
    status: str
    review_item_id: str
    decision_id: str
    review_event_id: str
    decision: str
    queue_status: str
    resulting_status: str
    review_item: Mapping[str, Any]
    review_event: Mapping[str, Any]
    reviewed_record_created: bool = False
    reviewed_index_mutated: bool = False
    public_index_mutated: bool = False
    master_index_mutated: bool = False
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "review event records decision state only",
        "reviewed index rebuild is a separate explicit operation",
        "public projection is read-only",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "review_item_id": self.review_item_id,
            "decision_id": self.decision_id,
            "review_event_id": self.review_event_id,
            "decision": self.decision,
            "queue_status": self.queue_status,
            "resulting_status": self.resulting_status,
            "review_item": dict(self.review_item),
            "review_event": dict(self.review_event),
            "review_event_recorded": True,
            "review_decision_persisted": True,
            "reviewed_record_created": self.reviewed_record_created,
            "reviewed_index_mutated": self.reviewed_index_mutated,
            "public_index_mutated": self.public_index_mutated,
            "master_index_mutated": self.master_index_mutated,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


class ReviewLedgerError(ValueError):
    """Raised when a review ledger request violates review boundary rules."""


def build_review_item_from_fallback_summary(
    fallback_summary: Mapping[str, Any],
    *,
    priority: int = 100,
) -> ReviewItemRecord:
    summary = dict(fallback_summary)
    status = _string(summary.get("status"), "unavailable")
    subject_kind, subject_id = _fallback_subject(summary)
    observation_refs = _source_observation_refs(summary)
    evidence_refs = _text_tuple(summary.get("evidence_refs"))
    fallback_refs = _fallback_refs(summary, subject_id)
    now = utc_now()
    return ReviewItemRecord(
        review_item_id=_stable_id("rvi_fallback", subject_kind, subject_id, fallback_refs),
        subject_kind=subject_kind,
        subject_id=subject_id,
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        priority=int(priority),
        evidence_id=evidence_refs[0] if evidence_refs else None,
        source_cache_entry_id=None,
        summary=_fallback_summary_text(summary, subject_kind, subject_id),
        payload={
            "schema_version": "review_ledger_fallback_handoff.v0",
            "input_kind": "resolution_run_fallback",
            "fallback_status": status,
            "fallback_mode": _string(summary.get("mode"), "indexless_live_search_fallback"),
            "fallback_trigger": _string(summary.get("trigger"), ""),
            "query": _string(summary.get("query"), ""),
            "source_id": _string(summary.get("source_id"), ""),
            "source_family": _string(summary.get("source_family"), ""),
            "candidate_ids": _candidate_ids(summary),
            "need_ids": _need_ids(summary),
            "source_observation_refs": list(observation_refs),
            "evidence_refs": list(evidence_refs),
            "fallback_refs": list(fallback_refs),
            "review_required": True,
            "self_promotion_allowed": False,
        },
        limitations=(
            "fallback output is review input only",
            "candidate_not_reviewed_truth",
            "review event required before reviewed projection",
        ),
        warnings=_text_tuple(summary.get("warnings")),
        created_at=now,
        updated_at=now,
    )


def enqueue_fallback_review_item(
    store: ReviewQueueStore,
    fallback_summary: Mapping[str, Any],
    *,
    priority: int = 100,
) -> ReviewItemRecord:
    item = build_review_item_from_fallback_summary(fallback_summary, priority=priority)
    store.enqueue_review_item(item)
    return item


def record_review_ledger_decision(
    store: ReviewQueueStore,
    request: ReviewLedgerDecisionRequest,
) -> ReviewLedgerDecisionResult:
    normalized = _normalize_decision_request(request)
    item = store.get_review_item(normalized.review_item_id)
    if item is None:
        raise ReviewLedgerError("review item was not found")
    if normalized.decision == "promote" and not normalized.local_only_confirmed:
        raise ReviewLedgerError("promote requires local-only confirmation")
    if not _has_citation_or_rationale(normalized):
        raise ReviewLedgerError("review decision requires evidence, source observation, absence, fallback ref, or rationale")

    decision_kind, resulting_status = _decision_mapping(normalized.decision)
    payload = _decision_payload(normalized, resulting_status)
    decision = ReviewDecision(
        review_item_id=normalized.review_item_id,
        decision_kind=decision_kind,
        decision_actor=normalized.actor,
        reason=normalized.reason,
        payload=payload,
        limitations=("review ledger decision only", "separate rebuild required for public index projection"),
    )
    stored = store.record_decision(normalized.review_item_id, decision)
    review_event = ReviewEvent(
        review_item_id=normalized.review_item_id,
        event_kind=ReviewEventKind.NOTE_ADDED,
        event_payload={
            **payload,
            "ledger_event_kind": "review_ledger_decision_context",
            "decision_id": str(stored.get("record_id", decision.decision_id)),
        },
        limitations=("audit context for review decision",),
    )
    event_result = store.append_event(review_event)
    updated_item = store.get_review_item(normalized.review_item_id) or item
    return ReviewLedgerDecisionResult(
        schema_version="review_ledger_decision_result.v0",
        status="pass",
        review_item_id=normalized.review_item_id,
        decision_id=str(stored.get("record_id", decision.decision_id)),
        review_event_id=str(event_result.get("record_id", review_event.event_id)),
        decision=normalized.decision,
        queue_status=str(stored.get("status", updated_item.queue_status.value)),
        resulting_status=resulting_status,
        review_item=updated_item.to_dict(),
        review_event=review_event.to_dict(),
    )


def review_boundary_report(subject: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "review_boundary_report.v0",
        "subject_kind": _string(subject.get("schema_version"), "unknown"),
        "candidate_can_self_promote": False,
        "fallback_can_self_promote": False,
        "source_observation_can_self_promote": False,
        "review_event_required_for_promotion": True,
        "public_projection_can_promote": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def _normalize_decision_request(request: ReviewLedgerDecisionRequest) -> ReviewLedgerDecisionRequest:
    decision = _string(request.decision, "").strip()
    if decision not in REVIEW_LEDGER_DECISIONS:
        raise ReviewLedgerError("unsupported review ledger decision")
    actor = _string(request.actor, "").strip()
    if not actor:
        raise ReviewLedgerError("actor is required")
    review_item_id = _string(request.review_item_id, "").strip()
    if not review_item_id:
        raise ReviewLedgerError("review item id is required")
    reason = _string(request.reason, "").strip() or None
    if decision in {"reject", "supersede", "mark_policy_blocked", "request_more_evidence"} and not reason:
        raise ReviewLedgerError("reason is required for this review decision")
    if decision == "supersede" and not _string(request.supersedes_review_item_id, "").strip():
        raise ReviewLedgerError("supersede requires supersedes_review_item_id")
    return ReviewLedgerDecisionRequest(
        review_item_id=review_item_id,
        decision=decision,
        actor=actor,
        reason=reason,
        evidence_refs=_clean_refs(request.evidence_refs),
        source_observation_refs=_clean_refs(request.source_observation_refs),
        absence_refs=_clean_refs(request.absence_refs),
        fallback_refs=_clean_refs(request.fallback_refs),
        visibility_posture=_string(request.visibility_posture, "operator_private"),
        supersedes_review_item_id=_string(request.supersedes_review_item_id, "").strip() or None,
        local_only_confirmed=bool(request.local_only_confirmed),
    )


def _decision_mapping(decision: str) -> tuple[ReviewDecisionKind, str]:
    return {
        "promote": (ReviewDecisionKind.ACCEPT, "verified"),
        "reject": (ReviewDecisionKind.REJECT, "rejected"),
        "supersede": (ReviewDecisionKind.SUPERSEDE, "superseded"),
        "mark_near_miss": (ReviewDecisionKind.NOTE_ONLY, "near_miss"),
        "mark_need": (ReviewDecisionKind.REQUEST_MORE_EVIDENCE, "need"),
        "mark_policy_blocked": (ReviewDecisionKind.BLOCK, "policy_blocked"),
        "request_more_evidence": (ReviewDecisionKind.REQUEST_MORE_EVIDENCE, "need"),
    }[decision]


def _decision_payload(request: ReviewLedgerDecisionRequest, resulting_status: str) -> dict[str, Any]:
    return {
        "schema_version": "review_ledger_decision_payload.v0",
        "ledger_decision": request.decision,
        "resulting_status": resulting_status,
        "evidence_refs": list(request.evidence_refs),
        "source_observation_refs": list(request.source_observation_refs),
        "absence_refs": list(request.absence_refs),
        "fallback_refs": list(request.fallback_refs),
        "visibility_posture": request.visibility_posture,
        "supersedes_review_item_id": request.supersedes_review_item_id,
        "rationale_present": bool(request.reason),
        "local_only_confirmed": bool(request.local_only_confirmed),
        "reviewed_index_rebuild_required": request.decision == "promote",
    }


def _has_citation_or_rationale(request: ReviewLedgerDecisionRequest) -> bool:
    return bool(
        request.reason
        or request.evidence_refs
        or request.source_observation_refs
        or request.absence_refs
        or request.fallback_refs
    )


def _fallback_subject(summary: Mapping[str, Any]) -> tuple[str, str]:
    status = _string(summary.get("status"), "unavailable")
    if status == "candidate":
        candidate_ids = _candidate_ids(summary)
        return "fallback_candidate", candidate_ids[0] if candidate_ids else _stable_id("fallback_candidate", summary)
    if status == "need":
        need_ids = _need_ids(summary)
        return "fallback_need", need_ids[0] if need_ids else _stable_id("fallback_need", summary)
    return f"fallback_{status}", _stable_id("fallback_state", summary)


def _fallback_summary_text(summary: Mapping[str, Any], subject_kind: str, subject_id: str) -> str:
    query = _string(summary.get("query"), "")
    source_family = _string(summary.get("source_family"), "unknown")
    return f"{subject_kind} {subject_id} from {source_family} fallback for query '{query}'"


def _candidate_ids(summary: Mapping[str, Any]) -> tuple[str, ...]:
    candidates = summary.get("candidates")
    if not isinstance(candidates, list):
        return ()
    return tuple(
        value
        for value in (_string(candidate.get("candidate_id"), "") for candidate in candidates if isinstance(candidate, Mapping))
        if value
    )


def _need_ids(summary: Mapping[str, Any]) -> tuple[str, ...]:
    needs = summary.get("needs")
    if not isinstance(needs, list):
        return ()
    return tuple(
        value
        for value in (_string(need.get("need_id"), "") for need in needs if isinstance(need, Mapping))
        if value
    )


def _source_observation_refs(summary: Mapping[str, Any]) -> tuple[str, ...]:
    observation = summary.get("source_observation")
    if not isinstance(observation, Mapping):
        return ()
    return _clean_refs((_string(observation.get("observation_id"), ""),))


def _fallback_refs(summary: Mapping[str, Any], subject_id: str) -> tuple[str, ...]:
    refs = [
        _string(summary.get("mode"), ""),
        _string(summary.get("trigger"), ""),
        _string(summary.get("status"), ""),
        subject_id,
    ]
    return (_stable_id("fallback_ref", refs),)


def _clean_refs(values: Any) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    if not isinstance(values, (list, tuple)):
        return ()
    refs: list[str] = []
    for value in values:
        text = _string(value, "").strip()
        if text and text not in refs:
            refs.append(text)
    return tuple(refs)


def _text_tuple(value: Any) -> tuple[str, ...]:
    return _clean_refs(value)


def _string(value: Any, default: str) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, (int, float)):
        return str(value)
    return default


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(canonical_json({"parts": parts}).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
