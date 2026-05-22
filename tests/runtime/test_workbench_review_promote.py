from __future__ import annotations

import unittest

from runtime.local_service.workbench_review_promote import run_review_promote_flow


class WorkbenchReviewPromoteTests(unittest.TestCase):
    def test_operator_dry_run_creates_review_item_and_preview(self) -> None:
        result = run_review_promote_flow(dry_run=True)
        self.assertEqual("pass", result["status"])
        self.assertTrue(result["review_item_created"])
        self.assertTrue(result["promotion_preview_created"])
        self.assertTrue(result["operator_token_required"])
        self.assertFalse(result["operator_instance_mutated"])
        self.assertFalse(result["master_index_mutated"])
        self.assertFalse(result["committed_data_public_index_mutated"])


if __name__ == "__main__":
    unittest.main()
