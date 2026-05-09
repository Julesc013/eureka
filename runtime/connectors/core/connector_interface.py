"""Core connector-interface helpers for Source OS.

These helpers are policy and fixture utilities only. They do not call
networks, open URLs, mutate runtime state, or accept connector output as
truth.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
import json
from pathlib import Path
from typing import Any


FORBIDDEN_TRUE_KEYS = {
    "accepted_as_public_truth",
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "accepted_source_truth",
    "capability_is_permission",
    "connector_capability_grants_permission",
    "connector_output_is_accepted_evidence",
    "connector_output_is_public_truth",
    "downloaded_file",
    "executed_artifact",
    "live_access_enabled",
    "live_call_allowed",
    "live_connector_enabled",
    "live_probe_envelope_grants_permission",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "network_calls_made",
    "network_used",
    "permission_granted",
    "public_index_mutated",
    "rights_clearance_claimed",
    "source_sync_enabled",
    "verified_installability_claimed",
}

FORBIDDEN_PRODUCT_TRUE_KEYS = {
    "changed_public_search_behavior",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "mutated_master_index",
    "mutated_public_index",
}


def load_connector_contract(path: str | Path) -> dict[str, Any]:
    """Load a connector contract JSON object."""

    return _load_json_object(path, "connector contract")


def load_source_policy(path: str | Path) -> dict[str, Any]:
    """Load a source or connector policy JSON object."""

    return _load_json_object(path, "source policy")


def summarize_connector_family_registry(records: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize connector families without granting any operation."""

    families = _family_list(records)
    source_family_counts: Counter[str] = Counter()
    access_counts: Counter[str] = Counter()
    forbidden_counts: Counter[str] = Counter()
    for family in families:
        source_family_counts.update(_strings(family.get("source_families_supported")))
        access_counts.update([str(family.get("current_default_access", "unknown"))])
        forbidden_counts.update(_strings(family.get("forbidden_default_operations")))
    return {
        "schema_version": "connector_family_summary.v0",
        "status": "pass",
        "family_count": len(families),
        "family_ids": sorted(str(item.get("family_id", "")) for item in families),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "default_access_counts": dict(sorted(access_counts.items())),
        "forbidden_operation_counts": dict(sorted(forbidden_counts.items())),
        "live_access_enabled_count": sum(1 for item in families if item.get("live_access_default") is True),
        "truth_boundary": {
            "connector_family_summary_is_public_truth": False,
            "connector_capability_grants_permission": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
        },
        "product_boundary": {
            "changed_public_search_behavior": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_downloads": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
    }


def detect_connector_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return truth-boundary violations for a connector artifact."""

    return [
        f"truth boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_TRUE_KEYS and value is True
    ]


def detect_connector_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    """Return product-boundary violations for a connector artifact."""

    return [
        f"product boundary violation: {path}=true"
        for path, key, value in _iter_key_values(record)
        if key in FORBIDDEN_PRODUCT_TRUE_KEYS and value is True
    ]


def validate_no_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_connector_truth_boundary_violations(record, policy) + detect_connector_product_boundary_violations(record, policy)
    if errors:
        raise ValueError("; ".join(errors))


def _load_json_object(path: str | Path, label: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def _family_list(records: Mapping[str, Any] | Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    if isinstance(records, Mapping):
        items = records.get("families", [])
        if isinstance(items, list):
            return [item for item in items if isinstance(item, Mapping)]
        return [records]
    return [item for item in records if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")
