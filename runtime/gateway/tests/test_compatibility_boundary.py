from __future__ import annotations

import unittest

from runtime.gateway import build_demo_compatibility_public_api
from runtime.gateway.public_api import CompatibilityEvaluationRequest


class CompatibilityPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_compatibility_public_api()

    def test_public_compatibility_boundary_returns_compatible_verdict(self) -> None:
        response = self.public_api.evaluate_compatibility(
            CompatibilityEvaluationRequest.from_parts(
                "fixture:software/compatibility-lab@3.2.1",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "evaluated")
        self.assertEqual(response.body["compatibility_status"], "compatible")
        self.assertEqual(response.body["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(response.body["primary_object"]["label"], "Compatibility Lab")
        self.assertEqual(response.body["reasons"][0]["code"], "os_family_supported")

    def test_public_compatibility_boundary_returns_unknown_verdict(self) -> None:
        response = self.public_api.evaluate_compatibility(
            CompatibilityEvaluationRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "evaluated")
        self.assertEqual(response.body["compatibility_status"], "unknown")
        self.assertEqual(response.body["reasons"][0]["code"], "compatibility_requirements_missing")

    def test_public_compatibility_boundary_returns_blocked_shape_for_missing_target(self) -> None:
        response = self.public_api.evaluate_compatibility(
            CompatibilityEvaluationRequest.from_parts(
                "fixture:software/missing-demo-app@0.0.1",
                "windows-x86_64",
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], "fixture:software/missing-demo-app@0.0.1")
        self.assertEqual(response.body["notices"][0]["code"], "target_ref_not_found")

