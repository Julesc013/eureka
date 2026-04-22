from __future__ import annotations

import unittest

from runtime.gateway import build_demo_subject_states_public_api
from runtime.gateway.public_api import SubjectStatesCatalogRequest


class SubjectStatesPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_subject_states_public_api()

    def test_public_subject_states_boundary_returns_ordered_state_listing(self) -> None:
        response = self.public_api.list_subject_states(
            SubjectStatesCatalogRequest.from_parts("archivebox")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "listed")
        self.assertEqual(response.body["subject"]["subject_key"], "archivebox")
        self.assertEqual(response.body["subject"]["state_count"], 3)
        self.assertEqual(
            [entry["target_ref"] for entry in response.body["states"]],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )
        self.assertEqual(response.body["states"][1]["source"]["family"], "github_releases")
        self.assertEqual(response.body["states"][1]["evidence"][1]["claim_kind"], "version")

    def test_public_subject_states_boundary_returns_blocked_shape_for_missing_subject(self) -> None:
        response = self.public_api.list_subject_states(
            SubjectStatesCatalogRequest.from_parts("missing-subject")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["requested_subject_key"], "missing-subject")
        self.assertEqual(response.body["notices"][0]["code"], "subject_not_found")


if __name__ == "__main__":
    unittest.main()
