from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.absence import DeterministicAbsenceService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import ResolveAbsenceRequest, SearchAbsenceRequest


class DeterministicAbsenceServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DeterministicAbsenceService(_build_demo_normalized_catalog())

    def test_exact_resolution_miss_produces_bounded_absence_report(self) -> None:
        report = self.service.explain_resolution_miss(
            ResolveAbsenceRequest.from_parts("fixture:software/archivebox@9.9.9"),
        )

        self.assertEqual(report.request_kind, "resolve")
        self.assertEqual(report.status, "explained")
        self.assertEqual(report.likely_reason_code, "known_subject_different_state")
        self.assertEqual(report.checked_source_families, ("synthetic_fixture", "github_releases"))
        self.assertEqual(len(report.near_matches), 3)
        self.assertEqual(report.near_matches[0].target_ref, "fixture:software/archivebox@0.8.5")
        self.assertEqual(report.near_matches[1].target_ref, "github-release:archivebox/archivebox@v0.8.5")
        self.assertEqual(report.near_matches[2].target_ref, "github-release:archivebox/archivebox@v0.8.4")
        self.assertEqual(report.near_matches[1].match_kind, "same_subject_different_state")
        self.assertEqual(report.near_matches[1].evidence[1].claim_kind, "version")

    def test_search_no_result_case_produces_bounded_absence_report(self) -> None:
        report = self.service.explain_search_miss(SearchAbsenceRequest.from_parts("archive box"))

        self.assertEqual(report.request_kind, "search")
        self.assertEqual(report.status, "explained")
        self.assertEqual(report.likely_reason_code, "related_subjects_exist")
        self.assertEqual(report.checked_record_count, 8)
        self.assertEqual(report.checked_subject_count, 6)
        self.assertGreaterEqual(len(report.near_matches), 3)
        self.assertEqual(report.near_matches[0].subject_key, "archivebox")
        self.assertEqual(report.near_matches[0].match_kind, "related_subject")
        self.assertTrue(report.next_steps)

    def test_missing_subject_space_reports_checked_source_families_honestly(self) -> None:
        report = self.service.explain_resolution_miss(
            ResolveAbsenceRequest.from_parts("fixture:software/definitely-missing@0.0.1"),
        )

        self.assertEqual(report.likely_reason_code, "subject_unknown_in_bounded_corpus")
        self.assertEqual(report.checked_source_families, ("synthetic_fixture", "github_releases"))
        self.assertEqual(report.near_matches, ())

    def test_search_miss_without_related_subjects_reports_absence_without_fake_near_matches(self) -> None:
        report = self.service.explain_search_miss(
            SearchAbsenceRequest.from_parts("totally missing bounded query"),
        )

        self.assertEqual(report.likely_reason_code, "query_not_present_in_bounded_corpus")
        self.assertEqual(report.near_matches, ())


def _build_demo_normalized_catalog() -> NormalizedCatalog:
    synthetic_connector = SyntheticSoftwareConnector()
    github_connector = GitHubReleasesConnector()
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in synthetic_connector.load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in github_connector.load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)
