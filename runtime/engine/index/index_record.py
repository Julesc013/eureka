from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IndexRecord:
    index_record_id: str
    record_kind: str
    label: str
    summary: str | None = None
    target_ref: str | None = None
    resolved_resource_id: str | None = None
    source_id: str | None = None
    source_family: str | None = None
    source_label: str | None = None
    subject_key: str | None = None
    version_or_state: str | None = None
    representation_id: str | None = None
    member_path: str | None = None
    parent_target_ref: str | None = None
    parent_resolved_resource_id: str | None = None
    parent_representation_id: str | None = None
    parent_object_label: str | None = None
    member_kind: str | None = None
    media_type: str | None = None
    size_bytes: int | None = None
    content_hash: str | None = None
    content_text: str | None = None
    evidence: tuple[str, ...] = ()
    action_hints: tuple[str, ...] = ()
    result_lanes: tuple[str, ...] = ()
    primary_lane: str | None = None
    user_cost_score: int | None = None
    user_cost_reasons: tuple[str, ...] = ()
    usefulness_summary: str | None = None
    route_hints: dict[str, Any] | None = None
    created_by_slice: str = "local_index_v0"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "index_record_id": self.index_record_id,
            "record_kind": self.record_kind,
            "label": self.label,
            "evidence": list(self.evidence),
            "route_hints": _clone_json_like(self.route_hints or {}),
            "created_by_slice": self.created_by_slice,
        }
        if self.summary is not None:
            payload["summary"] = self.summary
        if self.target_ref is not None:
            payload["target_ref"] = self.target_ref
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.source_id is not None:
            payload["source_id"] = self.source_id
        if self.source_family is not None:
            payload["source_family"] = self.source_family
        if self.source_label is not None:
            payload["source_label"] = self.source_label
        if self.subject_key is not None:
            payload["subject_key"] = self.subject_key
        if self.version_or_state is not None:
            payload["version_or_state"] = self.version_or_state
        if self.representation_id is not None:
            payload["representation_id"] = self.representation_id
        if self.member_path is not None:
            payload["member_path"] = self.member_path
        for field_name in (
            "parent_target_ref",
            "parent_resolved_resource_id",
            "parent_representation_id",
            "parent_object_label",
            "member_kind",
            "media_type",
            "content_hash",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        if self.size_bytes is not None:
            payload["size_bytes"] = self.size_bytes
        if self.content_text is not None:
            payload["content_text"] = self.content_text
        if self.action_hints:
            payload["action_hints"] = list(self.action_hints)
        if self.result_lanes:
            payload["result_lanes"] = list(self.result_lanes)
        if self.primary_lane is not None:
            payload["primary_lane"] = self.primary_lane
        if self.user_cost_score is not None:
            payload["user_cost_score"] = self.user_cost_score
        if self.user_cost_reasons:
            payload["user_cost_reasons"] = list(self.user_cost_reasons)
        if self.usefulness_summary is not None:
            payload["usefulness_summary"] = self.usefulness_summary
        return payload

    def search_text(self) -> str:
        fields = [
            self.label,
            self.summary,
            self.target_ref,
            self.resolved_resource_id,
            self.source_id,
            self.source_family,
            self.source_label,
            self.subject_key,
            self.version_or_state,
            self.representation_id,
            self.member_path,
            self.parent_target_ref,
            self.parent_resolved_resource_id,
            self.parent_representation_id,
            self.parent_object_label,
            self.member_kind,
            self.media_type,
            str(self.size_bytes) if self.size_bytes is not None else None,
            self.content_hash,
            self.content_text,
            " ".join(self.evidence),
            " ".join(self.action_hints),
            " ".join(self.result_lanes),
            self.primary_lane,
            str(self.user_cost_score) if self.user_cost_score is not None else None,
            " ".join(self.user_cost_reasons),
            self.usefulness_summary,
            _route_hints_text(self.route_hints),
        ]
        return " ".join(part for part in fields if isinstance(part, str) and part).strip()


def _clone_json_like(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clone_json_like(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone_json_like(item) for item in value]
    if isinstance(value, tuple):
        return [_clone_json_like(item) for item in value]
    return value


def _route_hints_text(value: dict[str, Any] | None) -> str:
    if not isinstance(value, dict):
        return ""
    parts: list[str] = []
    for key, item in sorted(value.items()):
        if isinstance(item, str) and item:
            parts.append(f"{key} {item}")
        elif isinstance(item, (int, float, bool)):
            parts.append(f"{key} {item}")
    return " ".join(parts)
