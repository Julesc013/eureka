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
    content_text: str | None = None
    evidence: tuple[str, ...] = ()
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
        if self.content_text is not None:
            payload["content_text"] = self.content_text
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
            self.content_text,
            " ".join(self.evidence),
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
