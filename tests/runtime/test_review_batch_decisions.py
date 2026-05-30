from __future__ import annotations

import unittest

from runtime.review.batch import run_review_batch_from_examples, validate_batch_decision


class ReviewBatchDecisionTests(unittest.TestCase):
    def test_operator_dry_run_decision_allowed(self) -> None:
        packet = run_review_batch_from_examples()["review_batch_packet"]
        decision = validate_batch_decision(
            packet,
            "mark_useful_lead",
            {"projection_profile": "operator_workbench", "dry_run": True},
        )
        self.assertTrue(decision["allowed"])
        self.assertFalse(decision["creates_accepted_truth"])

    def test_public_decision_blocked(self) -> None:
        packet = run_review_batch_from_examples()["review_batch_packet"]
        decision = validate_batch_decision(packet, "mark_useful_lead", {"projection_profile": "public_web"})
        self.assertFalse(decision["allowed"])
        self.assertIn("public_web projection is read-only", decision["blocked_reasons"])


if __name__ == "__main__":
    unittest.main()
