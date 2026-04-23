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
                "acquire",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "planned")
        self.assertEqual(response.body["compatibility_status"], "compatible")
        self.assertEqual(response.body["strategy_profile"]["strategy_id"], "acquire")
        self.assertEqual(response.body["actions"][1]["action_id"], "access_representation")
        self.assertEqual(response.body["actions"][1]["status"], "recommended")
        self.assertIn("route_hint", response.body["actions"][1])
        self.assertEqual(response.body["evidence"][0]["claim_kind"], "label")

    def test_public_action_plan_boundary_can_surface_compare_strategy_routes(self) -> None:
        response = self.public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                None,
                "compare",
            )
        )

        self.assertEqual(response.status_code, 200)
        compare_action = next(action for action in response.body["actions"] if action["action_id"] == "compare_target")
        states_action = next(action for action in response.body["actions"] if action["action_id"] == "list_subject_states")
        self.assertEqual(compare_action["route_hint"], "/compare?left=fixture%3Asoftware%2Farchivebox%400.8.5")
        self.assertEqual(states_action["route_hint"], "/subject?key=archivebox")

    def test_public_action_plan_boundary_returns_blocked_shape_for_missing_target(self) -> None:
        response = self.public_api.plan_actions(
            ActionPlanEvaluationRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(response.body["notices"][0]["code"], "target_ref_not_found")
