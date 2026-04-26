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
                "resolved_resource_id": "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2",
                "active_job": {
                    "job_id": "job-0001",
                    "status": "completed",
                    "target_ref": KNOWN_TARGET_REF,
                },
                "selected_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                    "result_lanes": ["installable_or_usable_now"],
                    "primary_lane": "installable_or_usable_now",
                    "user_cost_score": 2,
                    "user_cost_reasons": ["direct_bounded_record"],
                    "usefulness_summary": (
                        "installable or usable now; user cost 2; why: direct_bounded_record"
                    ),
                },
                "source": {
                    "family": "synthetic_fixture",
                    "source_id": "synthetic-fixtures",
                    "label": "Synthetic Fixture",
                    "locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                },
                "representations": [
                    {
                        "representation_id": "rep.synthetic-demo-app.source",
                        "representation_kind": "fixture_artifact",
                        "label": "Synthetic demo app fixture artifact",
                        "content_type": "application/vnd.eureka.synthetic.bundle",
                        "byte_length": 4096,
                        "filename": "synthetic-demo-app.bundle",
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture",
                        "access_kind": "inspect",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "is_direct": False,
                        "is_fetchable": True,
                    },
                    {
                        "representation_id": "rep.synthetic-demo-app.fixture-record",
                        "representation_kind": "fixture_record",
                        "label": "Synthetic demo app fixture record",
                        "content_type": "application/json",
                        "byte_length": 1024,
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.fixture-record",
                        "access_kind": "view",
                        "access_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json#fixture:software/synthetic-demo-app@1.0.0",
                        "is_direct": False,
                        "is_fetchable": False,
                    },
                    {
                        "representation_id": "rep.synthetic-demo-app.package",
                        "representation_kind": "fixture_archive",
                        "label": "Synthetic demo app package archive",
                        "content_type": "application/zip",
                        "byte_length": 501,
                        "filename": "synthetic-demo-app-package.zip",
                        "source_family": "synthetic_fixture",
                        "source_label": "Synthetic Fixture",
                        "source_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "access_path_id": "access.synthetic-demo-app.package",
                        "access_kind": "download",
                        "access_locator": "contracts/archive/fixtures/software/payloads/synthetic-demo-app-package.zip",
                        "is_direct": True,
                        "is_fetchable": True,
                    },
                ],
                "evidence": [
                    {
                        "claim_kind": "label",
                        "claim_value": "Synthetic Demo App",
                        "asserted_by_family": "synthetic_fixture",
                        "asserted_by_label": "Synthetic Fixture",
                        "evidence_kind": "recorded_fixture",
                        "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    },
                    {
                        "claim_kind": "source_locator",
                        "claim_value": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                        "asserted_by_family": "synthetic_fixture",
                        "asserted_by_label": "Synthetic Fixture",
                        "evidence_kind": "recorded_fixture",
                        "evidence_locator": "contracts/archive/fixtures/software/synthetic_resolution_fixture.json",
                    },
                ],
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
                        "code": "target_ref_not_found",
                        "severity": "warning",
                        "message": "No bounded record matched target_ref 'fixture:software/missing-demo-app@0.0.1'.",
                    }
                ],
            },
        )
