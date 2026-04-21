from __future__ import annotations

from io import BytesIO
import unittest
from urllib.parse import quote

from runtime.gateway import build_demo_resolution_jobs_public_api, build_demo_search_public_api
from surfaces.web.server import WorkbenchWsgiApp


class WebSurfaceSliceIntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_surface_path_renders_known_and_unknown_targets_from_full_runtime_flow(self) -> None:
        with self.subTest(target_ref="fixture:software/synthetic-demo-app@1.0.0"):
            status, body = self._fetch("fixture:software/synthetic-demo-app@1.0.0")
            self.assertEqual(status, "200 OK")
            self.assertIn("fixture:software/synthetic-demo-app@1.0.0", body)
            self.assertIn("completed", body)
            self.assertIn("obj.synthetic-demo-app", body)
            self.assertIn("resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2", body)

        with self.subTest(target_ref="fixture:software/missing-demo-app@0.0.1"):
            status, body = self._fetch("fixture:software/missing-demo-app@0.0.1")
            self.assertEqual(status, "200 OK")
            self.assertIn("fixture:software/missing-demo-app@0.0.1", body)
            self.assertIn("blocked", body)
            self.assertIn("fixture_target_not_found", body)

    def _fetch(self, target_ref: str) -> tuple[str, str]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/",
                    "QUERY_STRING": f"target_ref={quote(target_ref)}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")
        return str(captured["status"]), body
