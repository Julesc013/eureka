from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import build_demo_resolution_runs_public_api
from runtime.gateway.public_api import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    ResolutionRunReadRequest,
)


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class ResolutionRunsPublicApiTestCase(unittest.TestCase):
    def test_start_read_and_list_exact_and_search_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)

            resolve_response = public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(KNOWN_TARGET_REF)
            )
            search_response = public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts("synthetic")
            )
            listed_response = public_api.list_runs()
            read_response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("run-exact-resolution-0001")
            )

        self.assertEqual(resolve_response.status_code, 200)
        self.assertEqual(resolve_response.body["selected_run_id"], "run-exact-resolution-0001")
        self.assertEqual(resolve_response.body["runs"][0]["checked_source_ids"], [
            "github-releases-recorded-fixtures",
            "synthetic-fixtures",
        ])
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.body["selected_run_id"], "run-deterministic-search-0002")
        self.assertEqual(listed_response.body["run_count"], 2)
        self.assertEqual(read_response.body["runs"][0]["run_kind"], "exact_resolution")

    def test_missing_run_returns_structured_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("run-exact-resolution-9999")
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["notices"][0]["code"], "resolution_run_not_found")

    def test_missing_exact_target_records_absence_without_placeholder_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(MISSING_TARGET_REF)
            )

        self.assertEqual(response.status_code, 200)
        run = response.body["runs"][0]
        self.assertIsNone(run["result_summary"])
        self.assertEqual(run["absence_report"]["request_kind"], "resolve")
        self.assertNotIn("internet-archive-placeholder", run["checked_source_ids"])


if __name__ == "__main__":
    unittest.main()
