import json
import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_evidence import (
    build_ia_evidence_boundary_report,
    build_ia_evidence_candidates,
    build_ia_evidence_write_report,
    load_default_ia_source_cache_records,
    load_ia_evidence_policy,
    to_evidence_candidate_record,
)


ROOT = Path(__file__).resolve().parents[2]


class IAEvidenceBoundaryTests(unittest.TestCase):
    def test_ledger_payload_omits_reserved_truth_fields(self):
        policy = load_ia_evidence_policy(ROOT / "control/policies/ia_evidence_ledger_policy.json")
        source_record = load_default_ia_source_cache_records(include_live_preview=False)[0]
        candidate = build_ia_evidence_candidates(source_record, policy)[0]
        ledger_record = to_evidence_candidate_record(candidate)
        text = json.dumps(ledger_record.to_dict(), sort_keys=True)
        self.assertNotIn("accepted_truth", text)
        self.assertNotIn("master_index_mutated", text)
        self.assertNotIn("public_index_mutated", text)

    def test_boundary_report_keeps_index_and_download_mutations_false(self):
        report = build_ia_evidence_write_report(
            [],
            dry_run=True,
            store_result={"write_applied": False},
            write_scope="dry_run_no_instance_mutation",
        )
        boundary = build_ia_evidence_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertFalse(boundary["accepted_truth_created"])
        self.assertFalse(boundary["candidate_index_mutated"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])
        self.assertFalse(boundary["download_performed"])


if __name__ == "__main__":
    unittest.main()
