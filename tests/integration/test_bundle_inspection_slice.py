from __future__ import annotations

from io import BytesIO
import tempfile
import unittest
from urllib.parse import quote

from runtime.gateway import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from runtime.gateway.public_api import ResolutionActionRequest
from surfaces.web.server import WorkbenchWsgiApp


class BundleInspectionSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.actions_public_api = build_demo_resolution_actions_public_api()
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            actions_public_api=self.actions_public_api,
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_exported_bundle_can_be_read_back_through_public_inspection_and_rendered(self) -> None:
        bundle_response = self.actions_public_api.export_resolution_bundle(
            ResolutionActionRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )
        self.assertEqual(bundle_response.status_code, 200)

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = f"{temp_dir}/synthetic-demo-app.zip"
            with open(bundle_path, "wb") as handle:
                handle.write(bundle_response.payload)

            captured: dict[str, object] = {}

            def start_response(status: str, headers: list[tuple[str, str]]) -> None:
                captured["status"] = status
                captured["headers"] = headers

            body = b"".join(
                self.app(
                    {
                        "REQUEST_METHOD": "GET",
                        "PATH_INFO": "/inspect/bundle",
                        "QUERY_STRING": f"bundle_path={quote(bundle_path)}",
                        "wsgi.input": BytesIO(b""),
                    },
                    start_response,
                )
            ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("inspected", body)
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", body)
        self.assertIn("resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2", body)
        self.assertIn("obj.synthetic-demo-app", body)
        self.assertIn("bundle.json", body)
        self.assertIn("bundle_inspected_locally_offline", body)
