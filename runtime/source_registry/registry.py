from __future__ import annotations

import json
from pathlib import Path

from runtime.source_registry.source_record import (
    DuplicateSourceIdError,
    MalformedSourceRecordError,
    SourceInventoryNotFoundError,
    SourceRecord,
    SourceRecordNotFoundError,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "sources"


class SourceRegistry:
    def __init__(self, records: tuple[SourceRecord, ...]) -> None:
        self._records = records
        self._records_by_id = {record.source_id: record for record in records}

    @property
    def records(self) -> tuple[SourceRecord, ...]:
        return self._records

    def list_records(
        self,
        *,
        status: str | None = None,
        source_family: str | None = None,
        role: str | None = None,
        surface: str | None = None,
        coverage_depth: str | None = None,
        capability: str | None = None,
        connector_mode: str | None = None,
    ) -> tuple[SourceRecord, ...]:
        return tuple(
            record
            for record in self._records
            if (status is None or record.status == status)
            and (source_family is None or record.source_family == source_family)
            and (role is None or role in record.roles)
            and (surface is None or surface in record.surfaces)
            and (coverage_depth is None or record.coverage.coverage_depth == coverage_depth)
            and (capability is None or record.capabilities.supports(capability))
            and (connector_mode is None or record.coverage.connector_mode == connector_mode)
        )

    def get_record(self, source_id: str) -> SourceRecord:
        try:
            return self._records_by_id[source_id]
        except KeyError as error:
            raise SourceRecordNotFoundError(source_id) from error


def load_source_registry(inventory_dir: Path | None = None) -> SourceRegistry:
    normalized_inventory_dir = inventory_dir or DEFAULT_SOURCE_INVENTORY_DIR
    if not normalized_inventory_dir.is_dir():
        raise SourceInventoryNotFoundError(normalized_inventory_dir)

    records: list[SourceRecord] = []
    seen_source_ids: dict[str, Path] = {}

    for source_path in sorted(normalized_inventory_dir.glob("*.source.json")):
        raw_record = _load_json_record(source_path)
        if not isinstance(raw_record, dict):
            raise MalformedSourceRecordError(source_path, "Source record root must be an object.")
        record = SourceRecord.from_mapping(raw_record, source_path=source_path)
        first_path = seen_source_ids.get(record.source_id)
        if first_path is not None:
            raise DuplicateSourceIdError(record.source_id, first_path, source_path)
        seen_source_ids[record.source_id] = source_path
        records.append(record)

    return SourceRegistry(tuple(records))


def _load_json_record(source_path: Path) -> object:
    try:
        with source_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise MalformedSourceRecordError(source_path, f"Malformed JSON: {error.msg}.") from error
