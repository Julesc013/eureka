"""Audit event builders for local review operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


def build_review_audit_event(review_item_id: str, decision: str, operator_label: str, reason: str | None) -> Mapping[str, Any]:
    return {
        "schema_version": "local_review_audit_event.v0",
        "event_kind": "review_decision_recorded",
        "review_item_id": review_item_id,
        "decision": decision,
        "operator_label": operator_label,
        "reason_present": bool(reason),
        "local_only": True,
        "created_at": _utc_now(),
    }


def build_rebuild_audit_event(operator_label: str, dry_run: bool, included_count: int, excluded_count: int) -> Mapping[str, Any]:
    return {
        "schema_version": "local_review_rebuild_audit_event.v0",
        "event_kind": "reviewed_index_rebuild",
        "operator_label": operator_label,
        "dry_run": dry_run,
        "included_count": included_count,
        "excluded_count": excluded_count,
        "input_stores_mutated": False,
        "master_index_mutated": False,
        "site_dist_mutated": False,
        "created_at": _utc_now(),
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
