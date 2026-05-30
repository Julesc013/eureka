from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples


class ReviewBatchLocalApplyHandoffTests(unittest.TestCase):
    def test_local_apply_is_handoff_only(self) -> None:
        preview = run_review_batch_from_examples(
            "accept_local_reviewed_preview",
            {"projection_profile": "operator_workbench", "operator_token": "local-dev-token", "dry_run": True},
        )["decision_preview"]
        handoff = preview["local_apply_handoff"]
        self.assertTrue(handoff["local_apply_handoff_only"])
        self.assertFalse(handoff["local_apply_executed"])
        self.assertFalse(handoff["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()
