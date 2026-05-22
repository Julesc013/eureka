from __future__ import annotations

import unittest

from runtime.resolution_run import run_resolution_dry_run


class ResolutionRunProjectionTests(unittest.TestCase):
    def test_public_projection_hides_operator_lanes(self) -> None:
        result = run_resolution_dry_run("sampleproject", projection_profile="public_web")
        page = result["lane_snapshot"]["lane_page"]
        self.assertEqual("public_web", page["projection_profile"])
        self.assertLessEqual(page["visible_lane_count"], page["lane_count"])
        self.assertTrue(page["boundary_report"]["operator_fields_hidden"])

    def test_native_projection_is_read_only(self) -> None:
        result = run_resolution_dry_run("sampleproject", projection_profile="native_desktop_read_only")
        page = result["lane_snapshot"]["lane_page"]
        self.assertEqual("native_desktop_read_only", page["projection_profile"])
        for lane in page["lanes"]:
            posture = lane.get("action_posture", {})
            self.assertFalse(posture.get("can_rebuild_index"), lane.get("lane_kind"))
            self.assertFalse(posture.get("can_download"), lane.get("lane_kind"))
            self.assertFalse(posture.get("can_extract"), lane.get("lane_kind"))


if __name__ == "__main__":
    unittest.main()
