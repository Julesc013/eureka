from __future__ import annotations

import unittest

from runtime.local.service.workbench_review_promote import (
    create_review_item_from_candidate,
    get_review_item,
    list_review_items,
    record_review_decision,
)


class ReviewQueueFlowTests(unittest.TestCase):
    def test_review_item_created_from_candidate(self) -> None:
        item = create_review_item_from_candidate({"candidate_id": "candidate.review-flow.unit"})
        self.assertEqual("review_pending", item["queue_status"])
        self.assertFalse(item["accepted_truth"])
        detail = get_review_item(item["review_item_id"])
        self.assertTrue(detail["found"], detail)

    def test_operator_token_required_for_recorded_decision(self) -> None:
        item = create_review_item_from_candidate({"candidate_id": "candidate.review-flow.token"})
        blocked = record_review_decision(item["review_item_id"], "accept_local_reviewed", {"dry_run": False})
        self.assertFalse(blocked["allowed"], blocked)
        self.assertIn("operator token", " ".join(blocked["blocked_reasons"]))
        listing = list_review_items()
        self.assertGreaterEqual(listing["review_item_count"], 1)


if __name__ == "__main__":
    unittest.main()
