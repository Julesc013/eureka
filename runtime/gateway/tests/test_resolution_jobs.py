from __future__ import annotations

import unittest

from runtime.gateway import build_demo_resolution_jobs_public_api
from runtime.gateway.public_api import SubmitResolutionJobRequest


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
UNKNOWN_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class ResolutionJobServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_resolution_jobs_public_api()

    def test_submit_boundary_returns_accepted_envelope(self) -> None:
        response = self.public_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(KNOWN_TARGET_REF),
        )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            response.body,
            {
                "job_id": "job-0001",
                "status": "accepted",
                "target_ref": KNOWN_TARGET_REF,
                "resolved_resource_id": "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
                "requested_outputs": [],
                "notices": [],
            },
        )

    def test_read_boundary_returns_completed_job_for_known_target(self) -> None:
        submit_response = self.public_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(KNOWN_TARGET_REF),
        )

        response = self.public_api.read_resolution_job(submit_response.body["job_id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "completed")
        self.assertEqual(response.body["target_ref"], KNOWN_TARGET_REF)
        self.assertEqual(
            response.body["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )
        self.assertEqual(response.body["notices"], [])
        self.assertEqual(
            response.body["result"]["primary_object"],
            {
                "id": "obj.synthetic-demo-app",
                "kind": "software",
                "label": "Synthetic Demo App",
            },
        )
        self.assertEqual(
            response.body["result"]["resolved_resource_id"],
            "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
        )

    def test_read_boundary_returns_blocked_job_for_unknown_target(self) -> None:
        submit_response = self.public_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(UNKNOWN_TARGET_REF),
        )

        response = self.public_api.read_resolution_job(submit_response.body["job_id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["target_ref"], UNKNOWN_TARGET_REF)
        self.assertNotIn("result", response.body)
        self.assertEqual(response.body["notices"][0]["code"], "fixture_target_not_found")
        self.assertEqual(response.body["notices"][0]["severity"], "warning")

    def test_read_boundary_returns_not_found_for_missing_job_id(self) -> None:
        response = self.public_api.read_resolution_job("job-9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.body,
            {
                "code": "resolution_job_not_found",
                "message": "Unknown resolution job_id 'job-9999'.",
            },
        )
