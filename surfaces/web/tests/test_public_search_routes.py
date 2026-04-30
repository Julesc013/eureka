from __future__ import annotations

from io import BytesIO
import json
from urllib.parse import urlencode
import unittest

from runtime.gateway.public_api import (
    build_demo_absence_public_api,
    build_demo_action_plan_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_public_search_public_api,
    build_demo_query_planner_public_api,
    build_demo_representation_selection_public_api,
    build_demo_representations_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


class PublicSearchRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            absence_public_api=build_demo_absence_public_api(),
            action_plan_public_api=build_demo_action_plan_public_api(),
            comparison_public_api=build_demo_comparison_public_api(),
            compatibility_public_api=build_demo_compatibility_public_api(),
            decomposition_public_api=build_demo_decomposition_public_api(),
            handoff_public_api=build_demo_representation_selection_public_api(),
            query_planner_public_api=build_demo_query_planner_public_api(),
            representations_public_api=build_demo_representations_public_api(),
            search_public_api=build_demo_search_public_api(),
            public_search_public_api=build_demo_public_search_public_api(),
            source_registry_public_api=build_demo_source_registry_public_api(),
            subject_states_public_api=build_demo_subject_states_public_api(),
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

    def test_v1_search_route_returns_public_envelope(self) -> None:
        status, headers, body = self._request("/api/v1/search", {"q": "firefox xp"})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["contract_id"], "eureka_public_search_response_v0")
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertGreater(len(payload["results"]), 0)
        card = payload["results"][0]
        self.assertIn("source", card)
        self.assertIn("user_cost", card)
        self.assertIn("evidence", card)
        self.assertIn("compatibility", card)

    def test_v1_query_plan_status_and_source_routes(self) -> None:
        plan_status, _, plan_body = self._request("/api/v1/query-plan", {"q": "driver.inf"})
        status_status, _, status_body = self._request("/api/v1/status")
        sources_status, _, sources_body = self._request("/api/v1/sources")
        source_status, _, source_body = self._request("/api/v1/source/local-bundle-fixtures")

        self.assertEqual(plan_status, "200 OK")
        self.assertTrue(json.loads(plan_body)["no_live_probe"])
        self.assertEqual(status_status, "200 OK")
        status_payload = json.loads(status_body)
        self.assertTrue(status_payload["public_search"]["implemented"])
        self.assertFalse(status_payload["public_search"]["hosted_public_deployment"])
        self.assertFalse(status_payload["public_search"]["downloads_enabled"])
        self.assertEqual(sources_status, "200 OK")
        self.assertGreater(json.loads(sources_body)["source_count"], 0)
        self.assertEqual(source_status, "200 OK")
        self.assertEqual(json.loads(source_body)["selected_source_id"], "local-bundle-fixtures")

    def test_v1_search_rejects_forbidden_and_unbounded_inputs(self) -> None:
        cases = [
            ({"q": "archive", "index_path": "D:/private/index.sqlite3"}, "local_paths_forbidden"),
            ({"q": "archive", "url": "https://example.invalid"}, "forbidden_parameter"),
            ({"q": "archive", "live_probe": "1"}, "live_probes_disabled"),
            ({"q": "archive", "limit": "100"}, "limit_too_large"),
            ({"q": "archive", "mode": "live_probe"}, "live_probes_disabled"),
        ]
        for query, expected_code in cases:
            with self.subTest(query=query):
                status, _, body = self._request("/api/v1/search", query)
                payload = json.loads(body)
                self.assertEqual(status, "400 Bad Request")
                self.assertFalse(payload["ok"])
                self.assertEqual(payload["error"]["code"], expected_code)

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], str]:
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
        return str(captured["status"]), dict(captured["headers"]), body.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
