from __future__ import annotations

from typing import Any

from runtime.engine.interfaces.extract import ExtractedSyntheticRecord
from runtime.engine.interfaces.normalize.normalized_records import NormalizedResolutionRecord


def normalize_extracted_record(extracted_record: ExtractedSyntheticRecord) -> NormalizedResolutionRecord:
    object_record = extracted_record.object_record
    state_record = extracted_record.state_record
    representation_record = extracted_record.representation_record
    access_path_record = extracted_record.access_path_record

    return NormalizedResolutionRecord(
        target_ref=extracted_record.target_ref,
        source_name=extracted_record.source_name,
        source_locator=extracted_record.source_locator,
        object_id=_require_string(object_record.get("id"), "object.id"),
        object_kind=_optional_string(object_record.get("kind"), "object.kind"),
        object_label=_optional_string(object_record.get("label"), "object.label"),
        state_id=_optional_string(state_record.get("id"), "state.id"),
        state_kind=_optional_string(state_record.get("kind"), "state.kind"),
        representation_id=_optional_string(representation_record.get("id"), "representation.id"),
        representation_kind=_optional_string(representation_record.get("kind"), "representation.kind"),
        access_path_id=_optional_string(access_path_record.get("id"), "access_path.id"),
        access_path_kind=_optional_string(access_path_record.get("kind"), "access_path.kind"),
        access_path_locator=_optional_string(access_path_record.get("locator"), "access_path.locator"),
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string in the extracted record.")
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value
