from __future__ import annotations

import unittest

from evals.hard_queries.artifact_reviews.batch_00 import load_review_decisions, review_decision_records
from evals.hard_queries.reviewed_artifact_corpus.batch_01 import (
    artifact_decision_outcome_records,
    load_artifact_decision_backed_outcomes,
    load_artifact_level_inventory,
    load_cumulative_artifact_counts,
    load_non_promoted_artifact_leads,
    load_query_coverage,
    load_reviewed_artifact_records,
    load_source_reference_index,
    load_supersession_or_duplicate_control,
    non_promoted_lead_records,
    query_coverage_records,
    read_batch_text,
    reviewed_artifact_record_records,
    source_reference_records,
    validate_artifact_decision_backed_outcomes,
    validate_artifact_level_inventory,
    validate_cumulative_artifact_counts,
    validate_non_promoted_artifact_leads,
    validate_query_coverage,
    validate_reviewed_artifact_records,
    validate_source_reference_index,
    validate_supersession_or_duplicate_control,
)


class ReviewedArtifactCorpusBatchOneTests(unittest.TestCase):
    def test_corpus_package_loads_and_validates(self) -> None:
        self.assertEqual(validate_reviewed_artifact_records(load_reviewed_artifact_records()), ())
        self.assertEqual(validate_artifact_decision_backed_outcomes(load_artifact_decision_backed_outcomes()), ())
        self.assertEqual(validate_non_promoted_artifact_leads(load_non_promoted_artifact_leads()), ())
        self.assertEqual(validate_artifact_level_inventory(load_artifact_level_inventory()), ())
        self.assertEqual(validate_query_coverage(load_query_coverage()), ())
        self.assertEqual(validate_cumulative_artifact_counts(load_cumulative_artifact_counts()), ())
        self.assertEqual(validate_source_reference_index(load_source_reference_index()), ())
        self.assertEqual(validate_supersession_or_duplicate_control(load_supersession_or_duplicate_control()), ())

    def test_only_promoted_human_review_decisions_become_reviewed_artifact_records(self) -> None:
        promoted_record_ids = {
            decision["reviewed_artifact_record_id"]
            for decision in review_decision_records(load_review_decisions())
            if decision["review_decision"] == "promote"
        }
        corpus_record_ids = {
            record["artifact_record_id"]
            for record in reviewed_artifact_record_records(load_reviewed_artifact_records())
        }
        non_promoted_outcomes = [
            outcome
            for outcome in artifact_decision_outcome_records(load_artifact_decision_backed_outcomes())
            if outcome["decision"] != "promote"
        ]

        self.assertEqual(corpus_record_ids, promoted_record_ids)
        self.assertEqual(len(corpus_record_ids), 2)
        for outcome in non_promoted_outcomes:
            self.assertFalse(outcome["counts_as_reviewed_artifact_record"])
            self.assertIsNone(outcome["artifact_record_id"])
            self.assertFalse(outcome["verified_artifact"])

    def test_reviewed_artifact_records_are_not_verified_artifacts(self) -> None:
        for record in reviewed_artifact_record_records(load_reviewed_artifact_records()):
            self.assertEqual(record["status"], "reviewed_artifact_record")
            self.assertEqual(record["canonical_status"], "verified")
            self.assertEqual(record["artifact_level"], "artifact_level_3_artifact_identity_evidence")
            self.assertFalse(record["verified_artifact"])
            self.assertFalse(record["rights_posture"]["rights_clearance_claimed"])
            self.assertFalse(record["safety_posture"]["malware_safety_claimed"])
            self.assertFalse(record["reviewed_index_mutated"])
            self.assertIn("integrity evidence", record["known_gaps"])

    def test_level_zero_one_and_two_material_is_not_inflated(self) -> None:
        inventory = load_artifact_level_inventory()
        reviewed_levels = inventory["reviewed_artifact_record_level_counts"]
        non_promoted_levels = inventory["non_promoted_level_counts"]
        blocked_levels = inventory["blocked_for_user_details_level_counts"]

        self.assertEqual(reviewed_levels, {"artifact_level_3_artifact_identity_evidence": 2})
        self.assertEqual(non_promoted_levels["artifact_level_1_metadata_or_source_lead"], 1)
        self.assertEqual(non_promoted_levels["artifact_level_2_source_observed_artifact_listing"], 4)
        self.assertEqual(blocked_levels["artifact_level_0_mention_only"], 1)
        self.assertTrue(inventory["inflation_prevented"])

    def test_non_promoted_leads_keep_evidence_value_without_becoming_truth(self) -> None:
        leads = non_promoted_lead_records(load_non_promoted_artifact_leads())

        self.assertEqual(len(leads), 8)
        self.assertEqual({lead["decision"] for lead in leads}, {"request_more_evidence", "mark_near_miss"})
        self.assertEqual({lead["status"] for lead in leads}, {"need", "near_miss", "unavailable"})
        for lead in leads:
            self.assertFalse(lead["verified_artifact"])
            self.assertTrue(lead["required_evidence"])

    def test_query_coverage_and_source_references_remain_manual_only(self) -> None:
        coverage = {item["query_id"]: item for item in query_coverage_records(load_query_coverage())}
        refs = source_reference_records(load_source_reference_index())

        self.assertEqual(coverage["hq_driver_win98"]["best_artifact_status"], "blocked_for_user_details")
        self.assertEqual(coverage["hq_windows_7_apps"]["best_artifact_status"], "reviewed_artifact_record")
        self.assertEqual(coverage["hq_firefox_last_xp"]["best_artifact_status"], "reviewed_artifact_record")
        for item in coverage.values():
            self.assertFalse(item["public_alpha_ready"])

        self.assertEqual(len(refs), 11)
        for ref in refs:
            self.assertTrue(ref["manual_reference_only"])
            self.assertFalse(ref["runtime_source_call_performed"])
            self.assertFalse(ref["download_performed"])
            self.assertFalse(ref["file_fetch_performed"])
            self.assertFalse(ref["wayback_replay_performed"])

    def test_gap_and_blocker_reports_preserve_followup_paths(self) -> None:
        evidence_gaps = read_batch_text("evidence_gap_queue.yml")
        verification_gaps = read_batch_text("verification_gap_queue.yml")
        blockers = read_batch_text("blocked_for_user_details.yml")

        self.assertIn("ARTIFACT-EVIDENCE-GAP-BATCH-00", evidence_gaps)
        self.assertIn("exact_binary_package_identity", verification_gaps)
        self.assertIn("USER-HARDWARE-DETAILS-00", blockers)
        self.assertIn("device_id_or_chipset", blockers)


if __name__ == "__main__":
    unittest.main()

