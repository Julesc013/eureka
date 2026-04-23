from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INSPECT_PRIMARY_REPRESENTATION_ACTION_ID = "inspect_primary_representation"
ACCESS_REPRESENTATION_ACTION_ID = "access_representation"
EXPORT_RESOLUTION_MANIFEST_ACTION_ID = "export_resolution_manifest"
EXPORT_RESOLUTION_BUNDLE_ACTION_ID = "export_resolution_bundle"
INSPECT_BUNDLE_ACTION_ID = "inspect_bundle"
STORE_RESOLUTION_MANIFEST_ACTION_ID = "store_resolution_manifest"
STORE_RESOLUTION_BUNDLE_ACTION_ID = "store_resolution_bundle"
LIST_SUBJECT_STATES_ACTION_ID = "list_subject_states"
COMPARE_TARGET_ACTION_ID = "compare_target"


@dataclass(frozen=True)
class ActionPlanEntry:
    action_id: str
    label: str
    kind: str
    status: str
    reason_codes: tuple[str, ...] = ()
    reason_messages: tuple[str, ...] = ()
    parameter_hint: str | None = None
    representation_id: str | None = None
    representation_label: str | None = None
    representation_kind: str | None = None
    access_kind: str | None = None
    access_locator: str | None = None
    source_family: str | None = None
    source_locator: str | None = None
    subject_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "action_id": self.action_id,
            "label": self.label,
            "kind": self.kind,
            "status": self.status,
            "reason_codes": list(self.reason_codes),
            "reason_messages": list(self.reason_messages),
        }
        for key in (
            "parameter_hint",
            "representation_id",
            "representation_label",
            "representation_kind",
            "access_kind",
            "access_locator",
            "source_family",
            "source_locator",
            "subject_key",
        ):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        return payload
