from __future__ import annotations

import unittest

from runtime.gateway import build_demo_representation_selection_public_api
from runtime.gateway.public_api import RepresentationSelectionEvaluationRequest


class RepresentationSelectionPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_representation_selection_public_api()

    def test_public_handoff_boundary_returns_bounded_selection_envelope(self) -> None:
        response = self.public_api.select_representation(
            RepresentationSelectionEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "available")
        self.assertEqual(response.body["target_ref"], "github-release:cli/cli@v2.65.0")
        self.assertEqual(response.body["compatibility_status"], "compatible")
        self.assertEqual(response.body["strategy_profile"]["strategy_id"], "acquire")
        self.assertEqual(response.body["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(
            response.body["preferred_representation_id"],
            "rep.github-release.cli.cli.v2.65.0.asset.0",
        )
        preferred = next(
            entry for entry in response.body["selections"] if entry["selection_status"] == "preferred"
        )
        self.assertEqual(preferred["label"], "gh_2.65.0_windows_amd64.msi")

    def test_public_handoff_boundary_returns_blocked_shape_for_missing_target(self) -> None:
        response = self.public_api.select_representation(
            RepresentationSelectionEvaluationRequest.from_parts(
                "fixture:software/missing-demo-app@0.0.1"
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(response.body["notices"][0]["code"], "target_ref_not_found")


if __name__ == "__main__":
    unittest.main()
