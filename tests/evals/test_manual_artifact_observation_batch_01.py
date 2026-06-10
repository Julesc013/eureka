from __future__ import annotations

import unittest

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS
from evals.hard_queries.artifact_observations.batch_01 import (
    artifact_level_counts,
    load_artifact_observations,
    load_evidence_level_summary,
    load_public_alpha_artifact_gate,
    load_query_mapping,
    load_reviewable_artifact_items,
    load_source_reference_index,
    observation_records,
    read_batch_text,
    reviewable_item_records,
    source_reference_records,
    validate_artifact_observations,
    validate_evidence_level_summary,
    validate_public_alpha_artifact_gate,
    validate_query_mapping,
    validate_reviewable_artifact_items,
    validate_source_reference_index,
    validation_truth_flags,
)


class ManualArtifactObservationBatchOneTests(unittest.TestCase):
    def test_observation_package_loads_and_covers_all_hard_queries(self) -> None:
        payload = load_artifact_observations()
        observations = observation_records(payload)

        self.assertEqual(validate_artifact_observations(payload), ())
        self.assertEqual(len(observations), 7)
        self.assertEqual({item["query_id"] for item in observations}, set(REQUIRED_HARD_QUERY_IDS))
        self.assertEqual(len({item["observation_id"] for item in observations}), len(observations))
        for item in observations:
            self.assertTrue(item["manual_reference_only"])
            self.assertFalse(item["runtime_source_call_performed"])
            self.assertFalse(item["reviewed_artifact_record_created"])
            self.assertFalse(item["verified_artifact_created"])

    def test_artifact_level_summary_matches_observations(self) -> None:
        observations = load_artifact_observations()
        summary = load_evidence_level_summary()

        self.assertEqual(validate_evidence_level_summary(summary, observations), ())
        self.assertEqual(
            artifact_level_counts(observations),
            {
                "artifact_level_0_mention_only": 1,
                "artifact_level_1_metadata_or_source_lead": 0,
                "artifact_level_2_source_observed_artifact_listing": 0,
                "artifact_level_3_artifact_identity_evidence": 4,
                "artifact_level_4_artifact_integrity_evidence": 2,
                "artifact_level_5_verified_acquisition_or_reproducibility_path": 0,
            },
        )
        self.assertEqual(summary["reviewable_artifact_item_count"], 6)
        self.assertEqual(summary["reviewed_artifact_record_count"], 0)
        self.assertEqual(summary["verified_artifact_count"], 0)

    def test_query_mapping_reviewable_items_and_sources_validate(self) -> None:
        observations = load_artifact_observations()
        reviewable = load_reviewable_artifact_items()

        self.assertEqual(validate_query_mapping(load_query_mapping(), observations), ())
        self.assertEqual(validate_reviewable_artifact_items(reviewable, observations), ())
        self.assertEqual(validate_source_reference_index(load_source_reference_index()), ())
        self.assertEqual(len(reviewable_item_records(reviewable)), 6)
        self.assertEqual(len(source_reference_records(load_source_reference_index())), 12)
        for source in source_reference_records(load_source_reference_index()):
            self.assertTrue(source["manual_reference_only"])
            self.assertFalse(source["runtime_source_call_performed"])
            self.assertFalse(source["download_performed"])
            self.assertFalse(source["file_fetch_performed"])
            self.assertFalse(source["wayback_replay_performed"])

    def test_truth_boundary_flags_remain_false(self) -> None:
        for key, value in validation_truth_flags(load_artifact_observations()).items():
            self.assertFalse(value, key)

    def test_public_alpha_artifact_gate_remains_blocked(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_public_alpha_artifact_gate(gate), ())
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertEqual(gate["reviewed_artifact_record_count"], 2)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["new_reviewed_artifact_record_count"], 0)
        self.assertEqual(gate["new_verified_artifact_count"], 0)
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_blocked"])
        self.assertEqual(gate["next_recommended_task"], "HUMAN-ARTIFACT-REVIEW-BATCH-01")

    def test_windows_98_driver_remains_blocked_without_hardware_details(self) -> None:
        observations = observation_records(load_artifact_observations())
        blocker = next(item for item in observations if item["query_id"] == "hq_driver_win98")

        self.assertEqual(blocker["public_projection_status"], "need")
        self.assertTrue(blocker["unsafe_to_recommend_random_driver"])
        self.assertEqual(blocker["source_refs"], [])
        self.assertIn("hardware_vendor", blocker["missing_for_reviewed_artifact_record"])
        self.assertIn("USER-HARDWARE-DETAILS-00", read_batch_text("blocked_for_user_details.yml"))


if __name__ == "__main__":
    unittest.main()
