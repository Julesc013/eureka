from __future__ import annotations

import unittest

from runtime.gateway import build_demo_absence_public_api
from runtime.gateway.public_api import ExplainResolveMissRequest, ExplainSearchMissRequest


class AbsencePublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_absence_public_api()

    def test_public_absence_boundary_explains_exact_resolution_miss(self) -> None:
        response = self.public_api.explain_resolution_miss(
            ExplainResolveMissRequest.from_parts("fixture:software/archivebox@9.9.9"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["request_kind"], "resolve")
        self.assertEqual(response.body["status"], "explained")
        self.assertEqual(response.body["likely_reason_code"], "known_subject_different_state")
        self.assertEqual(
            [entry["target_ref"] for entry in response.body["near_matches"]],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )
        self.assertEqual(response.body["near_matches"][1]["evidence"][1]["claim_kind"], "version")

    def test_public_absence_boundary_explains_search_miss(self) -> None:
        response = self.public_api.explain_search_miss(
            ExplainSearchMissRequest.from_parts("archive box"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["request_kind"], "search")
        self.assertEqual(response.body["status"], "explained")
        self.assertEqual(response.body["likely_reason_code"], "related_subjects_exist")
        self.assertEqual(response.body["checked_source_families"], ["synthetic_fixture", "github_releases"])
        self.assertGreaterEqual(len(response.body["near_matches"]), 3)
