from __future__ import annotations

import unittest

from evals.hard_queries.artifact_record_gate.gate_01 import (
    load_gate_delta,
    load_public_alpha_artifact_gate,
    read_gate_text,
    validate_gate_delta,
    validate_public_alpha_artifact_gate,
)


class ArtifactRecordGateAfterHumanReviewTests(unittest.TestCase):
    def test_gate_01_validates_and_remains_blocked(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_public_alpha_artifact_gate(gate), ())
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])
        self.assertEqual(gate["reviewed_artifact_record_count"], 2)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["minimum_public_alpha_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 23)
        self.assertEqual(gate["next_recommended_task"], "REVIEWED-ARTIFACT-CORPUS-BATCH-01")

    def test_gate_delta_records_progress_without_launch_claim(self) -> None:
        delta = load_gate_delta()

        self.assertEqual(validate_gate_delta(delta), ())
        self.assertEqual(delta["from_gate"], "reviewed_artifact_record_gate_00")
        self.assertEqual(delta["to_gate"], "reviewed_artifact_record_gate_01")
        self.assertEqual(delta["delta"]["reviewed_artifact_record_count"], 2)
        self.assertEqual(delta["delta"]["verified_artifact_count"], 0)
        self.assertIn("public alpha remains blocked", delta["unchanged_blockers"])

    def test_failure_reasons_include_corpus_and_hardware_blockers(self) -> None:
        reasons = read_gate_text("gate_failure_reasons.yml")

        self.assertIn("insufficient_reviewed_artifact_record_count", reasons)
        self.assertIn("current: 2", reasons)
        self.assertIn("required: 25", reasons)
        self.assertIn("no_verified_artifacts", reasons)
        self.assertIn("win98_driver_blocked_for_user_details", reasons)
        self.assertIn("hq_blue_ftp_client_xp", reasons)

    def test_prior_green_full_discovery_is_stale_after_this_commit(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(
            gate["source_snapshot_release_gate_after_this_task"],
            "green_at_prior_head_but_stale_after_this_commit",
        )


if __name__ == "__main__":
    unittest.main()

