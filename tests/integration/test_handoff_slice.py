from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    RepresentationSelectionEvaluationRequest,
    build_demo_representation_selection_public_api,
    representation_selection_envelope_to_view_model,
)
from surfaces.native.cli.formatters import format_handoff


class HandoffSliceIntegrationTestCase(unittest.TestCase):
    def test_handoff_slice_preserves_host_and_strategy_aware_selection_into_surface_projection(self) -> None:
        public_api = build_demo_representation_selection_public_api()
        inspect_response = public_api.select_representation(
            RepresentationSelectionEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "inspect",
            )
        )
        acquire_response = public_api.select_representation(
            RepresentationSelectionEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )

        self.assertEqual(inspect_response.status_code, 200)
        self.assertEqual(acquire_response.status_code, 200)
        inspect_view_model = representation_selection_envelope_to_view_model(inspect_response.body)
        acquire_view_model = representation_selection_envelope_to_view_model(acquire_response.body)
        rendered = format_handoff(acquire_view_model)

        self.assertEqual(inspect_view_model["status"], "available")
        self.assertEqual(acquire_view_model["status"], "available")
        self.assertEqual(
            inspect_view_model["resolved_resource_id"],
            acquire_view_model["resolved_resource_id"],
        )
        self.assertEqual(inspect_view_model["evidence"], acquire_view_model["evidence"])
        self.assertEqual(
            inspect_view_model["preferred_representation_id"],
            "rep.github-release.cli.cli.release-metadata",
        )
        self.assertEqual(
            acquire_view_model["preferred_representation_id"],
            "rep.github-release.cli.cli.v2.65.0.asset.0",
        )
        self.assertIn("Preferred", rendered)
        self.assertIn("gh_2.65.0_windows_amd64.msi", rendered)
        self.assertIn("Available", rendered)
        self.assertIn("GitHub CLI 2.65.0 release page", rendered)


if __name__ == "__main__":
    unittest.main()
