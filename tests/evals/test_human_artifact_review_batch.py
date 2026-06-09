from __future__ import annotations

import unittest

from evals.hard_queries.artifact_observations.batch_00 import (
    load_reviewable_artifact_items,
    read_batch_text as read_observation_batch_text,
    reviewable_item_records,
)
from evals.hard_queries.artifact_reviews.batch_00 import (
    load_artifact_review_summary,
    load_review_decision_backed_outcomes,
    load_review_decisions,
    load_review_events,
    outcome_records,
    read_batch_text,
    review_decision_records,
    review_event_records,
    validate_artifact_review_summary,
    validate_review_decision_backed_outcomes,
    validate_review_decisions,
    validate_review_events,
)


class HumanArtifactReviewBatchTests(unittest.TestCase):
    def test_review_decisions_events_and_outcomes_validate(self) -> None:
        decisions = load_review_decisions()
        events = load_review_events()
        outcomes = load_review_decision_backed_outcomes()
        summary = load_artifact_review_summary()

        self.assertEqual(validate_review_decisions(decisions), ())
        self.assertEqual(validate_review_events(events, decisions), ())
        self.assertEqual(validate_review_decision_backed_outcomes(outcomes, decisions), ())
        self.assertEqual(validate_artifact_review_summary(summary), ())

    def test_all_reviewable_items_receive_a_review_decision(self) -> None:
        reviewable_ids = {item["review_item_id"] for item in reviewable_item_records(load_reviewable_artifact_items())}
        decision_item_ids = {item["source_review_item_id"] for item in review_decision_records(load_review_decisions())}

        self.assertEqual(reviewable_ids, decision_item_ids)

    def test_review_decision_counts_preserve_truth_boundary(self) -> None:
        decisions = review_decision_records(load_review_decisions())
        decision_counts: dict[str, int] = {}
        for decision in decisions:
            decision_counts[decision["review_decision"]] = decision_counts.get(decision["review_decision"], 0) + 1
            self.assertTrue(decision["evidence_refs"])
            self.assertTrue(decision["source_refs"])
            self.assertTrue(decision["rationale"])
            self.assertFalse(decision["verified_artifact_created"])
            self.assertFalse(decision["reviewed_index_mutated"])
            self.assertFalse(decision["public_index_mutated"])
            self.assertFalse(decision["master_index_mutated"])
            self.assertIn("verified", " ".join(decision["what_must_not_be_claimed_publicly"]))

        self.assertEqual(len(decisions), 10)
        self.assertEqual(decision_counts["promote"], 2)
        self.assertEqual(decision_counts["request_more_evidence"], 5)
        self.assertEqual(decision_counts["mark_near_miss"], 3)
        self.assertNotIn("reject", decision_counts)

    def test_promote_decisions_have_review_events_and_reviewed_record_ids(self) -> None:
        promote_decisions = [item for item in review_decision_records(load_review_decisions()) if item["review_decision"] == "promote"]
        event_by_review = {item["review_id"]: item for item in review_event_records(load_review_events())}
        outcome_by_review = {item["review_id"]: item for item in outcome_records(load_review_decision_backed_outcomes())}

        self.assertEqual(len(promote_decisions), 2)
        for decision in promote_decisions:
            event = event_by_review[decision["review_id"]]
            outcome = outcome_by_review[decision["review_id"]]
            self.assertEqual(event["event_type"], "artifact_review_decision")
            self.assertEqual(event["decision"], "promote")
            self.assertEqual(outcome["outcome_status"], "verified")
            self.assertEqual(outcome["artifact_claim_status"], "reviewed_artifact_record")
            self.assertEqual(outcome["reviewed_artifact_record_id"], decision["reviewed_artifact_record_id"])
            self.assertFalse(outcome["verified_artifact_created"])

    def test_blocked_driver_remains_a_user_detail_blocker(self) -> None:
        artifact_review_blockers = read_batch_text("blocked_for_user_details.yml")
        observation_blockers = read_observation_batch_text("blocked_for_user_details.yml")

        for text in (artifact_review_blockers, observation_blockers):
            self.assertIn("USER-HARDWARE-DETAILS-00", text)
            self.assertIn("hardware_vendor", text)
            self.assertIn("device_id_or_chipset", text)

    def test_truth_boundary_report_names_forbidden_actions(self) -> None:
        report = read_batch_text("truth_boundary_report.md")

        self.assertIn("does not create verified artifacts", report)
        self.assertIn("Reviewed/public/master indexes were not mutated", report)
        self.assertIn("No download", report)
        self.assertIn("Wayback replay", report)


if __name__ == "__main__":
    unittest.main()
