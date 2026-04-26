from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import build_demo_resolution_runs_public_api
from runtime.gateway.public_api import (
    DeterministicSearchRunRequest,
    ResolutionRunReadRequest,
    resolution_runs_envelope_to_view_model,
)


class ResolutionRunsViewModelTestCase(unittest.TestCase):
    def test_run_list_maps_to_shared_view_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts("archive")
            )
            response = public_api.list_runs()

        view_model = resolution_runs_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "listed")
        self.assertEqual(view_model["run_count"], 1)
        self.assertEqual(view_model["runs"][0]["run_kind"], "deterministic_search")
        self.assertEqual(view_model["runs"][0]["result_summary"]["result_count"], 7)

    def test_not_found_maps_to_blocked_view_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("missing-run")
            )

        view_model = resolution_runs_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "blocked")
        self.assertEqual(view_model["selected_run_id"], "missing-run")
        self.assertEqual(view_model["notices"][0]["code"], "resolution_run_not_found")


if __name__ == "__main__":
    unittest.main()
