from __future__ import annotations

import unittest

from evals.hard_queries.human_reviews.batch_01 import (
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


class HumanReviewBatchOneTests(unittest.TestCase):
    def test_review_decisions_load_and_validate(self) -> None:
        payload = load_review_decisions()
        decisions = review_decision_records(payload)

        self.assertEqual(validate_review_decisions(payload), ())
        self.assertEqual(len(decisions), 12)
        self.assertEqual({decision["decision"] for decision in decisions}, {"promote", "supersede", "mark_need", "mark_near_miss", "request_more_evidence"})
        for decision in decisions:
            self.assertIn(decision["decision"], REVIEW_DECISIONS)
            self.assertEqual(decision["resulting_status"], DECISION_RESULTING_STATUS[decision["decision"]])
            self.assertEqual(decision["actor_id"], "human_review_batch_01_operator")
            self.assertFalse(decision["synthetic_eval_fixture_used_as_evidence"])
            self.assertFalse(decision["ai_model_output_counted_as_truth"])
            self.assertFalse(decision["source_observation_self_promoted"])
            self.assertFalse(decision["candidate_self_promoted"])
            self.assertFalse(decision["fallback_summary_self_promoted"])
            self.assertFalse(decision["reviewed_index_mutated"])
            self.assertFalse(decision["public_index_mutated"])
            self.assertFalse(decision["master_index_mutated"])

    def test_only_promote_decision_creates_reviewed_seed_record(self) -> None:
        decisions = review_decision_records(load_review_decisions())
        promote_decisions = [decision for decision in decisions if decision["decision"] == "promote"]
        non_promote_decisions = [decision for decision in decisions if decision["decision"] != "promote"]

        self.assertEqual(len(promote_decisions), 1)
        self.assertEqual(promote_decisions[0]["reviewed_record_id"], "reviewed_seed_b01_hq_windows_7_7zip_support_fact")
        self.assertTrue(promote_decisions[0]["local_only_confirmed"])
        self.assertTrue(promote_decisions[0]["source_references_used"])
        self.assertTrue(promote_decisions[0]["citation_reference_ids"])
        self.assertTrue(promote_decisions[0]["reviewed_record_created"])

        for decision in non_promote_decisions:
            self.assertFalse(decision["reviewed_record_created"])
            self.assertIsNone(decision["reviewed_record_id"])
            self.assertNotEqual(decision["resulting_status"], "verified")

    def test_supersede_decisions_link_existing_records_without_creating_truth(self) -> None:
        supersede_decisions = [decision for decision in review_decision_records(load_review_decisions()) if decision["decision"] == "supersede"]

        self.assertEqual(len(supersede_decisions), 3)
        for decision in supersede_decisions:
            self.assertEqual(decision["resulting_status"], "superseded")
            self.assertTrue(decision["superseded_by_reviewed_record_id"])
            self.assertFalse(decision["reviewed_record_created"])

    def test_review_events_link_to_every_decision(self) -> None:
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
        record_items = reviewed_seed_record_records(records)
        self.assertEqual(len(record_items), 1)
        record = record_items[0]
        self.assertEqual(record["canonical_status"], "verified")
        self.assertEqual(record["review_decision_id"], "hrd_b01_hq_windows_7_7zip_promote")
        self.assertEqual(record["review_event_id"], "hre_b01_hq_windows_7_7zip_promote")
        self.assertTrue(record["accepted_truth"])
        self.assertTrue(record["evidence_refs"])
        self.assertTrue(record["source_observation_refs"])
        self.assertTrue(record["reviewed_record_created"])
        self.assertFalse(record["reviewed_index_mutated"])
        self.assertFalse(record["public_index_mutated"])
        self.assertFalse(record["master_index_mutated"])

    def test_decision_counts_match_batch_shape(self) -> None:
        counts = review_decision_counts(load_review_decisions())

        self.assertEqual(counts["promote"], 1)
        self.assertEqual(counts["supersede"], 3)
        self.assertEqual(counts["mark_need"], 1)
        self.assertEqual(counts["mark_near_miss"], 3)
        self.assertEqual(counts["request_more_evidence"], 4)
        self.assertEqual(counts["reviewed"], 1)
        self.assertEqual(counts["review_decision_backed"], 12)
        self.assertEqual(counts["blocked_for_user_details"], 1)


if __name__ == "__main__":
    unittest.main()
