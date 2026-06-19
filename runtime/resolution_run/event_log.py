"""Append-only event logs for resolution-run packets."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Mapping

from .run_store import FIXED_CREATED_AT, stable_id


HASH_FIELDS = (
    "schema_version",
    "event_id",
    "run_id",
    "sequence",
    "event_type",
    "created_at",
    "occurred_at",
    "producer_plane",
    "payload_schema_ref",
    "payload_hash",
    "previous_event_hash",
    "causation_id",
    "correlation_id",
    "workunit_id",
    "authority",
    "privacy_posture",
    "synthetic",
    "accepted_truth",
)


def canonical_json(value: Any) -> str:
    """Serialize JSON data in the stable form used by runner hashes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: str | bytes) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def payload_hash(payload: Mapping[str, Any] | None) -> str:
    return sha256_hex(canonical_json(dict(payload or {})))


def event_hash(event: Mapping[str, Any]) -> str:
    material = {key: event.get(key) for key in HASH_FIELDS if key in event}
    return sha256_hex(canonical_json(material))


def validate_event_hash_chain(events: list[Mapping[str, Any]]) -> list[str]:
    """Return hash-chain validation errors for a run event list."""
    errors: list[str] = []
    previous = ""
    expected_sequence = 0
    for event in events:
        sequence = event.get("sequence")
        if sequence != expected_sequence:
            errors.append(f"event sequence mismatch: expected {expected_sequence}, got {sequence}")
        if event.get("previous_event_hash") != previous:
            errors.append(f"previous hash mismatch at sequence {sequence}")
        expected_payload_hash = payload_hash(event.get("payload") if isinstance(event.get("payload"), Mapping) else {})
        if event.get("payload_hash") != expected_payload_hash:
            errors.append(f"payload hash mismatch at sequence {sequence}")
        expected_event_hash = event_hash(event)
        if event.get("event_hash") != expected_event_hash:
            errors.append(f"event hash mismatch at sequence {sequence}")
        previous = str(event.get("event_hash") or "")
        expected_sequence += 1
    return errors


@dataclass
class InMemoryRunEventLog:
    """Append-only in-memory event log used by the runner and compatibility tests."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def append(
        self,
        run_id: str,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
        *,
        producer_plane: str = "Discovery",
        payload_schema_ref: str = "",
        causation_id: str = "",
        correlation_id: str = "",
        workunit_id: str = "",
        authority: str = "runner_only",
        privacy_posture: str = "local_private",
        synthetic: bool = True,
    ) -> dict[str, Any]:
        sequence = len([event for event in self.events if event.get("run_id") == run_id])
        previous = ""
        for event in reversed(self.events):
            if event.get("run_id") == run_id:
                previous = str(event.get("event_hash") or "")
                break
        body = dict(payload or {})
        body_hash = payload_hash(body)
        event = {
            "schema_version": "run_event.v0",
            "event_id": stable_id("runevt", {"run_id": run_id, "event_type": event_type, "sequence": sequence, "payload_hash": body_hash}),
            "run_id": run_id,
            "sequence": sequence,
            "event_type": event_type,
            "created_at": FIXED_CREATED_AT,
            "occurred_at": FIXED_CREATED_AT,
            "producer_plane": producer_plane,
            "payload_schema_ref": payload_schema_ref,
            "payload": body,
            "payload_hash": body_hash,
            "previous_event_hash": previous,
            "causation_id": causation_id,
            "correlation_id": correlation_id,
            "workunit_id": workunit_id,
            "authority": authority,
            "privacy_posture": privacy_posture,
            "synthetic": synthetic,
            "accepted_truth": False,
            "review_required": False,
        }
        event["event_hash"] = event_hash(event)
        self.events.append(event)
        return event

    def list_events(self, run_id: str | None = None) -> list[dict[str, Any]]:
        if run_id is None:
            return [dict(event) for event in self.events]
        return [dict(event) for event in self.events if event.get("run_id") == run_id]
