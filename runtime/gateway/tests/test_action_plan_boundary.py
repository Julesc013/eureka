from __future__ import annotations

import unittest

from runtime.gateway import build_demo_action_plan_public_api
from runtime.gateway.public_api import ActionPlanEvaluationRequest


class ActionPlanPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_action_plan_public_api()

    def test_public_action_plan_boundary_returns_planned_envelope(self) -> None:
        response = self.public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "planned")
        self.assertEqual(response.body["compatibility_status"], "compatible")
        self.assertEqual(response.body["actions"][0]["action_id"], "inspect_primary_representation")
        self.assertIn("route_hint", response.body["actions"][0])

    def test_public_action_plan_boundary_returns_blocked_shape_for_missing_target(self) -> None:
        response = self.public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(response.body["notices"][0]["code"], "target_ref_not_found")
