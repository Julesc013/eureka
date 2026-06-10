from __future__ import annotations

import unittest

from evals.hard_queries.artifact_evidence_gaps.batch_00 import (
    load_public_alpha_artifact_gate,
    validate_public_alpha_artifact_gate,
)


class ArtifactEvidenceGapGateTests(unittest.TestCase):
    def test_gate_remains_blocked_after_gap_triage(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(validate_public_alpha_artifact_gate(gate), ())
        self.assertEqual(gate["status"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertEqual(gate["reviewed_artifact_record_count"], 2)
        self.assertEqual(gate["verified_artifact_count"], 0)
        self.assertEqual(gate["threshold_reviewed_artifact_records"], 25)
        self.assertEqual(gate["reviewed_artifact_record_gap"], 23)
        self.assertEqual(gate["new_reviewed_artifact_records_created"], 0)
        self.assertEqual(gate["new_verified_artifacts_created"], 0)
        self.assertTrue(gate["public_alpha_blocked"])
        self.assertTrue(gate["dev_to_main_promotion_blocked"])

    def test_gate_points_to_manual_observation_batch_one(self) -> None:
        gate = load_public_alpha_artifact_gate()

        self.assertEqual(gate["next_recommended_task"], "MANUAL-ARTIFACT-OBSERVATION-BATCH-01")
        self.assertEqual(gate["full_discovery_evidence_posture"], "stale_after_current_commit")
        self.assertEqual(gate["current_head"], "619b398dda1f0961e2935381430684b9c922aa10")


if __name__ == "__main__":
    unittest.main()

