from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.handoff.service import DeterministicRepresentationSelectionService
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import RepresentationSelectionRequest


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


class DeterministicRepresentationSelectionServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DeterministicRepresentationSelectionService(_build_demo_catalog())

    def test_target_with_multiple_representations_produces_bounded_selection_result(self) -> None:
        result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts("github-release:cli/cli@v2.65.0")
        )

        self.assertEqual(result.status, "available")
        self.assertEqual(result.resolved_resource_id[:16], "resolved:sha256:")
        self.assertEqual(result.primary_object.label, "GitHub CLI 2.65.0")
        self.assertEqual(result.preferred_representation_id, "rep.github-release.cli.cli.release-metadata")
        self.assertEqual(len(result.selections), 3)
        self.assertEqual(result.selections[0].selection_status, "preferred")
        self.assertEqual(result.selections[1].representation_kind, "release_asset")

    def test_host_profile_changes_suitability_for_payload_representation(self) -> None:
        windows_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )
        linux_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "linux-x86_64",
                "acquire",
            )
        )

        windows_asset = next(
            entry
            for entry in windows_result.selections
            if entry.representation_id == "rep.github-release.cli.cli.v2.65.0.asset.0"
        )
        linux_asset = next(
            entry
            for entry in linux_result.selections
            if entry.representation_id == "rep.github-release.cli.cli.v2.65.0.asset.0"
        )

        self.assertEqual(windows_result.compatibility_status, "compatible")
        self.assertEqual(windows_asset.selection_status, "preferred")
        self.assertEqual(linux_result.compatibility_status, "incompatible")
        self.assertEqual(linux_asset.selection_status, "unsuitable")
        self.assertEqual(linux_asset.reason_codes[0], "host_incompatible_for_payload_representation")

    def test_strategy_changes_which_suitable_representation_is_preferred(self) -> None:
        inspect_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "inspect",
            )
        )
        preserve_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "preserve",
            )
        )
        acquire_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )

        self.assertEqual(
            inspect_result.preferred_representation_id,
            "rep.github-release.cli.cli.release-metadata",
        )
        self.assertEqual(
            preserve_result.preferred_representation_id,
            "rep.github-release.cli.cli.v2.65.0.asset.1",
        )
        self.assertEqual(
            acquire_result.preferred_representation_id,
            "rep.github-release.cli.cli.v2.65.0.asset.0",
        )

    def test_unsuitable_and_unknown_entries_remain_explicit_with_reasons(self) -> None:
        unsuitable_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "linux-x86_64",
                "acquire",
            )
        )
        unknown_result = self.service.select_representation(
            RepresentationSelectionRequest.from_parts(
                "github-release:archivebox/archivebox@v0.8.5",
                "windows-x86_64",
                "acquire",
            )
        )

        unsuitable_entry = next(
            entry
            for entry in unsuitable_result.selections
            if entry.selection_status == "unsuitable"
        )
        unknown_entry = next(
            entry
            for entry in unknown_result.selections
            if entry.selection_status == "unknown"
        )

        self.assertEqual(unsuitable_entry.reason_codes[0], "host_incompatible_for_payload_representation")
        self.assertEqual(unknown_result.compatibility_status, "unknown")
        self.assertEqual(unknown_entry.reason_codes[0], "compatibility_unknown_for_payload_representation")


if __name__ == "__main__":
    unittest.main()
