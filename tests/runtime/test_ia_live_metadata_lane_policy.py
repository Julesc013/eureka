from __future__ import annotations

import unittest

from runtime.source.observation.ia_live_metadata_lane import request_ia_live_metadata_lane, run_ia_live_metadata_lane_live


class IALiveMetadataLanePolicyTests(unittest.TestCase):
    def test_live_now_requires_operator_token_and_allow_live(self) -> None:
        result = run_ia_live_metadata_lane_live("run-test", "sampleproject", allow_live=True)
        self.assertFalse(result["allowed"])
        self.assertIn("operator token is required for live IA metadata", result["policy_decision"]["blocked_reasons"])
        self.assertFalse(result["live_ia_call_performed"])

    def test_public_and_native_commands_are_blocked(self) -> None:
        for profile in ("public_web", "native_desktop_read_only"):
            result = request_ia_live_metadata_lane(
                "run-test",
                {"command_type": "run_live_ia_metadata_mock", "projection_profile": profile, "query": "sampleproject"},
            )
            self.assertFalse(result["allowed"])
            self.assertEqual("unavailable", result["state"])


if __name__ == "__main__":
    unittest.main()
