from __future__ import annotations

import unittest

from runtime.source.observation.ia_live_metadata_lane import (
    plan_ia_live_metadata_lane,
    run_ia_live_metadata_lane_dry_run,
    run_ia_live_metadata_lane_mock,
)


class IALiveMetadataLaneTests(unittest.TestCase):
    def test_default_plan_is_blocked_pending_approval(self) -> None:
        result = plan_ia_live_metadata_lane({"run_id": "run-test"}, "sampleproject")
        self.assertEqual("blocked_pending_operator_approval", result["state"])
        self.assertFalse(result["allowed"])
        self.assertFalse(result["live_ia_call_performed"])
        self.assertFalse(result["raw_response_committed"])

    def test_dry_run_emits_policy_events_without_network(self) -> None:
        result = run_ia_live_metadata_lane_dry_run("run-test", "sampleproject")
        event_types = {event["event_type"] for event in result["events"]}
        self.assertIn("ia_live_metadata.policy_checked", event_types)
        self.assertIn("ia_live_metadata.completed", event_types)
        self.assertTrue(result["allowed"])
        self.assertFalse(result["source_probe_executed"])

    def test_mock_live_projects_candidate_only_records(self) -> None:
        result = run_ia_live_metadata_lane_mock("run-test", "sampleproject")
        self.assertEqual("candidates_available", result["state"])
        self.assertGreater(result["candidate_count"], 0)
        self.assertFalse(result["live_ia_call_performed"])
        self.assertTrue(all(item["accepted_truth"] is False for item in result["normalized_candidates"]))


if __name__ == "__main__":
    unittest.main()
