from __future__ import annotations

from typing import Any, Mapping


def render_relay_api_response(relay_projection: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "snapshot_relay_api_response.v0",
        "projection_profile": relay_projection.get("projection_profile", "public_api_read_only"),
        "read_only": True,
        "response": dict(relay_projection.get("query_response", {})),
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "extraction_enabled": False,
    }
