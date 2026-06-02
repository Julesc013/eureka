from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyHandoffTests(unittest.TestCase):
    def test_snapshot_and_reassess_handoffs_are_handoff_only(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)

        self.assertTrue(result["snapshot_refresh_handoff"]["snapshot_refresh_handoff_only"])
        self.assertFalse(result["snapshot_refresh_handoff"]["snapshot_refresh_executed"])
        self.assertTrue(result["public_alpha_reassess_handoff"]["public_alpha_reassess_handoff_only"])
        self.assertFalse(result["public_alpha_reassess_handoff"]["public_alpha_reassess_executed"])


if __name__ == "__main__":
    unittest.main()
