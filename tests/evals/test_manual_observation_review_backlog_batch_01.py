from __future__ import annotations

import unittest

from evals.hard_queries.manual_observations.batch_01 import (
    load_non_reviewable_items,
    load_observations,
    load_reviewable_items,
    read_batch_text,
    reviewable_item_records,
    validate_non_reviewable_items,
    validate_reviewable_items,
)


class ManualObservationReviewBacklogBatchOneTests(unittest.TestCase):
    def test_reviewable_items_validate_and_do_not_create_review_events(self) -> None:
        observations = load_observations()
        reviewable = load_reviewable_items()
        items = reviewable_item_records(reviewable)

        self.assertEqual(validate_reviewable_items(reviewable, observations), ())
        self.assertEqual(len(items), 11)
        self.assertFalse(reviewable["review_ledger_decisions_created"])
        for item in items:
            self.assertFalse(item["review_event_created"])
            self.assertFalse(item["reviewed_record_created"])
            self.assertFalse(item["reviewed_index_mutated"])

    def test_non_reviewable_items_validate(self) -> None:
        observations = load_observations()
        non_reviewable = load_non_reviewable_items()

        self.assertEqual(validate_non_reviewable_items(non_reviewable, observations), ())
        self.assertEqual(len(non_reviewable["non_reviewable_items"]), 1)
        self.assertEqual(non_reviewable["non_reviewable_items"][0]["reviewability"], "blocked_for_user_details")

    def test_review_backlog_decision_buckets_are_present(self) -> None:
        backlog = read_batch_text("..\\..\\review_backlog\\batch_01\\review_backlog.yml")
        promote = read_batch_text("..\\..\\review_backlog\\batch_01\\promote_candidate_items.yml")
        needs = read_batch_text("..\\..\\review_backlog\\batch_01\\mark_need_items.yml")
        near_miss = read_batch_text("..\\..\\review_backlog\\batch_01\\mark_near_miss_items.yml")
        request_more = read_batch_text("..\\..\\review_backlog\\batch_01\\request_more_evidence_items.yml")

        self.assertIn("review_decisions_created: false", backlog)
        self.assertIn("review_b01_hq_windows_7_7zip_official_candidate", promote)
        self.assertIn("nonreviewable_b01_hq_driver_win98_user_hardware", needs)
        self.assertIn("review_b01_hq_blue_ftp_flashfxp_xp_near_miss", near_miss)
        self.assertIn("review_b01_hq_ray_tracing_parallel_course_author_candidate", request_more)


if __name__ == "__main__":
    unittest.main()
