from __future__ import annotations

import ast
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
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"
EXPECTED_RESOLVED_RESOURCE_ID = (
    "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2"
)
SURFACE_WEB_SERVER_ROOT = Path(__file__).resolve().parents[1] / "server"


class HttpApiRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref=DEFAULT_TARGET_REF,
        )

    def test_resolve_endpoint_returns_machine_readable_success_for_known_target(self) -> None:
        status, headers, body = self._request("/api/resolve", {"target_ref": DEFAULT_TARGET_REF})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["workbench_session"]["active_job"]["status"], "completed")
        self.assertEqual(
            payload["workbench_session"]["resolved_resource_id"],
            EXPECTED_RESOLVED_RESOURCE_ID,
        )
        self.assertEqual(
            payload["resolution_actions"]["resolved_resource_id"],
            EXPECTED_RESOLVED_RESOURCE_ID,
        )

    def test_resolve_endpoint_returns_honest_blocked_outcome_for_unknown_target(self) -> None:
        status, headers, body = self._request("/api/resolve", {"target_ref": MISSING_TARGET_REF})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["workbench_session"]["active_job"]["status"], "blocked")
        self.assertEqual(
            payload["workbench_session"]["notices"][0]["code"],
            "target_ref_not_found",
        )
        self.assertNotIn("resolved_resource_id", payload["workbench_session"])

    def test_search_endpoint_returns_deterministic_results_and_no_results_response(self) -> None:
        with self.subTest(query="synthetic"):
            status, headers, body = self._request("/api/search", {"q": "synthetic"})
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            payload = json.loads(body)
            self.assertEqual(payload["result_count"], 2)
            self.assertEqual(
                [result["target_ref"] for result in payload["results"]],
                [
                    "fixture:software/synthetic-demo-app@1.0.0",
                    "fixture:software/synthetic-demo-suite@2.0.0",
                ],
            )
            self.assertEqual(
                payload["results"][0]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )

        with self.subTest(query="missing"):
            status, _, body = self._request("/api/search", {"q": "missing"})
            self.assertEqual(status, "200 OK")
            payload = json.loads(body)
            self.assertEqual(payload["result_count"], 0)
            self.assertEqual(payload["absence"]["code"], "search_no_matches")

    def test_manifest_export_endpoint_returns_json_with_resolved_resource_id(self) -> None:
        status, headers, body = self._request(
            "/api/export/manifest",
            {"target_ref": DEFAULT_TARGET_REF},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)

    def test_bundle_export_endpoint_returns_zip_bytes(self) -> None:
        status, headers, body = self._request(
            "/api/export/bundle",
            {"target_ref": DEFAULT_TARGET_REF},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(BytesIO(body)) as bundle:
            self.assertEqual(
                bundle.namelist(),
                [
                    "README.txt",
                    "bundle.json",
                    "manifest.json",
                    "records/normalized_record.json",
                ],
            )

    def test_bundle_inspection_endpoint_returns_inspected_result_for_valid_bundle_path(self) -> None:
        _, _, bundle_bytes = self._request(
            "/api/export/bundle",
            {"target_ref": DEFAULT_TARGET_REF},
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / "synthetic-demo-bundle.zip"
            bundle_path.write_bytes(bundle_bytes)

            status, headers, body = self._request(
                "/api/inspect/bundle",
                {"bundle_path": str(bundle_path)},
            )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "inspected")
        self.assertEqual(payload["bundle"]["target_ref"], DEFAULT_TARGET_REF)
        self.assertIn("manifest.json", payload["bundle"]["member_list"])

    def test_store_list_and_read_endpoints_work_for_local_store(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status, _, body = self._request(
                "/api/store/manifest",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            manifest_store_payload = json.loads(body)
            manifest_artifact_id = manifest_store_payload["artifact"]["artifact_id"]
            self.assertEqual(
                manifest_store_payload["artifact"]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )

            status, _, body = self._request(
                "/api/store/bundle",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            bundle_store_payload = json.loads(body)
            bundle_artifact_id = bundle_store_payload["artifact"]["artifact_id"]
            self.assertEqual(
                bundle_store_payload["artifact"]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )

            status, headers, body = self._request(
                "/api/stored",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            stored_payload = json.loads(body)
            self.assertEqual(stored_payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)
            self.assertEqual(
                {artifact["artifact_id"] for artifact in stored_payload["artifacts"]},
                {manifest_artifact_id, bundle_artifact_id},
            )

            status, headers, body = self._request(
                "/api/stored/artifact",
                {"artifact_id": manifest_artifact_id, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            manifest_payload = json.loads(body)
            self.assertEqual(manifest_payload["manifest_kind"], "eureka.resolution_manifest")
            self.assertEqual(manifest_payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)

            status, headers, body = self._request(
                "/api/stored/artifact",
                {"artifact_id": bundle_artifact_id, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/zip")
            with zipfile.ZipFile(BytesIO(body)) as bundle:
                self.assertIn("manifest.json", bundle.namelist())

    def test_http_api_modules_do_not_import_engine_or_connector_internals(self) -> None:
        for path in (
            SURFACE_WEB_SERVER_ROOT / "api_routes.py",
            SURFACE_WEB_SERVER_ROOT / "api_serialization.py",
        ):
            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith("runtime.engine"),
                            f"{path} imports engine internals: {alias.name}",
                        )
                        self.assertFalse(
                            alias.name.startswith("runtime.connectors"),
                            f"{path} imports connector internals: {alias.name}",
                        )
                if isinstance(node, ast.ImportFrom) and node.module is not None:
                    self.assertFalse(
                        node.module.startswith("runtime.engine"),
                        f"{path} imports engine internals: {node.module}",
                    )
                    self.assertFalse(
                        node.module.startswith("runtime.connectors"),
                        f"{path} imports connector internals: {node.module}",
                    )

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
