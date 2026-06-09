from __future__ import annotations

import unittest

from evals.hard_queries.reviewed_artifact_corpus.batch_01 import (
    load_cumulative_artifact_counts,
    load_public_alpha_artifact_gate,
    validate_cumulative_artifact_counts,
    validate_public_alpha_artifact_gate,
)


class ReviewedArtifactGateBatchOneTests(unittest.TestCase):
    def test_public_alpha_artifact_gate_fails_below_threshold(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_public_alpha_artifact_gate(gate), ())
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertEqual(gate["reviewed_artifact_record_count"], 2)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["threshold_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 23)
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])

    def test_cumulative_counts_match_gate_and_keep_verified_zero(self) -> None:
        counts = load_cumulative_artifact_counts()
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_cumulative_artifact_counts(counts), ())
        self.assertEqual(counts["reviewed_artifact_record_count"], gate["reviewed_artifact_record_count"])
        self.assertEqual(counts["verified_artifact_count"], gate["verified_artifact_count"])
        self.assertEqual(counts["non_promoted_artifact_lead_count"], 8)
        self.assertEqual(counts["request_more_evidence_count"], 5)
        self.assertEqual(counts["near_miss_count"], 3)
        self.assertEqual(counts["blocked_for_user_details_count"], 1)

    def test_gate_records_stale_full_discovery_and_next_evidence_task(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(gate["source_snapshot_release_gate"], "stale_after_current_commit")
        self.assertEqual(gate["full_discovery_evidence_posture"], "stale_after_current_commit")
        self.assertEqual(gate["current_head"], "b7253dc3964ef8ac7ef6235965bdd2728e7d6690")
        self.assertEqual(gate["next_recommended_task"], "ARTIFACT-EVIDENCE-GAP-BATCH-00")
        self.assertIn("Windows 98 driver query remains blocked pending hardware identity", gate["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()

