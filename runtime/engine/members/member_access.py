from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice


@dataclass(frozen=True)
class MemberAccessResult:
    member_access_status: str
    target_ref: str
    representation_id: str
    member_path: str
    resolved_resource_id: str | None = None
    representation_kind: str | None = None
    label: str | None = None
    filename: str | None = None
    source_family: str | None = None
    source_label: str | None = None
    source_locator: str | None = None
    access_kind: str | None = None
    access_locator: str | None = None
    member_kind: str | None = None
    content_type: str | None = None
    byte_length: int | None = None
    sha256: str | None = None
    text_preview: str | None = None
    reason_codes: tuple[str, ...] = ()
    reason_messages: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()
    payload: bytes | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.member_access_status,
            "member_access_status": self.member_access_status,
            "target_ref": self.target_ref,
            "representation_id": self.representation_id,
            "member_path": self.member_path,
            "reason_codes": list(self.reason_codes),
            "reason_messages": list(self.reason_messages),
            "notices": [notice.to_dict() for notice in self.notices],
        }
        for field_name in (
            "resolved_resource_id",
            "representation_kind",
            "label",
            "filename",
            "source_family",
            "source_label",
            "source_locator",
            "access_kind",
            "access_locator",
            "member_kind",
            "content_type",
            "sha256",
            "text_preview",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        if self.byte_length is not None:
            payload["byte_length"] = self.byte_length
        return payload
