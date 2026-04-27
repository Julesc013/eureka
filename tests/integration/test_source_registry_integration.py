from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
import unittest
from urllib.parse import urlencode

from runtime.gateway.public_api import build_demo_source_registry_public_api
from runtime.source_registry import DEFAULT_SOURCE_INVENTORY_DIR, load_source_registry
from surfaces.web.server import WorkbenchWsgiApp


REQUIRED_FIELDS = {
    "source_id",
    "name",
    "source_family",
    "status",
    "roles",
    "surfaces",
    "trust_lane",
    "authority_class",
    "protocols",
    "object_types",
    "artifact_types",
    "identifier_types_emitted",
    "connector",
    "fixture_paths",
    "live_access",
    "extraction_policy",
    "rights_notes",
    "legal_posture",
    "freshness_model",
    "notes",
    "capabilities",
    "coverage",
}


class SourceRegistryIntegrationTestCase(unittest.TestCase):
    def test_seed_inventory_records_are_valid_json_with_unique_ids(self) -> None:
        source_ids: set[str] = set()
        source_paths = sorted(DEFAULT_SOURCE_INVENTORY_DIR.glob("*.source.json"))

        self.assertEqual(len(source_paths), 9)
        for source_path in source_paths:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
            self.assertTrue(REQUIRED_FIELDS.issubset(payload.keys()))
            self.assertIsInstance(payload["source_id"], str)
            self.assertNotIn(payload["source_id"], source_ids)
            source_ids.add(payload["source_id"])

    def test_inventory_projects_through_public_http_surface(self) -> None:
        registry = load_source_registry()
        self.assertEqual(len(registry.records), 9)

        app = WorkbenchWsgiApp(
            resolution_public_api=_FakeResolutionJobsPublicApi(),
            search_public_api=_FakeSearchPublicApi(),
            source_registry_public_api=build_demo_source_registry_public_api(),
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
                    "PATH_INFO": "/api/sources",
                    "QUERY_STRING": urlencode({"status": "active_fixture"}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        payload = json.loads(body.decode("utf-8"))

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(payload["source_count"], 2)
        self.assertEqual(
            {entry["source_id"] for entry in payload["sources"]},
            {"local-bundle-fixtures", "synthetic-fixtures"},
        )


class _FakeResolutionJobsPublicApi:
    def submit_resolution_job(self, request):
        raise AssertionError("Resolution API should not be called in source registry integration test.")

    def read_resolution_job(self, job_id: str):
        raise AssertionError("Resolution API should not be called in source registry integration test.")


class _FakeSearchPublicApi:
    def search_records(self, request):
        raise AssertionError("Search API should not be called in source registry integration test.")


if __name__ == "__main__":
    unittest.main()
