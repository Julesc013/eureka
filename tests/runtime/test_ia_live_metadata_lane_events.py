from __future__ import annotations

import unittest

from runtime.source_observation.ia_live_metadata_lane import REQUIRED_EVENT_TYPES, run_ia_live_metadata_lane_mock


class IALiveMetadataLaneEventsTests(unittest.TestCase):
    def test_required_mock_live_events_are_projection_safe(self) -> None:
        result = run_ia_live_metadata_lane_mock("run-test", "sampleproject")
        event_types = {event["event_type"] for event in result["events"]}
        for required in (
            "ia_live_metadata.requested",
            "ia_live_metadata.policy_checked",
            "ia_live_metadata.approved",
            "ia_live_metadata.started",
            "ia_live_metadata.request_succeeded",
            "ia_live_metadata.normalized",
            "ia_live_metadata.candidates_projected",
            "ia_live_metadata.completed",
        ):
            self.assertIn(required, event_types)
        self.assertIn("ia_live_metadata.rate_limited", REQUIRED_EVENT_TYPES)
        for event in result["events"]:
            self.assertNotIn("raw_response", str(event).lower())
            self.assertNotIn("operator-token", str(event).lower())


if __name__ == "__main__":
    unittest.main()
