from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import ResolutionRequest, SearchRequest
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService


class GitHubReleaseConnectorFlowTestCase(unittest.TestCase):
    def setUp(self) -> None:
        github_source_records = GitHubReleasesConnector().load_source_records()
        self.github_records = tuple(
            normalize_github_release_record(extract_github_release_source_record(record))
            for record in github_source_records
        )
        synthetic_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in SyntheticSoftwareConnector().load_source_records()
        )
        self.catalog = NormalizedCatalog(synthetic_records + self.github_records)

    def test_extract_and_normalize_steps_produce_bounded_github_release_records(self) -> None:
        first = self.github_records[0]

        self.assertEqual(first.target_ref, "github-release:cli/cli@v2.65.0")
        self.assertEqual(first.source_family, "github_releases")
        self.assertEqual(first.source_family_label, "GitHub Releases")
        self.assertEqual(first.object_id, "obj.github-release.cli.cli")
        self.assertEqual(first.object_label, "GitHub CLI 2.65.0")
        self.assertEqual(first.state_kind, "release")
        self.assertEqual(first.representation_kind, "release_metadata")
        self.assertEqual(
            first.access_path_locator,
            "https://github.com/cli/cli/releases/tag/v2.65.0",
        )
        self.assertEqual(
            [summary.claim_kind for summary in first.evidence],
            ["label", "version", "source_locator"],
        )
        self.assertEqual(first.evidence[1].claim_value, "v2.65.0")
        self.assertEqual(first.evidence[1].asserted_at, "2024-11-13T00:00:00Z")

    def test_deterministic_search_returns_mixed_synthetic_and_github_results(self) -> None:
        service = DeterministicSearchService(self.catalog)

        response = service.search(SearchRequest.from_parts("archive"))

        self.assertEqual(
            [result.target_ref for result in response.results],
            [
                "fixture:software/archive-viewer@0.9.0",
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
                "github-release:archivebox/archivebox@v0.8.5",
            ],
        )
        self.assertEqual(response.results[3].source.family, "github_releases")
        self.assertEqual(response.results[3].source.label, "GitHub Releases")
        self.assertEqual(response.results[3].evidence[0].claim_kind, "label")
        self.assertEqual(response.results[3].evidence[0].asserted_by_label, "GitHub Releases")
        self.assertIsNone(response.absence)

    def test_exact_resolution_can_resolve_known_github_release_target(self) -> None:
        service = ExactMatchResolutionService(self.catalog)

        outcome = service.resolve(ResolutionRequest.from_parts("github-release:cli/cli@v2.65.0"))

        self.assertEqual(outcome.status, "completed")
        assert outcome.result is not None
        self.assertEqual(outcome.result.primary_object.id, "obj.github-release.cli.cli")
        self.assertEqual(outcome.result.source.family, "github_releases")
        self.assertEqual(outcome.result.source.label, "GitHub Releases")
        self.assertEqual(
            outcome.result.source.locator,
            "https://github.com/cli/cli/releases/tag/v2.65.0",
        )
        self.assertEqual(outcome.result.evidence[1].claim_kind, "version")
        self.assertEqual(outcome.result.evidence[1].claim_value, "v2.65.0")

    def test_no_result_search_remains_honest_for_mixed_corpus(self) -> None:
        service = DeterministicSearchService(self.catalog)

        response = service.search(SearchRequest.from_parts("missing-live-source"))

        self.assertEqual(response.results, ())
        assert response.absence is not None
        self.assertEqual(response.absence.code, "search_no_matches")
        self.assertEqual(
            response.absence.message,
            "No bounded records matched query 'missing-live-source'.",
        )
