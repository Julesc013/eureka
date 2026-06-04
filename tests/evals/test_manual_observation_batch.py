from __future__ import annotations

import unittest

from evals.hard_queries.manual_observations.batch_00 import (
    CANONICAL_STATUSES,
    REQUIRED_HARD_QUERY_IDS,
    load_corpus_gate_status,
    load_observations,
    load_public_safe_examples,
    load_query_mapping,
    load_source_references,
    load_validation_summary,
    manual_observation_counts,
    observation_records,
    validate_corpus_gate_status,
    validate_observations,
)


class ManualObservationBatchTests(unittest.TestCase):
    def test_observations_parse_and_cover_required_hard_queries(self) -> None:
        payload = load_observations()
        observations = observation_records(payload)

        self.assertEqual(validate_observations(payload), ())
        self.assertEqual(len(observations), 6)
        self.assertEqual({item["query_id"] for item in observations}, set(REQUIRED_HARD_QUERY_IDS))
        for item in observations:
            self.assertIn(item["proposed_status"], CANONICAL_STATUSES)
            self.assertFalse(item["source_observation_self_promoted"])
            self.assertFalse(item["candidate_self_promoted"])
            self.assertFalse(item["reviewed_record_created"])
            self.assertFalse(item["review_event_created"])
            self.assertFalse(item["product_runtime_live_source_call"])
            self.assertFalse(item["synthetic_eval_fixture_used_as_evidence"])
            for snippet in item["evidence_snippets"]:
                self.assertLessEqual(len(snippet.split()), 25, item["observation_id"])

    def test_source_references_are_bounded_metadata_only(self) -> None:
        observations = observation_records(load_observations())
        source_payload = load_source_references()
        refs = {item["source_reference_id"]: item for item in source_payload["source_references"]}

        self.assertFalse(source_payload["source_policy"]["downloads_performed"])
        self.assertFalse(source_payload["source_policy"]["file_fetches_performed"])
        self.assertFalse(source_payload["source_policy"]["wayback_replay_performed"])
        self.assertFalse(source_payload["source_policy"]["product_runtime_live_source_calls_performed"])
        self.assertTrue(source_payload["source_policy"]["manual_web_reference_collection_performed"])
        for observation in observations:
            source_ref = refs[observation["source_reference"]]
            if not source_ref["uri"]:
                self.assertEqual(source_ref["source_family"], "missing_query_scope")
                self.assertEqual(observation["proposed_status"], "need")
            else:
                self.assertTrue(source_ref["uri"].startswith("https://"))

    def test_query_mapping_and_corpus_gate_counts_are_honest(self) -> None:
        observations = load_observations()
        mapping = load_query_mapping()
        gate = load_corpus_gate_status()

        self.assertEqual({item["query_id"] for item in mapping["query_maps"]}, set(REQUIRED_HARD_QUERY_IDS))
        self.assertEqual(validate_corpus_gate_status(gate, observations), ())
        self.assertEqual(manual_observation_counts(observations), {
            "reviewed": 0,
            "candidate": 3,
            "need": 1,
            "near_miss": 1,
            "mention_only": 0,
            "policy_blocked": 0,
            "unavailable": 1,
            "unknown": 0,
        })
        self.assertEqual(gate["public_alpha_corpus_gate"], "FAIL_INSUFFICIENT_REVIEWED_CORPUS")
        self.assertEqual(gate["counts"]["review_queue_items"], 5)
        self.assertEqual(gate["counts"]["manual_followup_items"], 1)
        self.assertEqual(gate["recommended_next_task"], "HUMAN-REVIEW-BATCH-00")

    def test_truth_boundary_flags_do_not_claim_runtime_or_review_work(self) -> None:
        batch_truth = load_observations()["batch_truth_boundary"]
        gate_truth = load_corpus_gate_status()["truth_boundary"]
        validation = load_validation_summary()

        for key, value in batch_truth.items():
            self.assertFalse(value, key)
        for key, value in gate_truth.items():
            self.assertFalse(value, key)
        self.assertEqual(validation["status"], "PASS_WITH_WARNINGS")
        self.assertFalse(validation["full_discovery_required"])

    def test_public_safe_examples_are_read_only_and_not_reviewed(self) -> None:
        examples = load_public_safe_examples()["examples"]

        self.assertGreaterEqual(len(examples), 4)
        for example in examples:
            self.assertIn(example["status"], CANONICAL_STATUSES)
            self.assertFalse(example["reviewed"])
            self.assertTrue(set(example["allowed_public_actions"]).issubset({"view", "inspect_evidence", "cite"}))


if __name__ == "__main__":
    unittest.main()
