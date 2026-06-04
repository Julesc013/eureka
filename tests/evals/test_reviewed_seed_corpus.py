from __future__ import annotations

from copy import deepcopy
import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.seed_corpus import (
    BASELINE_PROFILES,
    is_reviewed_seed_item,
    load_public_alpha_readiness,
    load_query_seed_map,
    load_review_backlog,
    load_seed_corpus,
    reviewed_seed_items,
    seed_corpus_counts,
    seed_items,
    validate_public_alpha_readiness,
    validate_query_seed_map,
    validate_review_backlog,
    validate_seed_corpus,
)


class ReviewedSeedCorpusTests(unittest.TestCase):
    def test_seed_corpus_loads_and_validates(self) -> None:
        seed_payload = load_seed_corpus()
        items = seed_items(seed_payload)

        self.assertEqual(validate_seed_corpus(seed_payload), ())
        self.assertEqual(len(items), 6)
        self.assertEqual({item["hard_query_id"] for item in items}, set(REQUIRED_HARD_QUERY_IDS))
        for item in items:
            self.assertEqual(tuple(item["renderer_profiles_expected"]), BASELINE_PROFILES)
            self.assertFalse(item["accepted_truth"])
            self.assertFalse(item["reviewed_seed_material"])
            self.assertFalse(item["reviewed_record_created"])
            self.assertFalse(item["reviewed_index_mutated"])
            self.assertFalse(item["public_index_mutated"])
            self.assertFalse(item["master_index_mutated"])
            self.assertFalse(item["live_source_calls"])

    def test_seed_corpus_counts_are_truthful(self) -> None:
        seed_payload = load_seed_corpus()
        counts = seed_corpus_counts(seed_payload)

        self.assertEqual(counts["reviewed"], 0)
        self.assertEqual(counts["candidate"], 2)
        self.assertEqual(counts["need"], 1)
        self.assertEqual(counts["near_miss"], 1)
        self.assertEqual(counts["policy_blocked"], 1)
        self.assertEqual(counts["unavailable"], 1)
        self.assertEqual(counts["unknown"], 0)
        self.assertEqual(reviewed_seed_items(seed_payload), ())
        for item in seed_items(seed_payload):
            self.assertFalse(is_reviewed_seed_item(item), item["seed_item_id"])
            self.assertNotEqual(item["status"], "verified")

    def test_verified_seed_requires_review_event_and_evidence(self) -> None:
        item = seed_items(load_seed_corpus())[0]
        verified_without_review = deepcopy(item)
        verified_without_review["status"] = "verified"
        verified_without_review["review_event_ref"] = None
        verified_without_review["evidence_refs"] = []
        verified_payload = {"seed_items": [verified_without_review]}

        self.assertIn(
            "seed_hq_windows_7_apps_candidate verified requires review_event_ref and evidence_refs",
            validate_seed_corpus(verified_payload),
        )
        self.assertFalse(is_reviewed_seed_item(verified_without_review))

        verified_with_review = deepcopy(verified_without_review)
        verified_with_review["review_event_ref"] = "review_event:manual_seed_example"
        verified_with_review["evidence_refs"] = ["source_observation:manual_seed_example"]

        self.assertTrue(is_reviewed_seed_item(verified_with_review))

    def test_query_seed_map_and_public_alpha_readiness_are_honest(self) -> None:
        seed_payload = load_seed_corpus()
        query_map = load_query_seed_map()
        readiness = load_public_alpha_readiness()

        self.assertEqual(validate_query_seed_map(query_map, seed_payload), ())
        self.assertEqual(validate_public_alpha_readiness(readiness, seed_payload), ())
        self.assertEqual(readiness["alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(readiness["recommended_next_task"], "MANUAL-OBSERVATION-BATCH-00")
        self.assertEqual(readiness["current"]["hard_queries_mapped"], 6)
        self.assertEqual(readiness["minimum_gap_to_alpha"]["reviewed_records"], 200)
        for item in query_map["query_maps"]:
            self.assertEqual(item["public_alpha_readiness"], "not_ready")
            self.assertEqual(item["reviewed_record_count"], 0)
            self.assertIn("best_available_seed_item_id", item)

    def test_review_backlog_is_not_a_review_decision(self) -> None:
        seed_payload = load_seed_corpus()
        backlog = load_review_backlog()

        self.assertEqual(validate_review_backlog(backlog, seed_payload), ())
        self.assertFalse(backlog["review_decisions_created"])
        self.assertEqual(len(backlog["backlog_items"]), len(seed_items(seed_payload)))
        for item in backlog["backlog_items"]:
            self.assertIn(item["seed_item_id"], {seed["seed_item_id"] for seed in seed_items(seed_payload)})
            self.assertNotIn("review_event_ref", item)
            self.assertNotIn("reviewed_record_created", item)

    def test_truth_boundary_flags_do_not_claim_live_or_reviewed_work(self) -> None:
        readiness = load_public_alpha_readiness()
        truth = readiness["truth_boundary"]

        for key, value in truth.items():
            self.assertFalse(value, key)
        self.assertFalse(readiness["external_full_discovery_required"])
        self.assertTrue(readiness["manual_observation_required"])


if __name__ == "__main__":
    unittest.main()
