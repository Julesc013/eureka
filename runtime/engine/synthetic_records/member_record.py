from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class SyntheticMemberRecord:
    member_record_id: str
    synthetic_target_ref: str
    parent_target_ref: str
    parent_resolved_resource_id: str | None
    parent_representation_id: str
    parent_object_label: str | None
    source_id: str | None
    source_family: str
    source_label: str | None
    member_path: str
    member_label: str
    member_kind: str
    media_type: str | None
    size_bytes: int | None
    content_hash: str | None
    evidence: tuple[EvidenceSummary, ...]
    parent_lineage: dict[str, Any]
    action_hints: tuple[str, ...]
    created_by_slice: str = "member_level_synthetic_records_v0"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "member_record_id": self.member_record_id,
            "synthetic_target_ref": self.synthetic_target_ref,
            "parent_target_ref": self.parent_target_ref,
            "parent_representation_id": self.parent_representation_id,
            "source_family": self.source_family,
            "member_path": self.member_path,
            "member_label": self.member_label,
            "member_kind": self.member_kind,
            "evidence": [summary.to_dict() for summary in self.evidence],
            "parent_lineage": _clone_json_like(self.parent_lineage),
            "action_hints": list(self.action_hints),
            "created_by_slice": self.created_by_slice,
        }
        for field_name in (
            "parent_resolved_resource_id",
            "parent_object_label",
            "source_id",
            "source_label",
            "media_type",
            "content_hash",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        if self.size_bytes is not None:
            payload["size_bytes"] = self.size_bytes
        return payload


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    return value
