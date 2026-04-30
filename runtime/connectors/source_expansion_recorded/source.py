from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from runtime.engine.interfaces.ingest import SourceExpansionRecordedSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_EXPANSION_RECORDED_FIXTURE_PATH = (
    REPO_ROOT
    / "runtime"
    / "connectors"
    / "source_expansion_recorded"
    / "fixtures"
    / "source_expansion_v2_fixture.json"
)
ALLOWED_SOURCE_FAMILIES = {
    "manual_document_recorded",
    "package_registry_recorded",
    "review_description_recorded",
    "software_heritage_recorded",
    "sourceforge_recorded",
    "wayback_memento_recorded",
}


def load_source_expansion_recorded_source_records(
    path: Path | None = None,
) -> tuple[SourceExpansionRecordedSourceRecord, ...]:
    fixture_path = path or DEFAULT_SOURCE_EXPANSION_RECORDED_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_records = document.get("records")
    if not isinstance(raw_records, list):
        raise ValueError("Source expansion recorded fixture must define a top-level 'records' list.")
    fixture_notes = document.get("fixture_notes")
    return tuple(
        _coerce_source_record(raw_record, fixture_path, index, fixture_notes)
        for index, raw_record in enumerate(raw_records)
    )


def source_expansion_recorded_target_ref(source_family: str, fixture_id: str) -> str:
    normalized_source_family = _safe_ref_part(source_family, "source_family").replace("_", "-")
    normalized_fixture_id = _safe_ref_part(fixture_id, "fixture_id")
    return f"{normalized_source_family}:{normalized_fixture_id}"


def _coerce_source_record(
    raw_record: Any,
    fixture_path: Path,
    index: int,
    fixture_notes: Any,
) -> SourceExpansionRecordedSourceRecord:
    if not isinstance(raw_record, dict):
        raise ValueError(f"records[{index}] must be an object.")
    source_family = _require_string(raw_record, "source_family", index)
    if source_family not in ALLOWED_SOURCE_FAMILIES:
        raise ValueError(f"records[{index}].source_family uses unsupported family '{source_family}'.")
    fixture_id = _require_string(raw_record, "fixture_id", index)
    if "object" not in raw_record or not isinstance(raw_record["object"], dict):
        raise ValueError(f"records[{index}].object must be an object.")
    if "representations" not in raw_record or not isinstance(raw_record["representations"], list):
        raise ValueError(f"records[{index}].representations must be a list.")
    if not raw_record["representations"]:
        raise ValueError(f"records[{index}].representations must not be empty.")
    if "evidence" not in raw_record or not isinstance(raw_record["evidence"], list):
        raise ValueError(f"records[{index}].evidence must be a list.")

    payload = dict(raw_record)
    if fixture_notes is not None:
        payload["fixture_notes"] = fixture_notes
    target_ref = payload.get("target_ref")
    if target_ref is None:
        target_ref = source_expansion_recorded_target_ref(source_family, fixture_id)
    if not isinstance(target_ref, str) or not _is_safe_target_ref(target_ref):
        raise ValueError(f"records[{index}].target_ref is not a safe public fixture ref.")
    payload["target_ref"] = target_ref
    return SourceExpansionRecordedSourceRecord(
        target_ref=target_ref,
        source_name=f"{source_family}_fixture",
        payload=payload,
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )


def _require_string(raw_record: dict[str, Any], field_name: str, index: int) -> str:
    value = raw_record.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"records[{index}].{field_name} must be a non-empty string.")
    return value.strip()


def _safe_ref_part(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", normalized):
        raise ValueError(
            f"{field_name} must contain only letters, numbers, dots, underscores, or hyphens."
        )
    return normalized


def _is_safe_target_ref(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._:-]+", value))
