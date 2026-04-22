from __future__ import annotations

import unittest

from runtime.gateway import build_demo_resolution_actions_public_api
from runtime.gateway.public_api import ResolutionActionRequest


class ResolutionActionsPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_resolution_actions_public_api()

    def test_public_action_boundary_lists_manifest_and_bundle_exports_for_known_target(self) -> None:
        response = self.public_api.list_resolution_actions(
            ResolutionActionRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            {
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "resolved_resource_id": "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
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
                "notices": [],
            },
        )

    def test_public_action_boundary_marks_manifest_and_bundle_exports_unavailable_for_unknown_target(self) -> None:
        response = self.public_api.list_resolution_actions(
            ResolutionActionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [action["availability"] for action in response.body["actions"]],
            ["unavailable", "unavailable"],
        )
        self.assertEqual(
            [notice["code"] for notice in response.body["notices"]],
            ["resolution_manifest_not_available", "resolution_bundle_not_available"],
        )

    def test_public_action_boundary_exports_manifest_for_known_target(self) -> None:
        response = self.public_api.export_resolution_manifest(
            ResolutionActionRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(response.body["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(
            response.body["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )

    def test_public_action_boundary_returns_blocked_export_for_unknown_target(self) -> None:
        response = self.public_api.export_resolution_manifest(
            ResolutionActionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.body,
            {
                "action_id": "export_resolution_manifest",
                "status": "blocked",
                "target_ref": "fixture:software/missing-demo-app@0.0.1",
                "code": "resolution_manifest_not_available",
                "message": "No resolved bounded record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
            },
        )

    def test_public_action_boundary_exports_bundle_for_known_target(self) -> None:
        response = self.public_api.export_resolution_bundle(
            ResolutionActionRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/zip")
        self.assertEqual(
            response.filename,
            "eureka-resolution-bundle-fixture-software-synthetic-demo-app-1.0.0.zip",
        )
        self.assertGreater(len(response.payload), 0)

    def test_public_action_boundary_returns_blocked_bundle_export_for_unknown_target(self) -> None:
        response = self.public_api.export_resolution_bundle(
            ResolutionActionRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json; charset=utf-8")
        self.assertEqual(
            response.json_body(),
            {
                "action_id": "export_resolution_bundle",
                "status": "blocked",
                "target_ref": "fixture:software/missing-demo-app@0.0.1",
                "code": "resolution_bundle_not_available",
                "message": "No resolved bounded record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
            },
        )
