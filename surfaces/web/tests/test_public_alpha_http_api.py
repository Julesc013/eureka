from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import tempfile
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_archive_resolution_evals_public_api,
    build_demo_local_index_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp


class PublicAlphaHttpApiTestCase(unittest.TestCase):
    def test_status_endpoint_reports_public_alpha_without_paths(self) -> None:
        app = _build_app(WebServerConfig.public_alpha(index_root="D:/private/index-root"))

        status, _headers, body = _request(app, "/api/status", {})
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["mode"], "public_alpha")
        self.assertTrue(payload["safe_mode_enabled"])
        self.assertEqual(payload["configured_root_kinds"]["index_root"], "configured")
        self.assertNotIn("D:/private/index-root", body.decode("utf-8"))

    def test_status_endpoint_blocks_local_path_parameters_in_public_alpha(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(
            app,
            "/api/status",
            {"store_root": "D:/private/export-root"},
        )
        payload = json.loads(body)

        self.assertEqual(status, "403 Forbidden")
        self.assertEqual(payload["code"], "local_path_parameters_blocked")
        self.assertIn("store_root", payload["blocked_parameters"])

    def test_safe_route_works_in_public_alpha(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(app, "/api/search", {"q": "synthetic"})
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["query"], "synthetic")

    def test_eval_route_works_without_index_path_in_public_alpha(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(
            app,
            "/api/evals/archive-resolution",
            {"task_id": "windows_7_apps"},
        )
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["status"], "evaluated")
        self.assertEqual(payload["eval_suite"]["total_task_count"], 1)

    def test_unsafe_route_is_blocked_in_public_alpha(self) -> None:
        app = _build_app(WebServerConfig.public_alpha())

        status, _headers, body = _request(
            app,
            "/api/index/status",
            {"index_path": "D:/private/local-index.sqlite3"},
        )
        payload = json.loads(body)

        self.assertEqual(status, "403 Forbidden")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["code"], "local_path_parameters_blocked")
        self.assertIn("index_path", payload["blocked_parameters"])

    def test_same_local_path_route_remains_allowed_in_local_dev(self) -> None:
        app = _build_app(WebServerConfig.local_dev())
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = str(Path(temp_dir) / "local-index.sqlite3")
            status, _headers, body = _request(
                app,
                "/api/index/status",
                {"index_path": index_path},
            )
        payload = json.loads(body)

        self.assertNotEqual(status, "403 Forbidden")
        self.assertIn(payload["status"], {"available", "blocked", "missing"})


def _build_app(config: WebServerConfig) -> WorkbenchWsgiApp:
    return WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        local_index_public_api=build_demo_local_index_public_api(),
        search_public_api=build_demo_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
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
