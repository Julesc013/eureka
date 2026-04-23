from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    CompatibilityEvaluationRequest,
    build_demo_compatibility_public_api,
    compatibility_envelope_to_view_model,
)
from surfaces.native.cli.formatters import format_compatibility


class CompatibilitySliceIntegrationTestCase(unittest.TestCase):
    def test_compatibility_slice_preserves_bounded_host_verdict_into_surface_projection(self) -> None:
        public_api = build_demo_compatibility_public_api()
        response = public_api.evaluate_compatibility(
            CompatibilityEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 200)
        view_model = compatibility_envelope_to_view_model(response.body)
        rendered = format_compatibility(view_model)

        self.assertEqual(view_model["status"], "evaluated")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(view_model["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(view_model["source"]["family"], "github_releases")
        self.assertIn("compatibility_status: compatible", rendered)
        self.assertIn("host_profile_id: windows-x86_64", rendered)
        self.assertIn("os_family_supported", rendered)
