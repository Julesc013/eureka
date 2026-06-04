"""Degraded-state helpers for SurfaceKernel."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.surface.profiles import HTML_BASIC_V0, JSON_V0, SNAPSHOT_V0, TEXT_V0


CANONICAL_STATUSES = {
    "verified",
    "candidate",
    "need",
    "near_miss",
    "mention_only",
    "policy_blocked",
    "private_local",
    "superseded",
    "rejected",
    "unknown",
    "unavailable",
}

PROFILE_FALLBACK_ORDER = {
    HTML_BASIC_V0: (HTML_BASIC_V0, TEXT_V0, JSON_V0),
    TEXT_V0: (TEXT_V0, JSON_V0),
    JSON_V0: (JSON_V0,),
    SNAPSHOT_V0: (SNAPSHOT_V0, JSON_V0),
}


def canonical_status(value: Any) -> tuple[str, list[str]]:
    text = str(value or "").strip()
    if text in CANONICAL_STATUSES:
        return text, []
    if text in {"degraded", "failed"}:
        return "unavailable", [f"status {text} mapped to unavailable"]
    return "unknown", [f"status {text or 'missing'} mapped to unknown"]


def fallback_profile_order(profile: str) -> tuple[str, ...]:
    return PROFILE_FALLBACK_ORDER.get(profile, (HTML_BASIC_V0, TEXT_V0, JSON_V0))


def safe_degraded_view(route_id: str, entity_id: str, reason: str) -> dict[str, Any]:
    status, notes = canonical_status("unknown")
    return {
        "schema_version": "surface_view_model.v0",
        "view_model_version": "surface_view_model.v0",
        "view_family": "degraded",
        "route_id": route_id,
        "entity_id": entity_id,
        "canonical_status": status,
        "title": "Unavailable",
        "summary": reason,
        "actions": [{"action_id": "view", "classification": "read_only"}],
        "policy_notes": notes + [reason],
        "payload": {},
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def missing_summary_note(value: Mapping[str, Any] | None) -> list[str]:
    if value:
        return []
    return ["summary unavailable"]
