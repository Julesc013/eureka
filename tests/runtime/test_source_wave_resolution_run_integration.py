from __future__ import annotations

import unittest

from runtime.source.action import SOURCE_WAVE_FAMILIES, run_source_family_fixture_action


class SourceWaveResolutionRunIntegrationTests(unittest.TestCase):
    def test_source_action_run_has_lane_projection_for_resolution_kernel(self) -> None:
        run = run_source_family_fixture_action(
            "internet_archive_metadata_v2",
            SOURCE_WAVE_FAMILIES["internet_archive_metadata_v2"].capabilities[0],
            "sampleproject",
        )
        self.assertEqual("completed", run["status"])
        self.assertTrue(run["result_lane_projection_plan"]["lanes"])
        self.assertTrue(run["review_handoff_plan"]["review_item_plan_count"])


if __name__ == "__main__":
    unittest.main()
