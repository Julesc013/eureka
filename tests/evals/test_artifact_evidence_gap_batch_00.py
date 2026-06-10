from __future__ import annotations

import unittest

from evals.hard_queries.artifact_evidence_gaps.batch_00 import (
    evidence_gap_records,
    load_evidence_gap_triage,
    load_source_target_plan,
    load_verification_gap_triage,
    read_batch_text,
    source_target_records,
    validate_evidence_gap_triage,
    validate_source_target_plan,
    validate_verification_gap_triage,
    verification_gap_records,
)


class ArtifactEvidenceGapBatchZeroTests(unittest.TestCase):
    def test_gap_triage_validates_and_prioritizes_collection(self) -> None:
        payload = load_evidence_gap_triage()
        records = evidence_gap_records(payload)

        self.assertEqual(validate_evidence_gap_triage(payload), ())
        self.assertEqual(len(records), 6)
        self.assertEqual(payload["triage_counts"]["p0_count"], 2)
        self.assertEqual(payload["triage_counts"]["p1_count"], 2)
        self.assertEqual(payload["triage_counts"]["p2_count"], 2)
        for record in records:
            self.assertEqual(record["triage_status"], "ready_for_manual_observation")
            self.assertFalse(record["runtime_source_call_allowed"])
            self.assertFalse(record["download_allowed"])

    def test_verification_gaps_do_not_create_verified_artifacts(self) -> None:
        payload = load_verification_gap_triage()
        records = verification_gap_records(payload)

        self.assertEqual(validate_verification_gap_triage(payload), ())
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertFalse(record["verified_artifact"])
            self.assertFalse(record["runtime_source_call_allowed"])
            self.assertFalse(record["download_allowed"])
            self.assertFalse(record["safety_claim_allowed"])
            self.assertFalse(record["rights_clearance_claim_allowed"])

    def test_source_target_plan_remains_manual_only(self) -> None:
        payload = load_source_target_plan()
        records = source_target_records(payload)

        self.assertEqual(validate_source_target_plan(payload), ())
        self.assertEqual(payload["allowed_collection_mode"], "manual_reference_packet_only")
        self.assertFalse(payload["runtime_source_calls_allowed"])
        self.assertFalse(payload["downloads_allowed"])
        self.assertEqual(len(records), 6)
        for record in records:
            self.assertEqual(record["safe_next_task"], "MANUAL-ARTIFACT-OBSERVATION-BATCH-01")

    def test_blocked_user_details_remain_explicit(self) -> None:
        blockers = read_batch_text("blocked_for_user_details.yml")

        self.assertIn("USER-HARDWARE-DETAILS-00", blockers)
        self.assertIn("hardware_vendor", blockers)
        self.assertIn("device_id_or_chipset", blockers)


if __name__ == "__main__":
    unittest.main()

