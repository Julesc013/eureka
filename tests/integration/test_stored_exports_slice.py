from __future__ import annotations

from io import BytesIO
import json
import tempfile
import unittest
from urllib.parse import quote
import zipfile

from runtime.gateway import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_stored_exports_public_api,
)
from runtime.gateway.public_api import StoredExportsTargetRequest
from surfaces.web.server import WorkbenchWsgiApp


class StoredExportsSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.stored_exports_public_api = build_demo_stored_exports_public_api(self.temp_dir.name)
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            stored_exports_public_api=self.stored_exports_public_api,
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_store_slice_round_trips_stored_exports_through_public_boundary_and_workbench(self) -> None:
        manifest_status, manifest_headers, manifest_body = self._fetch_json(
            "/store/manifest",
            "fixture:software/synthetic-demo-app@1.0.0",
        )
        bundle_status, bundle_headers, bundle_body = self._fetch_json(
            "/store/bundle",
            "fixture:software/synthetic-demo-app@1.0.0",
        )

        self.assertEqual(manifest_status, "200 OK")
        self.assertEqual(manifest_headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(bundle_status, "200 OK")
        manifest_payload = json.loads(manifest_body)
        bundle_payload = json.loads(bundle_body)
        manifest_artifact_id = manifest_payload["artifact"]["artifact_id"]
        bundle_artifact_id = bundle_payload["artifact"]["artifact_id"]
        resolved_resource_id = "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2"
        self.assertEqual(manifest_payload["artifact"]["resolved_resource_id"], resolved_resource_id)
        self.assertEqual(bundle_payload["artifact"]["resolved_resource_id"], resolved_resource_id)

        listed = self.stored_exports_public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.body["resolved_resource_id"], resolved_resource_id)
        self.assertEqual(
            {artifact["artifact_id"] for artifact in listed.body["artifacts"]},
            {manifest_artifact_id, bundle_artifact_id},
        )

        manifest_read_status, manifest_read_headers, manifest_read_body = self._fetch_stored_artifact(
            manifest_artifact_id
        )
        self.assertEqual(manifest_read_status, "200 OK")
        self.assertEqual(manifest_read_headers["Content-Type"], "application/json; charset=utf-8")
        manifest_document = json.loads(manifest_read_body.decode("utf-8"))
        self.assertEqual(manifest_document["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(manifest_document["resolved_resource_id"], resolved_resource_id)

        bundle_read_status, bundle_read_headers, bundle_read_body = self._fetch_stored_artifact(
            bundle_artifact_id
        )
        self.assertEqual(bundle_read_status, "200 OK")
        self.assertEqual(bundle_read_headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(BytesIO(bundle_read_body)) as bundle:
            self.assertEqual(
                bundle.namelist(),
                [
                    "README.txt",
                    "bundle.json",
                    "manifest.json",
                    "records/normalized_record.json",
                ],
            )

        page_status, _, page_body = self._fetch_page("/", "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(page_status, "200 OK")
        self.assertIn("Stored Exports", page_body)
        self.assertIn(manifest_artifact_id, page_body)
        self.assertIn(bundle_artifact_id, page_body)
        self.assertIn(resolved_resource_id, page_body)
        self.assertIn("Store resolution manifest locally", page_body)
        self.assertIn("Store resolution bundle locally", page_body)

    def _fetch_page(self, path: str, target_ref: str) -> tuple[str, dict[str, str], str]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": f"target_ref={quote(target_ref)}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")
        return str(captured["status"]), dict(captured["headers"]), body

    def _fetch_json(self, path: str, target_ref: str) -> tuple[str, dict[str, str], str]:
        return self._fetch_page(path, target_ref)

    def _fetch_stored_artifact(self, artifact_id: str) -> tuple[str, dict[str, str], bytes]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/stored/artifact",
                    "QUERY_STRING": f"artifact_id={quote(artifact_id)}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body
