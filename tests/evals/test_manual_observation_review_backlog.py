from __future__ import annotations

import unittest

from evals.hard_queries.manual_observations.batch_00 import (
    load_blocked_or_unavailable,
    load_manual_followup_needed,
    load_non_reviewable_items,
    load_observations,
    load_review_backlog,
    load_reviewable_items,
    observation_records,
    validate_non_reviewable_items,
    validate_reviewable_items,
)


class ManualObservationReviewBacklogTests(unittest.TestCase):
    def test_reviewable_items_require_source_observation_and_do_not_decide(self) -> None:
        observations = load_observations()
        payload = load_reviewable_items()

        self.assertEqual(validate_reviewable_items(payload, observations), ())
        self.assertFalse(payload["review_ledger_decisions_created"])
        self.assertEqual(len(payload["reviewable_items"]), 5)
        for item in payload["reviewable_items"]:
            self.assertTrue(item["source_observation_ref"].startswith("manual_source_observation:"))
            self.assertIn(item["recommended_review_decision"], {
                "promote",
                "reject",
                "supersede",
                "mark_near_miss",
                "mark_need",
                "mark_policy_blocked",
                "request_more_evidence",
            })
            self.assertFalse(item["review_event_created"])
            self.assertFalse(item["reviewed_record_created"])
            self.assertFalse(item["reviewed_index_mutated"])

    def test_non_reviewable_items_are_followup_only(self) -> None:
        observations = load_observations()
        payload = load_non_reviewable_items()

        self.assertEqual(validate_non_reviewable_items(payload, observations), ())
        self.assertEqual(len(payload["non_reviewable_items"]), 1)
        item = payload["non_reviewable_items"][0]
        self.assertEqual(item["query_id"], "hq_driver_win98")
        self.assertFalse(item["reviewable_now"])
        self.assertEqual(item["recommended_next_task"], "USER-SOURCE-COLLECTION-00")

    def test_review_backlog_mirror_matches_reviewable_items(self) -> None:
        reviewable_ids = {item["reviewable_item_id"] for item in load_reviewable_items()["reviewable_items"]}
        backlog = load_review_backlog()

        self.assertFalse(backlog["review_ledger_decisions_created"])
        self.assertFalse(backlog["review_event_records_created"])
        self.assertEqual({item["backlog_item_id"] for item in backlog["items"]}, reviewable_ids)

    def test_followup_and_blocked_unavailable_files_reference_known_observations(self) -> None:
        observation_ids = {item["observation_id"] for item in observation_records(load_observations())}
        followup = load_manual_followup_needed()
        blocked = load_blocked_or_unavailable()

        for item in followup["items"]:
            self.assertIn(item["observation_id"], observation_ids)
            self.assertEqual(item["recommended_next_task"], "USER-SOURCE-COLLECTION-00")
        for item in blocked["items"]:
            self.assertIn(item["observation_id"], observation_ids)
            self.assertIn(item["status"], {"need", "unavailable", "policy_blocked", "unknown"})

    def test_promote_recommendation_is_not_a_review_decision(self) -> None:
        firefox_item = next(item for item in load_reviewable_items()["reviewable_items"] if item["query_id"] == "hq_firefox_last_xp")

        self.assertEqual(firefox_item["recommended_review_decision"], "promote")
        self.assertFalse(firefox_item["review_event_created"])
        self.assertFalse(firefox_item["reviewed_record_created"])


if __name__ == "__main__":
    unittest.main()
