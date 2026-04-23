from __future__ import annotations

import unittest

from runtime.gateway import build_demo_action_plan_public_api
from runtime.gateway.public_api import (
    ActionPlanEvaluationRequest,
    action_plan_envelope_to_view_model,
)


class ActionPlanViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_action_plan_public_api()

    def test_action_plan_envelope_maps_to_shared_view_model(self) -> None:
        response = self.public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                store_actions_enabled=True,
            )
        )

        view_model = action_plan_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "planned")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(view_model["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(view_model["actions"][1]["action_id"], "access_representation")
        self.assertEqual(view_model["actions"][1]["status"], "recommended")
        self.assertEqual(view_model["actions"][5]["route_hint"], "/store/manifest?target_ref=github-release%3Acli%2Fcli%40v2.65.0")
