import json
import unittest
from pathlib import Path

from scripts.validate_search_hunt_closeout import validate_future_gate


class SearchHuntFutureTrackGateTests(unittest.TestCase):
    def test_future_track_gate_requires_hunt_workunit_path(self):
        gate = json.loads(Path("control/inventory/search_hunt_future_track_gate_final.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["syn_must_use_hunt_and_local_appliance_for_query_pressure"])
        self.assertTrue(gate["f0_extraction_tasks_must_be_generated_as_workunits_where_applicable"])
        self.assertTrue(gate["future_tracks_may_not_bypass_hunt_workunit_review_index_without_exception"])

    def test_future_track_gate_rejects_bypass(self):
        errors = []
        validate_future_gate(
            {
                "control/inventory/search_hunt_future_track_gate_final.json": {
                    "schema_version": "search_hunt_future_track_gate_final.v0",
                    "future_tracks_may_not_bypass_hunt_workunit_review_index_without_exception": False,
                }
            },
            errors,
        )
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
