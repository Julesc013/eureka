from __future__ import annotations

import unittest

from runtime.gateway import build_demo_comparison_public_api
from runtime.gateway.public_api import CompareTargetsRequest


class ComparisonPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_comparison_public_api()

    def test_public_comparison_boundary_returns_agreements_and_disagreements(self) -> None:
        response = self.public_api.compare_targets(
            CompareTargetsRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "compared")
        self.assertEqual(response.body["left"]["target_ref"], "fixture:software/archivebox@0.8.5")
        self.assertEqual(response.body["right"]["target_ref"], "github-release:archivebox/archivebox@v0.8.5")
        self.assertEqual(
            [(entry["category"], entry["value"]) for entry in response.body["agreements"]],
            [
                ("subject_key", "archivebox"),
                ("object_kind", "software"),
                ("normalized_version_or_state", "0.8.5"),
            ],
        )
        self.assertEqual(response.body["disagreements"][0]["category"], "object_label")
        self.assertEqual(response.body["right"]["evidence"][1]["claim_kind"], "version")

    def test_public_comparison_boundary_returns_blocked_shape_for_unresolved_side(self) -> None:
        response = self.public_api.compare_targets(
            CompareTargetsRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                "fixture:software/missing-demo-app@0.0.1",
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["left"]["status"], "completed")
        self.assertEqual(response.body["right"]["status"], "blocked")
        self.assertEqual(response.body["notices"][0]["code"], "comparison_right_unresolved")


if __name__ == "__main__":
    unittest.main()
