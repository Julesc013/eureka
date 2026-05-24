from __future__ import annotations

from typing import Any, Mapping


def validate_relay_manifest(relay_manifest: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in (
        "relay_id",
        "relay_version",
        "snapshot_ref",
        "read_only",
        "live_source_actions_enabled",
        "mutation_enabled",
        "download_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "supported_projection_profiles",
        "capability_profile_ref",
        "boundary_report_ref",
    ):
        if field not in relay_manifest:
            errors.append(f"missing {field}")
    for field in (
        "live_source_actions_enabled",
        "mutation_enabled",
        "download_enabled",
        "extraction_enabled",
        "model_provider_enabled",
    ):
        if relay_manifest.get(field) is not False:
            errors.append(f"{field} must be false")
    if relay_manifest.get("read_only") is not True:
        errors.append("read_only must be true")
    return {
        "schema_version": "relay_validation_report.v0",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "relay_id": relay_manifest.get("relay_id"),
    }


__all__ = ["validate_relay_manifest"]
