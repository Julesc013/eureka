from __future__ import annotations

from typing import Any, Mapping, Sequence

from runtime.capabilities import build_capability_profile
from runtime.snapshots.relay_foundation import CREATED_AT, UNSAFE_FALSE_FIELDS, stable_id


def build_relay_manifest(
    snapshot_envelope: Mapping[str, Any],
    capability_profile: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    return {
        "schema_version": "relay_manifest.v0",
        "record_type": "relay_manifest",
        "relay_id": stable_id("relay", snapshot_envelope.get("snapshot_id")),
        "relay_version": "snapshot_relay_00.v0",
        "created_at": CREATED_AT,
        "snapshot_ref": snapshot_envelope.get("snapshot_id"),
        "read_only": True,
        "live_source_actions_enabled": False,
        "mutation_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "supported_projection_profiles": list(capability_profile.get("supported_projection_profiles", [])),
        "capability_profile_ref": capability_profile.get("profile_id"),
        "boundary_report_ref": stable_id("relay_boundary", snapshot_envelope.get("snapshot_id")),
        "limitations": ["read-only relay manifest for snapshot fixture"],
    }


def build_relay_record_index(snapshot_records: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    records = [dict(record) for record in snapshot_records]
    return {
        "schema_version": "relay_record_index.v0",
        "record_type": "relay_record_index",
        "relay_record_index_id": stable_id("relay_record_index", [record.get("record_id") for record in records]),
        "created_at": CREATED_AT,
        "read_only": True,
        "records": records,
        "record_count": len(records),
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }


def query_relay_snapshot(record_index: Mapping[str, Any], query: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    needle = " ".join(query.lower().split())
    records = list(record_index.get("records", []))
    matches = [
        record
        for record in records
        if needle in " ".join([str(record.get("title", "")), str(record.get("object_id", "")), str(record.get("domain_id", ""))]).lower()
    ]
    if not matches and records:
        matches = records[:1]
    return {
        "schema_version": "relay_query_response.v0",
        "record_type": "relay_query_response",
        "query_response_id": stable_id("relay_query_response", query, [record.get("record_id") for record in matches]),
        "created_at": CREATED_AT,
        "query": query,
        "read_only": True,
        "result_count": len(matches),
        "results": matches,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "limitations": ["read-only relay query over snapshot records"],
    }


def project_relay_response(
    results: Mapping[str, Any],
    projection_profile: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del policy
    return {
        "schema_version": "relay_projection.v0",
        "record_type": "relay_projection",
        "projection_id": stable_id("relay_projection", projection_profile, results.get("query_response_id")),
        "created_at": CREATED_AT,
        "projection_profile": projection_profile,
        "read_only": True,
        "query_response": dict(results),
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
        "limitations": [f"{projection_profile} projection is read-only"],
    }


def build_relay_health_packet(relay_manifest: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    return {
        "schema_version": "relay_health_packet.v0",
        "record_type": "relay_health_packet",
        "health_packet_id": stable_id("relay_health_packet", relay_manifest.get("relay_id")),
        "created_at": CREATED_AT,
        "relay_id": relay_manifest.get("relay_id"),
        "status": "ready_read_only_fixture",
        "read_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "deployment_performed": False,
    }


def build_relay_boundary_report(relay_result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    report: dict[str, Any] = {
        "schema_version": "relay_boundary_report.v0",
        "record_type": "relay_boundary_report",
        "relay_id": relay_result.get("relay_id", stable_id("relay_boundary", relay_result)),
        "created_at": CREATED_AT,
        "read_only": True,
        "limitations": ["relay boundary report for read-only snapshot projection"],
    }
    for field in UNSAFE_FALSE_FIELDS:
        report[field] = False
    return report


def build_relay_from_snapshot(snapshot_build_result: Mapping[str, Any], projection_profile: str = "public_api_read_only") -> dict[str, Any]:
    profile = build_capability_profile(projection_profile)
    envelope = snapshot_build_result["envelope"]
    record_set = snapshot_build_result["record_set"]
    manifest = build_relay_manifest(envelope, profile)
    index = build_relay_record_index(record_set["records"])
    query_response = query_relay_snapshot(index, "sampleproject")
    projection = project_relay_response(query_response, projection_profile)
    health = build_relay_health_packet(manifest)
    boundary = build_relay_boundary_report(manifest)
    return {
        "schema_version": "relay_build_result.v0",
        "relay_id": manifest["relay_id"],
        "relay_manifest": manifest,
        "relay_record_index": index,
        "relay_query_response": query_response,
        "relay_projection": projection,
        "relay_health_packet": health,
        "relay_boundary_report": boundary,
    }
