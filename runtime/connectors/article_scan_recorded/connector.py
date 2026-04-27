from __future__ import annotations

from pathlib import Path

from runtime.connectors.article_scan_recorded.source import (
    load_article_scan_recorded_source_records,
)
from runtime.engine.interfaces.ingest import ArticleScanRecordedSourceRecord


class ArticleScanRecordedConnector:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path

    def load_source_records(self) -> tuple[ArticleScanRecordedSourceRecord, ...]:
        return load_article_scan_recorded_source_records(self._fixture_path)

    def default_target_ref(self) -> str:
        records = self.load_source_records()
        if not records:
            raise ValueError("Article scan recorded connector returned no source records.")
        return records[0].target_ref
