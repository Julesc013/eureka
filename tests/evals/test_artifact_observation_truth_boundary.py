from __future__ import annotations

import unittest

from evals.hard_queries.artifact_observations.batch_00 import (
    load_artifact_observations,
    load_public_alpha_artifact_gate,
    observation_records,
    read_batch_text,
    validation_truth_flags,
)


class ArtifactObservationTruthBoundaryTests(unittest.TestCase):
    def test_batch_truth_flags_remain_false(self) -> None:
        payload = load_artifact_observations()

        for key, value in validation_truth_flags(payload).items():
            self.assertFalse(value, key)

    def test_no_observation_claims_reviewed_or_verified_artifact_truth(self) -> None:
        for observation in observation_records(load_artifact_observations()):
            self.assertFalse(observation["reviewed_artifact_record_created"], observation["observation_id"])
            self.assertFalse(observation["verified_artifact_created"], observation["observation_id"])
            posture = observation["rights_risk_posture"]
            self.assertFalse(posture["rights_clearance_claimed"], observation["observation_id"])
            self.assertFalse(posture["malware_safety_claimed"], observation["observation_id"])
            self.assertFalse(posture["download_offered"], observation["observation_id"])

    def test_level_three_identity_observations_still_require_human_review(self) -> None:
        level_three = [
            item
            for item in observation_records(load_artifact_observations())
            if item["artifact_level"] == "artifact_level_3_artifact_identity_evidence"
        ]

        self.assertEqual(len(level_three), 5)
        for observation in level_three:
            self.assertIn(observation["review_recommendation"], {"review_candidate", "mark_near_miss"})
            self.assertFalse(observation["reviewed_artifact_record_created"])
            self.assertFalse(observation["verified_artifact_created"])

    def test_metadata_source_and_support_leads_are_not_verified_artifacts(self) -> None:
        for observation in observation_records(load_artifact_observations()):
            if observation["artifact_level"] in {
                "artifact_level_0_mention_only",
                "artifact_level_1_metadata_or_source_lead",
                "artifact_level_2_source_observed_artifact_listing",
            }:
                self.assertFalse(observation["verified_artifact_created"], observation["observation_id"])
                self.assertFalse(observation["reviewed_artifact_record_created"], observation["observation_id"])

    def test_gate_and_reports_preserve_no_runtime_source_or_download_policy(self) -> None:
        gate = load_public_alpha_artifact_gate()
        truth_report = read_batch_text("truth_boundary_report.md")
        rights_report = read_batch_text("rights_risk_posture.md")

        self.assertEqual(gate["reviewed_artifact_record_count"], 0)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertIn("perform runtime source calls", truth_report)
        self.assertIn("download files", truth_report)
        self.assertIn("rights_clearance_claimed: false", rights_report)
        self.assertIn("malware_safety_claimed: false", rights_report)


if __name__ == "__main__":
    unittest.main()
