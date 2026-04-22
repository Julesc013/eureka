from __future__ import annotations

import unittest

from runtime.connectors.github_releases import (
    GitHubReleasesConnector,
    github_release_target_ref,
    load_github_release_source_records,
)


class GitHubReleasesConnectorTestCase(unittest.TestCase):
    def test_source_loading_returns_small_recorded_github_release_corpus(self) -> None:
        records = load_github_release_source_records()

        self.assertEqual(len(records), 3)
        self.assertEqual(
            [record.target_ref for record in records],
            [
                "github-release:cli/cli@v2.65.0",
                "github-release:archivebox/archivebox@v0.8.4",
                "github-release:archivebox/archivebox@v0.8.5",
            ],
        )
        self.assertEqual(records[0].source_name, "github_releases_fixture")
        self.assertEqual(
            records[0].source_locator,
            "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
        )

    def test_connector_reports_default_target_ref_from_loaded_source(self) -> None:
        connector = GitHubReleasesConnector()

        self.assertEqual(connector.default_target_ref(), "github-release:cli/cli@v2.65.0")

    def test_target_ref_helper_normalizes_repository_name(self) -> None:
        self.assertEqual(
            github_release_target_ref("CLI/CLI", "v2.65.0"),
            "github-release:cli/cli@v2.65.0",
        )
