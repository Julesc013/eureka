from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples


class ReviewBatchSnapshotHandoffTests(unittest.TestCase):
    def test_snapshot_refresh_is_handoff_only(self) -> None:
        preview = run_review_batch_from_examples(
            "accept_local_reviewed_preview",
            {"projection_profile": "operator_workbench", "operator_token": "local-dev-token", "dry_run": True},
        )["decision_preview"]
        handoff = preview["snapshot_refresh_handoff"]
        self.assertTrue(handoff["snapshot_refresh_handoff_only"])
        self.assertFalse(handoff["snapshot_refresh_executed"])
        self.assertFalse(handoff["public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
