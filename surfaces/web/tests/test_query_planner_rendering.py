from __future__ import annotations

from io import BytesIO
import unittest

from runtime.gateway.public_api import (
    build_demo_query_planner_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp, render_query_plan_page


class QueryPlannerRenderingTestCase(unittest.TestCase):
    def test_render_query_plan_page_shows_expected_fields(self) -> None:
        html = render_query_plan_page(
            build_demo_query_planner_public_api(),
            "latest Firefox before XP support ended",
        )

        self.assertIn("Eureka Query Plan", html)
        self.assertIn("find_latest_compatible_release", html)
        self.assertIn("Firefox", html)
        self.assertIn("Windows XP", html)
        self.assertIn("latest_before_support_drop", html)

    def test_wsgi_app_handles_query_plan_requests(self) -> None:
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            query_planner_public_api=build_demo_query_planner_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/query-plan",
                    "QUERY_STRING": "q=Windows+7+apps",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("browse_software", body)
        self.assertIn("Windows 7", body)
        self.assertIn("platform_is_constraint", body)
        self.assertIn("os_iso_image", body)


if __name__ == "__main__":
    unittest.main()
