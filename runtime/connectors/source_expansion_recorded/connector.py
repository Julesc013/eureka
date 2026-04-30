from __future__ import annotations

from pathlib import Path

from runtime.connectors.source_expansion_recorded.source import (
    load_source_expansion_recorded_source_records,
)
from runtime.engine.interfaces.ingest import SourceExpansionRecordedSourceRecord


class SourceExpansionRecordedConnector:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path

    def load_source_records(self) -> tuple[SourceExpansionRecordedSourceRecord, ...]:
        return load_source_expansion_recorded_source_records(self._fixture_path)

    def default_target_ref(self) -> str:
        records = self.load_source_records()
        if not records:
            raise ValueError("Source expansion recorded connector returned no source records.")
        return records[0].target_ref
