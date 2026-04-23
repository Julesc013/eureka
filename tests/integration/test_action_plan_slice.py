from __future__ import annotations

import unittest

from runtime.gateway.public_api import (
    ActionPlanEvaluationRequest,
    action_plan_envelope_to_view_model,
    build_demo_action_plan_public_api,
)
from surfaces.native.cli.formatters import format_action_plan


class ActionPlanSliceIntegrationTestCase(unittest.TestCase):
    def test_action_plan_slice_preserves_strategy_aware_emphasis_into_surface_projection(self) -> None:
        public_api = build_demo_action_plan_public_api()
        inspect_response = public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "inspect",
            )
        )
        acquire_response = public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )

        self.assertEqual(inspect_response.status_code, 200)
        self.assertEqual(acquire_response.status_code, 200)
        inspect_view_model = action_plan_envelope_to_view_model(inspect_response.body)
        acquire_view_model = action_plan_envelope_to_view_model(acquire_response.body)
        rendered = format_action_plan(acquire_view_model)

        self.assertEqual(inspect_view_model["status"], "planned")
        self.assertEqual(acquire_view_model["status"], "planned")
        self.assertEqual(inspect_view_model["resolved_resource_id"], acquire_view_model["resolved_resource_id"])
        self.assertEqual(inspect_view_model["evidence"], acquire_view_model["evidence"])
        inspect_direct = next(action for action in inspect_view_model["actions"] if action["action_id"] == "access_representation")
        acquire_direct = next(action for action in acquire_view_model["actions"] if action["action_id"] == "access_representation")
        self.assertEqual(inspect_direct["status"], "available")
        self.assertEqual(acquire_direct["status"], "recommended")
        self.assertEqual(acquire_view_model["strategy_profile"]["strategy_id"], "acquire")
        self.assertIn("Recommended", rendered)
        self.assertIn("Access gh_2.65.0_windows_amd64.msi", rendered)
        self.assertIn("Available", rendered)
