from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RepresentationSummary:
    representation_id: str
    representation_kind: str
    label: str
    source_family: str
    access_kind: str
    content_type: str | None = None
    byte_length: int | None = None
    filename: str | None = None
    source_label: str | None = None
    source_locator: str | None = None
    access_path_id: str | None = None
    access_locator: str | None = None
    is_direct: bool = False
    is_fetchable: bool = False
    fetch_locator: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "representation_id": self.representation_id,
            "representation_kind": self.representation_kind,
            "label": self.label,
            "source_family": self.source_family,
            "access_kind": self.access_kind,
            "is_direct": self.is_direct,
            "is_fetchable": self.is_fetchable,
        }
        if self.content_type is not None:
            payload["content_type"] = self.content_type
        if self.byte_length is not None:
            payload["byte_length"] = self.byte_length
        if self.filename is not None:
            payload["filename"] = self.filename
        if self.source_label is not None:
            payload["source_label"] = self.source_label
        if self.source_locator is not None:
            payload["source_locator"] = self.source_locator
        if self.access_path_id is not None:
            payload["access_path_id"] = self.access_path_id
        if self.access_locator is not None:
            payload["access_locator"] = self.access_locator
        return payload
