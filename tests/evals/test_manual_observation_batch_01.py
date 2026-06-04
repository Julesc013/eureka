from __future__ import annotations

import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.manual_observations.batch_01 import (
    CANONICAL_STATUSES,
    load_observations,
    load_public_alpha_corpus_delta,
    load_query_mapping,
    load_validation_summary,
    manual_observation_counts,
    observation_records,
    read_batch_text,
    validate_observations,
    validate_public_alpha_corpus_delta,
    validate_query_mapping,
    validation_truth_flags,
)


class ManualObservationBatchOneTests(unittest.TestCase):
    def test_observations_parse_and_cover_all_required_hard_queries(self) -> None:
        payload = load_observations()
        observations = observation_records(payload)

        self.assertEqual(validate_observations(payload), ())
        self.assertEqual(len(observations), 12)
        self.assertEqual({item["query_id"] for item in observations}, set(REQUIRED_HARD_QUERY_IDS))
        for item in observations:
            self.assertIn(item["projected_status"], CANONICAL_STATUSES)
            self.assertLessEqual(item["quote_word_count"], 25)
            self.assertFalse(item["source_observation_self_promoted"])
            self.assertFalse(item["candidate_self_promoted"])
            self.assertFalse(item["reviewed_record_created"])
            self.assertFalse(item["review_event_created"])
            self.assertFalse(item["product_runtime_live_source_call"])
            self.assertFalse(item["synthetic_eval_fixture_used_as_evidence"])

    def test_manual_observation_counts_are_honest(self) -> None:
        counts = manual_observation_counts(load_observations())

        self.assertEqual(counts["reviewed"], 0)
        self.assertEqual(counts["candidate"], 6)
        self.assertEqual(counts["need"], 2)
        self.assertEqual(counts["near_miss"], 3)
        self.assertEqual(counts["policy_blocked"], 0)
        self.assertEqual(counts["unavailable"], 1)
        self.assertEqual(counts["blocked_for_user_details"], 1)

    def test_query_mapping_and_public_alpha_delta_validate(self) -> None:
        observations = load_observations()
        mapping = load_query_mapping()
        delta = load_public_alpha_corpus_delta()

        self.assertEqual(validate_query_mapping(mapping, observations), ())
        self.assertEqual(validate_public_alpha_corpus_delta(delta, observations), ())
        self.assertEqual(delta["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(delta["cumulative_counts_after_batch"]["reviewed_count"], 2)
        self.assertEqual(delta["recommended_next_task"], "HUMAN-REVIEW-BATCH-01")

    def test_windows_98_driver_remains_blocked_for_user_details(self) -> None:
        win98 = next(item for item in observation_records(load_observations()) if item["query_id"] == "hq_driver_win98")

        self.assertEqual(win98["reviewability"], "blocked_for_user_details")
        self.assertEqual(win98["projected_status"], "need")
        self.assertEqual(win98["source_url"], "")
        self.assertIn("hardware_vendor_missing", win98["known_gaps"])
        self.assertIn("forbidden_action: recommend_a_specific_driver", read_batch_text("blocked_for_user_details.yml"))

    def test_source_policy_is_metadata_only(self) -> None:
        sources = read_batch_text("observation_sources.yml")

        self.assertIn("downloads_performed: false", sources)
        self.assertIn("file_fetches_performed: false", sources)
        self.assertIn("wayback_replay_performed: false", sources)
        self.assertIn("product_runtime_live_source_calls_performed: false", sources)
        self.assertIn("manual_web_reference_collection_performed: true", sources)

    def test_truth_boundary_flags_are_false(self) -> None:
        validation = load_validation_summary()

        for key, value in validation_truth_flags(load_observations()).items():
            self.assertFalse(value, key)
        self.assertEqual(validation["status"], "PASS_WITH_WARNINGS")
        self.assertFalse(validation["reviewed_records_created"])
        self.assertFalse(validation["review_events_created"])
        self.assertFalse(validation["product_runtime_live_source_calls_performed"])


if __name__ == "__main__":
    unittest.main()
