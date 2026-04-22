from __future__ import annotations

import unittest

from runtime.engine.provenance import EvidenceSummary


class EvidenceSummaryTestCase(unittest.TestCase):
    def test_to_dict_round_trips_compact_evidence_fields(self) -> None:
        summary = EvidenceSummary(
            claim_kind="version",
            claim_value="v2.65.0",
            asserted_by_family="github_releases",
            asserted_by_label="GitHub Releases",
            evidence_kind="recorded_source_payload",
            evidence_locator="runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
            asserted_at="2024-11-13T00:00:00Z",
        )

        self.assertEqual(
            summary.to_dict(),
            {
                "claim_kind": "version",
                "claim_value": "v2.65.0",
                "asserted_by_family": "github_releases",
                "asserted_by_label": "GitHub Releases",
                "evidence_kind": "recorded_source_payload",
                "evidence_locator": "runtime/connectors/github_releases/fixtures/github_releases_fixture.json",
                "asserted_at": "2024-11-13T00:00:00Z",
            },
        )
