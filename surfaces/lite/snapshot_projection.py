from __future__ import annotations

from typing import Any, Mapping


def render_snapshot_lite_packet(snapshot_build_result: Mapping[str, Any]) -> dict[str, Any]:
    envelope = snapshot_build_result["envelope"]
    return {
        "schema_version": "snapshot_lite_packet.v0",
        "projection_profile": "lite_client_read_only",
        "snapshot_id": envelope["snapshot_id"],
        "record_count": envelope["record_count"],
        "read_only": True,
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
    }
