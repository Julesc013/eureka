from __future__ import annotations

import unittest

from runtime.local.service.workbench_result_lanes import LANE_KINDS, build_demo_lane_page, build_result_lane_packet


class WorkbenchResultLanesRuntimeTest(unittest.TestCase):
    def test_required_lane_kinds_exist(self) -> None:
        self.assertEqual(
            {
                "reviewed_local_results",
                "local_candidate_results",
                "source_cache_hits",
                "ia_metadata_candidates",
                "review_queue_items",
                "known_absence",
                "near_misses",
                "blocked_actions",
                "running_workunits",
                "deferred_deepening",
                "future_extraction_work",
            },
            set(LANE_KINDS),
        )

    def test_lane_packet_has_required_fields(self) -> None:
        lane = build_result_lane_packet("local_candidate_results", [{"item_id": "candidate-1", "title": "Candidate"}])
        for field in (
            "schema_version",
            "packet_type",
            "emitted_at",
            "lane_id",
            "lane_kind",
            "projection_profile",
            "truth_level",
            "review_required",
            "items",
            "action_posture",
            "blocked_actions",
            "limitations",
            "provenance",
        ):
            self.assertIn(field, lane)

    def test_truth_levels_and_review_required_are_explicit(self) -> None:
        reviewed = build_result_lane_packet("reviewed_local_results", [{"item_id": "reviewed-1"}])
        candidate = build_result_lane_packet("ia_metadata_candidates", [{"item_id": "ia-candidate-1"}])
        self.assertEqual("reviewed_local_not_master_public_truth", reviewed["truth_level"])
        self.assertFalse(reviewed["review_required"])
        self.assertEqual("ia_metadata_candidate_not_truth", candidate["truth_level"])
        self.assertTrue(candidate["review_required"])

    def test_demo_includes_absence_and_deferred_lanes(self) -> None:
        page = build_demo_lane_page("sampleproject", "operator_workbench", from_play_demo=True, from_ia_examples=True)
        lanes = {lane["lane_kind"]: lane for lane in page["lanes"]}
        self.assertIn("known_absence", lanes)
        self.assertIn("deferred_deepening", lanes)
        self.assertIn("ia_metadata_candidates", lanes)
        self.assertTrue(lanes["ia_metadata_candidates"]["review_required"])


if __name__ == "__main__":
    unittest.main()
