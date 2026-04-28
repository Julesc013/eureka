from __future__ import annotations

from io import BytesIO
import json
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from surfaces.web.server import (
    PublicAlphaWrapperConfig,
    WorkbenchWsgiApp,
    load_public_alpha_wrapper_config,
)


class PublicAlphaWrapperConfigTest(unittest.TestCase):
    def test_default_config_is_public_alpha_and_safe(self) -> None:
        config = load_public_alpha_wrapper_config({})
        summary = config.to_summary_dict()

        self.assertEqual(summary["status"], "valid")
        self.assertEqual(summary["mode"], "public_alpha")
        self.assertEqual(summary["host"], "127.0.0.1")
        self.assertFalse(summary["live_probes_enabled"])
        self.assertFalse(summary["live_internet_archive_enabled"])
        self.assertFalse(summary["downloads_enabled"])
        self.assertFalse(summary["local_paths_enabled"])
        self.assertFalse(summary["user_storage_enabled"])
        self.assertFalse(summary["deployment_approved"])
        self.assertFalse(summary["production_ready"])

    def test_nonlocal_bind_requires_explicit_gate(self) -> None:
        config = load_public_alpha_wrapper_config({"EUREKA_BIND_HOST": "0.0.0.0"})

        self.assertEqual(config.bind_scope, "nonlocal")
        self.assertIn("nonlocal bind", "\n".join(config.validation_errors()))

    def test_nonlocal_bind_gate_allows_config_without_production_claim(self) -> None:
        config = load_public_alpha_wrapper_config(
            {"EUREKA_BIND_HOST": "0.0.0.0", "EUREKA_ALLOW_NONLOCAL_BIND": "1"}
        )
        summary = config.to_summary_dict()

        self.assertEqual(summary["status"], "valid")
        self.assertEqual(summary["bind_scope"], "nonlocal")
        self.assertFalse(summary["deployment_approved"])
        self.assertFalse(summary["production_ready"])
        self.assertTrue(summary["warnings"])

    def test_live_probe_env_is_rejected(self) -> None:
        config = load_public_alpha_wrapper_config({"EUREKA_ALLOW_LIVE_PROBES": "1"})

        self.assertEqual(config.to_summary_dict()["status"], "invalid")
        self.assertIn("live probes", "\n".join(config.validation_errors()))

    def test_path_root_env_names_are_reported_without_values(self) -> None:
        private_path = "D:/private/eureka-index"
        config = load_public_alpha_wrapper_config({"EUREKA_WEB_INDEX_ROOT": private_path})
        summary_text = json.dumps(config.to_summary_dict(), sort_keys=True)

        self.assertIn("EUREKA_WEB_INDEX_ROOT", summary_text)
        self.assertNotIn(private_path, summary_text)
        self.assertEqual(config.to_summary_dict()["status"], "invalid")

    def test_web_server_status_exposes_closed_capabilities(self) -> None:
        config = PublicAlphaWrapperConfig().to_web_server_config()
        status = config.to_status_dict()

        self.assertEqual(status["mode"], "public_alpha")
        self.assertFalse(status["live_probes_enabled"])
        self.assertFalse(status["live_internet_archive_enabled"])
        self.assertFalse(status["downloads_enabled"])
        self.assertFalse(status["local_paths_enabled"])
        self.assertFalse(status["user_storage_enabled"])
        self.assertIn("live_source_probes", status["disabled_capabilities"])
        self.assertIn("payload_downloads", status["disabled_capabilities"])
        self.assertIn("external_baseline_observations", status)
        self.assertEqual(
            status["source_mode_summary"]["active_source_posture"],
            "fixture_backed_local_corpus",
        )
        self.assertFalse(status["source_mode_summary"]["live_source_probes_enabled"])

    def test_status_endpoint_projects_wrapper_summary_safely(self) -> None:
        wrapper_config = PublicAlphaWrapperConfig()
        app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
            server_config=wrapper_config.to_web_server_config(),
        )
        status, _headers, body = _request(app, "/api/status", {})
        payload = json.loads(body)

        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["wrapper_config_summary"]["status"], "valid")
        self.assertEqual(payload["wrapper_config_summary"]["bind_scope"], "local")
        self.assertFalse(payload["downloads_enabled"])
        self.assertEqual(
            payload["source_mode_summary"]["placeholder_sources"],
            "remain_placeholders",
        )
        self.assertNotIn("D:/", body.decode("utf-8"))


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
