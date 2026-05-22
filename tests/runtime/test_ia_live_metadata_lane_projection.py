from __future__ import annotations

import unittest

from runtime.local_service.workbench_live_run import build_command_response, create_workbench_resolution_run, get_workbench_resolution_run


class IALiveMetadataLaneProjectionTests(unittest.TestCase):
    def test_workbench_run_projects_blocked_lane_by_default(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", "operator_workbench")
        self.assertEqual("blocked_pending_operator_approval", packet["ia_live_metadata_lane"]["state"])
        lane_kinds = [lane["lane_kind"] for lane in packet["lane_snapshot"]["lane_page"]["lanes"]]
        self.assertIn("ia_live_metadata_candidates", lane_kinds)

    def test_mock_command_updates_operator_lane(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", "operator_workbench")
        response = build_command_response(packet["run_id"], "run_live_ia_metadata_mock", "operator_workbench")
        self.assertTrue(response["allowed"])
        updated = get_workbench_resolution_run(packet["run_id"], "operator_workbench")
        self.assertEqual("candidates_available", updated["ia_live_metadata_lane"]["state"])
        self.assertEqual(1, updated["ia_live_metadata_lane"]["result_count"])

    def test_public_projection_blocks_lane_command(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", "public_web")
        response = build_command_response(packet["run_id"], "run_live_ia_metadata_mock", "public_web")
        self.assertFalse(response["allowed"])
        self.assertEqual("unavailable", response["lane"]["state"])


if __name__ == "__main__":
    unittest.main()
