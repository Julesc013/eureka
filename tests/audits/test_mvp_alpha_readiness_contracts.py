
import json
import unittest
from pathlib import Path

from scripts.validate_mvp_alpha_audit import detect_forbidden_mvp_claims, validate_mvp_alpha_audit

REPO_ROOT = Path(__file__).resolve().parents[2]


class MvpAlphaReadinessContractTests(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_contracts_and_examples_validate(self) -> None:
        report = validate_mvp_alpha_audit(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_integration_matrix_covers_required_rows(self) -> None:
        matrix = self.load("examples/audits/mvp_alpha/mvp_alpha_integration_matrix_v0.json")
        rows = {row["component_id"] for row in matrix["rows"]}
        self.assertIn("track_b_local_foundry", rows)
        self.assertIn("h1_metadata_wave", rows)
        self.assertIn("track_e_hosting_readiness", rows)
        self.assertIn("obs_side_lane_status", rows)
        for row in matrix["rows"]:
            self.assertTrue(row["product_boundary_preserved"])
            self.assertTrue(row["truth_boundary_preserved"])

    def test_readiness_audit_keeps_claim_boundary_false(self) -> None:
        audit = self.load("examples/audits/mvp_alpha/mvp_alpha_readiness_audit_v0.json")
        self.assertEqual(audit["audit_status"], "pass_with_warnings")
        self.assertFalse(audit["truth_boundary"]["readiness_audit_is_launch"])
        self.assertFalse(audit["truth_boundary"]["operator_signoff_inferred"])
        self.assertFalse(audit["product_boundary"]["deployment_performed"])

    def test_forbidden_claim_detector_rejects_unsafe_truth(self) -> None:
        errors = detect_forbidden_mvp_claims({"truth_boundary": {"public_index_mutated": True}})
        self.assertTrue(errors)
        errors = detect_forbidden_mvp_claims({"product_boundary": {"enabled_downloads": True}})
        self.assertTrue(errors)
        errors = detect_forbidden_mvp_claims({"truth_boundary": {"rights_clearance_claimed": True}})
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
