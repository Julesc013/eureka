from __future__ import annotations

import tempfile
import unittest

from runtime.gateway import (
    build_demo_resolution_memory_public_api,
    build_demo_resolution_runs_public_api,
)
from runtime.gateway.public_api import (
    PlannedSearchRunRequest,
    ResolutionMemoryCreateRequest,
    ResolutionMemoryReadRequest,
    resolution_memory_envelope_to_view_model,
)
from surfaces.web.workbench import render_resolution_memory_html


class ResolutionMemoryIntegrationTestCase(unittest.TestCase):
    def test_planned_search_run_can_be_saved_as_memory_and_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runs_public_api = build_demo_resolution_runs_public_api(temp_dir)
            memory_public_api = build_demo_resolution_memory_public_api(
                temp_dir,
                run_store_root=temp_dir,
            )
            start_response = runs_public_api.start_planned_search_run(
                PlannedSearchRunRequest.from_parts("latest Firefox before XP support ended")
            )
            create_response = memory_public_api.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts("run-planned-search-0001")
            )
            read_response = memory_public_api.get_memory(
                ResolutionMemoryReadRequest.from_parts("memory-absence-finding-0001")
            )
            view_model = resolution_memory_envelope_to_view_model(read_response.body)
            html = render_resolution_memory_html(
                view_model,
                memory_store_root=temp_dir,
                run_store_root=temp_dir,
                requested_run_id="run-planned-search-0001",
            )

        self.assertEqual(start_response.status_code, 200)
        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(view_model["selected_memory_id"], "memory-absence-finding-0001")
        self.assertIn("latest Firefox before XP support ended", html)
        self.assertIn("memory-absence-finding-0001", html)


if __name__ == "__main__":
    unittest.main()
