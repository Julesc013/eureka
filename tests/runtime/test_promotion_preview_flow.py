from __future__ import annotations

import unittest

from runtime.local_service.workbench_review_promote import (
    build_promotion_preview,
    create_review_item_from_candidate,
    record_review_decision,
)


class PromotionPreviewFlowTests(unittest.TestCase):
    def test_accept_decision_creates_promotion_preview(self) -> None:
        item = create_review_item_from_candidate({"candidate_id": "candidate.preview.accept"})
        decision = record_review_decision(
            item["review_item_id"],
            "accept_local_reviewed",
            {"operator_token": "local-dev-token", "dry_run": False},
        )
        preview = build_promotion_preview(decision)
        self.assertTrue(preview["promotion_preview_created"], preview)
        self.assertTrue(preview["promotion_preview_is_not_promotion"])
        self.assertFalse(preview["accepted_truth"])

    def test_reject_decision_does_not_create_preview(self) -> None:
        item = create_review_item_from_candidate({"candidate_id": "candidate.preview.reject"})
        decision = record_review_decision(
            item["review_item_id"],
            "reject_wrong_object",
            {"operator_token": "local-dev-token", "dry_run": False},
        )
        preview = build_promotion_preview(decision)
        self.assertFalse(preview["promotion_preview_created"], preview)
        self.assertEqual("blocked", preview["status"])


if __name__ == "__main__":
    unittest.main()
