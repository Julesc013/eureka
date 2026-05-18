import json
import unittest
from pathlib import Path

from runtime.source_observation.internet_archive_candidate_index import (
    build_ia_candidate_boundary_report,
    build_ia_candidate_write_report,
    build_ia_candidates_from_evidence,
    load_default_ia_evidence_candidates,
    load_ia_candidate_policy,
)


ROOT = Path(__file__).resolve().parents[2]


class IACandidateBoundaryTests(unittest.TestCase):
    def test_candidate_records_omit_reviewed_truth_mutation_flags(self):
        policy = load_ia_candidate_policy(ROOT / "control/policies/ia_candidate_index_policy.json")
        candidate = build_ia_candidates_from_evidence(load_default_ia_evidence_candidates()[:4], policy)[0]
        text = json.dumps(candidate, sort_keys=True)
        self.assertIn('"review_required": true', text)
        self.assertIn('"accepted_truth": false', text)
        self.assertIn('"reviewed_record_created": false', text)
        self.assertIn('"master_index_mutation_performed": false', text)

    def test_boundary_report_keeps_reviewed_and_master_mutations_false(self):
        report = build_ia_candidate_write_report(
            [],
            dry_run=True,
            store_result={"write_applied": False},
            write_scope="dry_run_no_instance_mutation",
        )
        boundary = build_ia_candidate_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertFalse(boundary["accepted_truth_created"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])
        self.assertFalse(boundary["download_performed"])


if __name__ == "__main__":
    unittest.main()
