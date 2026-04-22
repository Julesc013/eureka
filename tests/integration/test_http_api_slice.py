from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
import tempfile
from urllib.parse import urlencode
import unittest
import zipfile

from runtime.gateway.public_api import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


DEFAULT_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class HttpApiSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref=DEFAULT_TARGET_REF,
        )

    def test_http_api_surface_reuses_public_boundaries_for_end_to_end_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            resolve_status, _, resolve_body = self._request(
                "/api/resolve",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(resolve_status, "200 OK")
            resolve_payload = json.loads(resolve_body)
            resolved_resource_id = resolve_payload["workbench_session"]["resolved_resource_id"]

            search_status, _, search_body = self._request("/api/search", {"q": "synthetic"})
            self.assertEqual(search_status, "200 OK")
            search_payload = json.loads(search_body)
            self.assertEqual(search_payload["results"][0]["resolved_resource_id"], resolved_resource_id)

            manifest_status, manifest_headers, manifest_body = self._request(
                "/api/export/manifest",
                {"target_ref": DEFAULT_TARGET_REF},
            )
            self.assertEqual(manifest_status, "200 OK")
            self.assertEqual(manifest_headers["Content-Type"], "application/json; charset=utf-8")
            manifest_payload = json.loads(manifest_body)
            self.assertEqual(manifest_payload["resolved_resource_id"], resolved_resource_id)

            store_status, _, store_body = self._request(
                "/api/store/bundle",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(store_status, "200 OK")
            store_payload = json.loads(store_body)
            artifact_id = store_payload["artifact"]["artifact_id"]

            stored_status, _, stored_body = self._request(
                "/api/stored",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(stored_status, "200 OK")
            stored_payload = json.loads(stored_body)
            self.assertEqual(stored_payload["resolved_resource_id"], resolved_resource_id)
            self.assertIn(
                artifact_id,
                [artifact["artifact_id"] for artifact in stored_payload["artifacts"]],
            )

            artifact_status, artifact_headers, artifact_body = self._request(
                "/api/stored/artifact",
                {"artifact_id": artifact_id, "store_root": temp_dir},
            )
            self.assertEqual(artifact_status, "200 OK")
            self.assertEqual(artifact_headers["Content-Type"], "application/zip")

            bundle_path = Path(temp_dir) / "stored-bundle.zip"
            bundle_path.write_bytes(artifact_body)
            with zipfile.ZipFile(BytesIO(artifact_body)) as bundle:
                self.assertIn("bundle.json", bundle.namelist())

            inspect_status, inspect_headers, inspect_body = self._request(
                "/api/inspect/bundle",
                {"bundle_path": str(bundle_path)},
            )
            self.assertEqual(inspect_status, "200 OK")
            self.assertEqual(inspect_headers["Content-Type"], "application/json; charset=utf-8")
            inspect_payload = json.loads(inspect_body)
            self.assertEqual(inspect_payload["status"], "inspected")
            self.assertEqual(inspect_payload["bundle"]["target_ref"], DEFAULT_TARGET_REF)
            self.assertEqual(inspect_payload["primary_object"]["id"], "obj.synthetic-demo-app")

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], bytes]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": urlencode(query or {}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body


if __name__ == "__main__":
    unittest.main()
