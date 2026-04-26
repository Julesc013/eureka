from __future__ import annotations

import unittest

from runtime.engine.ranking import assign_result_usefulness


class ResultLaneAssignmentTestCase(unittest.TestCase):
    def test_synthetic_member_gets_inside_bundle_and_direct_lanes(self) -> None:
        usefulness = assign_result_usefulness(
            {
                "record_kind": "synthetic_member",
                "member_path": "drivers/wifi/thinkpad_t42/windows2000/driver.inf",
                "member_kind": "driver",
                "parent_target_ref": "local-bundle-fixture:driver-support-cd@1.0",
                "parent_representation_id": "rep.local-bundle.driver-support-cd.zip",
                "source_family": "local_bundle_fixtures",
                "evidence": ["member_path drivers/wifi/thinkpad_t42/windows2000/driver.inf"],
                "action_hints": ["inspect_parent_bundle", "read_member", "preview_member"],
            }
        )

        self.assertEqual(usefulness.primary_lane, "inside_bundles")
        self.assertIn("best_direct_answer", usefulness.result_lanes)
        self.assertIn("member_has_path", usefulness.user_cost_reasons)
        self.assertIn("member_has_preview_or_readback_action", usefulness.user_cost_reasons)

    def test_documentation_member_gets_documentation_lane(self) -> None:
        usefulness = assign_result_usefulness(
            {
                "record_kind": "synthetic_member",
                "member_path": "README.txt",
                "member_kind": "readme",
                "parent_target_ref": "local-bundle-fixture:driver-support-cd@1.0",
                "source_family": "local_bundle_fixtures",
                "evidence": ["member_text readme"],
            }
        )

        self.assertIn("inside_bundles", usefulness.result_lanes)
        self.assertIn("documentation", usefulness.result_lanes)
        self.assertEqual(usefulness.user_cost_score, 5)
        self.assertIn("documentation_only", usefulness.user_cost_reasons)

    def test_mention_only_record_gets_trace_lane(self) -> None:
        usefulness = assign_result_usefulness(
            {
                "record_kind": "evidence",
                "label": "Firefox XP support note evidence",
                "evidence": ["release note mention"],
            }
        )

        self.assertEqual(usefulness.primary_lane, "mentions_or_traces")
        self.assertEqual(usefulness.user_cost_score, 6)
        self.assertIn("mention_only", usefulness.user_cost_reasons)

    def test_os_media_with_app_suppression_is_demoted(self) -> None:
        usefulness = assign_result_usefulness(
            {
                "record_kind": "resolved_object",
                "label": "Windows 7 ISO install media",
                "object_kind": "operating_system_image",
            },
            suppression_hints=("operating_system_image",),
        )

        self.assertEqual(usefulness.primary_lane, "other")
        self.assertEqual(usefulness.user_cost_score, 8)
        self.assertIn("os_media_suppressed_for_app_intent", usefulness.user_cost_reasons)


if __name__ == "__main__":
    unittest.main()
