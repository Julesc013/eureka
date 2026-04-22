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
from runtime.engine.interfaces.public import RepresentationsRequest
from runtime.engine.representations.service import DeterministicRepresentationsService


class DeterministicRepresentationsServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        synthetic_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in SyntheticSoftwareConnector().load_source_records()
        )
        github_records = tuple(
            normalize_github_release_record(extract_github_release_source_record(record))
            for record in GitHubReleasesConnector().load_source_records()
        )
        self.service = DeterministicRepresentationsService(
            NormalizedCatalog(synthetic_records + github_records)
        )

    def test_synthetic_target_returns_bounded_representation_and_access_path_summaries(self) -> None:
        result = self.service.list_representations(
            RepresentationsRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(result.status, "available")
        self.assertEqual(len(result.representations), 2)
        self.assertEqual(result.representations[0].representation_kind, "fixture_artifact")
        self.assertEqual(result.representations[0].access_kind, "inspect")
        self.assertEqual(
            result.representations[1].access_locator,
            "contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_github_release_target_returns_release_page_and_asset_summaries(self) -> None:
        result = self.service.list_representations(
            RepresentationsRequest.from_parts("github-release:cli/cli@v2.65.0")
        )

        self.assertEqual(result.status, "available")
        self.assertEqual(len(result.representations), 3)
        self.assertEqual(result.representations[0].representation_kind, "release_page")
        self.assertEqual(result.representations[0].access_kind, "view")
        self.assertEqual(result.representations[1].representation_kind, "release_asset")
        self.assertEqual(result.representations[1].source_family, "github_releases")
        self.assertEqual(
            result.representations[1].access_locator,
            "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_windows_amd64.msi",
        )

    def test_missing_target_returns_blocked_shape(self) -> None:
        result = self.service.list_representations(
            RepresentationsRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.target_ref, "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(result.representations, ())
        self.assertEqual(result.notices[0].code, "target_ref_not_found")
