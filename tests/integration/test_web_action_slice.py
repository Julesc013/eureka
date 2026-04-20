from __future__ import annotations

from io import BytesIO
import json
import unittest
import zipfile
from urllib.parse import quote

from runtime.gateway import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class WebActionSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_action_surface_renders_known_and_unknown_action_states_and_portable_exports(self) -> None:
        with self.subTest(target_ref="fixture:software/synthetic-demo-app@1.0.0"):
            status, headers, body = self._fetch_page("/", "fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(status, "200 OK")
            self.assertIn("Export resolution manifest", body)
            self.assertIn("Export resolution bundle", body)
            self.assertIn(
                "/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                body,
            )
            self.assertIn(
                "/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0",
                body,
            )

            export_status, export_headers, export_body = self._fetch_json(
                "/actions/export-resolution-manifest",
                "fixture:software/synthetic-demo-app@1.0.0",
            )
            self.assertEqual(export_status, "200 OK")
            self.assertEqual(export_headers["Content-Type"], "application/json; charset=utf-8")
            manifest = json.loads(export_body)
            self.assertEqual(manifest["manifest_kind"], "eureka.resolution_manifest")
            self.assertEqual(manifest["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(manifest["primary_object"]["id"], "obj.synthetic-demo-app")

            bundle_status, bundle_headers, bundle_body = self._fetch_binary(
                "/actions/export-resolution-bundle",
                "fixture:software/synthetic-demo-app@1.0.0",
            )
            self.assertEqual(bundle_status, "200 OK")
            self.assertEqual(bundle_headers["Content-Type"], "application/zip")
            self.assertIn(
                "eureka-resolution-bundle-fixture-software-synthetic-demo-app-1.0.0.zip",
                bundle_headers["Content-Disposition"],
            )
            with zipfile.ZipFile(BytesIO(bundle_body)) as bundle:
                self.assertEqual(
                    bundle.namelist(),
                    [
                        "README.txt",
                        "bundle.json",
                        "manifest.json",
                        "records/normalized_record.json",
                    ],
                )
                manifest_from_bundle = json.loads(bundle.read("manifest.json").decode("utf-8"))
                bundle_metadata = json.loads(bundle.read("bundle.json").decode("utf-8"))
            self.assertEqual(manifest_from_bundle["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(bundle_metadata["bundle_kind"], "eureka.resolution_bundle")

        with self.subTest(target_ref="fixture:software/missing-demo-app@0.0.1"):
            status, _, body = self._fetch_page("/", "fixture:software/missing-demo-app@0.0.1")
            self.assertEqual(status, "200 OK")
            self.assertIn("No available actions are exposed for this target.", body)
            self.assertIn("resolution_manifest_not_available", body)
            self.assertIn("resolution_bundle_not_available", body)

            export_status, export_headers, export_body = self._fetch_json(
                "/actions/export-resolution-manifest",
                "fixture:software/missing-demo-app@0.0.1",
            )
            self.assertEqual(export_status, "404 Not Found")
            self.assertEqual(export_headers["Content-Type"], "application/json; charset=utf-8")
            blocked = json.loads(export_body)
            self.assertEqual(blocked["code"], "resolution_manifest_not_available")
            self.assertEqual(blocked["status"], "blocked")

            bundle_status, bundle_headers, bundle_body = self._fetch_json(
                "/actions/export-resolution-bundle",
                "fixture:software/missing-demo-app@0.0.1",
            )
            self.assertEqual(bundle_status, "404 Not Found")
            self.assertEqual(bundle_headers["Content-Type"], "application/json; charset=utf-8")
            blocked_bundle = json.loads(bundle_body)
            self.assertEqual(blocked_bundle["code"], "resolution_bundle_not_available")
            self.assertEqual(blocked_bundle["status"], "blocked")

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

    def _fetch_binary(self, path: str, target_ref: str) -> tuple[str, dict[str, str], bytes]:
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
        )
        return str(captured["status"]), dict(captured["headers"]), body
