from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RepresentationSelectionEntry:
    representation_id: str
    representation_kind: str
    label: str
    selection_status: str
    reason_codes: tuple[str, ...]
    reason_messages: tuple[str, ...]
    source_family: str
    access_kind: str
    content_type: str | None = None
    byte_length: int | None = None
    source_label: str | None = None
    source_locator: str | None = None
    access_locator: str | None = None
    is_direct: bool = False
    host_profile_id: str | None = None
    strategy_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "representation_id": self.representation_id,
            "representation_kind": self.representation_kind,
            "label": self.label,
            "selection_status": self.selection_status,
            "reason_codes": list(self.reason_codes),
            "reason_messages": list(self.reason_messages),
            "source_family": self.source_family,
            "access_kind": self.access_kind,
            "is_direct": self.is_direct,
        }
        for field_name in (
            "content_type",
            "byte_length",
            "source_label",
            "source_locator",
            "access_locator",
            "host_profile_id",
            "strategy_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                payload[field_name] = value
        return payload
