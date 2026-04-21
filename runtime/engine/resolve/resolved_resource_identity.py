from __future__ import annotations

import hashlib
import json
from typing import Any

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord


def resolved_resource_id_for_record(record: NormalizedResolutionRecord) -> str:
    return resolved_resource_id_for_values(
        object_id=record.object_id,
        target_ref=record.target_ref,
        state_id=record.state_id,
        representation_id=record.representation_id,
    )


def resolved_resource_id_for_values(
    *,
    object_id: str,
    target_ref: str,
    state_id: str | None = None,
    representation_id: str | None = None,
) -> str:
    identity_payload = _compact_mapping(
        {
            "object_id": object_id,
            "target_ref": target_ref,
            "state_id": state_id,
            "representation_id": representation_id,
        }
    )
    canonical_bytes = json.dumps(
        identity_payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"resolved:sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"


def _compact_mapping(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}
