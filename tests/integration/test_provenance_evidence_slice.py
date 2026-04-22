from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_stored_exports_public_api,
)
from runtime.gateway.public_api import (
    InspectResolutionBundleRequest,
    ResolutionActionRequest,
    StoredArtifactRequest,
    StoredExportsTargetRequest,
    SubmitResolutionJobRequest,
    resolution_job_envelope_to_workbench_session,
)
from surfaces.web.workbench import render_resolution_workspace_html


class ProvenanceEvidenceSliceIntegrationTestCase(unittest.TestCase):
    def test_evidence_summary_survives_resolution_export_store_inspection_and_rendering(self) -> None:
        target_ref = "fixture:software/synthetic-demo-app@1.0.0"
        resolution_public_api = build_demo_resolution_jobs_public_api()
        actions_public_api = build_demo_resolution_actions_public_api()
        inspection_public_api = build_demo_resolution_bundle_inspection_public_api()

        with tempfile.TemporaryDirectory() as temp_dir:
            stored_exports_public_api = build_demo_stored_exports_public_api(temp_dir)

            submitted = resolution_public_api.submit_resolution_job(
                SubmitResolutionJobRequest.from_parts(target_ref)
            )
            resolved = resolution_public_api.read_resolution_job(submitted.body["job_id"])
            workbench_session = resolution_job_envelope_to_workbench_session(
                resolved.body,
                session_id="session.provenance-slice",
            )

            manifest = actions_public_api.export_resolution_manifest(
                ResolutionActionRequest.from_parts(target_ref)
            ).body
            stored = stored_exports_public_api.store_resolution_bundle(
                StoredExportsTargetRequest.from_parts(target_ref)
            ).body
            artifact_id = stored["artifact"]["artifact_id"]
            stored_artifact = stored_exports_public_api.get_stored_artifact_metadata(
                StoredArtifactRequest.from_parts(artifact_id)
            ).body["artifact"]
            bundle_payload = stored_exports_public_api.get_stored_artifact_content(
                StoredArtifactRequest.from_parts(artifact_id)
            ).payload
            inspected = inspection_public_api.inspect_bundle(
                InspectResolutionBundleRequest.from_bundle_bytes(
                    bundle_payload,
                    source_name=stored_artifact["filename"],
                )
            ).body
            rendered = render_resolution_workspace_html(workbench_session)

        expected_evidence = manifest["evidence"]
        self.assertEqual(workbench_session["evidence"], expected_evidence)
        self.assertEqual(stored_artifact["evidence"], expected_evidence)
        self.assertEqual(inspected["evidence"], expected_evidence)
        self.assertIn("Evidence", rendered)
        self.assertIn("label = Synthetic Demo App", rendered)
