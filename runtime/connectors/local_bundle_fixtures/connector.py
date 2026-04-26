from __future__ import annotations

from pathlib import Path

from runtime.connectors.local_bundle_fixtures.source import load_local_bundle_source_records
from runtime.engine.interfaces.ingest import LocalBundleSourceRecord


class LocalBundleFixturesConnector:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path

    def load_source_records(self) -> tuple[LocalBundleSourceRecord, ...]:
        return load_local_bundle_source_records(self._fixture_path)

    def default_target_ref(self) -> str:
        records = self.load_source_records()
        if not records:
            raise ValueError("Local bundle fixtures connector returned no source records.")
        return records[0].target_ref
