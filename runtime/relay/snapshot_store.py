"""Explicit fixture snapshot store used by the read-only relay."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from runtime.relay.profiles import ensure_allowed_relay_input_path, load_json, stable_id
from runtime.snapshots.manifest import build_snapshot_manifest, build_snapshot_record


TYPE_ALIASES = {
    "object": "object_record",
    "source": "source_record",
    "need": "need_record",
    "action": "action_manifest",
    "search": "search_result",
}


def load_snapshot_for_relay(snapshot_input: str | Path | Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(snapshot_input, Mapping):
        payload = dict(snapshot_input)
    else:
        payload = load_json(ensure_allowed_relay_input_path(snapshot_input))
    schema = payload.get("schema_version", "")
    if schema == "snapshot_manifest.v0":
        manifest = payload
    elif schema == "snapshot_record.v0":
        manifest = build_snapshot_manifest([payload])
    elif isinstance(payload.get("records"), list):
        manifest = build_snapshot_manifest([record for record in payload["records"] if isinstance(record, Mapping)])
    else:
        manifest = build_snapshot_manifest([build_snapshot_record(payload)])
    records = [record for record in manifest.get("records", []) if isinstance(record, Mapping)]
    return {
        "schema_version": "relay_snapshot_store.v0",
        "snapshot_store_id": stable_id("relay_snapshot_store", manifest.get("snapshot_manifest_id", "")),
        "snapshot_ref": manifest.get("snapshot_manifest_id", ""),
        "manifest": manifest,
        "records": records,
        "records_by_type": _records_by_type(records),
        "limitations": ["Explicit fixture snapshot store only; no live source access or state mutation."],
    }


def query_snapshot_records(snapshot_store: Mapping[str, Any], query: str | Mapping[str, Any] | None = None, policy: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    query_text = ""
    if isinstance(query, Mapping):
        query_text = " ".join(str(value) for value in query.values())
    elif query:
        query_text = str(query)
    query_text = query_text.casefold().strip()
    records = [record for record in snapshot_store.get("records", []) if isinstance(record, Mapping)]
    candidates = [record for record in records if record.get("record_type") in {"search_result", "known_absence", "policy_blocked_record"}]
    if not query_text:
        return [dict(record) for record in candidates]
    matches = []
    for record in candidates:
        haystack = " ".join(
            str(record.get(key, ""))
            for key in ("snapshot_record_id", "record_type", "canonical_ref", "title", "summary")
        ).casefold()
        if query_text in haystack:
            matches.append(dict(record))
    return matches or [dict(record) for record in candidates]


def get_snapshot_record(snapshot_store: Mapping[str, Any], record_type: str, record_id: str | None = None, policy: Mapping[str, Any] | None = None) -> dict[str, Any] | None:
    normalized = TYPE_ALIASES.get(record_type, record_type)
    records = [record for record in snapshot_store.get("records", []) if isinstance(record, Mapping)]
    typed = [record for record in records if record.get("record_type") == normalized]
    if normalized == "action_manifest":
        typed.extend(record for record in records if record.get("record_type") == "blocked_action")
    if not record_id:
        return dict(typed[0]) if typed else None
    needle = record_id.casefold()
    for record in typed:
        values = [
            str(record.get("snapshot_record_id", "")),
            str(record.get("canonical_ref", "")),
            str(record.get("title", "")),
        ]
        if any(needle == value.casefold() or needle in value.casefold().split(":")[-1] or needle in value.casefold() for value in values):
            return dict(record)
    return None


def _records_by_type(records: list[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record.get("record_type", "unknown")), []).append(dict(record))
    return grouped

