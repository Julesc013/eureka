from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.acquisition.service import DeterministicAcquisitionService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.decomposition.service import DeterministicDecompositionService
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import DecompositionRequest


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


class DeterministicDecompositionServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        acquisition_service = DeterministicAcquisitionService(_build_demo_catalog())
        self.service = DeterministicDecompositionService(acquisition_service)

    def test_synthetic_decomposable_representation_returns_member_listing(self) -> None:
        result = self.service.decompose_representation(
            DecompositionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
            )
        )

        self.assertEqual(result.decomposition_status, "decomposed")
        self.assertEqual(result.representation_kind, "fixture_archive")
        self.assertEqual(result.filename, "synthetic-demo-app-package.zip")
        self.assertEqual(result.content_type, "application/zip")
        self.assertEqual(
            [member.member_path for member in result.members],
            [
                "config/settings.json",
                "docs/evidence.txt",
                "README.txt",
            ],
        )
        self.assertEqual(result.members[0].content_type, "application/json")
        self.assertEqual(result.members[1].content_type, "text/plain")
        self.assertEqual(result.members[2].byte_length, 62)
        self.assertEqual(result.reason_codes, ("representation_decomposed",))

    def test_unsupported_fetchable_representation_returns_structured_unsupported_result(self) -> None:
        result = self.service.decompose_representation(
            DecompositionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
            )
        )

        self.assertEqual(result.decomposition_status, "unsupported")
        self.assertEqual(result.representation_kind, "release_asset")
        self.assertEqual(result.filename, "gh_2.65.0_windows_amd64.msi")
        self.assertEqual(result.reason_codes, ("representation_format_unsupported",))
        self.assertEqual(result.members, ())

    def test_unknown_representation_returns_structured_blocked_result(self) -> None:
        result = self.service.decompose_representation(
            DecompositionRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.unknown",
            )
        )

        self.assertEqual(result.decomposition_status, "blocked")
        self.assertEqual(result.reason_codes, ("representation_not_found",))
        self.assertEqual(result.members, ())


if __name__ == "__main__":
    unittest.main()
