from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice


@dataclass(frozen=True)
class AcquisitionResult:
    acquisition_status: str
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
    reason_codes: tuple[str, ...] = ()
    reason_messages: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()
    payload: bytes | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.acquisition_status,
            "acquisition_status": self.acquisition_status,
            "target_ref": self.target_ref,
            "representation_id": self.representation_id,
            "reason_codes": list(self.reason_codes),
            "reason_messages": list(self.reason_messages),
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.representation_kind is not None:
            payload["representation_kind"] = self.representation_kind
        if self.label is not None:
            payload["label"] = self.label
        if self.filename is not None:
            payload["filename"] = self.filename
        if self.content_type is not None:
            payload["content_type"] = self.content_type
        if self.byte_length is not None:
            payload["byte_length"] = self.byte_length
        if self.source_family is not None:
            payload["source_family"] = self.source_family
        if self.source_label is not None:
            payload["source_label"] = self.source_label
        if self.source_locator is not None:
            payload["source_locator"] = self.source_locator
        if self.access_kind is not None:
            payload["access_kind"] = self.access_kind
        if self.access_locator is not None:
            payload["access_locator"] = self.access_locator
        return payload
