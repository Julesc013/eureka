from __future__ import annotations

from pathlib import Path

from runtime.connectors.github_releases.source import load_github_release_source_records
from runtime.engine.interfaces.ingest import GitHubReleaseSourceRecord


class GitHubReleasesConnector:
    def __init__(self, fixture_path: Path | None = None) -> None:
        self._fixture_path = fixture_path

    def load_source_records(self) -> tuple[GitHubReleaseSourceRecord, ...]:
        return load_github_release_source_records(self._fixture_path)

    def default_target_ref(self) -> str:
        records = self.load_source_records()
        if not records:
            raise ValueError("GitHub releases connector returned no source records.")
        return records[0].target_ref
