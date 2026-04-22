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
from runtime.engine.interfaces.public import SubjectStatesRequest
from runtime.engine.states import DeterministicSubjectStatesService


class DeterministicSubjectStatesServiceTestCase(unittest.TestCase):
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
        self.service = DeterministicSubjectStatesService(self.catalog)

    def test_grouping_produces_multiple_states_for_archivebox(self) -> None:
        result = self.service.list_states(SubjectStatesRequest.from_parts("archivebox"))

        self.assertEqual(result.status, "listed")
        assert result.subject is not None
        self.assertEqual(result.subject.subject_key, "archivebox")
        self.assertEqual(result.subject.subject_label, "ArchiveBox")
        self.assertEqual(result.subject.state_count, 3)
        self.assertEqual(result.subject.source_family_hint, "mixed")
        self.assertEqual(
            [state.target_ref for state in result.states],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )

    def test_state_ordering_is_deterministic_and_version_first(self) -> None:
        result = self.service.list_states(SubjectStatesRequest.from_parts("archivebox"))

        self.assertEqual(
            [state.normalized_version_or_state for state in result.states],
            ["0.8.5", "0.8.5", "0.8.4"],
        )
        self.assertEqual(result.states[0].resolved_resource_id[:16], "resolved:sha256:")
        self.assertLess(result.states[0].target_ref, result.states[1].target_ref)

    def test_missing_subject_returns_structured_blocked_result(self) -> None:
        result = self.service.list_states(SubjectStatesRequest.from_parts("missing-subject"))

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.requested_subject_key, "missing-subject")
        self.assertIsNone(result.subject)
        self.assertEqual(result.states, ())
        self.assertEqual(result.notices[0].code, "subject_not_found")

    def test_state_summaries_preserve_source_and_evidence(self) -> None:
        result = self.service.list_states(SubjectStatesRequest.from_parts("archivebox"))

        synthetic_state = result.states[0]
        github_state = result.states[1]

        self.assertEqual(synthetic_state.source.family, "synthetic_fixture")
        self.assertEqual(synthetic_state.evidence[0].claim_kind, "label")
        self.assertEqual(github_state.source.family, "github_releases")
        self.assertEqual(github_state.source.label, "GitHub Releases")
        self.assertEqual(github_state.evidence[1].claim_kind, "version")


if __name__ == "__main__":
    unittest.main()
