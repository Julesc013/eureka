from __future__ import annotations

import json
import tempfile
import unittest

from runtime.gateway import build_demo_stored_exports_public_api
from runtime.gateway.public_api import StoredArtifactRequest, StoredExportsTargetRequest


class StoredExportsPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.public_api = build_demo_stored_exports_public_api(self.temp_dir.name)

    def test_public_store_boundary_stores_and_lists_manifest_and_bundle_exports(self) -> None:
        manifest_response = self.public_api.store_resolution_manifest(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )
        bundle_response = self.public_api.store_resolution_bundle(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )
        listed = self.public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(manifest_response.status_code, 200)
        self.assertEqual(bundle_response.status_code, 200)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(
            [artifact["artifact_kind"] for artifact in listed.body["artifacts"]],
            ["resolution_bundle", "resolution_manifest"],
        )

    def test_public_store_boundary_returns_blocked_results_for_unknown_target(self) -> None:
        manifest_response = self.public_api.store_resolution_manifest(
            StoredExportsTargetRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )
        bundle_response = self.public_api.store_resolution_bundle(
            StoredExportsTargetRequest.from_parts("fixture:software/missing-demo-app@0.0.1")
        )

        self.assertEqual(manifest_response.status_code, 404)
        self.assertEqual(bundle_response.status_code, 404)
        self.assertEqual(manifest_response.body["code"], "store_resolution_manifest_not_available")
        self.assertEqual(bundle_response.body["code"], "store_resolution_bundle_not_available")

    def test_public_store_boundary_returns_blocked_results_for_unknown_artifact_id(self) -> None:
        metadata_response = self.public_api.get_stored_artifact_metadata(
            StoredArtifactRequest.from_parts("sha256:" + "0" * 64)
        )
        content_response = self.public_api.get_stored_artifact_content(
            StoredArtifactRequest.from_parts("sha256:" + "0" * 64)
        )

        self.assertEqual(metadata_response.status_code, 404)
        self.assertEqual(metadata_response.body["code"], "stored_artifact_not_found")
        self.assertEqual(content_response.status_code, 404)
        self.assertEqual(content_response.content_type, "application/json; charset=utf-8")
        self.assertEqual(
            json.loads(content_response.payload.decode("utf-8"))["code"],
            "stored_artifact_not_found",
        )

    def test_public_store_boundary_returns_blocked_results_for_invalid_artifact_id(self) -> None:
        metadata_response = self.public_api.get_stored_artifact_metadata(
            StoredArtifactRequest.from_parts("not-a-content-address")
        )

        self.assertEqual(metadata_response.status_code, 404)
        self.assertEqual(metadata_response.body["code"], "stored_artifact_id_invalid")
