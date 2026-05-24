from __future__ import annotations

from typing import Any, Mapping


def render_snapshot_text(snapshot_build_result: Mapping[str, Any]) -> str:
    envelope = snapshot_build_result["envelope"]
    manifest = snapshot_build_result["manifest"]
    return "\n".join(
        [
            f"Snapshot: {envelope['snapshot_id']}",
            f"Records: {manifest['record_count']}",
            "Mode: read-only",
            "Live source actions: disabled",
        ]
    )
