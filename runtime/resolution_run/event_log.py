"""Append-only in-memory event log for resolution-run packets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .run_store import FIXED_CREATED_AT, stable_id


@dataclass
class InMemoryRunEventLog:
    """Tiny event log used by the foundation kernel and tests."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def append(
        self,
        run_id: str,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "schema_version": "run_event.v0",
            "event_id": stable_id("runevt", {"run_id": run_id, "event_type": event_type, "index": len(self.events)}),
            "run_id": run_id,
            "event_type": event_type,
            "created_at": FIXED_CREATED_AT,
            "payload": dict(payload or {}),
            "accepted_truth": False,
            "review_required": False,
        }
        self.events.append(event)
        return event

    def list_events(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is None:
            return [dict(event) for event in self.events]
        return [dict(event) for event in self.events if event.get("run_id") == run_id]
