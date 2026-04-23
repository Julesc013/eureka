from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.acquisition.service import DeterministicAcquisitionService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import AcquisitionRequest


def _build_demo_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


class DeterministicAcquisitionServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DeterministicAcquisitionService(_build_demo_catalog())

    def test_synthetic_fetchable_representation_can_be_fetched_successfully(self) -> None:
        result = self.service.fetch_representation(
            AcquisitionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.source",
            )
        )

        self.assertEqual(result.acquisition_status, "fetched")
        self.assertEqual(result.representation_kind, "fixture_artifact")
        self.assertEqual(result.filename, "synthetic-demo-app.bundle")
        self.assertEqual(result.content_type, "application/vnd.eureka.synthetic.bundle")
        self.assertEqual(result.byte_length, len(result.payload or b""))
        self.assertIsNotNone(result.payload)
        self.assertIn(b"EUREKA-SYNTHETIC-BUNDLE", result.payload or b"")

    def test_github_release_fetchable_representation_can_be_fetched_from_recorded_fixture(self) -> None:
        result = self.service.fetch_representation(
            AcquisitionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
            )
        )

        self.assertEqual(result.acquisition_status, "fetched")
        self.assertEqual(result.source_family, "github_releases")
        self.assertEqual(result.filename, "gh_2.65.0_windows_amd64.msi")
        self.assertEqual(result.content_type, "application/x-msi")
        self.assertEqual(result.byte_length, len(result.payload or b""))
        self.assertIsNotNone(result.payload)
        self.assertIn(b"MSI-STUB", result.payload or b"")

    def test_non_fetchable_representation_returns_structured_unavailable_result(self) -> None:
        result = self.service.fetch_representation(
            AcquisitionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.release-metadata",
            )
        )

        self.assertEqual(result.acquisition_status, "unavailable")
        self.assertEqual(result.reason_codes, ("representation_not_fetchable",))
        self.assertIsNone(result.payload)
        self.assertEqual(result.access_kind, "view")

    def test_unknown_representation_returns_structured_blocked_result(self) -> None:
        result = self.service.fetch_representation(
            AcquisitionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.missing",
            )
        )

        self.assertEqual(result.acquisition_status, "blocked")
        self.assertEqual(result.reason_codes, ("representation_not_found",))
        self.assertIsNone(result.payload)


if __name__ == "__main__":
    unittest.main()
