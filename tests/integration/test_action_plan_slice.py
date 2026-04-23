from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    ActionPlanEvaluationRequest,
    action_plan_envelope_to_view_model,
    build_demo_action_plan_public_api,
)
from surfaces.native.cli.formatters import format_action_plan


class ActionPlanSliceIntegrationTestCase(unittest.TestCase):
    def test_action_plan_slice_preserves_recommendation_statuses_into_surface_projection(self) -> None:
        public_api = build_demo_action_plan_public_api()
        response = public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 200)
        view_model = action_plan_envelope_to_view_model(response.body)
        rendered = format_action_plan(view_model)

        self.assertEqual(view_model["status"], "planned")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(view_model["actions"][1]["action_id"], "access_representation")
        self.assertEqual(view_model["actions"][1]["status"], "recommended")
        self.assertIn("Recommended", rendered)
        self.assertIn("Access gh_2.65.0_windows_amd64.msi", rendered)
        self.assertIn("Available", rendered)
