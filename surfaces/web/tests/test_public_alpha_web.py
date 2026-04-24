from __future__ import annotations

from io import BytesIO
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_archive_resolution_evals_public_api,
    build_demo_local_index_public_api,
    build_demo_representations_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp
from surfaces.web.workbench import render_archive_resolution_evals_html


class PublicAlphaWebTestCase(unittest.TestCase):
    def test_status_page_renders_public_alpha_mode(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(app, "/status", {})
        html = body.decode("utf-8")

        self.assertEqual(status, "200 OK")
        self.assertIn("Eureka Server Status", html)
        self.assertIn("public_alpha", html)
        self.assertIn("caller_local_index_paths", html)

    def test_blocked_page_renders_for_public_alpha_local_path_route(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(
            app,
            "/index/build",
            {"index_path": "D:/private/eureka.sqlite3"},
        )
        html = body.decode("utf-8")

        self.assertEqual(status, "403 Forbidden")
        self.assertIn("Operation Blocked", html)
        self.assertIn("local_path_parameters_blocked", html)
        self.assertIn("index_path", html)

    def test_local_dev_index_page_keeps_local_path_controls(self) -> None:
        app = _build_app(WebServerConfig.local_dev())

        status, _headers, body = _request(app, "/index/build", {})
        html = body.decode("utf-8")

        self.assertEqual(status, "200 OK")
        self.assertIn("index_path", html)
        self.assertIn("Index path", html)

    def test_public_alpha_eval_page_can_hide_index_path_control(self) -> None:
        html = render_archive_resolution_evals_html(
            {
                "status": "evaluated",
                "eval_suite": {
                    "total_task_count": 0,
                    "status_counts": {},
                    "task_summaries": [],
                    "tasks": [],
                    "created_at": "2026-04-24T00:00:00+00:00",
                    "created_by_slice": "archive_resolution_eval_runner_v0",
                    "load_errors": [],
                    "notices": [],
                },
            },
            allow_index_path=False,
        )

        self.assertIn("Public-alpha mode uses the server-owned transient index path only.", html)
        self.assertNotIn("name=\"index_path\"", html)

    def test_public_alpha_representation_page_hides_payload_readback_link(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(
            app,
            "/representations",
            {"target_ref": "fixture:software/synthetic-demo-app@1.0.0"},
        )
        html = body.decode("utf-8")

        self.assertEqual(status, "200 OK")
        self.assertIn("Disabled in public-alpha mode.", html)
        self.assertNotIn("Retrieve local fixture payload", html)
        self.assertNotIn("/fetch?target_ref=", html)


def _build_app(config: WebServerConfig) -> WorkbenchWsgiApp:
    return WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        local_index_public_api=build_demo_local_index_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        search_public_api=build_demo_search_public_api(),
        default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        server_config=config,
    )


def _request(
    app: WorkbenchWsgiApp,
    path: str,
    query: dict[str, str],
) -> tuple[str, dict[str, str], bytes]:
    captured: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "GET",
                "PATH_INFO": path,
                "QUERY_STRING": urlencode(query),
                "wsgi.input": BytesIO(b""),
            },
            start_response,
        )
    )
    return str(captured["status"]), dict(captured["headers"]), body


if __name__ == "__main__":
    unittest.main()
