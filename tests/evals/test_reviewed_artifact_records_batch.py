from __future__ import annotations

import unittest

from evals.hard_queries.artifact_reviews.batch_00 import load_review_decisions, review_decision_records
from evals.hard_queries.reviewed_artifact_records.batch_00 import (
    load_artifact_record_counts,
    load_non_promoted_artifact_leads,
    load_query_coverage,
    load_reviewed_artifact_records,
    load_source_reference_index,
    load_verified_artifacts,
    non_promoted_lead_records,
    query_coverage_records,
    reviewed_artifact_record_records,
    source_reference_records,
    validate_artifact_record_counts,
    validate_non_promoted_artifact_leads,
    validate_query_coverage,
    validate_reviewed_artifact_records,
    validate_source_reference_index,
    validate_verified_artifacts,
)


class ReviewedArtifactRecordsBatchTests(unittest.TestCase):
    def test_reviewed_artifact_record_package_validates(self) -> None:
        self.assertEqual(validate_reviewed_artifact_records(load_reviewed_artifact_records()), ())
        self.assertEqual(validate_verified_artifacts(load_verified_artifacts()), ())
        self.assertEqual(validate_non_promoted_artifact_leads(load_non_promoted_artifact_leads()), ())
        self.assertEqual(validate_artifact_record_counts(load_artifact_record_counts()), ())
        self.assertEqual(validate_query_coverage(load_query_coverage()), ())
        self.assertEqual(validate_source_reference_index(load_source_reference_index()), ())

    def test_only_promote_decisions_materialize_reviewed_artifact_records(self) -> None:
        promoted_ids = {
            item["reviewed_artifact_record_id"]
            for item in review_decision_records(load_review_decisions())
            if item["review_decision"] == "promote"
        }
        reviewed_ids = {
            item["reviewed_artifact_record_id"]
            for item in reviewed_artifact_record_records(load_reviewed_artifact_records())
        }

        self.assertEqual(reviewed_ids, promoted_ids)
        self.assertEqual(len(reviewed_ids), 2)

    def test_reviewed_artifact_records_are_not_verified_artifacts(self) -> None:
        for record in reviewed_artifact_record_records(load_reviewed_artifact_records()):
            self.assertEqual(record["artifact_claim_status"], "reviewed_artifact_record")
            self.assertEqual(record["artifact_level"], "artifact_level_3_artifact_identity_evidence")
            self.assertEqual(record["canonical_status"], "verified")
            self.assertFalse(record["verified_artifact"])
            self.assertFalse(record["rights_clearance_claimed"])
            self.assertFalse(record["malware_safety_claimed"])
            self.assertFalse(record["download_offered"])
            self.assertFalse(record["reviewed_index_mutated"])
            self.assertIn("verified artifact", record["must_not_claim"])
            self.assertIn("integrity evidence", record["missing_for_verified_artifact"])

        self.assertEqual(load_verified_artifacts()["verified_artifact_count"], 0)
        self.assertEqual(load_verified_artifacts()["verified_artifacts"], [])

    def test_non_promoted_leads_remain_non_truth_states(self) -> None:
        leads = non_promoted_lead_records(load_non_promoted_artifact_leads())

        self.assertEqual(len(leads), 8)
        self.assertEqual({lead["decision"] for lead in leads}, {"request_more_evidence", "mark_near_miss"})
        self.assertEqual({lead["status"] for lead in leads}, {"need", "near_miss", "unavailable"})
        for lead in leads:
            self.assertNotEqual(lead["decision"], "promote")

    def test_counts_and_query_coverage_keep_alpha_blocked(self) -> None:
        counts = load_artifact_record_counts()
        coverage = load_query_coverage()
        coverage_by_query = {item["query_id"]: item for item in query_coverage_records(coverage)}

        self.assertEqual(counts["reviewed_artifact_record_count"], 2)
        self.assertEqual(counts["verified_artifact_count"], 0)
        self.assertEqual(counts["public_alpha_artifact_gate"], "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS")
        self.assertEqual(coverage["hard_query_reviewed_artifact_coverage"], "2/6")
        self.assertEqual(coverage["hard_query_verified_artifact_coverage"], "0/6")
        self.assertEqual(coverage_by_query["hq_driver_win98"]["best_status"], "blocked_for_user_details")
        for item in coverage_by_query.values():
            self.assertFalse(item["public_alpha_ready"])

    def test_source_references_are_manual_review_references_only(self) -> None:
        refs = source_reference_records(load_source_reference_index())

        self.assertEqual(len(refs), 3)
        for ref in refs:
            self.assertEqual(ref["source_posture"], "manual_reference_only")
            self.assertFalse(ref["runtime_source_call_performed"])
            self.assertFalse(ref["download_performed"])
            self.assertFalse(ref["file_fetch_performed"])
            self.assertFalse(ref["wayback_replay_performed"])


if __name__ == "__main__":
    unittest.main()
