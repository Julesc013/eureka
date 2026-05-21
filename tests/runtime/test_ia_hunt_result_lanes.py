import unittest
from typing import Any

from runtime.search_hunt.ia_bridge import (
    build_ia_hunt_result_lanes,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
)


class IAHuntResultLaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.outputs = run_ia_hunt_pipeline_dry_run(plan_ia_hunt_pipeline("sampleproject"))

    def test_operator_projection_includes_ia_hunt_lanes(self) -> None:
        page = build_ia_hunt_result_lanes(self.outputs, "operator_workbench")
        lanes = {lane["lane_kind"]: lane for lane in page["lanes"]}

        for lane_kind in (
            "reviewed_local_results",
            "ia_metadata_candidates",
            "source_cache_hits",
            "review_queue_items",
            "blocked_actions",
            "running_workunits",
            "deferred_deepening",
            "future_extraction_work",
        ):
            self.assertIn(lane_kind, lanes)
        self.assertGreater(lanes["ia_metadata_candidates"]["result_count"], 0)
        self.assertGreater(lanes["running_workunits"]["result_count"], 0)

    def test_public_projection_hides_operator_only_fields(self) -> None:
        page = build_ia_hunt_result_lanes(self.outputs, "public_web")
        self.assertTrue(page["boundary_report"]["operator_fields_hidden"])
        self.assertFalse(_contains_key(page, "operator_notes"))
        self.assertFalse(_contains_key(page, "debug"))
        self.assertFalse(_contains_key(page, "private_local_path_refs"))

    def test_native_projection_is_read_only(self) -> None:
        page = build_ia_hunt_result_lanes(self.outputs, "native_desktop_read_only")
        for lane in page["lanes"]:
            posture = lane["action_posture"]
            self.assertFalse(posture["can_review"])
            self.assertFalse(posture["can_promote_preview"])
            self.assertFalse(posture["can_rebuild_index"])
            self.assertFalse(posture["can_download"])
            self.assertFalse(posture["can_extract"])
            self.assertFalse(posture["can_call_model"])


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


if __name__ == "__main__":
    unittest.main()
