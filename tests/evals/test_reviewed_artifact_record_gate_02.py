from __future__ import annotations

import unittest

from evals.hard_queries.artifact_record_gate.gate_02 import (
    load_gate_delta,
    load_public_alpha_artifact_gate,
    read_gate_text,
    validate_gate_delta,
    validate_public_alpha_artifact_gate,
)
from evals.hard_queries.artifact_reviews.batch_01 import (
    load_artifact_review_summary,
    validate_artifact_review_summary,
)


class ReviewedArtifactRecordGateTwoTests(unittest.TestCase):
    def test_gate_02_validates_and_remains_blocked(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_public_alpha_artifact_gate(gate), ())
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])
        self.assertEqual(gate["reviewed_artifact_record_count"], 4)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["minimum_public_alpha_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 21)
        self.assertEqual(gate["next_recommended_task"], "EXTERNAL-FULL-DISCOVERY-RERUN-03")

    def test_gate_delta_records_progress_without_launch_claim(self) -> None:
        delta = load_gate_delta()

        self.assertEqual(validate_gate_delta(delta), ())
        self.assertEqual(delta["from_gate"], "reviewed_artifact_record_gate_01")
        self.assertEqual(delta["to_gate"], "reviewed_artifact_record_gate_02")
        self.assertEqual(delta["delta"]["reviewed_artifact_record_count"], 2)
        self.assertEqual(delta["delta"]["verified_artifact_count"], 0)
        self.assertEqual(delta["current_totals"]["reviewed_artifact_record_count"], 4)
        self.assertIn("public alpha remains blocked", delta["unchanged_blockers"])

    def test_gate_matches_human_review_batch_one_summary(self) -> None:
        gate = load_public_alpha_artifact_gate()
        summary = load_artifact_review_summary()

        self.assertEqual(validate_artifact_review_summary(summary), ())
        self.assertEqual(gate["reviewed_artifact_record_count"], summary["cumulative_reviewed_artifact_record_count"])
        self.assertEqual(gate["verified_artifact_count"], summary["verified_artifact_count"])

    def test_failure_reasons_include_artifact_and_discovery_blockers(self) -> None:
        reasons = read_gate_text("gate_failure_reasons.yml")

        self.assertIn("insufficient_reviewed_artifact_record_count", reasons)
        self.assertIn("current: 4", reasons)
        self.assertIn("required: 25", reasons)
        self.assertIn("no_verified_artifacts", reasons)
        self.assertIn("win98_driver_blocked_for_user_details", reasons)
        self.assertIn("full_discovery_stale_after_gate_commit", reasons)

    def test_gate_does_not_claim_public_alpha_or_verified_artifacts(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(gate["hard_query_reviewed_artifact_coverage"], "3/6")
        self.assertEqual(gate["hard_query_verified_artifact_coverage"], "0/6")
        self.assertIn("verified artifact", gate["forbidden_public_claims_now"])
        self.assertIn("public alpha ready", gate["forbidden_public_claims_now"])

    def test_prior_green_full_discovery_is_stale_after_this_gate(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(gate["source_snapshot_release_gate_after_this_task"], "stale_after_current_gate_commit")
        self.assertEqual(gate["full_discovery_evidence_posture"], "stale_after_current_gate_commit")


if __name__ == "__main__":
    unittest.main()
