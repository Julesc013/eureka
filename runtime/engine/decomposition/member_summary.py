from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice


@dataclass(frozen=True)
class MemberSummary:
    member_path: str
    member_kind: str
    byte_length: int | None = None
    content_type: str | None = None
    sha256: str | None = None
    text_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "member_path": self.member_path,
            "member_kind": self.member_kind,
        }
        if self.byte_length is not None:
            payload["byte_length"] = self.byte_length
        if self.content_type is not None:
            payload["content_type"] = self.content_type
        if self.sha256 is not None:
            payload["sha256"] = self.sha256
        if self.text_hint is not None:
            payload["text_hint"] = self.text_hint
        return payload


@dataclass(frozen=True)
class DecompositionResult:
    decomposition_status: str
    target_ref: str
    representation_id: str
    resolved_resource_id: str | None = None
    representation_kind: str | None = None
    label: str | None = None
    filename: str | None = None
    content_type: str | None = None
    byte_length: int | None = None
    source_family: str | None = None
    source_label: str | None = None
    source_locator: str | None = None
    access_kind: str | None = None
    access_locator: str | None = None
    members: tuple[MemberSummary, ...] = ()
    reason_codes: tuple[str, ...] = ()
    reason_messages: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.decomposition_status,
            "decomposition_status": self.decomposition_status,
            "target_ref": self.target_ref,
            "representation_id": self.representation_id,
            "members": [member.to_dict() for member in self.members],
            "reason_codes": list(self.reason_codes),
            "reason_messages": list(self.reason_messages),
            "notices": [notice.to_dict() for notice in self.notices],
        }
        for field_name in (
            "resolved_resource_id",
            "representation_kind",
            "label",
            "filename",
            "content_type",
            "byte_length",
            "source_family",
            "source_label",
            "source_locator",
            "access_kind",
            "access_locator",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload
