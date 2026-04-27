from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import build_demo_resolution_runs_public_api
from runtime.gateway.public_api import (
    DeterministicSearchRunRequest,
    ResolutionRunReadRequest,
    resolution_runs_envelope_to_view_model,
)
from surfaces.web.workbench import render_resolution_runs_html


class ResolutionRunsIntegrationTestCase(unittest.TestCase):
    def test_run_can_be_started_reloaded_and_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            start_response = public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts("archive")
            )
            read_response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("run-deterministic-search-0001")
            )
            view_model = resolution_runs_envelope_to_view_model(read_response.body)
            html = render_resolution_runs_html(view_model, run_store_root=temp_dir, requested_query="archive")

        self.assertEqual(start_response.status_code, 200)
        self.assertEqual(view_model["selected_run_id"], "run-deterministic-search-0001")
        self.assertGreaterEqual(view_model["runs"][0]["result_summary"]["result_count"], 15)
        self.assertIn("run-deterministic-search-0001", html)
        self.assertIn("ArchiveBox", html)


if __name__ == "__main__":
    unittest.main()
