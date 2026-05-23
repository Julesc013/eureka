"""Product-facing local review service functions."""

from __future__ import annotations

from typing import Any

from .decisions import LocalReviewDecisionRequest, apply_local_review_decision
from .rebuild import LocalReviewedIndexRebuildRequest, rebuild_local_reviewed_index
from .validation import safe_limit


def list_review_items(runtime: Any, status: str | None = None, limit: int = 100) -> dict[str, Any]:
    items = runtime.review_queue.list_review_items(status=status, limit=safe_limit(limit))
    return {
        "schema_version": "local_review_list_result.v0",
        "status": "pass",
        "result_count": len(items),
        "review_items": [item.to_dict() for item in items],
        "warnings": [],
        "limitations": ["local review queue only", "reviewed index is rebuilt separately"],
    }


def get_review_item(runtime: Any, review_item_id: str) -> dict[str, Any]:
    item = runtime.review_queue.get_review_item(review_item_id)
    decisions = runtime.review_queue.list_decisions(review_item_id=review_item_id, limit=100)
    events = runtime.review_queue.list_events(review_item_id=review_item_id, limit=100)
    evidence = None
    source_cache_entry = None
    if item is not None and item.evidence_id:
        evidence_record = runtime.evidence_ledger.get_evidence_candidate(item.evidence_id)
        evidence = evidence_record.to_dict() if evidence_record else None
    if item is not None and item.source_cache_entry_id:
        cache_entry = runtime.source_cache.get_cache_entry(item.source_cache_entry_id)
        source_cache_entry = cache_entry.to_dict() if cache_entry else None
    return {
        "schema_version": "local_review_item_result.v0",
        "status": "pass" if item is not None else "fail",
        "found": item is not None,
        "review_item_id": review_item_id,
        "review_item": item.to_dict() if item else None,
        "decisions": [decision.to_dict() for decision in decisions],
        "events": [event.to_dict() for event in events],
        "evidence": evidence,
        "source_cache_entry": source_cache_entry,
        "warnings": [] if item else ["review item was not found locally"],
        "limitations": ["local review state only"],
    }


def record_review_decision(
    runtime: Any,
    review_item_id: str,
    decision: str,
    reason: str | None,
    operator_label: str,
    local_only_confirmed: bool,
) -> dict[str, Any]:
    result = apply_local_review_decision(
        runtime,
        LocalReviewDecisionRequest(
            review_item_id=review_item_id,
            decision=decision,
            reason=reason,
            operator_label=operator_label,
            local_only_confirmed=local_only_confirmed,
        ),
    )
    return result.to_dict()


def rebuild_reviewed_index(runtime: Any, operator_label: str, dry_run: bool = False) -> dict[str, Any]:
    result = rebuild_local_reviewed_index(
        runtime,
        LocalReviewedIndexRebuildRequest(operator_label=operator_label, dry_run=dry_run),
    )
    return result.to_dict()
