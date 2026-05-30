from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples


class ReviewBatchStateUpdateTests(unittest.TestCase):
    def test_state_updates_are_preview_only(self) -> None:
        preview = run_review_batch_from_examples(
            "mark_useful_lead",
            {"projection_profile": "operator_workbench", "dry_run": True},
        )["decision_preview"]
        self.assertGreaterEqual(len(preview["state_updates"]), 1)
        self.assertTrue(all(item["transition_preview"] for item in preview["state_updates"]))
        self.assertTrue(all(item["transition_applied"] is False for item in preview["state_updates"]))


if __name__ == "__main__":
    unittest.main()
