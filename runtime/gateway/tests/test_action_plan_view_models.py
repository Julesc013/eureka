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
                "preserve",
                store_actions_enabled=True,
            )
        )

        view_model = action_plan_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "planned")
        self.assertEqual(view_model["compatibility_status"], "compatible")
        self.assertEqual(view_model["strategy_profile"]["strategy_id"], "preserve")
        self.assertTrue(view_model["strategy_rationale"])
        self.assertEqual(view_model["host_profile"]["host_profile_id"], "windows-x86_64")
        store_manifest = next(action for action in view_model["actions"] if action["action_id"] == "store_resolution_manifest")
        direct_access = next(action for action in view_model["actions"] if action["action_id"] == "access_representation")
        self.assertEqual(direct_access["status"], "available")
        self.assertEqual(store_manifest["status"], "recommended")
        self.assertEqual(
            store_manifest["route_hint"],
            "/store/manifest?target_ref=github-release%3Acli%2Fcli%40v2.65.0",
        )
        self.assertEqual(view_model["evidence"][0]["claim_kind"], "label")
