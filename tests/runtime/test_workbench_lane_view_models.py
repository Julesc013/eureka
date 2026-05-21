from __future__ import annotations

import unittest

from runtime.local_service.workbench_result_lanes import build_demo_lane_page, project_lane_for_profile


class WorkbenchLaneViewModelTest(unittest.TestCase):
    def test_operator_projection_preserves_operator_metadata(self) -> None:
        page = build_demo_lane_page("sampleproject", "operator_workbench", from_play_demo=True, from_ia_examples=True)
        reviewed = page["lanes"][0]
        self.assertEqual("operator_workbench", reviewed["projection_profile"])
        self.assertIn("operator_notes", reviewed["items"][0])
        self.assertIn("evidence_refs", reviewed["items"][0])

    def test_public_projection_hides_operator_metadata(self) -> None:
        page = build_demo_lane_page("sampleproject", "public_web", from_play_demo=True, from_ia_examples=True)
        self.assertTrue(page["boundary_report"]["operator_fields_hidden"])
        self.assertFalse(_contains_key(page, "operator_notes"))
        self.assertFalse(_contains_key(page, "evidence_refs"))
        hidden_candidate = [lane for lane in page["lanes"] if lane["lane_kind"] == "ia_metadata_candidates"][0]
        self.assertFalse(hidden_candidate["visible"])
        self.assertEqual([], hidden_candidate["items"])

    def test_project_lane_for_profile_is_read_only_for_native(self) -> None:
        page = build_demo_lane_page("sampleproject", "operator_workbench", from_play_demo=True, from_ia_examples=True)
        native = project_lane_for_profile(page["lanes"][0], "native_desktop_read_only")
        self.assertTrue(native["visible"])
        self.assertFalse(native["action_posture"]["can_download"])
        self.assertFalse(native["action_posture"]["can_extract"])
        self.assertFalse(native["action_posture"]["can_execute"])
        self.assertFalse(native["action_posture"]["can_call_model"])
        self.assertFalse(native["action_posture"]["can_deploy"])


def _contains_key(value: object, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


if __name__ == "__main__":
    unittest.main()
