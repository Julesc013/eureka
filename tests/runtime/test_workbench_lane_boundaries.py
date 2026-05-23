from __future__ import annotations

import unittest

from runtime.local.service.workbench_result_lanes import build_blocked_action_lane, build_demo_lane_page


class WorkbenchLaneBoundaryTest(unittest.TestCase):
    def test_blocked_actions_lane_blocks_unsafe_actions(self) -> None:
        lane = build_blocked_action_lane()
        posture = lane["action_posture"]
        self.assertFalse(posture["can_download"])
        self.assertFalse(posture["can_extract"])
        self.assertFalse(posture["can_execute"])
        self.assertFalse(posture["can_call_model"])
        self.assertFalse(posture["can_deploy"])
        self.assertIn("run_source_probe", posture["blocked_actions"])

    def test_boundary_report_records_no_side_effects(self) -> None:
        page = build_demo_lane_page("sampleproject", "operator_workbench", from_play_demo=True, from_ia_examples=True)
        boundary = page["boundary_report"]
        for key in (
            "source_probe_executed",
            "live_ia_call_performed",
            "source_cache_write_performed",
            "evidence_write_performed",
            "candidate_index_mutated",
            "reviewed_index_mutated",
            "master_index_mutated",
            "operator_instance_mutated",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
            "marketplace_or_app_store_readiness_claimed",
        ):
            self.assertFalse(boundary[key])


if __name__ == "__main__":
    unittest.main()
