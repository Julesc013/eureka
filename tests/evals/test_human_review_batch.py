from __future__ import annotations

import unittest

from evals.hard_queries.human_reviews.batch_00 import (
    DECISION_RESULTING_STATUS,
    REVIEW_DECISIONS,
    load_review_decisions,
    load_review_events,
    load_reviewed_seed_records,
    review_decision_counts,
    review_decision_records,
    reviewed_seed_record_records,
    validate_review_decisions,
    validate_review_events,
    validate_reviewed_seed_records,
)


class HumanReviewBatchTests(unittest.TestCase):
    def test_review_decisions_load_and_validate(self) -> None:
        payload = load_review_decisions()
        decisions = review_decision_records(payload)

        self.assertEqual(validate_review_decisions(payload), ())
        self.assertEqual(len(decisions), 6)
        self.assertEqual({decision["decision"] for decision in decisions}, {"promote", "mark_need", "mark_near_miss", "request_more_evidence"})
        for decision in decisions:
            self.assertIn(decision["decision"], REVIEW_DECISIONS)
            self.assertEqual(decision["resulting_status"], DECISION_RESULTING_STATUS[decision["decision"]])
            self.assertEqual(decision["actor_id"], "human_review_batch_00_operator")
            self.assertFalse(decision["synthetic_eval_fixture_used_as_evidence"])
            self.assertFalse(decision["ai_model_output_counted_as_truth"])
            self.assertFalse(decision["source_observation_self_promoted"])
            self.assertFalse(decision["candidate_self_promoted"])
            self.assertFalse(decision["fallback_summary_self_promoted"])
            self.assertFalse(decision["reviewed_index_mutated"])
            self.assertFalse(decision["public_index_mutated"])
            self.assertFalse(decision["master_index_mutated"])

    def test_promote_decisions_require_sources_and_create_reviewed_records(self) -> None:
        promote_decisions = [decision for decision in review_decision_records(load_review_decisions()) if decision["decision"] == "promote"]

        self.assertEqual(len(promote_decisions), 2)
        for decision in promote_decisions:
            self.assertTrue(decision["local_only_confirmed"])
            self.assertTrue(decision["source_references_used"])
            self.assertTrue(decision["citation_reference_ids"])
            self.assertTrue(decision["reviewed_record_created"])
            self.assertIsNotNone(decision["reviewed_record_id"])

    def test_non_promote_decisions_do_not_count_as_reviewed(self) -> None:
        non_promote_decisions = [decision for decision in review_decision_records(load_review_decisions()) if decision["decision"] != "promote"]

        self.assertEqual(len(non_promote_decisions), 4)
        for decision in non_promote_decisions:
            self.assertFalse(decision["reviewed_record_created"])
            self.assertIsNone(decision["reviewed_record_id"])
            self.assertNotEqual(decision["resulting_status"], "verified")

    def test_review_events_link_to_decisions(self) -> None:
        decisions = load_review_decisions()
        events = load_review_events()

        self.assertEqual(validate_review_events(events, decisions), ())
        event_ids = {event["review_event_id"] for event in events["review_events"]}
        self.assertEqual(event_ids, {decision["review_event_id"] for decision in review_decision_records(decisions)})
        for event in events["review_events"]:
            self.assertEqual(event["event_kind"], "decision_recorded")
            self.assertFalse(event["reviewed_index_mutated"])
            self.assertFalse(event["public_index_mutated"])
            self.assertFalse(event["master_index_mutated"])

    def test_reviewed_seed_records_are_review_event_backed(self) -> None:
        decisions = load_review_decisions()
        records = load_reviewed_seed_records()

        self.assertEqual(validate_reviewed_seed_records(records, decisions), ())
        self.assertEqual(len(reviewed_seed_record_records(records)), 2)
        promote_event_ids = {decision["review_event_id"] for decision in review_decision_records(decisions) if decision["decision"] == "promote"}
        for record in reviewed_seed_record_records(records):
            self.assertEqual(record["canonical_status"], "verified")
            self.assertIn(record["review_event_id"], promote_event_ids)
            self.assertTrue(record["evidence_refs"])
            self.assertTrue(record["source_observation_refs"])
            self.assertTrue(record["reviewed_record_created"])
            self.assertFalse(record["reviewed_index_mutated"])
            self.assertFalse(record["public_index_mutated"])
            self.assertFalse(record["master_index_mutated"])

    def test_decision_counts_match_expected_batch_shape(self) -> None:
        counts = review_decision_counts(load_review_decisions())

        self.assertEqual(counts["promote"], 2)
        self.assertEqual(counts["mark_need"], 1)
        self.assertEqual(counts["mark_near_miss"], 1)
        self.assertEqual(counts["request_more_evidence"], 2)
        self.assertEqual(counts["reviewed"], 2)
        self.assertEqual(counts["review_decision_backed"], 6)
        self.assertEqual(counts["blocked_for_user_details"], 1)


if __name__ == "__main__":
    unittest.main()
