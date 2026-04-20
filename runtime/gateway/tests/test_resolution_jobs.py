from __future__ import annotations

import unittest

from runtime.gateway.public_api import SubmitResolutionJobRequest, build_demo_resolution_job_service


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
UNKNOWN_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class ResolutionJobServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = build_demo_resolution_job_service()

    def test_known_target_returns_completed_job(self) -> None:
        job = self.service.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(KNOWN_TARGET_REF),
        )

        self.assertEqual(job["status"], "completed")
        self.assertEqual(job["target_ref"], KNOWN_TARGET_REF)
        self.assertEqual(job["notices"], [])
        self.assertEqual(
            job["result"]["primary_object"],
            {
                "id": "obj.synthetic-demo-app",
                "kind": "software",
                "label": "Synthetic Demo App",
            },
        )
        self.assertEqual(self.service.get_resolution_job(job["job_id"]), job)

    def test_unknown_target_returns_blocked_job(self) -> None:
        job = self.service.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(UNKNOWN_TARGET_REF),
        )

        self.assertEqual(job["status"], "blocked")
        self.assertEqual(job["target_ref"], UNKNOWN_TARGET_REF)
        self.assertNotIn("result", job)
        self.assertEqual(job["notices"][0]["code"], "fixture_target_not_found")
        self.assertEqual(job["notices"][0]["severity"], "warning")

    def test_completed_job_envelope_shape_is_stable(self) -> None:
        job = self.service.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(
                KNOWN_TARGET_REF,
                requested_outputs=("primary_object",),
            ),
        )

        self.assertEqual(
            list(job.keys()),
            ["job_id", "status", "target_ref", "requested_outputs", "notices", "result"],
        )
        self.assertEqual(job["requested_outputs"], ["primary_object"])
        self.assertEqual(list(job["result"].keys()), ["notices", "primary_object"])
