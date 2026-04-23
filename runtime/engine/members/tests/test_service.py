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
from runtime.engine.interfaces.public import MemberAccessRequest
from runtime.engine.members.service import DeterministicMemberAccessService


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


class DeterministicMemberAccessServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        catalog = _build_demo_catalog()
        acquisition_service = DeterministicAcquisitionService(catalog)
        decomposition_service = DeterministicDecompositionService(acquisition_service)
        self.service = DeterministicMemberAccessService(acquisition_service, decomposition_service)

    def test_known_synthetic_zip_member_can_be_previewed_successfully(self) -> None:
        result = self.service.read_member(
            MemberAccessRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "config/settings.json",
            )
        )

        self.assertEqual(result.member_access_status, "previewed")
        self.assertEqual(result.member_kind, "file")
        self.assertEqual(result.content_type, "application/json")
        self.assertEqual(result.byte_length, len(result.payload or b""))
        self.assertIsNotNone(result.payload)
        self.assertIsNotNone(result.text_preview)
        self.assertIn('"mode": "demo"', result.text_preview or "")
        self.assertEqual(result.reason_codes, ("member_preview_available",))

    def test_unknown_member_path_returns_structured_blocked_result(self) -> None:
        result = self.service.read_member(
            MemberAccessRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "rep.synthetic-demo-app.package",
                "missing/member.txt",
            )
        )

        self.assertEqual(result.member_access_status, "blocked")
        self.assertEqual(result.reason_codes, ("member_not_found",))
        self.assertIsNone(result.payload)

    def test_unsupported_outer_representation_returns_structured_unsupported_result(self) -> None:
        result = self.service.read_member(
            MemberAccessRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "rep.github-release.cli.cli.v2.65.0.asset.0",
                "README.txt",
            )
        )

        self.assertEqual(result.member_access_status, "unsupported")
        self.assertEqual(result.reason_codes, ("representation_format_unsupported",))
        self.assertIsNone(result.payload)
