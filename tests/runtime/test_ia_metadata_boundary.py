import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_fixture_replay import replay_fixture_directory_report
from runtime.source.observation.internet_archive_validation import validate_boundary_report, validate_normalized_ia_record


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "examples" / "internet_archive_metadata"


class IAMetadataBoundaryTests(unittest.TestCase):
    def test_normalized_records_require_review_and_do_not_claim_truth(self):
        report = replay_fixture_directory_report(FIXTURE_DIR)
        for record in report["normalized_records"]:
            self.assertEqual((), validate_normalized_ia_record(record))
            self.assertTrue(record["review_required"])
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["source_cache_write_performed"])
            self.assertFalse(record["evidence_ledger_write_performed"])
            self.assertFalse(record["index_mutation_performed"])

    def test_boundary_reports_have_no_side_effects(self):
        report = replay_fixture_directory_report(FIXTURE_DIR)
        for boundary in report["boundary_reports"]:
            self.assertEqual((), validate_boundary_report(boundary))
            self.assertTrue(boundary["passed"])
            self.assertFalse(boundary["network_imports_detected"])
            for key in (
                "live_source_call_performed",
                "source_probe_executed",
                "source_cache_write_performed",
                "evidence_ledger_write_performed",
                "candidate_index_mutated",
                "reviewed_index_mutated",
                "master_index_mutated",
                "download_performed",
                "upload_performed",
                "model_provider_used",
                "deployment_performed",
                "production_readiness_claimed",
                "public_launch_readiness_claimed",
            ):
                self.assertFalse(boundary[key], key)

    def test_no_download_proof_passes(self):
        report = replay_fixture_directory_report(FIXTURE_DIR)
        records = {record["fixture_id"]: record for record in report["normalized_records"]}
        proof = records["no_download_proof"]
        self.assertTrue(proof["file_metadata_candidates"])
        self.assertFalse(proof["download_performed"])


if __name__ == "__main__":
    unittest.main()
