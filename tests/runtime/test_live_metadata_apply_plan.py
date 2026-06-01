from __future__ import annotations

import unittest

from runtime.local_apply import (
    build_live_metadata_local_apply_plan,
    load_live_metadata_review_previews,
    select_eligible_live_metadata_previews,
)


class LiveMetadataApplyPlanTests(unittest.TestCase):
    def test_plan_selects_only_eligible_preview_kinds(self) -> None:
        input_state = load_live_metadata_review_previews()
        eligible = select_eligible_live_metadata_previews(input_state)
        plan = build_live_metadata_local_apply_plan(eligible)

        self.assertEqual(plan["apply_target"], "temp_explicit_instance")
        self.assertFalse(plan["operator_instance_apply_requested"])
        self.assertEqual(plan["eligible_preview_count"], 3)
        self.assertEqual(
            [row["record_type"] for row in plan["records_to_create"]],
            ["reviewed_metadata_record", "reviewed_source_lead", "reviewed_source_lead"],
        )


if __name__ == "__main__":
    unittest.main()
