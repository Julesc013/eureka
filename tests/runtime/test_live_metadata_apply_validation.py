from __future__ import annotations

import unittest

from runtime.local_apply import (
    build_live_metadata_local_apply_plan,
    load_live_metadata_review_previews,
    select_eligible_live_metadata_previews,
    validate_live_metadata_apply_plan,
)


class LiveMetadataApplyValidationTests(unittest.TestCase):
    def test_validation_passes_for_temp_plan(self) -> None:
        input_state = load_live_metadata_review_previews()
        plan = build_live_metadata_local_apply_plan(select_eligible_live_metadata_previews(input_state))
        validation = validate_live_metadata_apply_plan(plan)

        self.assertEqual(validation["status"], "pass")
        self.assertTrue(validation["apply_plan_valid"])
        self.assertTrue(validation["temp_instance_required"])
        self.assertFalse(validation["operator_instance_apply_allowed"])


if __name__ == "__main__":
    unittest.main()
