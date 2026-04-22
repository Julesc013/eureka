from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.compare import DeterministicComparisonService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import ComparisonRequest


class DeterministicComparisonServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        synthetic_records = tuple(
            normalize_extracted_record(extract_synthetic_source_record(record))
            for record in SyntheticSoftwareConnector().load_source_records()
        )
        github_records = tuple(
            normalize_github_release_record(extract_github_release_source_record(record))
            for record in GitHubReleasesConnector().load_source_records()
        )
        self.catalog = NormalizedCatalog(synthetic_records + github_records)
        self.service = DeterministicComparisonService(self.catalog)

    def test_comparison_produces_agreements_and_disagreements_for_overlapping_pair(self) -> None:
        result = self.service.compare(
            ComparisonRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
            )
        )

        self.assertEqual(result.status, "compared")
        self.assertEqual(result.left.status, "completed")
        self.assertEqual(result.right.status, "completed")
        self.assertEqual(
            [(agreement.category, agreement.value) for agreement in result.agreements],
            [
                ("subject_key", "archivebox"),
                ("object_kind", "software"),
                ("normalized_version_or_state", "0.8.5"),
            ],
        )
        self.assertEqual(
            [(disagreement.category, disagreement.left_value, disagreement.right_value) for disagreement in result.disagreements],
            [
                ("object_label", "ArchiveBox 0.8.5", "ArchiveBox v0.8.5"),
                ("version_or_state", "0.8.5", "v0.8.5"),
                ("source_family", "synthetic_fixture", "github_releases"),
                (
                    "source_locator",
                    "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    "https://github.com/archivebox/archivebox/releases/tag/v0.8.5",
                ),
            ],
        )
        self.assertEqual(result.left.evidence[0].claim_kind, "label")
        self.assertEqual(result.right.evidence[1].claim_kind, "version")

    def test_comparison_supports_synthetic_to_synthetic_pair(self) -> None:
        result = self.service.compare(
            ComparisonRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "fixture:software/synthetic-demo-suite@2.0.0",
            )
        )

        self.assertEqual(result.status, "compared")
        self.assertEqual(result.left.source.family, "synthetic_fixture")
        self.assertEqual(result.right.source.family, "synthetic_fixture")
        self.assertEqual(
            [(agreement.category, agreement.value) for agreement in result.agreements],
            [("object_kind", "software")],
        )
        self.assertEqual(
            [disagreement.category for disagreement in result.disagreements],
            ["object_label", "version_or_state"],
        )

    def test_comparison_returns_blocked_shape_when_one_side_is_unresolved(self) -> None:
        result = self.service.compare(
            ComparisonRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                "fixture:software/missing-demo-app@0.0.1",
            )
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.left.status, "completed")
        self.assertEqual(result.right.status, "blocked")
        self.assertEqual(result.agreements, ())
        self.assertEqual(result.disagreements, ())
        self.assertEqual(result.notices[0].code, "comparison_right_unresolved")
        self.assertEqual(result.right.notices[0].code, "target_ref_not_found")


if __name__ == "__main__":
    unittest.main()
