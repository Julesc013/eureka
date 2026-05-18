import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IALiveMetadataProbeBoundaryTests(unittest.TestCase):
    def test_boundary_report_keeps_mutation_download_and_provider_flags_false(self):
        path = ROOT / "control/inventory/ia_live_probe_boundary_report.json"
        boundary = json.loads(path.read_text(encoding="utf-8"))
        for key in (
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
        self.assertFalse(boundary["raw_response_committed"])

    def test_normalized_preview_never_claims_truth(self):
        path = ROOT / "control/inventory/ia_live_probe_normalized_preview.json"
        preview = json.loads(path.read_text(encoding="utf-8"))
        for record in preview.get("preview_records", []):
            self.assertTrue(record["review_required"])
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["download_performed"])
            self.assertFalse(record["source_cache_write_performed"])
            self.assertFalse(record["evidence_ledger_write_performed"])
            self.assertFalse(record["candidate_index_mutated"])
            self.assertFalse(record["reviewed_index_mutated"])
            self.assertFalse(record["master_index_mutated"])

    def test_redacted_summary_has_no_raw_response_body(self):
        path = ROOT / "control/inventory/ia_live_probe_result_summary.json"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("body_text", text)
        self.assertNotIn("response_body", text)
        summary = json.loads(text)
        self.assertFalse(summary["raw_response_committed"])


if __name__ == "__main__":
    unittest.main()
