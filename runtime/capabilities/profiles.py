from __future__ import annotations

from typing import Any, Mapping

from runtime.snapshots.relay_foundation import CREATED_AT, stable_id


PROJECTION_PROFILES = (
    "operator_workbench_snapshot_reader",
    "public_web_read_only",
    "public_api_read_only",
    "relay_client_read_only",
    "native_desktop_read_only",
    "lite_client_read_only",
    "text_client_read_only",
)


def build_capability_profile(profile_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    if profile_id not in PROJECTION_PROFILES:
        raise KeyError(f"unknown capability profile: {profile_id}")
    return {
        "schema_version": "capability_profile.v0",
        "record_type": "capability_profile",
        "profile_id": profile_id,
        "profile_version": "0.0",
        "created_at": CREATED_AT,
        "supported_packet_versions": ["snapshot_relay_00.v0"],
        "supported_projection_profiles": list(PROJECTION_PROFILES),
        "supports_read_only_search": True,
        "supports_live_source_actions": False,
        "supports_review": False,
        "supports_mutation": False,
        "supports_download": False,
        "supports_extraction": False,
        "supports_native_read_only": profile_id == "native_desktop_read_only",
        "limitations": ["read-only snapshot/relay capability profile"],
    }


def validate_capability_profile(profile: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    del policy
    errors: list[str] = []
    required = (
        "profile_id",
        "profile_version",
        "supported_packet_versions",
        "supported_projection_profiles",
        "supports_read_only_search",
        "supports_live_source_actions",
        "supports_review",
        "supports_mutation",
        "supports_download",
        "supports_extraction",
        "supports_native_read_only",
        "limitations",
    )
    for field in required:
        if field not in profile:
            errors.append(f"missing {field}")
    for field in (
        "supports_live_source_actions",
        "supports_review",
        "supports_mutation",
        "supports_download",
        "supports_extraction",
    ):
        if profile.get(field) is not False:
            errors.append(f"{field} must be false")
    return {
        "schema_version": "capability_profile_validation.v0",
        "status": "pass" if not errors else "fail",
        "profile_id": profile.get("profile_id"),
        "errors": errors,
    }


def negotiate_projection_capability(
    client_request: Mapping[str, Any],
    server_profile: Mapping[str, Any],
) -> dict[str, Any]:
    requested = str(client_request.get("projection_profile", "public_api_read_only"))
    supported = requested in set(server_profile.get("supported_projection_profiles", []))
    return {
        "schema_version": "projection_capability.v0",
        "negotiation_id": stable_id("projection_capability", requested, server_profile.get("profile_id")),
        "requested_projection_profile": requested,
        "supported": supported,
        "read_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
    }


def build_server_capability_response(
    profile: Mapping[str, Any],
    client_request: Mapping[str, Any],
) -> dict[str, Any]:
    negotiation = negotiate_projection_capability(client_request, profile)
    return {
        "schema_version": "server_capability_response.v0",
        "response_id": stable_id("server_capability_response", profile.get("profile_id"), client_request),
        "profile": dict(profile),
        "negotiation": negotiation,
        "read_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "limitations": ["capability response for read-only snapshot relay"],
    }
