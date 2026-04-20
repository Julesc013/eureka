from __future__ import annotations

import unittest

from runtime.gateway import build_demo_resolution_actions_public_api
from runtime.gateway.public_api import ResolutionActionRequest, resolution_actions_envelope_to_view_model


class ResolutionActionsViewModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_resolution_actions_public_api()

    def test_available_action_response_maps_to_shared_view_model(self) -> None:
        response = self.public_api.list_resolution_actions(
            ResolutionActionRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        view_model = resolution_actions_envelope_to_view_model(response.body)

        self.assertEqual(
            view_model,
            {
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "actions": [
                    {
                        "action_id": "export_resolution_manifest",
                        "label": "Export resolution manifest",
                        "availability": "available",
                        "href": "/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    },
                    {
                        "action_id": "export_resolution_bundle",
                        "label": "Export resolution bundle",
                        "availability": "available",
                        "href": "/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                    }
                ],
            },
        )

    def test_unavailable_action_response_maps_to_shared_view_model(self) -> None:
        response = self.public_api.list_resolution_actions(
            ResolutionActionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        view_model = resolution_actions_envelope_to_view_model(response.body)

        self.assertEqual(
            [action["availability"] for action in view_model["actions"]],
            ["unavailable", "unavailable"],
        )
        self.assertEqual(
            [notice["code"] for notice in view_model["notices"]],
            ["resolution_manifest_not_available", "resolution_bundle_not_available"],
        )
