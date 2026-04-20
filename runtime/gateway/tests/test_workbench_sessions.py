from __future__ import annotations

import unittest

from runtime.gateway import build_demo_resolution_jobs_public_api
from runtime.gateway.public_api import SubmitResolutionJobRequest, resolution_job_envelope_to_workbench_session


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
UNKNOWN_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class WorkbenchSessionMappingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_resolution_jobs_public_api()

    def test_completed_job_maps_to_shared_workbench_session(self) -> None:
        submit_response = self.public_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(KNOWN_TARGET_REF),
        )
        read_response = self.public_api.read_resolution_job(submit_response.body["job_id"])

        workbench_session = resolution_job_envelope_to_workbench_session(
            read_response.body,
            session_id="session.synthetic-known",
        )

        self.assertEqual(
            workbench_session,
            {
                "session_id": "session.synthetic-known",
                "active_job": {
                    "job_id": "job-0001",
                    "status": "completed",
                    "target_ref": KNOWN_TARGET_REF,
                },
                "selected_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
            },
        )

    def test_blocked_job_maps_to_shared_workbench_session(self) -> None:
        submit_response = self.public_api.submit_resolution_job(
            SubmitResolutionJobRequest.from_parts(UNKNOWN_TARGET_REF),
        )
        read_response = self.public_api.read_resolution_job(submit_response.body["job_id"])

        workbench_session = resolution_job_envelope_to_workbench_session(
            read_response.body,
            session_id="session.synthetic-missing",
        )

        self.assertEqual(
            workbench_session,
            {
                "session_id": "session.synthetic-missing",
                "active_job": {
                    "job_id": "job-0001",
                    "status": "blocked",
                    "target_ref": UNKNOWN_TARGET_REF,
                },
                "notices": [
                    {
                        "code": "fixture_target_not_found",
                        "severity": "warning",
                        "message": "No governed synthetic record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    }
                ],
            },
        )
