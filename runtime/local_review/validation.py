"""Validation helpers for local review and rebuild services."""

from typing import Any

from .errors import LocalReviewDecisionError


ALLOWED_DECISIONS = ("accept", "reject", "block", "request_more_evidence", "note_only")
REASON_REQUIRED = ("reject", "block", "request_more_evidence")


def validate_decision_name(value: str) -> str:
    decision = str(value or "").strip()
    if decision not in ALLOWED_DECISIONS:
        raise LocalReviewDecisionError("unsupported review decision")
    return decision


def validate_reason(decision: str, reason: str | None) -> str | None:
    text = str(reason or "").strip()
    if decision in REASON_REQUIRED and not text:
        raise LocalReviewDecisionError("reason is required for this review decision")
    return text or None


def validate_local_only_confirmation(decision: str, confirmed: bool) -> bool:
    if decision == "accept" and not confirmed:
        raise LocalReviewDecisionError("accept requires local-only confirmation")
    return bool(confirmed)


def safe_limit(value: Any, default: int = 100, maximum: int = 500) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return default
    if limit < 1:
        return default
    return min(limit, maximum)
