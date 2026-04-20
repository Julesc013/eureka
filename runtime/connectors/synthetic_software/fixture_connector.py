from __future__ import annotations

from pathlib import Path

from runtime.connectors.synthetic_software.fixture_source import load_synthetic_source_records
from runtime.engine.interfaces.ingest import SyntheticSourceRecord


class SyntheticSoftwareConnector:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path

    def load_source_records(self) -> tuple[SyntheticSourceRecord, ...]:
        return load_synthetic_source_records(self._fixture_path)

    def default_target_ref(self) -> str:
        records = self.load_source_records()
        if not records:
            raise ValueError("Synthetic software connector returned no source records.")
        return records[0].target_ref
