from __future__ import annotations

import unittest

from runtime.local_apply import run_review_batch_apply_next


class ReviewBatchApplyKnownNeedsAbsencesTests(unittest.TestCase):
    def test_reviewed_needs_and_absences_are_not_truth(self) -> None:
        result = run_review_batch_apply_next(from_examples=True, use_temp_instance=True)

        self.assertEqual(result["reviewed_known_needs_created"], 2)
        self.assertEqual(result["reviewed_bounded_absences_created"], 2)
        for record in result["reviewed_known_needs"] + result["reviewed_bounded_absences"]:
            self.assertFalse(record["accepted_truth"])
            self.assertIn("reviewed_claim_scope", record)


if __name__ == "__main__":
    unittest.main()
