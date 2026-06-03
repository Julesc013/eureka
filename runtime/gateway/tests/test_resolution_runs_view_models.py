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
        self.assertGreaterEqual(
            view_model["runs"][0]["result_summary"]["result_count"],
            15,
        )

    def test_fallback_summary_maps_to_shared_view_model(self) -> None:
        envelope = {
            "status": "available",
            "run_count": 1,
            "selected_run_id": "run-deterministic-search-0001",
            "runs": [
                {
                    "run_id": "run-deterministic-search-0001",
                    "run_kind": "deterministic_search",
                    "requested_value": "missing",
                    "status": "completed",
                    "started_at": "2026-04-24T00:00:00+00:00",
                    "completed_at": "2026-04-24T00:00:00+00:00",
                    "checked_source_ids": [],
                    "checked_source_families": [],
                    "checked_sources": [],
                    "notices": [],
                    "created_by_slice": "resolution_runs_v0",
                    "fallback_summary": {
                        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
                        "mode": "indexless_live_search_fallback",
                        "status": "candidate",
                        "candidate_count": 1,
                        "candidates": [
                            {
                                "candidate_id": "ia-meta-candidate:test",
                                "status": "candidate",
                                "verified": False,
                                "accepted_truth": False,
                            }
                        ],
                        "accepted_truth": False,
                        "verified": False,
                        "public_action_posture": {
                            "allowed": ["view", "inspect_evidence"],
                            "operator_actions_exposed": False,
                            "unsafe_actions_enabled": False,
                        },
                    },
                }
            ],
        }

        view_model = resolution_runs_envelope_to_view_model(envelope)

        fallback = view_model["runs"][0]["fallback_summary"]
        self.assertEqual(fallback["status"], "candidate")
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["public_action_posture"]["operator_actions_exposed"])

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
