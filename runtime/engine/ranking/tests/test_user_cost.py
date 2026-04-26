from __future__ import annotations

import unittest

from runtime.engine.ranking import assign_result_usefulness


class UserCostAssignmentTestCase(unittest.TestCase):
    def test_synthetic_member_cost_is_lower_than_parent_bundle(self) -> None:
        member = assign_result_usefulness(
            {
                "record_kind": "synthetic_member",
                "member_path": "utilities/7z920.exe.txt",
                "member_kind": "utility",
                "parent_target_ref": "local-bundle-fixture:windows-utility-bundle@1.0",
                "source_family": "local_bundle_fixtures",
                "evidence": ["member_path utilities/7z920.exe.txt"],
                "action_hints": ["read_member", "preview_member"],
            }
        )
        parent = assign_result_usefulness(
            {
                "record_kind": "resolved_object",
                "label": "Windows 7 utility bundle recorded fixture",
                "source_family": "local_bundle_fixtures",
                "evidence": ["bundle fixture evidence"],
            }
        )

        self.assertLess(member.user_cost_score, parent.user_cost_score)
        self.assertIn("parent_bundle_context_only", parent.user_cost_reasons)

    def test_unknown_record_falls_back_to_safe_high_cost(self) -> None:
        usefulness = assign_result_usefulness({"record_kind": "unknown"})

        self.assertEqual(usefulness.primary_lane, "other")
        self.assertEqual(usefulness.user_cost_score, 9)
        self.assertIn("compatibility_unknown", usefulness.user_cost_reasons)

    def test_reasons_are_deterministic_and_unique(self) -> None:
        usefulness = assign_result_usefulness(
            {
                "record_kind": "synthetic_member",
                "member_path": "compatibility/windows7.txt",
                "member_kind": "compatibility_note",
                "parent_target_ref": "local-bundle-fixture:windows-utility-bundle@1.0",
                "source_family": "local_bundle_fixtures",
                "evidence": ["Windows 7 compatibility"],
                "action_hints": ["read_member", "read_member", "preview_member"],
            }
        )

        self.assertEqual(
            list(usefulness.user_cost_reasons),
            list(dict.fromkeys(usefulness.user_cost_reasons)),
        )
        self.assertIn("user cost 5", usefulness.usefulness_summary)


if __name__ == "__main__":
    unittest.main()
