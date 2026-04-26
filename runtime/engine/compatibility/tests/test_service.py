from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.local_bundle_fixtures import LocalBundleFixturesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.compatibility.service import DeterministicCompatibilityService
from runtime.engine.synthetic_records import synthesize_member_normalized_records
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_local_bundle_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
    normalize_local_bundle_record,
)
from runtime.engine.interfaces.public.compatibility import CompatibilityRequest


def _build_demo_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    local_bundle_records = tuple(
        normalize_local_bundle_record(extract_local_bundle_source_record(record))
        for record in LocalBundleFixturesConnector().load_source_records()
    )
    synthetic_member_records = synthesize_member_normalized_records(local_bundle_records)
    return NormalizedCatalog(
        synthetic_records + github_records + local_bundle_records + synthetic_member_records
    )


class DeterministicCompatibilityServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DeterministicCompatibilityService(_build_demo_catalog())

    def test_synthetic_target_with_compatible_host_returns_compatible(self) -> None:
        result = self.service.evaluate_compatibility(
            CompatibilityRequest.from_parts(
                "fixture:software/compatibility-lab@3.2.1",
                "windows-x86_64",
            )
        )

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.compatibility_status, "compatible")
        self.assertEqual(result.host_profile.host_profile_id, "windows-x86_64")
        self.assertEqual(result.primary_object.label, "Compatibility Lab")
        self.assertEqual(
            [reason.code for reason in result.reasons],
            ["os_family_supported", "architecture_supported"],
        )

    def test_synthetic_target_with_incompatible_host_returns_incompatible(self) -> None:
        result = self.service.evaluate_compatibility(
            CompatibilityRequest.from_parts(
                "fixture:software/archive-viewer@0.9.0",
                "linux-x86_64",
            )
        )

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.compatibility_status, "incompatible")
        self.assertEqual(result.host_profile.os_family, "linux")
        self.assertEqual([reason.code for reason in result.reasons], ["os_family_not_supported"])
        self.assertIn("Try another bootstrap host profile preset.", result.next_steps)

    def test_target_with_insufficient_data_returns_unknown(self) -> None:
        result = self.service.evaluate_compatibility(
            CompatibilityRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.compatibility_status, "unknown")
        self.assertEqual(result.reasons[0].code, "compatibility_requirements_missing")
        self.assertIn("Inspect known representations and evidence directly.", result.next_steps)

    def test_github_release_target_can_return_bounded_compatibility_verdict(self) -> None:
        result = self.service.evaluate_compatibility(
            CompatibilityRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.compatibility_status, "compatible")
        self.assertEqual(result.source.family, "github_releases")
        self.assertEqual(result.source.label, "GitHub Releases")
        self.assertEqual(result.resolved_resource_id[:16], "resolved:sha256:")

    def test_member_target_returns_source_backed_compatibility_evidence(self) -> None:
        member = next(
            record
            for record in _build_demo_catalog().records
            if record.member_path == "drivers/wifi/thinkpad_t42/windows2000/driver.inf"
        )

        result = self.service.evaluate_compatibility(
            CompatibilityRequest.from_parts(member.target_ref, "windows-x86_64")
        )

        self.assertEqual(result.status, "evaluated")
        self.assertTrue(result.compatibility_evidence)
        self.assertIsNotNone(result.compatibility_evidence_verdict)
        assert result.compatibility_evidence_verdict is not None
        self.assertEqual(result.compatibility_evidence_verdict.verdict, "partial")
        self.assertEqual(result.compatibility_evidence[0].platform.name, "Windows 2000")
