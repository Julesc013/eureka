from __future__ import annotations

import unittest

from runtime.gateway import build_demo_comparison_public_api
from runtime.gateway.public_api import CompareTargetsRequest, comparison_envelope_to_view_model


class ComparisonViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_comparison_public_api()

    def test_comparison_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.compare_targets(
            CompareTargetsRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
            )
        )

        view_model = comparison_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "compared")
        self.assertEqual(view_model["left"]["version_or_state"], "0.8.5")
        self.assertEqual(view_model["right"]["version_or_state"], "v0.8.5")
        self.assertEqual(view_model["agreements"][0]["category"], "subject_key")
        self.assertEqual(view_model["disagreements"][1]["category"], "version_or_state")
        self.assertEqual(view_model["left"]["evidence"][0]["claim_kind"], "label")


if __name__ == "__main__":
    unittest.main()
